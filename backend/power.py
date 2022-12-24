'''Power ROI functions'''

import numpy as np

ours2orig = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 
28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 254, 41, 42, 43, 44, 45, 
46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 
65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 85, 
86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 
104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 
119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 136, 138, 132, 
133, 134, 135, 220, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 
153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 
168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 185, 186, 
187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 
202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 
217, 218, 219, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 
233, 137, 234, 235, 236, 237, 238, 239, 240, 241, 250, 251, 255, 256, 257, 
258, 259, 260, 261, 262, 263, 242, 243, 244, 245, 0, 1, 2, 3, 4, 5, 6, 7, 8, 
9, 10, 11, 83, 84, 131, 139, 140, 141, 181, 182, 183, 184, 246, 247, 248, 
249, 252, 253]

def make_fn_map(bounds):
    fnidx = 0
    bmap = dict()
    for i in range(264):
        if i >= bounds[fnidx]:
            fnidx += 1
        bmap[i] = fnidx
    return bmap

bounds = [30, 35, 49, 62, 120, 125, 156, 181, 199, 212, 221, 232, 236, 264]
fn_map = make_fn_map(bounds)

fn_names = 'SMT,SMH,CNG,AUD,DMN,MEM,VIS,FRNT,SAL,SUB,VATN,DATN,CB,UNK'.split(',')
fn_names_map = {idx: fn_names[fn] for idx,fn in fn_map.items()}

rois_a, rois_b = np.triu_indices(264,1)

def remap(fc, roimap=ours2orig):
    fc = fc[roimap,:]
    fc = fc[:,roimap]
    return fc

def label(idcs, labtype='raw'):
    if labtype == 'raw':
        return [str(idx) for idx in idcs]
    if labtype == 'rois':
        return [f'{rois_a[idx]}-{rois_b[idx]}' for idx in idcs]
    if labtype == 'fns':
        fns = []
        for idx in idcs:
            a, b = rois_a[idx], rois_b[idx]
            fns.append(f'{fn_names_map[a]}-{fn_names_map[b]}')
        return fns
