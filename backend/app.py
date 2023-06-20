from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import numpy as np
from math import isnan
from natsort import natsorted
#from pprint import pprint

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

'''Icon'''
@app.route('/favicon.png', methods=(['GET']))
def favicon():
    print('got here')
    return send_file('../dist/favicon.png')

'''List cohorts'''
@app.route('/data/cohorts', methods=(['GET']))
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
    group = [str(i) for i in list(df.query(query).index)]
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
    # Optional: task, session, cat
    args_err = validate_args(['cohort', 'query', 'field1', 'field2'], args, request.url)
    if args_err:
        return args_err
    # Params
    cohort = args['cohort']
    query = args['query']
    field1 = args['field1']
    field2 = args['field2']
    cat = args['cat'] if 'cat' in args else None
    # Load demographics 
    demo = data.get_demo('anton', cohort)
    df = data.demo2df(demo)
    # Load group
    subset = df.query(query) if query != 'All' else df
    # Both categorical
    a = subset[field1].tolist()
    b = subset[field2].tolist()
    if isinstance(a[0], str) and isinstance(b[0], str):
        aset = natsorted(list(set(a)))
        bset = natsorted(list(set(b)))
        dd = {aa: {bb: 0 for bb in bset} for aa in aset}
        for aa,bb in zip(a,b):
            dd[aa][bb] += 1
        mat = np.zeros((len(aset),len(bset)))
        for i in range(len(aset)):
            for j in range(len(bset)):
                mat[i,j] = dd[aset[i]][bset[j]]
        img = image.matshow(aset, bset, mat)
    elif cat is not None:
        a = subset.query(f'{field1} == "{cat}"')[field2]
        b = subset.query(f'{field1} != "{cat}"')[field2]
        a = a.to_numpy()
        a = a[np.invert(np.isnan(a))] 
        b = b.to_numpy()
        b = b[np.invert(np.isnan(b))] 
        img = image.violin([a,b], [cat, 'Other'], field2)
    else:
        img = image.scatter(subset[field1], subset[field2], field1, field2)
    return jsonify({'data': img})

'''Correlation of demographic feature with FC'''
@app.route('/analysis/corr/fc', methods=(['GET']))
def corr_fc():
    args = request.args
    # Optional: task, ses, thresh, cat
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
    cat = args['cat'] if 'cat' in args else None
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
                p = df.loc[sub][field]
                if cat is not None:
                    p = p == cat
                # pandas will fill in data fields that don't exist for an FC with nan?
                # This is easiest way to solve
                elif isnan(p):
                    continue
                pheno.append(p)
                fc = data.get_fc('anton', coh, sub, task, ses, typ=typ)
                fcs.append(fc)
    fcs = np.stack(fcs)
    # Get correlation and p-value
    #cat = 'M' if field == 'sex' else None
    rho, p = correlation.corr_feat(fcs, pheno, cat=None)
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
    args_err = validate_args(['id', 'cohort'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    di = args['id']
    co = args['cohort']
    fcimg = session.load(di)
    fcvec = data.mat2vec(fcimg)
    fname = f'corr/id{di}.pkl'
    wobj = dict(w=fcvec, noremap='true', trsubs=[], tsubs=[], desc='test')
    data.save_weights(wobj, 'anton', co, fname)
    return jsonify({'resp': fname})

''' Correlate demographic features with SNPs '''
@app.route('/analysis/corr/snps', methods=(['GET']))
def corr_snps():
    args = request.args
    # Optional: labtype
    args_err = validate_args(
        ['cohort', 'query', 'field', 'set', 'n', 'hap'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    query = args['query']
    field = args['field']
    subset = args['set']
    n = int(args['n'])
    hap = int(args['hap'])
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
            snp = snp == hap
            snps.append(snp)
    snps = np.stack(snps)
    # Get correlation and p-value
    cat = 'M' if field == 'sex' else None
    rho, p = correlation.corr_feat(snps, pheno, cat=cat)
    # Get distribution image
    # Display p-value as alternate axes on distribution image
    idcs = np.argsort(rho)
    p = p[idcs]
    rho_img = image.two_axes_plot(
        rho[idcs], p, 'Correlation', 'log(p-value)') # p-value already log
    # Get top correlated SNPs
    # Note sorting done above
    bot = idcs[:n]
    top = idcs[-n:]
    top_bot_idcs = np.concatenate([bot, top])
    top_bot = rho[top_bot_idcs]
    #top_bot, top_bot_idcs = data.get_top_bot_snps(rho, idcs, n)
    labs = data.relabel_snps('anton', coh, top_bot_idcs, subset, labtype)
    top_img = image.bar(top_bot, labs)
    return jsonify({'rho': rho_img, 'top': top_img})

''' Correlate demographic features with decomposition weights '''
@app.route('/analysis/corr/decomp', methods=(['GET']))
def corr_decomp():
    args = request.args
    # Optional: category
    # category is for categorical phenotypes
    args_err = validate_args(
        ['cohort', 'query', 'field', 'name', 'n'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    query = args['query']
    field = args['field']
    name = args['name']
    n = int(args['n'])
    cat = args['cat'] if 'cat' in args else None
    # Load demographics
    demo = data.get_demo('anton', coh)
    df = data.demo2df(demo)
    # Load group
    group = df.index if query == 'All' else df.query(query).index
    # Get decomposition weights for subjects and pheno
    ws = []
    pheno = []
    for sub in group:
        # TODO check if weights exist doesn't work for some reason
        #if data.has_decomp_weights('anton', coh, sub, name):
        p = df.loc[sub][field]
        if cat is not None:
            p = p == cat
        try:
            w = data.get_decomp_weights('anton', coh, sub, name)
            pheno.append(p)
            ws.append(w)
        except:
            #print(data.get_decomp_weights_name('anton', coh, sub, name))
            pass
    # Find correlation
    rho = correlation.corr_decomp_pheno(ws, pheno, n)
    # Plot correlation over components
    img = image.plot(rho)
    return jsonify({'data': img})

''' Correlate SNPs with decomposition weights '''
@app.route('/analysis/corr/decomp-snps', methods=(['GET']))
def corr_decomp_snps():
    args = request.args
    args_err = validate_args(
        ['cohort', 'query', 'name', 'n', 'set', 'hap', 'ntop', 'labtype'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    query = args['query']
    name = args['name']
    n = int(args['n'])
    subset = args['set']
    hap = int(args['hap'])
    ntop = int(args['ntop'])
    labtype = args['labtype']
    # Load demographics
    demo = data.get_demo('anton', coh)
    df = data.demo2df(demo)
    # Load group
    group = df.index if query == 'All' else df.query(query).index
    # Get decomposition weights and snps for subjects
    ws = []
    snps = []
    for sub in group:
        if (data.has_decomp_weights('anton', coh, sub, name) and
            data.has_snps('anton', coh, sub, subset)):
            w = data.get_decomp_weights('anton', coh, sub, name)
            ws.append(w)
            snp = data.get_snps('anton', coh, sub, subset)
            snp = snp == hap
            snps.append(snp)
    # Find correlation
    rho_mat = correlation.corr_decomp_snps(ws, snps, n)
    a,b = rho_mat.shape
    rho = rho_mat.reshape(-1)
    # Get top correlations
    idcs = np.argsort(rho)
    bot_idcs = idcs[:ntop]
    top_idcs = idcs[-ntop:]
    best_idcs = np.concatenate([bot_idcs, top_idcs])
    widcs = np.floor(best_idcs/b).astype('int')
    sidcs = best_idcs-widcs*b
    # Label
    snps_labs = data.relabel_snps('anton', coh, sidcs, subset, labtype)
    labs = [f'{i}-{snp}' for i,snp in zip(widcs, snps_labs)]
    # Return image
    dist_img = image.plot(rho[idcs])
    img = image.bar(rho[best_idcs], labs)
    return jsonify({'data': img, 'dist': dist_img})

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

''' Get weights data for FC or Partial Corr'''
@app.route('/data/weights/fc', methods=(['GET']))
def weights_fc():
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

''' Get weights data for FC or Partial Corr'''
@app.route('/data/weights/snps', methods=(['GET']))
def weights_snps():
    args = request.args
    # Optional: AVERAGE, limvar
    # Average takes average of all compatible files in the directory
    # limvar means max q1-q3 range is 3x average
    args_err = validate_args(
        ['cohort', 'fname', 'hap', 'n', 'labtype', 'set'], 
        args, request.url) 
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    fname = args['fname']
    hap = int(args['hap'])
    n = int(args['n'])
    labtype = args['labtype']
    subset = args['set']
    avg = 'average' in args
    limiqr = 'limiqr' in args
    # Get weights
    wobj = data.get_weights('anton', coh, fname)
    # If average, get all compatible in directory
    # RESHAPE because of sklearn coef_ dimensions
    if avg:
        ws = data.get_weights_dir('anton', coh, fname, wobj)
        ws = ws.reshape(ws.shape[0], -1)
        w = np.mean(ws, axis=0)
    else:
        w = wobj['w'].reshape(-1)
    # Get part by haptype and sort
    d = int(len(w)/3)
    w = w[hap*d:(hap+1)*d]
    if avg:
        ws = ws[:,hap*d:(hap+1)*d]
    idcs = np.argsort(w)
    # Display distribution
    if avg:
        # Get quartiles
        q1,q3 = data.get_quartiles(ws[:,idcs])
        qmean = np.mean(q3-q1)
        # Plot whole distribution
        img = image.fill_between(q1, q3)
        # Limit SNPs by interquartile range or not
        if limiqr:
            bidcs = []
            tidcs = []
            for i in range(50):
                db = q3[i]-q1[i]
                dt = q3[-i-1]-q1[-i-1]
                if db < 2*qmean:
                    bidcs.append(idcs[i])
                if dt < 2*qmean:
                    tidcs.append(idcs[-i-1])
            bidcs = bidcs[:n]
            tidcs = tidcs[:n][::-1]
        else:
            bidcs = idcs[:n]
            tidcs = idcs[-n:]
        # Get top SNP features
        top_bot_idcs = np.concatenate([bidcs,tidcs])
        top_bot = ws[:,top_bot_idcs]
    else:
        # Plot whole distribution
        img = image.plot(w[idcs])
        # Get top SNP features
        bidcs = idcs[:n]
        tidcs = idcs[-n:]
        top_bot_idcs = np.concatenate([bidcs,tidcs])
        top_bot = w[top_bot_idcs]
    # top_bot, top_bot_idcs = data.get_top_bot_snps(part, idcs, n)
    labs = data.relabel_snps('anton', coh, top_bot_idcs, subset, labtype)
    if avg:
        # top_bot_ws, _ = data.get_top_bot_snps(ws.transpose(1,0), idcs, n)
        top_img = image.boxplot(top_bot, labs)
    else:
        top_img = image.bar(top_bot, labs)
    return jsonify({
        'desc': wobj['desc'], 
        'ntrain': len(wobj['trsubs']), 
        'ntest': len(wobj['tsubs']),
        'w': img,
        'top': top_img})

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

'''
Get component of dictionary
'''
@app.route('/data/component', methods=(['GET']))
def component():
    args = request.args
    # Optional: remap
    args_err = validate_args(
        ['name', 'cohort', 'n'], 
        args, request.url)
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    name = args['name']
    n = int(args['n']) 
    remap = 'remap' in args
    # Get component, remap, and show as image
    comp = data.get_comp('anton', coh, name, n)
    cimg = data.vec2mat(comp, fillones=False)
    if remap:
        cimg = power.remap(cimg)
    img = image.imshow(cimg, colorbar=True)
    return jsonify({'data': img})

'''
Get variance explained by components of a decomposition
'''
@app.route('/data/decomp/varexp', methods=(['GET']))
def decomp_varexp():
    args = request.args
    # Optional: remap
    args_err = validate_args(
        ['name', 'cohort'], 
        args, request.url)
    if args_err:
        return args_err
    # Params
    coh = args['cohort']
    name = args['name']
    # Get variance explained by component and also the number of components
    varexp = data.get_var_exp('anton', coh, name)
    img = image.plot(varexp)
    return jsonify({'data': img})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
