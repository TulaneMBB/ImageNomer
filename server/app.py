from flask import Flask, request, jsonify, render_template, send_file, Response
import threading

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

# Which content view is active (Phenotypes, Connectivity, etc.)
content = None              

# List of groups, their id, and whether they are checked
groups = [dict(name='All', sel=False)]

# Subjects and subject pagination
n_subs_per_page = 8
subs = list(range(1, 100))
filtered_subs = subs
subs_page = 1

# For server-sent events
cv = threading.Condition()

to_update = dict(GroupsList=True, SubsPagination=True, SubsList=True)

# Home screen
@app.route('/')
def index():
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
            html = render_template('subs-list.html', subs=filtered_subs[st:end])
            return html

# Server-sent events
@app.route('/sse')
def sse():
    def event_stream():
        while True:
            with cv:
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
    with cv:
        cv.notify()
    return ('', 204)

# Filter subjects
@app.route('/filter-subjects', methods=['POST'])
def filter_subjects():
    args = request.form
    err = validate_args(['filter-text'], args, '/filter-subjects')
    if err is not None:
        print(err)
        return jsonify(err)
    global filtered_subs
    pattern = args['filter-text']
    filtered_subs = [s for s in subs if pattern in str(s)]
    if len(filtered_subs) < (subs_page-1) * n_subs_per_page + 1:
        subs_page = 1
    to_update['SubsPagination'] = True
    to_update['SubsList'] = True
    with cv:
        cv.notify()
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True, threaded=True)
