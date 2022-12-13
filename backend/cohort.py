
from pathlib import Path

# Our modules
import data

def ls_cohorts(user):
    return [f.name for f in Path(f'data/{user}/cohorts').iterdir() if f.is_dir()]

def get_cohort(user, cohort):
    p = Path(f'data/{user}/cohorts/{cohort}')
    fc = p/'fc'
    demo = p/'demographics.pkl'
    dat = {}
    if fc.is_dir():
        dat['fc'] = [f.name for f in fc.iterdir() if not f.is_dir()]
    if demo.exists():
        dat['demo'] = data.get_demo(user, cohort)
    return dat
    
