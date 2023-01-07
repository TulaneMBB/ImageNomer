
from pathlib import Path
import re
from natsort import natsorted

# Our modules
import data

def ls_cohorts(user):
    return [f.name for f in 
        Path(f'data/{user}/cohorts').iterdir() if f.is_dir()]

def get_weights_tree(basepath):
    node = {}
    node['dirs'] = {}
    node['fnames'] = []
    for f in basepath.iterdir():
        if f.is_dir() and f.name != '.' and f.name != '..':
            node['dirs'][f.name] = get_weights_tree(f)
        elif not f.is_dir():
            node['fnames'].append(f.name)
    node['fnames'] = natsorted(node['fnames']) # e.g., rest2 before rest11
    return node

def get_snps_sets(sdir):
    snps = dict()
    for f in sdir.iterdir():
        if 'snps.npy' in f.name:
            subset = re.match('.*set-([^_]+)', f.name).group(1)
            if subset not in snps:
                snps[subset] = [f.name]
            else:
                snps[subset].append(f.name)
    for subset in snps:
        snps[subset] = natsorted(snps[subset])
    return snps

def get_cohort(user, cohort):
    p = Path(f'data/{user}/cohorts/{cohort}')
    fc = p/'fc'
    partial = p/'partial'
    demo = p/'demographics.pkl'
    weights = p/'weights'
    snps = p/'snps'
    dat = {}
    if fc.is_dir():
        dat['fc'] = [f.name 
            for f in fc.iterdir() if not f.is_dir()]
    if partial.is_dir():
        dat['partial'] = [f.name 
            for f in partial.iterdir() if not f.is_dir()]
    if demo.exists():
        dat['demo'] = data.get_demo(user, cohort)
    if weights.is_dir():
        dat['weights'] = get_weights_tree(weights)
    if snps.is_dir():
        dat['snps'] = get_snps_sets(snps)
    return dat

def get_tasks(user, cohort):
    c = get_cohort(user, cohort)
    tasks = set()
    for fname in c['fc']:
        tasks.add(re.match('.*task-([^_]+)', fname).group(1))
    return list(tasks)
    
