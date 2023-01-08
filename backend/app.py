from flask import Flask, request, jsonify, render_template
import os
import json
import numpy as np

# Our modules
import power
import data
import image
import cohort
import correlation
import session
import image_math

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
def ls():
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
    group = list(df.query(query).index)
    return jsonify(group)

'''Get demographics graph'''
@app.route('/data/demo/hist', methods=(['GET', 'POST']))
def demo_hist():
    if request.method == 'GET':
        args = request.args
    else:
        args = request.form
    args_err = validate_args(['cohort', 'groups', 'field'], 
        args, request.url)
    if args_err:
        return args_err
    cohort = args['cohort']
    field = args['field']
    groups = json.loads(args['groups'])
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    img = image.groups_hist(df, groups, field)
    return jsonify({'data': img})

'''Get subject FC'''
@app.route('/data/fc', methods=(['GET']))
def fc():
    args = request.args
    # Optional: task, session, colorbar, remap, type (fc or partial)
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
    typ = args['type'] if 'type' in args else 'fc'
    # Load and display FC
    fc = data.get_fc('anton', cohort, sub, task, ses, typ=typ)
    fc = data.vec2mat(fc, fillones=False)
    if remap:
        fc = power.remap(fc)
    img = image.imshow(fc, colorbar)
    return jsonify({'data': img})

''' Get subject SNPs '''
@app.route('/data/snps', methods=(['GET']))
def spns():
    args = request.args
    args_err = validate_args(['cohort', 'sub', 'set'], args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    sub = args['sub']
    subset = args['set']
    # Load and display histogram of SNP values
    snps = data.get_snps('anton', coh, sub, subset)
    img = image.snps_hist(snps)
    return jsonify({'data': img})

'''Get images of one demographic feature correlated with another'''
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
    # Optional: task, ses, thresh
    args_err = validate_args(['cohort', 'query', 'field'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    query = args['query']
    field = args['field']
    task = args['task'] if 'task' in args else None
    ses = args['ses'] if 'ses' in args else None
    thresh = args['thresh'] if 'thresh' in args else None
    remap = 'remap' in args
    typ = args['fctype']
    # Load demographics
    demo = data.get_demo('anton', coh)
    df = data.demo2df(demo)
    # Load group
    group = df.index if query == 'All' else df.query(query).index
    # Get list of tasks
    tasks = (cohort.get_tasks('anton', coh) 
        if task is None else [task])
    # Get fcs and pheno
    fcs = []
    pheno = []
    for task in tasks:
        for sub in group:
            if data.has_fc('anton', coh, sub, task, ses, typ=typ):
                pheno.append(df.loc[sub][field])
                fc = data.get_fc('anton', coh, sub, task, ses, typ=typ)
                fcs.append(fc)
    fcs = np.stack(fcs)
    # Get correlation and p-value
    cat = 'M' if field == 'sex' else None
    rho, p = correlation.corr_feat(fcs, pheno, cat=cat)
    rho = data.vec2mat(rho, fillones=False)
    p = data.vec2mat(p, fillones=False)
    # Apply threshold
    if thresh == 'pos':
        p[rho < 0] = 0
        rho[rho < 0] = 0
    elif thresh == 'neg':
        p[rho > 0] = 0
        rho[rho > 0] = 0
    # Remap FCs
    if remap:
        rho = power.remap(rho)
        p = power.remap(p)
    # Save correlation for image math
    rid = session.save(rho)
    pid = session.save(p)
    # Send image
    rimg = image.imshow(rho, colorbar=True)
    pimg = image.imshow(p, colorbar=True, reverse_cmap=True)
    return jsonify({'rdata': rimg, 'rid': rid, 'pdata': pimg, 'pid': pid})

'''Save a correlation image for equivalent functionality to model weights'''
@app.route('/analysis/corr/save', methods=(['GET']))
def corr_save():
    args = request.args
    args_err = validate_args(['id'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    di = args['id']
    fcimg = session.load(di)
    fcvec = data.mat2vec(fcimg)
    fname = f'corr/id{di}.pkl'
    wobj = dict(w=fcvec, noremap='true', trsubs=[], tsubs=[], desc='test')
    data.save_weights(wobj, 'anton', 'test', fname)
    return jsonify({'resp': fname})

''' Correlate demographic features with SNPs '''
@app.route('/analysis/corr/snps', methods=(['GET']))
def corr_snps():
    args = request.args
    # Optional: labtype
    args_err = validate_args(
        ['cohort', 'query', 'field', 'set', 'n'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    query = args['query']
    field = args['field']
    subset = args['set']
    n = int(args['n'])
    labtype = args['labtype'] if 'labtype' in args else 'rs'
    # Load demographics
    demo = data.get_demo('anton', coh)
    df = data.demo2df(demo)
    # Load group
    group = df.index if query == 'All' else df.query(query).index
    # Get snps and pheno
    snps = []
    pheno = []
    for sub in group:
        if data.has_snps('anton', coh, sub, subset):
            pheno.append(df.loc[sub][field])
            snp = data.get_snps('anton', coh, sub, subset)
            snps.append(snp)
    snps = np.stack(snps)
    # Zero heterozygous and set nans to zero
    snps[np.isnan(snps)] = 1
    snps = snps-1
    # Get correlation and p-value
    cat = 'M' if field == 'sex' else None
    rho, p = correlation.corr_feat(snps, pheno, cat=cat)
    # Get distribution image
    # Display p-value as alternate axes on distribution image
    idcs = np.argsort(rho)
    print(idcs[-5:])
    rho = rho[idcs]
    p = p[idcs]
    rho_img = image.two_axes_plot(
        rho, p, 'Correlation', 'log(p-value)') # p-value already log
    # Get top correlated SNPs
    # Note sorting done above
    top_bot, top_bot_idcs = data.get_top_bot_snps(rho, idcs, n)
    labs = data.relabel_snps('anton', coh, top_bot_idcs, subset, 'rs')
    top_img = image.bar(top_bot, labs)
    return jsonify({'rho': rho_img, 'top': top_img})

'''Perform image math'''
@app.route('/math/image', methods=(['GET']))
def imgmath():
    args = request.args
    # Optional: task, session
    args_err = validate_args(['expr'], args, request.url) 
    if args_err:
        return args_err
    # Params
    expr = args['expr']
    try:
        res = image_math.eval(expr)
    except err:
        return error(err)
    img = image.imshow(res, colorbar=True)
    return jsonify({'data': img})

''' Get weights data '''
@app.route('/data/weights', methods=(['GET']))
def weights():
    args = request.args
    # Optional session, mult, task, query, remap
    args_err = validate_args(['cohort', 'fname'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    fname = args['fname']
    ses = args['ses'] if 'ses' in args else None
    mult = args['mult'] if 'mult' in args else 'no'
    task = args['task'] if 'task' in args else 'All'
    query = args['query'] if 'query' in args else 'All'
    remap = 'remap' in args
    # Get weights
    # TODO non-FC or image features
    # TODO remap as wobj field
    wobj = data.get_weights('anton', coh, fname)
    w = wobj['w']
    # If multiplying, load subject features
    if mult != 'no':
        # Load demographics
        demo = data.get_demo('anton', coh)
        df = data.demo2df(demo)
        # Load group
        group = df.index if query == 'All' else df.query(query).index
        # Get list of tasks
        tasks = (cohort.get_tasks('anton', coh) 
            if task == 'All' else [task])
        # Get fcs
        fcs = []
        for task in tasks:
            for sub in group:
                if data.has_fc('anton', coh, sub, task, ses):
                    fc = data.get_fc('anton', coh, sub, task, ses=None)
                    fcs.append(fc)
        fcs = np.stack(fcs)
        # Multiply
        if mult == 'mean':
            feat = np.mean(fcs, axis=0)
        elif mult == 'std':
            feat = np.std(fcs, axis=0)
        w *= feat
    # Save weights, remapping first
    # Noremap on corr-generated weights
    if remap and 'noremap' not in wobj:
        wimg = power.remap(data.vec2mat(w, fillones=False))
        w = data.mat2vec(wimg)
    else:
        wimg = data.vec2mat(w, fillones=False)
    session.save_weights(w)
    # Display as image
    img = image.imshow(wimg)
    return jsonify({
        'desc': wobj['desc'], 
        'ntrain': len(wobj['trsubs']), 
        'ntest': len(wobj['tsubs']),
        'w': img})

''' Bar graph of top values '''
@app.route('/image/top', methods=(['GET']))
def imgtop():
    args = request.args
    # Optional params: ntop, rank, labtype
    ntop = int(args['ntop']) if 'ntop' in args else 20
    rank = args['rank'] if 'rank' in args else 'abs'
    labtype = args['labtype'] if 'labtype' in args else 'raw'  
    # Load weights
    w = session.load_weights()
    # Get top weights
    vec, idcs = data.get_top(w, n=ntop, rank=rank)
    labels = power.label(idcs, labtype)
    # Draw image
    img = image.bar(vec, labels)
    return jsonify({'data': img})

'''
Get statistics image 
Mean or standard deviation for FC/partial
Or violin plot for SNPs
'''
@app.route('/analysis/stats', methods=(['POST']))
def stats():
    args = request.form
    # Optional: remap
    args_err = validate_args(
        ['type', 'cohort', 'fnames'], 
        args, request.url)
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    typ = args['type']
    fnames = json.loads(args['fnames'])
    remap = 'remap' in args
    # If mean or std dev
    # Get FC/partial images and calculate stat
    if typ in ['mean', 'std']:
        res = data.get_conn_stats(typ, 'anton', coh, fnames)
        mat = data.vec2mat(res, fillones=False)
        if remap:
           mat = power.remap(mat)
        # Save in cache
        id = session.save(mat)
        # Display and send to frontend
        img = image.imshow(mat) 
        return jsonify({'data': img, 'id': id})
    # If snps, make violin plot of missing, recessive, het, and dominant
    # No saving in cache
    elif typ == 'snps':
        stats_lst = data.get_snps_stats('anton', coh, fnames)
        img = image.snps_violin(stats_lst)
        return jsonify({'data': img})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
