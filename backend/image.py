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

def has_many_rare(y):
    yset = set()
    for yy in y:
        yset.add(yy)
    return len(yset) > 10

def collapse_rare(y):
    counts = dict()
    tot = 0
    for yy in y:
        if yy not in counts:
            counts[yy] = 1
        else:
            counts[yy] += 1
        tot += 1
    for i in range(len(y)):
        if counts[y[i]] < 0.02*tot:
            y[i] = 'other'
    return y

def histogram(ys, ylabels=None, bins=20, density=True):
    fig, ax = plt.subplots()
    if ylabels is None:
        ax.hist(ys, bins=bins)
    else:
        for y, lab in zip(ys, ylabels):
            # If categorical histogram, and many different distinct values,
            # Put less that 2% in other category
            if isinstance(y[0], str) and has_many_rare(y):
                collapse_rare(y)
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

def boxplot_private(data, labels):
    fig, ax = plt.subplots()
    ax.boxplot(data, labels=labels)
    ax.tick_params(axis='x', labelrotation=-60)
    return tobase64(fig)

def snps_hist_private(data):
    fig, ax = plt.subplots()
    data[np.isnan(data)] = -1
    ax.hist(data, bins=[-1.5,-0.5,0.5,1.5,2.5], rwidth=0.8)
    ax.set_xticks(ticks=[-1,0,1,2], 
        labels=['Miss', 'Resv', 'Het', 'Dom'], 
        fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=20)
    return tobase64(fig)

def snps_violin_private(lst):
    fig, ax = plt.subplots()
    labels=['Miss', 'Resv', 'Het', 'Dom']
    ax.violinplot(lst, positions=[-1,0,1,2])
    ax.set_xticks([-1,0,1,2])
    ax.set_xticklabels(labels)
    ax.set_ylabel('# SNPs')
    return tobase64(fig)

def two_axes_plot_private(dat1, dat2, lab1, lab2):
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = iter(prop_cycle.by_key()['color'])
    c1 = next(colors)
    c2 = next(colors)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(np.arange(len(dat1)), dat1, color=c1)
    ax2.plot(np.arange(len(dat1)), dat2, color=c2)
    ax1.set_xlabel('SNP')
    ax1.set_ylabel(lab1, color=c1)
    ax2.set_ylabel(lab2, color=c2)
    return tobase64(fig)

def plot_private(data, labels=None):
    fig, ax = plt.subplots()
    if isinstance(data, list):
        if labels is None:
            labels = len(data)*[None]
        for d,lab in zip(data, labels):
            ax.plot(d, label=lab)
        ax.legend()
    else:
        ax.plot(data)
    return tobase64(fig)

def fill_between_private(bot, top):
    fig, ax = plt.subplots()
    ax.fill_between(np.arange(bot.shape[0]), bot, y2=top, alpha=1)
    return tobase64(fig)

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

def snps_violin(lst):
    return mp_wrap(snps_violin_private, lst)

def two_axes_plot(dat1, dat2, lab1, lab2):
    return mp_wrap(two_axes_plot_private, dat1, dat2, lab1, lab2)

def plot(data, labels=None):
    return mp_wrap(plot_private, data, labels)

def fill_between(bot, top):
    return mp_wrap(fill_between_private, bot, top)

def boxplot(data, labels):
    return mp_wrap(boxplot_private, data, labels)
