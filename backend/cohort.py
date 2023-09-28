
from pathlib import Path
import re
from natsort import natsorted

# Our modules
import data

def ls_cohorts():
    return [f.name for f in 
        Path(f'data/').iterdir() if f.is_dir()]

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

def get_decomp_comps(f, name):
    cnames = []
    for comp in f.iterdir():
        cmobj = re.match(f'{name}_comp-([0-9]+).npy', comp.name)
        if not cmobj:
            continue
        cnames.append(comp.name)
    # Sort for easy lookup in UI
    cnames.sort(key=lambda cstr: 
        int(re.match('.*comp-([0-9]+).', cstr).group(1)))
    return cnames

def get_decomp_weights(f, name):
    ws = dict()
    for wf in f.iterdir():
        wmobj = re.match(f'([^_]+)_comp-{name}_weights.npy', 
            wf.name)
        if not wmobj:
            continue
        subid = wmobj.group(1)
        ws[subid] = wf.name
    return ws

def get_comps(comps):
    cdct = dict()
    wdct = dict()
    for f in comps.iterdir():
        if not f.is_dir():
            continue
        mobj = re.match('([^-]+)-(comps|weights)', f.name)
        if not mobj:
            continue
        name = mobj.group(1)
        if mobj.group(2) == 'comps':
            cdct[name] = get_decomp_comps(f, name)
        if mobj.group(2) == 'weights':
            wdct[name] = get_decomp_weights(f, name)
    res = dict()
    for name in cdct.keys():
        if name in wdct:
            res[name] = dict()
            res[name]['comps'] = cdct[name]
            res[name]['weights'] = wdct[name] 
    return res

def get_cohort(cohort):
    p = Path(f'data/{cohort}')
    fc = p/'fc'
    partial = p/'partial'
    demo = p/'demographics.pkl'
    weights = p/'weights'
    snps = p/'snps'
    components = p/'decomp'
    dat = {}
    if fc.is_dir():
        dat['fc'] = [f.name 
            for f in fc.iterdir() if not f.is_dir()]
    if partial.is_dir():
        dat['partial'] = [f.name 
            for f in partial.iterdir() if not f.is_dir()]
    if demo.exists():
        dat['demo'] = data.get_demo(cohort)
    if weights.is_dir():
        dat['weights'] = get_weights_tree(weights)
    if snps.is_dir():
        dat['snps'] = get_snps_sets(snps)
    if components.is_dir():
        dat['decomp'] = get_comps(components)
    return dat

def get_tasks(cohort):
    c = get_cohort(cohort)
    tasks = set()
    for fname in c['fc']:
        tasks.add(re.match('.*task-([^_]+)', fname).group(1))
    return list(tasks)
    
