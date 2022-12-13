from flask import Flask, request, jsonify, render_template
import os
import json

# Our modules
import power
import data
import image
import cohort
import correlation

app = Flask(__name__,
    template_folder='../dist',
    static_folder='../dist/static')

def error(msg):
    return jsonify({'err': msg})

def validate_args(keywords, args, url):
    for kw in keywords:
        if kw not in args:
            return error(f'{kw} not in args ({url})')
    return None

'''Home screen'''
@app.route('/')
def index():
    return render_template('index.html')

'''List cohorts'''
@app.route('/data/list', methods=(['GET']))
def list():
    args = request.args
    task = args['task'] if 'task' in args else None
    return jsonify({'cohorts': cohort.ls_cohorts('anton')})

'''Get info about subjects'''
@app.route('/data/info', methods=(['GET']))
def info():
    args = request.args
    args_err = validate_args(['cohort'], args, request.url) 
    if args_err:
        return args_err
    coh = args['cohort']
    return jsonify(cohort.get_cohort('anton', coh))

'''Get subgroup of cohort'''
@app.route('/data/group', methods=(['GET']))
def group():
    args = request.args
    args_err = validate_args(['cohort', 'query'], args, request.url) 
    if args_err:
        return args_err
    cohort = args['cohort']
    query = args['query']
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    group = data.make_group_query(df, query)
    return jsonify(group)

'''Get demographics graph'''
@app.route('/data/demo/hist', methods=(['GET', 'POST']))
def demo_hist():
    if request.method == 'GET':
        args = request.args
    else:
        args = request.form
    args_err = validate_args(['cohort', 'groups', 'field'], args, request.url)
    if args_err:
        return args_err
    cohort = args['cohort']
    field = args['field']
    groups = json.loads(args['groups'])
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    img = image.groups_hist(df, groups, field)
    return jsonify({'data': img})

'''Get or post subject FC'''
@app.route('/data/fc', methods=(['GET']))
def fc():
    args = request.args
    # Optional: task, session
    args_err = validate_args(['cohort', 'sub'], args, request.url) 
    if args_err:
        return args_err
    # Params
    cohort = args['cohort']
    sub = args['sub']
    task = args['task'] if 'task' in args else None
    ses = args['ses'] if 'ses' in args else None
    colorbar = 'colorbar' in args
    remap = 'remap' in args
    # Load and display FC
    fc = data.get_fc('anton', cohort, sub, task, ses)
    fc = data.vec2mat(fc)
    if remap:
        fc = power.remap(fc)
    img = image.imshow(fc, colorbar)
    return jsonify({'data': img})

@app.route('/analysis/corr/demo', methods=(['GET']))
def corr_demo():
    args = request.args
    # Optional: task, session
    args_err = validate_args(['cohort', 'query', 'field1', 'field2'], args, request.url)
    if args_err:
        return args_err
    # Params
    cohort = args['cohort']
    query = args['query']
    field1 = args['field1']
    field2 = args['field2']
    # Load demographics 
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    # Load group
    subset = df.query(query) if query != 'All' else df
    if field1 == 'sex' or field2 == 'sex':
        field = field2 if field1 == 'sex' else field1
        m = subset.query('sex == "M"')[field]
        f = subset.query('sex == "F"')[field]
        img = image.violin([m,f], ['Male', 'Female'], field)
    else:
        img = image.scatter(subset[field1], subset[field2], field1, field2)
    return jsonify({'data': img})

'''Correlation of demographic feature with FC'''
@app.route('/analysis/corr/fc', methods=(['GET']))
def corr_fc():
    args = request.args
    # Optional: task, session
    args_err = validate_args(['cohort', 'query', 'field'], args, request.url) 
    if args_err:
        return args_err
    # Params
    cohort = args['cohort']
    query = args['query']
    field = args['field']
    task = args['task'] if 'task' in args else None
    ses = args['ses'] if 'ses' in args else None
    remap = 'remap' in args
    # Load demographics 
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    # Load group
    group = data.make_group_query(df, query) if query != 'All' else df.index
    # Get FCs
    fcs = []
    for sub in group:
        fc = data.get_fc('anton', cohort, sub, task, ses)
        fcs.append(fc)
    cat = 'M' if field == 'sex' else None
    rho = correlation.correlate_feat(fcs, df[field], cat=cat)
    rho = data.vec2mat(rho, fillones=False)
    if remap:
        rho = power.remap(rho)
    img = image.imshow(rho, colorbar=True)
    return jsonify({'data': img})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
