'''Read data from files on server'''

import numpy as np
import pickle
import pandas as pd
import sys
from pathlib import Path

'''
Now a dictionary, see below
class Weights:
    def __init__(self, w, subs_tr, subs_t, desc):
        self.w = self.to_numpy(w)
        self.subs_tr = subs_tr
        self.subs_t = subs_t
        self.desc = desc
        
    def to_numpy(self, data):
        if isinstance(data, torch.Tensor):
            return data.detach().cpu().numpy()
        elif isinstance(data, np.ndarray):
            return data
        else:
            raise TypeError(data)
            
    def save(self, fname):
        with open(fname, 'wb') as f:
            pickle.dump(self, f)
'''

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

def get_fc_fname(user, cohort, sub, task=None, ses=None):
    task = f'_task-{task}' if task is not None else ''
    ses = f'_ses-{ses}' if ses is not None else ''
    fname = f'data/{user}/cohorts/{cohort}/fc/{sub}{task}{ses}_fc.npy'
    return fname

def has_fc(user, cohort, sub, task=None, ses=None):
    return Path(get_fc_fname(user, cohort, sub, task, ses)).exists

def get_fc(user, cohort, sub, task=None, ses=None):
    return np.load(get_fc_fname(user, cohort, sub, task, ses))

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

def get_stats(typ, user, cohort, fnames):
    imgs = []
    for fname in fnames:
        path = f'data/{user}/cohorts/{cohort}/fc/{fname}'
        img = np.load(path)
        imgs.append(img)
    imgs = np.stack(imgs)
    match typ:
        case 'mean': return np.mean(imgs, axis=0)
        case 'std': return np.std(imgs, axis=0)

def get_top(data, n=20, rank='abs'):
    match rank:
        case 'abs': idcs = np.argsort(np.abs(data))
        case 'pos': idcs = np.argsort(data)
        case 'neg': idcs = np.argsort(-data)
    if n > len(idcs):
        n = len(idcs)
    return data[idcs[-1:-n:-1]], idcs[-1:-n:-1]

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
    
