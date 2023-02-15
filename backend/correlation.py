
import numpy as np
import scipy.stats as stats

'''
Get feature correlations, either Pearson's r or Spearman's r
And associated p values
P values assumes normality of input features
Default is to perform Bonferroni correction
'''
def corr_feat(feats, var, cat=None, typ='Pearson', bonf=True):
    if cat is not None:
        var = [1 if item == cat else 0 for item in var]
    if isinstance(feats, list):
        feats = np.stack(feats)
    mu = np.mean(feats, axis=0, keepdims=True)
    feats = feats - mu
    var = var - np.mean(var)
    if typ == 'Spearman':
       # Convert to ranks
       feats = np.argsort(feats)
       var = np.argsort(var)
    # Calculate correlation
    sigma_fv = np.einsum('ab,a->b',feats,var)
    sigma_ff = np.einsum('ab,ab->b',feats,feats)
    sigma_vv = np.einsum('a,a->',var,var)
    rho = sigma_fv/(sigma_ff*sigma_vv)**0.5
    # Sometimes happens with SNPs
    rho[np.isnan(rho)] = 0
    # Get t distribution
    n = feats.shape[0]
    m = feats.shape[1]
    df = n-2
    #rho[rho > 0] = 0
    t = rho*(df/(1-rho**2))**0.5
    t[t < 0] = -t[t < 0]
    # Convert to 2-sided p value
    p = (1-stats.t.cdf(t, df))*2
    # Bonferroni correction
    if bonf:
        p *= m
    p[p > 1] = 1
    p[p < 1e-5] = 1e-5
    return rho, np.log10(p)

def corr_var(var1, var2):
    return np.corrcoef(var1, var2)[0,1]

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
