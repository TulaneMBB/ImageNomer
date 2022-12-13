'''View data as images'''

import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import multiprocessing as mp

def tobase64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def imshow_private(fc, colorbar=True):
    fig, ax = plt.subplots()
    im = ax.imshow(fc)
    if colorbar:
        fig.colorbar(mappable=im, ax=ax)
    return tobase64(fig)

def mp_wrap(f, *args):
    q = mp.Queue()
    def wrapper(q, *args):
        img = f(*args)
        q.put(img)
    p = mp.Process(target=wrapper, args=(q,*args))
    p.start()
    img = q.get()
    p.join()
    return img

def histogram(ys, ylabels, bins=20, density=True):
    fig, ax = plt.subplots()
    for y, lab in zip(ys, ylabels):
        ax.hist(y, label=lab, bins=bins, histtype='step')
    ax.legend()
    return tobase64(fig)
    
def groups_hist_private(df, groups, field):
    ys = []
    ylabels = []
    for group in groups.keys():
        ylabels.append(group)
        ys.append(df.loc[groups[group], field])
    return histogram(ys, ylabels)


def scatter_private(var1, var2, name1, name2):
    fig, ax = plt.subplots()
    ax.scatter(var1, var2)
    ax.set_xlabel(name1)
    ax.set_ylabel(name2)
    return tobase64(fig)

def violin_private(data, labels, field):
    fig, ax = plt.subplots()
    ax.violinplot(data, positions=[1,2])
    ax.set_xticks([1,2])
    ax.set_xticklabels(labels)
    ax.set_ylabel(field)
    return tobase64(fig)

# Weird stuff with matplotlib and multithreading? crashes the process
# Can fix with mutliprocessing
def imshow(fc, colorbar=True):
    return mp_wrap(imshow_private, fc, colorbar)

def groups_hist(df, groups, field):
    return mp_wrap(groups_hist_private, df, groups, field)

def scatter(var1, var2, name1, name2):
    return mp_wrap(scatter_private, var1, var2, name1, name2)

def violin(data, labels, field):
    return mp_wrap(violin_private, data, labels, field)