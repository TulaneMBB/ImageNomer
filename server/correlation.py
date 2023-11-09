
import numpy as np
import scipy.stats as stats
from sklearn.cross_decomposition import CCA
from natsort import natsorted

# My modules
import data
import image

# Get correlation between two one-dimensional variables
# Can be either Pearson's r or Spearman's r
# Do this instead of np.corrcoef to get stats and eliminate nans

def corr_vars(a, b, typ='Pearson'):
    if isinstance(a, list):
        a = np.stack(a)
    if isinstance(b, list):
        b = np.stack(b)
    # Eliminate all nan values
    agood = np.invert(np.isnan(a))
    bgood = np.invert(np.isnan(b))
    a = a[agood*bgood]
    b = b[agood*bgood]
    mu_a = np.mean(a, axis=0, keepdims=True)
    mu_b = np.mean(b, axis=0, keepdims=True)
    a = a - mu_a
    b = b - mu_b
    if typ == 'Spearman':
       # Convert to ranks
       a = np.argsort(a)
       b = np.argsort(b)
    # Calculate correlation
    sigma_ab = np.einsum('a,a->',a,b)
    sigma_aa = np.einsum('a,a->',a,a)
    sigma_bb = np.einsum('a,a->',b,b)
    rho = sigma_ab/(sigma_aa*sigma_bb)**0.5
    # Get t value and p value
    df = len(a)-2
    t = rho*(df/(1-rho**2))**0.5
    if t < 0:
        t = -t
    # Convert to 2-sided p value
    p = (1-stats.t.cdf(t, df))*2
    if p < 1e-20:
        p = 1e-20
    return rho, np.log10(p), df

# Get feature-phenotype correlations, either Pearson's r or Spearman's r
# And associated p values
# p values assumes normality of input features
# Default is to perform Bonferroni correction

def corr_feats(feat, var, typ='Pearson', bonf=True):
    feat = feat - np.mean(feat, axis=0, keepdims=True)
    var = var - np.mean(var)
    if typ == 'Spearman':
       # Convert to ranks
       feat = np.argsort(feat, axis=0)
       var = np.argsort(var)
    # Calculate correlation
    sigma_fv = np.einsum('ab,a->b',feat,var)
    sigma_ff = np.einsum('ab,ab->b',feat,feat)
    sigma_vv = np.einsum('a,a->',var,var)
    rho = sigma_fv/(sigma_ff*sigma_vv)**0.5
    # Sometimes happens with SNPs
    rho[np.isnan(rho)] = 0
    # Get t distribution
    n = feat.shape[0]
    m = feat.shape[1]
    df = n-2
    t = rho*(df/(1-rho**2))**0.5
    t[t < 0] = -t[t < 0]
    # Convert to 2-sided p value
    p = (1-stats.t.cdf(t, df))*2
    # Bonferroni correction
    if bonf:
        p *= m
    # Clamp to prevent huge p values
    p[p > 1] = 1
    p[p < 1e-5] = 1e-5
    return rho, np.log10(p), df

def corr_feats_cca(feat, var):
    feat = feat - np.mean(feat, axis=0, keepdims=True)
    var = var - np.mean(var)
    cca = CCA(n_components=1)
    cca.fit(feat, var)
    load = cca.x_loadings_
    scalar = (feat@load).squeeze()
    rho = np.corrcoef(var, scalar)[0,1]
    n = feat.shape[0]
    m = feat.shape[1]
    df = n-2
    t = rho*(df/(1-rho**2))**0.5
    if t < 0:
        t = -t
    # Convert to 2-sided p value
    p = (1-stats.t.cdf(t, df))*2
    return load.squeeze(), rho, np.log10(p)

# Create correlation matrix and p-value matrix
# For connectivity versus phenotype

def corr_conn_pheno(coh, df, query, typ, tasks, field, cat=None, ses=None):
    group = df.index if query == 'All' else df.query(query).index
    # Get fcs and pheno
    # Fcs allocated later
    pheno = []
    # Get map from index to row number
    # So we can use iloc instead of loc later
    rowmap = dict()
    colmap = df.columns.get_loc(field)
    for sub in group:
        rowmap[sub] = df.index.get_loc(sub)
    # To remove memory pressure, preallocate array
    count = 0
    size = None
    for task in tasks:
        for sub in group:
            if data.has_conn(coh, sub, task, ses, typ=typ):
                p = df.iloc[rowmap[sub], colmap]
                if cat is not None:
                    p = p == cat
                # pandas will fill in data fields that don't exist for an FC with nan?
                # This is easiest way to solve
                elif np.isnan(p):
                    continue
                count += 1
                if count % 10000 == 0:
                    print(count)
                if size is None:
                    fc = data.get_conn(coh, sub, task, ses, typ=typ)
                    size = fc.shape[0]
    fcs = np.empty((count, size))
    print('Done preallocating')
    count = 0
    for task in tasks:
        for sub in group:
            if data.has_conn(coh, sub, task, ses, typ=typ):
                p = df.iloc[rowmap[sub], colmap]
                if cat is not None:
                    p = p == cat
                # pandas will fill in data fields that don't exist for an FC with nan?
                # This is easiest way to solve
                elif np.isnan(p):
                    continue
                pheno.append(p)
                fc = data.get_conn(coh, sub, task, ses, typ=typ)
                fcs[count,:] = fc
                count += 1
                if count % 10000 == 0:
                    print(count)
    #fcs = np.stack(fcs)
    # Get correlation and p-value
    rho, p, df = corr_feats(fcs, pheno)
    _, rhocca, pcca = corr_feats_cca(fcs, pheno)
    rho = data.vec2mat(rho, fillones=False)
    p = data.vec2mat(p, fillones=False)
    # Save correlation for image math
    #rid = session.save(rho)
    #pid = session.save(p)
    # Send image
    rimg = image.imshow(rho, colorbar=True)
    pimg = image.imshow(p, colorbar=True, reverse_cmap=True)
    return rimg, pimg, rhocca, df, pcca

# Create pheno-pheno correlation image as well as statistics
def corr_pheno_pheno(coh, df, query, field1, field2, cat=None):
    # Load group
    subset = df.query(query) if query != 'All' else df
    a = subset[field1].tolist()
    b = subset[field2].tolist()
    c = None
    df = None
    log10p = None
    # Both categorical
    if isinstance(a[0], str) and isinstance(b[0], str):
        aset = natsorted(list(set(a)))
        bset = natsorted(list(set(b)))
        dd = {aa: {bb: 0 for bb in bset} for aa in aset}
        for aa,bb in zip(a,b):
            dd[aa][bb] += 1
        mat = np.zeros((len(aset),len(bset)))
        for i in range(len(aset)):
            for j in range(len(bset)):
                mat[i,j] = dd[aset[i]][bset[j]]
        img = image.matshow(aset, bset, mat, field1, field2)
    elif cat is not None:
        a = subset.query(f'{field1} == "{cat}"')[field2]
        b = subset.query(f'{field1} != "{cat}"')[field2]
        a = a.to_numpy()
        a = a[np.invert(np.isnan(a))] 
        b = b.to_numpy()
        b = b[np.invert(np.isnan(b))] 
        img = image.violin([a,b], [cat, 'Other'], field1, field2)
        a = list(subset[field1] == cat)
        b = list(subset[field2])
        c, log10p, df = corr_vars(a, b)
    else:
        img = image.scatter(a, b, field1, field2)
        c, log10p, df = corr_vars(a, b)
    return img, c, df, log10p

def corr_decomp_pheno(ws, pheno, n):
    ws = np.stack(ws)
    ws = ws[:,:n]
    mu_ws = np.mean(ws, axis=0, keepdims=True)
    ws = ws - mu_ws
    pheno = np.array(pheno)
    mu_pheno = np.mean(pheno) 
    pheno = pheno - mu_pheno
    xx = np.einsum('ab,ab->b', ws, ws)
    xy = np.einsum('ab,a->b', ws, pheno)
    yy = np.einsum('a,a->', pheno, pheno)
    rho = xy / (xx*yy)**0.5
    return rho

def corr_decomp_snps(ws, snps, n):
    ws = np.stack(ws)
    ws = ws[:,:n]
    mu_ws = np.mean(ws, axis=0, keepdims=True)
    ws = ws - mu_ws
    snps = np.stack(snps)
    mu_snps = np.mean(snps, axis=0, keepdims=True)
    snsp = snps - mu_snps
    #rho = []
    #for i in range(n):
    #    xx = np.einsum('a,a->', ws[:,i], ws[:,i])
    #    xy = np.einsum('a,ab->b', ws[:,i], snps)
    #    yy = np.einsum('ab,ab->b', snps, snsp)
    #    rho.append(xy / (xx*yy)**0.5)
    #rho = np.stack(rho)
    xx = np.einsum('ab,ab->b', ws, ws)
    xy = np.einsum('ab,ac->bc', ws, snps)
    yy = np.einsum('ac,ac->c', snps, snsp)
    denom = np.einsum('b,c->bc', xx, yy)
    rho = xy / denom**0.5
    # Sometimes happens with SNPs
    rho[np.isnan(rho)] = 0
    return rho
