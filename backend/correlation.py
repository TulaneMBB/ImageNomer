
import numpy as np

def correlate_feat(feats, var, cat=None):
    if cat is not None:
        var = [1 if item == cat else 0 for item in var]
    if isinstance(feats, list):
        feats = np.stack(feats)
    mu = np.mean(feats, axis=0, keepdims=True)
    feats -= mu
    var -= np.mean(var)
    sigma_fv = np.einsum('ab,a->b',feats,var)
    sigma_ff = np.einsum('ab,ab->b',feats,feats)
    sigma_vv = np.einsum('a,a->',var,var)
    rho = sigma_fv/(sigma_ff*sigma_vv)**0.5
    return rho

def correlate_var(var1, var2):
    return np.corrcoef(var1, var2)[0,1]