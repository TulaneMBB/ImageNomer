
from pathlib import Path
import re

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
    return node

def get_cohort(user, cohort):
    p = Path(f'data/{user}/cohorts/{cohort}')
    fc = p/'fc'
    demo = p/'demographics.pkl'
    weights = p/'weights'
    dat = {}
    if fc.is_dir():
        dat['fc'] = [f.name for f in fc.iterdir() if not f.is_dir()]
    if demo.exists():
        dat['demo'] = data.get_demo(user, cohort)
    if weights.is_dir():
        dat['weights'] = get_weights_tree(weights)
    return dat

def get_tasks(user, cohort):
    c = get_cohort(user, cohort)
    tasks = set()
    for fname in c['fc']:
        tasks.add(re.match('.*task-([^_]+)', fname).group(1))
    return list(tasks)
    
