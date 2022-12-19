
from pathlib import Path
import re

# Our modules
import data

def ls_cohorts(user):
    return [f.name for f in Path(f'data/{user}/cohorts').iterdir() if f.is_dir()]

def get_cohort(user, cohort):
    p = Path(f'data/{user}/cohorts/{cohort}')
    fc = p/'fc'
    demo = p/'demographics.pkl'
    feats = p/'features'
    dat = {}
    if fc.is_dir():
        dat['fc'] = [f.name for f in fc.iterdir() if not f.is_dir()]
    if demo.exists():
        dat['demo'] = data.get_demo(user, cohort)
    if feats.is_dir():
        dat['feats'] = sorted([f.name for f in feats.iterdir() if not f.is_dir()])
    return dat

def get_tasks(user, cohort):
    c = get_cohort(user, cohort)
    tasks = set()
    for fname in c['fc']:
        tasks.add(re.match('.*task-([^_]+)', fname).group(1))
    return list(tasks)
    
