'''Read data from files on server'''

import numpy as np
import pickle
import pandas as pd
import sys
from pathlib import Path
import re
from operator import itemgetter

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

def get_fc_fname(user, cohort, sub, task=None, ses=None, typ='fc'):
    task = f'_task-{task}' if task is not None else ''
    ses = f'_ses-{ses}' if ses is not None else ''
    fname = f'data/{user}/cohorts/{cohort}/{typ}/{sub}{task}{ses}_{typ}.npy'
    return fname

def has_fc(user, cohort, sub, task=None, ses=None, typ='fc'):
    return Path(get_fc_fname(user, cohort, sub, task, ses, typ)).exists

def get_fc(user, cohort, sub, task=None, ses=None, typ='fc'):
    return np.load(get_fc_fname(user, cohort, sub, task, ses, typ))

def has_snps(user, cohort, sub, subset):
    fname = f'data/{user}/cohorts/{cohort}/snps/{sub}_set-{subset}_snps.npy'
    return Path(fname).exists

def get_snps(user, cohort, sub, subset):
    fname = f'data/{user}/cohorts/{cohort}/snps/{sub}_set-{subset}_snps.npy'
    return np.load(fname)

def get_demo(user, cohort, file=False):
    fname = f'data/{user}/cohorts/{cohort}/demographics.pkl'
    with open(fname, 'rb') as f:
        return pickle.load(f)

'''
Weights objects contain at least the following fields:
w (numpy.ndarray), trsubs (list(str)), tsubs (list(str)), desc (str)
'''
def get_weights(user, cohort, fname):
    # Hack for python's module structure
    #sys.modules['__main__'].Weights = Weights
    fname = f'data/{user}/cohorts/{cohort}/weights/{fname}'
    with open(fname, 'rb') as f:
        return pickle.load(f)

def save_weights(wobj, user, cohort, fname):
    with open(f'data/{user}/cohorts/{cohort}/weights/{fname}', 'wb') as f:
        pickle.dump(wobj, f)

def get_conn_stats(typ, user, cohort, fnames):
    imgs = []
    ftype = fnames[0].split('_')[-1].split('.')[0]
    for fname in fnames:
        path = f'data/{user}/cohorts/{cohort}/{ftype}/{fname}'
        img = np.load(path)
        imgs.append(img)
    imgs = np.stack(imgs)
    match typ:
        case 'mean': return np.mean(imgs, axis=0)
        case 'std': return np.std(imgs, axis=0)

def get_snps_stats(user, cohort, fnames):
    snps = []
    for fname in fnames:
        path = f'data/{user}/cohorts/{cohort}/snps/{fname}'
        dat = np.load(path)
        snps.append(dat)
    snps = np.stack(snps)
    miss = np.sum(np.isnan(snps), axis=1)
    recv = np.sum(snps == 0, axis=1)
    het = np.sum(snps == 1, axis=1)
    homo = np.sum(snps == 2, axis=1)
    return [miss, recv, het, homo]

def get_top(data, n=20, rank='abs'):
    match rank:
        case 'abs': idcs = np.argsort(np.abs(data))
        case 'pos': idcs = np.argsort(data)
        case 'neg': idcs = np.argsort(-data)
    if n > len(idcs):
        n = len(idcs)
    return data[idcs[-1:-n:-1]], idcs[-1:-n:-1]

def get_top_bot_snps(rho, idcs, n=10):
    top = rho[:-n-1:-1]
    top_idcs = idcs[:-n-1:-1]
    bot = rho[n-1::-1]
    bot_idcs = idcs[n-1::-1]
    dat = np.concatenate([top, bot])
    labs = np.concatenate([top_idcs, bot_idcs])
    return dat, labs

def get_comp(user, coh, name, n):
    fname = f'data/{user}/cohorts/{coh}/decomp/{name}-comps/{name}_comp-{n}.npy'
    return np.load(fname)

def get_var_exp(user, coh, name):
    pcomps = Path(f'data/{user}/cohorts/{coh}/decomp/{name}-comps')
    pweights = Path(f'data/{user}/cohorts/{coh}/decomp/{name}-weights')
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

def relabel_snps(user, cohort, idcs, subset, labtype=None):
    if labtype is None or labtype == 'index':
        return idcs
    if labtype == 'rs':
        fname = f'data/{user}/cohorts/{cohort}/snps_{subset}.pkl'
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
    subs = list(subs)
    for col in cols:
        dct[col] = len(subs)*[float('nan')]
    sub2idx = {sub: i for i,sub in enumerate(subs)}
    # Get column values
    for i,col in enumerate(cols):
        for sub,val in demo[col].items():
            dct[col][sub2idx[sub]] = val
    # Create DataFrame
    return pd.DataFrame(dct, index=subs)

# def flatten(lst):
#     return [item for sublist in lst for item in sublist]
    
