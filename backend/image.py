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

def histogram(ys, ylabels=None, bins=20, density=True):
    fig, ax = plt.subplots()
    if ylabels is None:
        ax.hist(ys, bins=bins)
    else:
        for y, lab in zip(ys, ylabels):
            ax.hist(y, label=lab, bins=bins, histtype='step')
        ax.legend()
    return tobase64(fig)

def imshow_private(fc, colorbar=True, reverse_cmap=False):
    fig, ax = plt.subplots()
    cmap = 'viridis_r' if reverse_cmap else 'viridis'
    im = ax.imshow(fc, cmap=cmap)
    if colorbar:
        fig.colorbar(mappable=im, ax=ax)
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

def bar_private(data, labels):
    fig, ax = plt.subplots()
    x = np.arange(len(data))
    ax.bar(x, height=data, tick_label=labels)
    ax.tick_params(axis='x', labelrotation=-60)
    return tobase64(fig)

# No labels, since this is single subject
def snps_hist_private(data):
    return histogram(data)

# def plot_private(data, labels=None):
#     fig, ax = plt.subplots()
#     if isinstance(data, list):
#         if labels is None:
#             labels = len(data)*[None]
#         for d,lab in zip(data, labels):
#             ax.plot(d, label=lab)
#     else:
#         ax.plot(data)
#     ax.legend()
#     return tobase64(fig)

# Weird stuff with matplotlib and multithreading? crashes the process
# Can fix with mutliprocessing
def imshow(fc, colorbar=True, reverse_cmap=False):
    return mp_wrap(imshow_private, fc, colorbar, reverse_cmap)

def groups_hist(df, groups, field):
    return mp_wrap(groups_hist_private, df, groups, field)

def scatter(var1, var2, name1, name2):
    return mp_wrap(scatter_private, var1, var2, name1, name2)

def violin(data, labels, field):
    return mp_wrap(violin_private, data, labels, field)

def bar(data, labels):
    return mp_wrap(bar_private, data, labels)

def snps_hist(data):
    return mp_wrap(snps_hist_private, data)

# def plot(data, labels):
#     return mp_wrap(plot_private, data, labels)
