'''Read data from files on server'''

import numpy as np
import pickle
import pandas as pd
import pandasql as ps

def vec2mat(fc, fillones=True):
    n = len(fc)
    d = int(round((1+(1+8*n)**0.5)/2))
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

def get_fc(user, cohort, sub, task=None, ses=None):
    task = f'_task-{task}' if task is not None else ''
    ses = f'_ses-{ses}' if ses is not None else ''
    fname = f'data/{user}/cohorts/{cohort}/fc/{sub}{task}{ses}_fc.npy'
    return np.load(fname)

def get_demo(user, cohort, file=False):
    fname = f'data/{user}/cohorts/{cohort}/demographics.pkl'
    with open(fname, 'rb') as f:
        return pickle.load(f)

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
    
'''
def make_group(df, col, val_or_range):
    if isinstance(val_or_range, tuple):
        # Range
        valmin, valmax = val_or_range
        query = f'select * from df where {col} >= {valmin} and {col} <= {valmax}'
    else:
        if isinstance(val_or_range, str):
            val_or_range = f'"{val_or_range}"'
        query = f'select * from df where {col} = {val_or_range}'
    return ps.sqldf(query, locals())

def make_group_query(df, query):
    return list(df.query(query).index)
'''

def flatten(lst):
    return [item for sublist in lst for item in sublist]
    