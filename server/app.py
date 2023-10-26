from flask import Flask, request, jsonify, render_template, send_file, Response
import threading
from collections import defaultdict
from natsort import natsorted
import numbers
import re

# Our modules
import cohort
import data
import image
import correlation

app = Flask(__name__,
    template_folder='../static',
    static_folder='../static')

def error(msg):
    return jsonify({'err': msg})

def validate_args(keywords, args, url):
    for kw in keywords:
        if kw not in args:
            return error(f'{kw} not in args ({url})')
    return None

# Content pane visible
content = None

# Overview content pane
overview_html = None

# Phenotype content pane
pheno_img = None
pheno_field = None

# Correlation content pane
corr_group = None
corr_img = None
corr_pval = None
corr_pheno = None
corr_cat = None
corr_var = None
corr_task_types = None

# Cohorts
cohorts = []
sel_cohort_name = None
sel_cohort = None
sel_cohort_df = None

# List of groups, their id, and whether they are checked
groups = [dict(name='All', sel=False)]

# Subjects and subject pagination
n_subs_per_page = 8
subs = []
filtered_subs = subs
subs_page = 1
subs_checked = defaultdict(bool)

# For server-sent events
cv = threading.Condition()

to_update = dict(Cohorts=True, GroupsList=True, SubsPagination=True, 
                 SubsList=True, Overview=False, Phenotypes=False,
                 Correlation=False)
client_idx = 0

# Home screen
@app.route('/')
def index():
    global client_idx, cohorts
    client_idx += 1
    cohorts = cohort.ls_cohorts()
    for k in to_update:
        to_update[k] = True
    return render_template('index.html')

def get_component(comp):
    with app.app_context():
        if comp == 'GroupsList':
            html = render_template('groups-list.html', groups=enumerate(groups))
            return html
        if comp == 'SubsPagination':
            if len(filtered_subs) == 0:
                view_pages = []
                has_prev = False
                has_next = False
            else:
                last_page = (len(filtered_subs)-1) // n_subs_per_page + 1
                pages = list(range(1, last_page + 1))
                st = subs_page-3 if subs_page > 2 else 0
                end = subs_page+2
                view_pages = pages[st:end]
                has_prev = subs_page > 1
                has_next = subs_page < last_page
            html = render_template('subs-pagination.html', view_pages=view_pages, has_prev=has_prev, has_next=has_next)
            return html
        if comp == 'SubsList':
            st = (subs_page-1) * n_subs_per_page
            end = st + n_subs_per_page
            checked = []
            for i in range(st, end):
                if i >= len(filtered_subs):
                    break
                sub = filtered_subs[i]
                checked.append(subs_checked[sub])
            nsel = 0
            for v in subs_checked.values():
                if v:
                    nsel += 1
            # Range is for sub indices
            html = render_template('subs-list.html', subs=zip(range(st, end), filtered_subs[st:end], checked), nsubs=len(subs), nsel=nsel)
            return html
        if comp == 'Cohorts':
            global sel_cohort_name, cohorts
            html = render_template('cohorts.html', cohorts=cohorts, sel_cohort=sel_cohort_name)
            return html
        if comp == 'Overview':
            global overview_html
            if overview_html is None:
                return '<div></div>'
            else:
                return overview_html
        if comp == 'Phenotypes':
            global sel_cohort_df, pheno_img, pheno_field
            have_img = pheno_img is not None
            fields = sel_cohort_df.columns if sel_cohort_df is not None else []
            html = render_template('phenotypes.html', data=pheno_img, have_img=have_img, fields=fields, sel_field=pheno_field)
            return html
        if comp == 'Correlation':
            global corr_group, corr_img, pval_img, corr_pheno, corr_cat, corr_var, corr_task_types
            grps = [g['name'] for g in groups]
            phenos = []
            cats = None
            if sel_cohort_df is not None:
                phenos = sel_cohort_df.columns
                demo = sel_cohort['demo']
                if corr_pheno in demo and len(demo[corr_pheno]) > 0:
                    sub, val = demo[corr_pheno].popitem()
                    # Put back
                    demo[corr_pheno][sub] = val
                    if not isinstance(val, numbers.Number):
                        cats = set()
                        for v in demo[corr_pheno].values():
                            cats.add(v)
                        cats = list(cats)
                if cats is None:
                    corr_cat = None
            rvars = [p for p in phenos]
            if sel_cohort is not None:
                conns = sel_cohort['conn']
                task_types = set()
                conn_types = set()
                for f in conns:
                    m = re.match('.*task-([^_]+).*_([^.]+)\.[^.]+$', f)
                    if m is not None:
                        task_types.add(f'{m.group(1)}_{m.group(2)}')
                        conn_types.add(f'All_{m.group(2)}')
                task_types = list(task_types)
                conn_types = list(conn_types)
                rvars += task_types
                rvars += conn_types
                corr_task_types = task_types
            html = render_template('correlation.html', groups=grps, sel_group=corr_group, corr_img=corr_img, pval_img=corr_pval, 
                                   phenos=phenos, sel_pheno=corr_pheno, cats=cats, sel_cat=corr_cat, sel_var=corr_var, resp_vars=rvars)
            return html
            
# Server-sent events
@app.route('/sse')
def sse():
    my_client_idx = client_idx
    def event_stream():
        while True:
            with cv:
                if my_client_idx != client_idx:
                    return
                for comp, upd in to_update.items():
                    if upd:
                        to_update[comp] = False
                        data = get_component(comp)
                        data = " ".join(line.strip() for line in data.splitlines())
                        msg = f'event: {comp}\ndata: {data}\n\n'
                        yield msg
                cv.wait()
    return Response(event_stream(), mimetype='text/event-stream')

# Create a group
@app.route('/create-group', methods=['POST'])
def create_group():
    args = request.form
    err = validate_args(['group-text'], args, '/create-group')
    if err is not None:
        print(err)
        return jsonify(err)
    groups.append(dict(name=args['group-text'], sel=False))
    to_update['GroupsList'] = True
    to_update['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Filter subjects
@app.route('/filter-subjects', methods=['POST'])
def filter_subjects():
    args = request.form
    err = validate_args(['filter-text'], args, '/filter-subjects')
    if err is not None:
        print(err)
        return jsonify(err)
    global filtered_subs, subs_page
    pattern = args['filter-text']
    filtered_subs = [s for s in subs if pattern in str(s)]
    if len(filtered_subs) < (subs_page-1) * n_subs_per_page + 1:
        subs_page = 1
    to_update['SubsPagination'] = True
    to_update['SubsList'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Change subjects page
@app.route('/subjects-page', methods=['POST'])
def change_subjects_page():
    args = request.form
    err = validate_args(['page'], args, '/subjects-page')
    if err is not None:
        print(err)
        return jsonify(err)
    global filtered_subs, subs_page
    p = args['page']
    if p == 'First':
        subs_page = 1
    elif p == 'Last':
        subs_page = (len(filtered_subs)+1) // n_subs_per_page + 1
    else:
        subs_page = int(p)
    to_update['SubsPagination'] = True
    to_update['SubsList'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Subject checked or unchecked
@app.route('/subject-checked', methods=['POST'])
def change_subject_checked():
    args = request.form
    err = validate_args(['subid'], args, '/subject-checked')
    if err is not None:
        print(err)
        return jsonify(err)
    global subs_checked
    subid = args['subid']
    subs_checked[subid] = False if subs_checked[subid] else True
    to_update['SubsList'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Cohort changed
@app.route('/cohort', methods=['POST'])
def change_cohort():
    args = request.form
    err = validate_args(['cohort'], args, '/cohort')
    if err is not None:
        print(err)
        return ('', 204)
    coh = args['cohort']
    if coh == '':
        return ('', 204)
    global sel_cohort_name, sel_cohort, sel_cohort_df, subs, filtered_subs, overview_html
    sel_cohort_name = coh
    sel_cohort = cohort.get_cohort(coh)
    sel_cohort_df = data.demo2df(sel_cohort['demo'])
    subs = natsorted(list(sel_cohort_df.index))
    filtered_subs = subs
    overview_html = None
    if content == 'Overview':
        overview_panel()
    for comp in to_update:
        to_update[comp] = True
    with cv:
        cv.notify_all()
    return ('', 204)

def decim(v):
    return "{:.2f}".format(v)

# Overview pane
@app.route('/overview', methods=['POST'])
def overview_panel():
    if sel_cohort is None:
        return ('', 204)
    global overview_html, content
    content = 'Overview'
    if overview_html is None:
        demo = sel_cohort['demo']
        # Get stats
        stats = []
        for col, vals in demo.items():
            if len(vals) == 0:
                continue
            sub, val = vals.popitem()
            # Replace after popitem
            vals[sub] = val
            d = dict(name=col, size=len(vals))
            if isinstance(val, numbers.Number):
                d['numeric'] = True
                d['min'] = decim(min(vals.values()))
                d['max'] = decim(max(vals.values()))
                d['mean'] = decim(sum(vals.values())/len(vals))
            else:
                counts = dict()
                for v in vals.values():
                    if v not in counts:
                        counts[v] = 1
                    else:
                        counts[v] += 1
                counts = [(c,v) for v,c in counts.items()]
                counts.sort(key=lambda x: x[0], reverse=True)
                d['counts'] = counts
                d['numeric'] = False
            stats.append(d)
        overview_html = render_template('overview.html', stats=stats)
        to_update['Overview'] = True
        with cv:
            cv.notify_all()
    return ('', 204)

# Group checked
@app.route('/group-checked', methods=['POST'])
def change_group_checked():
    args = request.form
    err = validate_args(['group'], args, '/group-checked')
    if err is not None:
        print(err)
        return ('', 204)
    global groups, content
    idx = int(args['group'])
    groups[idx]['sel'] = not groups[idx]['sel']
    to_update['Phenotypes'] = True
    if content == 'Phenotypes':
        phenotypes_panel()
    return ('', 204)

# Phenotypes panel
@app.route('/phenotypes', methods=['POST'])
def phenotypes_panel():
    global sel_cohort_df, groups, pheno_img, content, pheno_field
    if sel_cohort_df is None:
        pheno_img = None
        return ('', 204)
    if pheno_field is None:
        pheno_img = None
        return ('', 204)
    queries = [g['name'] for g in groups if g['sel']]
    grps = dict()
    for query in queries:
        if query == 'All':
            grps['All'] = subs
            continue
        try:
            g = [str(i) for i in list(sel_cohort_df.query(query).index)]
            if len(g) > 0:
                grps[query] = g
        except:
            print(f'Bad group {query}')
    if len(grps) == 0:
        pheno_img = None
    else:
        pheno_img = image.groups_hist(sel_cohort_df, grps, pheno_field)
    content = 'Phenotypes'
    to_update['Phenotypes'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Phenotypes panel field
@app.route('/phenotypes-field', methods=['POST'])
def change_phenotypes_field():
    args = request.form
    err = validate_args(['field'], args, '/phenotypes-field')
    if err is not None:
        print(err)
        return ('', 204)
    global pheno_field
    field = args['field']
    if field == '':
        return ('', 204)
    pheno_field = field
    phenotypes_panel()
    return ('', 204)

# Correlation panel
@app.route('/correlation', methods=['POST'])
def correlation_panel():
    content = 'Correlation'
    to_update['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Select phenotype in correlation
@app.route('/corr-change-select', methods=['POST'])
def corr_select_pheno():
    args = request.form
    global corr_group, corr_pheno, corr_var, corr_cat
    corr_group = args['group'] if args['group'] != '' else None
    corr_pheno = args['pheno'] if args['pheno'] != '' else None
    corr_var = args['var'] if args['var'] != '' else None
    corr_cat = args['cat'] if 'cat' in args else None
    to_update['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Create correlation plots
@app.route('/get-correlation', methods=['POST'])
def get_correlation_plots():
    args = request.form
    err = validate_args(['group', 'pheno', 'var'], args, '/get-correlation')
    if err is not None:
        print(err)
        return ('', 204)
    if sel_cohort is None:
        return ('', 204)
    global corr_img, corr_group, corr_pval, corr_pheno, corr_var, corr_cat
    corr_group = args['group']
    corr_pheno = args['pheno']
    corr_var = args['var']
    corr_cat = args['cat'] if 'cat' in args else None
    # FC or SNPs
    # Otherwise phenotype-phenotype correlation
    if corr_var not in sel_cohort_df.columns:
        task, typ = corr_var.split('_')
        # Get all tasks associated with type
        if task == 'All':
            tasks = [t.split('_') for t in corr_task_types]
            tasks = [t[0] for t in tasks if t[1] == typ and t[0] != 'All']
        else:
            tasks = [task]
        corr_img, corr_pval = correlation.corr_conn_pheno(sel_cohort['name'], sel_cohort_df, corr_group, typ, tasks, corr_pheno, corr_cat)
    else:
        corr_img, rho, df, pval = correlation.corr_pheno_pheno(sel_cohort['name'], sel_cohort_df, corr_group, corr_pheno, corr_var, corr_cat)
    to_update['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True, threaded=True)
