
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
    feats -= mu
    var -= np.mean(var)
    if typ == 'Spearman':
       # Convert to ranks
       feats = np.argsort(feats)
       var = np.argsort(var)
    # Calculate correlation
    sigma_fv = np.einsum('ab,a->b',feats,var)
    sigma_ff = np.einsum('ab,ab->b',feats,feats)
    sigma_vv = np.einsum('a,a->',var,var)
    rho = sigma_fv/(sigma_ff*sigma_vv)**0.5
    # Get t distribution
    n = feats.shape[0]
    m = feats.shape[1]
    df = n-2
    #rho[rho > 0] = 0
    t = rho*(df/(1-rho**2))**0.5
    t[t < 0] = -t[t < 0]
    # Convert to 2-sided p value
    p = (1-stats.t.cdf(t, df))*2
    if bonf:
        p *= m
    p[p > 1] = 1
    p[p < 1e-5] = 1e-5
    return rho, np.log10(p)

def corr_var(var1, var2):
    return np.corrcoef(var1, var2)[0,1]
