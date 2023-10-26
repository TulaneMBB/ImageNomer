'''Read data from files on server'''

import numpy as np
import pickle
import pandas as pd
import sys
from pathlib import Path
import re
from operator import itemgetter
import math

def d_from_vec(fc):
    n = fc.size
    return int(round((1+(1+8*n)**0.5)/2))

def vec2mat(fc, fillones=True):
    d = d_from_vec(fc) 
    a,b = np.triu_indices(d,1)
    mat = np.zeros((d,d))
    mat[a,b] = fc
    mat += mat.T
    ones = np.arange(d)
    if fillones:
        mat[ones,ones] = 1
    return mat

def mat2vec(fc):
    d = fc.shape[0]
    a,b = np.triu_indices(d,1)
    return fc[a,b]

def get_conn_fname(cohort, sub, task=None, ses=None, typ='fc'):
    task = f'_task-{task}' if task is not None else ''
    ses = f'_ses-{ses}' if ses is not None else ''
    fname = f'data/{cohort}/conn/{sub}{task}{ses}_{typ}.npy'
    return fname

def has_conn(cohort, sub, task=None, ses=None, typ='fc'):
    p = Path(get_conn_fname(cohort, sub, task, ses, typ))
    return p.exists()

def get_conn(cohort, sub, task=None, ses=None, typ='fc'):
    return np.load(get_conn_fname(cohort, sub, task, ses, typ))

def has_snps(cohort, sub, subset):
    fname = f'data/{cohort}/snps/{sub}_set-{subset}_snps.npy'
    return Path(fname).exists

def has_decomp_weights(cohort, sub, name):
    return Path(get_decomp_weights_name(cohort, sub, name)).exists
   
def get_decomp_weights_name(cohort, sub, name): 
    fname = f'data/{cohort}/decomp/{name}-weights/{sub}_comp-{name}_weights.npy'
    return fname

def get_decomp_weights(cohort, sub, name):
    return np.load(get_decomp_weights_name(cohort, sub, name))

def get_snps(cohort, sub, subset):
    fname = f'data/{cohort}/snps/{sub}_set-{subset}_snps.npy'
    return np.load(fname)

def get_demo(cohort, file=False):
    fname = f'data/{cohort}/demographics.pkl'
    with open(fname, 'rb') as f:
        return pickle.load(f)

'''
Weights dictionaries contain at least the following keys:
w (numpy.ndarray, flat 1D array), trsubs (list(str)), tsubs (list(str)), desc (str)
'''
def get_weights(cohort, fname):
    fname = f'data/{cohort}/weights/{fname}'
    with open(fname, 'rb') as f:
        return pickle.load(f)

def get_weights_dir(cohort, fname, wobj):
    p = Path(fname).parts[:-1]
    basedir = f'data/{cohort}/weights'
    p = [basedir] + list(p)
    p = Path('/'.join(p))
    ws = []
    for f in p.iterdir():
        if f.is_dir():
            continue
        with open(f, 'rb') as ff:
            dct = pickle.load(ff)
            if dct['w'].shape == wobj['w'].shape:
                ws.append(dct['w'])
    return np.stack(ws)

def save_weights(wobj, cohort, fname):
    with open(f'data/{cohort}/weights/{fname}', 'wb') as f:
        pickle.dump(wobj, f)

def get_conn_stats(typ, cohort, fnames):
    imgs = []
    ftype = fnames[0].split('_')[-1].split('.')[0]
    for fname in fnames:
        path = f'data/{cohort}/{ftype}/{fname}'
        img = np.load(path)
        imgs.append(img)
    imgs = np.stack(imgs)
    if typ == 'mean':
        return np.mean(imgs, axis=0)
    elif typ == 'std':
        return np.std(imgs, axis=0)

def get_snps_stats(cohort, fnames):
    snps = []
    for fname in fnames:
        path = f'data/{cohort}/snps/{fname}'
        dat = np.load(path)
        snps.append(dat)
    snps = np.stack(snps)
    miss = np.sum(np.isnan(snps), axis=1)
    recv = np.sum(snps == 0, axis=1)
    het = np.sum(snps == 1, axis=1)
    homo = np.sum(snps == 2, axis=1)
    return [miss, recv, het, homo]

def get_top(data, n=20, rank='abs'):
    if rank == 'abs':
        idcs = np.argsort(np.abs(data))
    elif rank == 'pos':
        idcs = np.argsort(data)
    elif rank == 'neg':
        idcs = np.argsort(-data)
    if n > len(idcs):
        n = len(idcs)
    return data[idcs[-1:-n:-1]], idcs[-1:-n:-1]

# def get_top_bot_snps(rho, idcs, n=10):
#     top = rho[:-n-1:-1]
#     top_idcs = idcs[:-n-1:-1]
#     bot = rho[n-1::-1]
#     bot_idcs = idcs[n-1::-1]
#     dat = np.concatenate([top, bot])
#     labs = np.concatenate([top_idcs, bot_idcs])
#     return dat, labs

def get_quartiles(ws):
    ws = np.sort(ws, axis=0)
    n = ws.shape[0]
    q1 = math.floor(0.25*n)
    q3 = math.floor(0.75*n)
    return ws[int(q1)], ws[int(q3)]

def get_comp(coh, name, n):
    fname = f'data/{coh}/decomp/{name}-comps/{name}_comp-{n}.npy'
    return np.load(fname)

def get_var_exp(coh, name):
    pcomps = Path(f'data/{coh}/decomp/{name}-comps')
    pweights = Path(f'data/{coh}/decomp/{name}-weights')
    comps = []
    for c in pcomps.iterdir():
        mobj = re.match(f'{name}_comp-([0-9]+).npy', c.name)
        if mobj:
            cnp = np.load(str(c))
            cnp = cnp.reshape(-1)
            comps.append((cnp, int(mobj.group(1))))
    comps.sort(key=itemgetter(1))
    comps = np.stack([c[0] for c in comps])
    comps = np.mean(np.abs(comps), axis=1)
    ws = []
    for w in pweights.iterdir():
        if re.match(f'.*{name}_weights.npy', w.name):
            wnp = np.load(str(w))
            wnp = wnp.reshape(-1)
            ws.append(wnp)
    ws = np.stack(ws)
    ws = np.mean(np.abs(ws), axis=0)
    var_exp = ws*comps
    var_exp = var_exp/np.sum(var_exp)
    return np.sort(var_exp)[::-1]

def relabel_snps(cohort, idcs, subset, labtype=None):
    if labtype is None or labtype == 'index':
        return idcs
    if labtype == 'rs':
        fname = f'data/{cohort}/snps_{subset}.pkl'
        with open(fname, 'rb') as f:
            st = pickle.load(f)
        lst = list(st)
        res = [lst[i] for i in idcs]
        return res

'''
Combine all vars into one dict
Then create a DataFrame
'''
def demo2df(demo):
    cols = list(demo.keys())
    subs = set()
    dct = dict()
    # Get list and number of subs
    for col in cols:
        for sub in demo[col].keys():
            subs.add(sub)
    subs = [str(s) for s in list(subs)]
    for col in cols:
        dct[col] = len(subs)*[float('nan')]
    sub2idx = {sub: i for i,sub in enumerate(subs)}
    # Get column values
    for i,col in enumerate(cols):
        for sub,val in demo[col].items():
            dct[col][sub2idx[str(sub)]] = val
    # Create DataFrame
    return pd.DataFrame(dct, index=subs)

# def flatten(lst):
#     return [item for sublist in lst for item in sublist]
    
