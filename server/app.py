from flask import Flask, request, jsonify, render_template, send_file, Response, make_response
import threading
from collections import defaultdict
from natsort import natsorted
import numbers
import re
import numpy as np
import math

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

# Server-sent events and state
cv = threading.Condition()

# Multiple simultaneous users
client_idx = 0
clients = dict()

def make_state():
    state = dict()

    # Which content pane is visible
    state['content'] = None

    # Overview content pane
    state['overview_html'] = None

    # Phenotype content pane
    state['pheno_img'] = None
    state['pheno_field']= None

    # Connectivity content pane
    state['conn_types'] = dict()
    state['conn_tasks'] = dict()
    state['conn_fields'] = dict()
    state['conn_subs'] = []
    state['conn_page'] = 1
    state['n_conn_per_page'] = 20
    state['conn_summary_img'] = None

    # Correlation content pane
    state['corr_group'] = None
    state['corr_img']= None
    state['corr_pval'] = None
    state['corr_pheno'] = None
    state['corr_cat'] = None
    state['corr_var'] = None
    state['corr_task_types'] = None
    state['corr_stats'] = None

    # Cohorts
    state['cohorts'] = cohort.ls_cohorts()
    state['sel_cohort'] = None
    state['sel_cohort_df'] = None

    # List of groups, their id, and whether they are checked
    state['groups'] = [dict(name='All', sel=False)]

    # Subjects and subject pagination
    state['n_subs_per_page'] = 8
    state['subs'] = []
    state['filtered_subs'] = state['subs']
    state['subs_page'] = 1
    state['subs_checked'] = defaultdict(bool)

    # Saved images
    state['saved_imgs'] = dict()
    state['saved_count'] = 0
    state['saved_desc'] = dict()

    # For server-sent events
    state['to_update'] = dict(Cohorts=True, GroupsList=True, SubsPagination=True, 
                              SubsList=True, Overview=False, Phenotypes=False,
                              Correlation=False, Connectivity=False, ImageMath=False)

    return state

def next_saved_id(state):
    m = state['saved_count']
    sid = []
    while True:
        n = m%26+1
        sid.append(chr(64+n))
        m = math.floor(m/26)
        if m <= 0:
            break
    state['saved_count'] += 1
    return ''.join(sid[::-1])

# Home screen
@app.route('/')
def index():
    global clients, client_idx
    resp = make_response(render_template('index.html'))
    resp.set_cookie('client_idx', str(client_idx))
    clients[client_idx] = make_state()
    client_idx += 1
    return resp

def get_component(comp, idx):
    with app.app_context():
        global clients
        state = clients[idx]
        if comp == 'GroupsList':
            html = render_template('groups-list.html', groups=enumerate(state['groups']))
            return html
        if comp == 'SubsPagination':
            if len(state['filtered_subs']) == 0:
                view_pages = []
                has_prev = False
                has_next = False
            else:
                filtered_subs = state['filtered_subs']
                n_subs_per_page = state['n_subs_per_page']
                subs_page = state['subs_page']
                last_page = (len(filtered_subs)-1) // n_subs_per_page + 1
                pages = list(range(1, last_page + 1))
                subs_page = state['subs_page']
                st = subs_page-3 if subs_page > 2 else 0
                end = subs_page+2
                view_pages = pages[st:end]
                has_prev = subs_page > 1
                has_next = subs_page < last_page
            html = render_template('subs-pagination.html', view_pages=view_pages, has_prev=has_prev, has_next=has_next)
            return html
        if comp == 'SubsList':
            filtered_subs = state['filtered_subs']
            n_subs_per_page = state['n_subs_per_page']
            subs_page = state['subs_page']
            subs_checked = state['subs_checked']
            subs = state['subs']
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
            cohorts = state['cohorts']
            if state['sel_cohort'] is not None:
                sel_cohort_name = state['sel_cohort']['name']
            else:
                sel_cohort_name = None
            html = render_template('cohorts.html', cohorts=cohorts, sel_cohort=sel_cohort_name)
            return html
        if comp == 'Overview':
            overview_html = state['overview_html']
            if overview_html is None:
                return '<div></div>'
            else:
                return overview_html
        if comp == 'Phenotypes':
            sel_cohort_df = state['sel_cohort_df']
            pheno_img = state['pheno_img']
            pheno_field = state['pheno_field']
            have_img = pheno_img is not None
            fields = sel_cohort_df.columns if sel_cohort_df is not None else []
            html = render_template('phenotypes.html', data=pheno_img, have_img=have_img, fields=fields, sel_field=pheno_field)
            return html
        if comp == 'Correlation':
            corr_group = state['corr_group']
            corr_img = state['corr_img']
            corr_pval = state['corr_pval']
            corr_pheno = state['corr_pheno']
            corr_cat = state['corr_cat']
            corr_var = state['corr_var']
            corr_task_types = state['corr_task_types']
            corr_stats = state['corr_stats']
            sel_cohort = state['sel_cohort']
            sel_cohort_df = state['sel_cohort_df']
            grps = [g['name'] for g in state['groups']]
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
                state['corr_task_types'] = task_types
            html = render_template('correlation.html', groups=grps, sel_group=corr_group, corr_img=corr_img, pval_img=corr_pval, 
                                   phenos=phenos, sel_pheno=corr_pheno, cats=cats, sel_cat=corr_cat, sel_var=corr_var, resp_vars=rvars, 
                                   stats=corr_stats)
            return html
        if comp == 'Connectivity':
            summary = state['conn_summary_img']
            if summary is not None:
                html = render_template('connectivity.html', summary_img=summary)
                return html
            conn_types = state['conn_types']
            conn_tasks = state['conn_tasks']
            conn_fields = state['conn_fields']
            sel_cohort = state['sel_cohort']
            sel_cohort_df = state['sel_cohort_df']
            # Initialize types
            if len(conn_types) == 0 and sel_cohort is not None:
                conns = sel_cohort['conn']
                tasks = set()
                types = set()
                for f in conns:
                    m = re.match('.*task-([^_]+).*_([^.]+)\.[^.]+$', f)
                    if m is not None:
                        tasks.add(m.group(1))
                        types.add(m.group(2))
                for typ in types:
                    conn_types[typ] = True
                for task in tasks:
                    conn_tasks[task] = True
                for field in sel_cohort_df.columns:
                    conn_fields[field] = False
            html = render_template('connectivity.html', summary_img=None, conn_types=conn_types, conn_tasks=conn_tasks, conn_fields=conn_fields)
            return html
            
# Server-sent events
@app.route('/sse')
def sse():
    global clients
    my_client_idx = int(request.cookies.get('client_idx'))
    print(my_client_idx)
    def event_stream():
        while True:
            with cv:
                for client_idx, state in clients.items():
                    if my_client_idx == client_idx:
                        to_update = state['to_update']
                        for comp, upd in to_update.items():
                            if upd:
                                to_update[comp] = False
                                data = get_component(comp, client_idx)
                                data = " ".join(line.strip() for line in data.splitlines())
                                msg = f'event: {comp}\ndata: {data}\n\n'
                                yield msg
                cv.wait()
    return Response(event_stream(), mimetype='text/event-stream')

# Create a group
@app.route('/create-group', methods=['POST'])
def create_group():
    args = request.form
    my_client_idx = int(request.cookies.get('client_idx'))
    err = validate_args(['group-text'], args, '/create-group')
    if err is not None:
        print(err)
        return jsonify(err)
    global clients
    state = clients[my_client_idx]
    groups = state['groups']
    to_update = state['to_update']
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    err = validate_args(['filter-text'], args, '/filter-subjects')
    if err is not None:
        print(err)
        return jsonify(err)
    pattern = args['filter-text']
    subs = state['subs']
    subs_page = state['subs_page']
    n_subs_per_page = state['n_subs_per_page']
    to_update = state['to_update']
    state['filtered_subs'] = [s for s in subs if pattern in str(s)]
    if len(state['filtered_subs']) < (subs_page-1) * n_subs_per_page + 1:
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    if err is not None:
        print(err)
        return jsonify(err)
    p = args['page']
    filtered_subs = state['filtered_subs']
    n_subs_per_page = state['n_subs_per_page']
    if p == 'First':
        state['subs_page'] = 1
    elif p == 'Last':
        state['subs_page'] = (len(filtered_subs)+1) // n_subs_per_page + 1
    else:
        state['subs_page'] = int(p)
    to_update = state['to_update']
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    if err is not None:
        print(err)
        return jsonify(err)
    subs_checked = state['subs_checked']
    to_update = state['to_update']
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    if err is not None:
        print(err)
        return ('', 204)
    coh = args['cohort']
    if coh == '':
        return ('', 204)
    to_update = state['to_update']
    content = state['content']
    state['sel_cohort'] = cohort.get_cohort(coh)
    state['sel_cohort_df'] = data.demo2df(state['sel_cohort']['demo'])
    state['subs'] = natsorted(list(state['sel_cohort_df'].index))
    state['filtered_subs'] = state['subs']
    state['overview_html'] = None
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    if state['sel_cohort'] is None:
        return ('', 204)
    state['content'] = 'Overview'
    if state['overview_html'] is None:
        demo = state['sel_cohort']['demo']
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
        state['overview_html'] = render_template('overview.html', stats=stats)
        to_update = state['to_update']
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
    idx = int(args['group'])
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    groups = state['groups']
    content = state['content']
    to_update = state['to_update']
    groups[idx]['sel'] = not groups[idx]['sel']
    to_update['Phenotypes'] = True
    if content == 'Phenotypes':
        phenotypes_panel()
    return ('', 204)

# Phenotypes panel
@app.route('/phenotypes', methods=['POST'])
def phenotypes_panel():
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    sel_cohort_df = state['sel_cohort_df']
    groups = state['groups']
    pheno_field = state['pheno_field']
    if sel_cohort_df is None:
        state['pheno_img'] = None
        return ('', 204)
    if pheno_field is None:
        state['pheno_img'] = None
        return ('', 204)
    queries = [g['name'] for g in groups if g['sel']]
    grps = dict()
    for query in queries:
        if query == 'All':
            grps['All'] = state['subs']
            continue
        try:
            g = [str(i) for i in list(sel_cohort_df.query(query).index)]
            if len(g) > 0:
                grps[query] = g
        except:
            print(f'Bad group {query}')
    if len(grps) == 0:
        state['pheno_img'] = None
    else:
        state['pheno_img'] = image.groups_hist(sel_cohort_df, grps, pheno_field)
    state['content'] = 'Phenotypes'
    state['to_update']['Phenotypes'] = True
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    field = args['field']
    if field == '':
        return ('', 204)
    state['pheno_field'] = field
    phenotypes_panel()
    return ('', 204)

# Correlation panel
@app.route('/correlation', methods=['POST'])
def correlation_panel():
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    state['content'] = 'Correlation'
    state['to_update']['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Select phenotype in correlation
@app.route('/corr-change-select', methods=['POST'])
def corr_select_pheno():
    args = request.form
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    state['corr_group'] = args['group'] if args['group'] != '' else None
    state['corr_pheno'] = args['pheno'] if args['pheno'] != '' else None
    state['corr_var'] = args['var'] if args['var'] != '' else None
    state['corr_cat'] = args['cat'] if 'cat' in args else None
    state['to_update']['Correlation'] = True
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
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    if state['sel_cohort'] is None:
        return ('', 204)
    state['corr_group'] = args['group']
    state['corr_pheno'] = args['pheno']
    state['corr_var'] = args['var']
    state['corr_cat'] = args['cat'] if 'cat' in args else None
    sel_cohort = state['sel_cohort']
    sel_cohort_df = state['sel_cohort_df']
    corr_group = state['corr_group']
    corr_pheno = state['corr_pheno']
    corr_var = state['corr_var']
    corr_cat = state['corr_cat']
    corr_task_types = state['corr_task_types']
    to_update = state['to_update']
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
        state['corr_img'], state['corr_pval'] = correlation.corr_conn_pheno(sel_cohort['name'], sel_cohort_df, corr_group, typ, tasks, corr_pheno, corr_cat)
        corr_stats = None
    else:
        state['corr_img'], rho, df, pval = correlation.corr_pheno_pheno(sel_cohort['name'], sel_cohort_df, corr_group, corr_pheno, corr_var, corr_cat)
        state['corr_pval'] = None
        state['corr_stats'] = {'rho': decim(rho), 'df': df, 'pval': decim(pval)}
    to_update['Correlation'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Connectivity panel
@app.route('/connectivity', methods=['POST'])
def connectivity_panel():
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    state['content'] = 'Connectivity'
    state['conn_summary_img'] = None
    state['to_update']['Connectivity'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Connectivity panel checkbox selection changed
@app.route('/conn-change-checked', methods=['POST'])
def connectivity_checked_changed():
    args = request.form
    # Args can be variable and are preceded by type- task- and field-
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    state['content'] = 'Connectivity'
    state['to_update']['Connectivity'] = True
    conn_types = state['conn_types']
    conn_tasks = state['conn_tasks']
    conn_fields = state['conn_fields']
    for typ in conn_types:
        conn_types[typ] = False
    for task in conn_tasks:
        conn_tasks[task] = False
    for field in conn_fields:
        conn_fields[field] = False
    for typ in conn_types:
        for k in args:
            if k == f'type-{typ}':
                conn_types[typ] = True
    for task in conn_tasks:
        for k in args:
            if k == f'task-{task}':
                conn_tasks[task] = True
    # ID always displayed
    for field in conn_fields:
        for k in args:
            if k == f'field-{field}':
                conn_fields[field] = True
    with cv:
        cv.notify_all()
    return ('', 204)

# Connectivity mean image
@app.route('/conn-mean', methods=['POST'])
def get_connectivity_mean():
    my_client_idx = int(request.cookies.get('client_idx'))
    args = request.form
    if 'mean' not in args and 'std' not in args:
        print('Not mean or std img')
        return ('', 204)
    global clients
    state = clients[my_client_idx]
    sel_cohort = state['sel_cohort']
    sel_cohort_df = state['sel_cohort_df']
    conn_types = state['conn_types']
    conn_tasks = state['conn_tasks']
    groups = state['groups']
    if sel_cohort == None:
        print('No cohort selected')
        return ('', 204)
    # Get subjects
    group_subs = set()
    group_descs = list()
    for g in groups:
        if g['sel']:
            if g['name'] == 'All':
                group_subs.update(sel_cohort_df.index)
                group_descs = ['All']
                break
            else:
                group_subs.update(sel_cohort_df.query(g['name']).index)
                group_descs.append(g['name'])
    if len(group_subs) == 0:
        print('No subjects selected')
        return ('', 204)
    ps = []
    # Sorts by subject since it's first field
    for f in natsorted(sel_cohort['conn']):
        m = re.match('(.*)_task-([^_]+)_?[^_]*_([^.]+)\.[^.]+$', f)
        if m:
            sub = m.group(1)
            task = m.group(2)
            typ = m.group(3)
            if sub not in group_subs:
                continue
            if conn_types[typ] and conn_tasks[task]:
                ps.append(np.load(f'data/{sel_cohort["name"]}/conn/{f}'))
    if len(ps) == 0:
        print('No connectivity files')
        return ('', 204)    
    summary = None
    sum_im_type = None
    if 'mean' in args:
        sum_im_type = 'mean'
        summary = np.mean(ps, axis=0)
    elif 'std' in args:
        sum_im_type = 'std'
        summary = np.std(ps, axis=0)
    summary = data.vec2mat(summary, fillones=False)
    # Save for image math
    saved_imgs = state['saved_imgs']
    saved_desc = state['saved_desc']
    sid = next_saved_id(state)
    saved_imgs[sid] = summary
    sum_types = []
    sum_tasks = []
    # Get conn types and tasks
    for c,sel in conn_types.items():
        if sel:
            sum_types.append(c)
    for c,sel in conn_tasks.items():
        if sel:
            sum_tasks.append(c)
    saved_desc[sid] = {'im_type': sum_im_type, 'types': sum_types, 'tasks': sum_tasks, 'groups': group_descs, 'nsubs': len(group_subs), 'nscans': len(ps)}
    print(saved_desc)
    summary = image.imshow(summary)
    state['content'] = 'Connectivity'
    state['to_update']['Connectivity'] = True
    state['conn_summary_img'] = summary
    with cv:
        cv.notify_all()
    return ('', 204)

# Connectivity panel
@app.route('/image-math', methods=['POST'])
def image_math_panel():
    my_client_idx = int(request.cookies.get('client_idx'))
    global clients
    state = clients[my_client_idx]
    state['content'] = 'ImageMath'
    state['to_update']['ImageMath'] = True
    with cv:
        cv.notify_all()
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True, threaded=True)
