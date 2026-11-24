"""Bridge v1 (Tater): controlled one-rule-at-a-time comparison between core ba2ea57 and Purp's frozen clean-room ref (effc85ac).
Each variant starts from an exact Python port of the core and swaps in exactly the named clean-room assumption(s)."""
import numpy as np
f32=np.float32
TIERS=['None','T1','T2','T3']

def signs(x, stride1_nocap):
    x=np.asarray(x,dtype=np.int64); n=len(x)
    if stride1_nocap:
        return np.sign(x[1:]-x[:-1]).astype(np.int64)
    if n<2: return np.zeros(0,dtype=np.int64)
    stride = n//512 if n>1024 else 1
    stride=max(stride,1)
    idx=np.arange(0,n,stride); idx=idx[idx+stride<n][:512]
    return np.sign(x[idx+stride]-x[idx]).astype(np.int64)

def sigma_core(s, nocap):
    T=len(s)
    if T<4: return f32(0)
    above=(s>0)
    ev=np.nonzero(above[1:]!=above[:-1])[0]+1
    if not nocap: ev=ev[:512]
    if len(ev)<4: return f32(0)
    e=ev[0::2]
    if not nocap: e=e[:256]
    if len(e)<2: return f32(0)
    vals=s[e].astype(np.float64)
    ve=vals[0::2]; vo=vals[1::2]
    me=f32(ve.sum())/f32(len(ve)) if len(ve) else f32(0)
    mo=f32(vo.sum())/f32(len(vo)) if len(vo) else f32(0)
    return f32(me-mo)

def sigma_A3(s):
    z=(s==0).astype(np.float64)
    ev=z[0::2]; od=z[1::2]
    return (ev.mean() if len(ev) else 0.0)-(od.mean() if len(od) else 0.0)

def classical_core(s):
    return f32(np.abs(s).sum())/f32(len(s))

def classical_A4(s):
    pairs=len(s)-1
    if pairs<=0: return 0.0
    a=s[:-1]; b=s[1:]
    return float(((a!=0)&(b!=0)&(a!=b)).sum())/pairs

def tier(x, G19=False, G23=False, G4=False, G56=False, G78=False):
    n=len(x)
    if G19 and n<3: return 'None'
    if not G19 and n<2: return 'None'
    s=signs(x, G19)
    if len(s)<4 and not G19: return 'None'
    if len(s)<2 and G19: return 'None'
    sd = sigma_A3(s) if G23 else sigma_core(s, nocap=G19)
    cl = classical_A4(s) if G4 else classical_core(s)
    if G56 and not (s==0).any(): return 'None'           # A5 refuse on tie-free
    floor_ok = (abs(sd) > 0.005) if G78 else not (abs(sd) < f32(0.005))
    owned = ((cl > 0.04) or floor_ok) if G56 else ((cl > f32(0.04)) and floor_ok)
    if not owned: return 'None'
    t2 = abs(sd) > (0.1 if G78 else f32(0.1)); t3 = cl > (0.2 if G78 else f32(0.2))
    if G78:
        return 'T3' if t3 else ('T2' if t2 else 'T1')
    return 'T2' if t2 else ('T3' if t3 else 'T1')

RULES=['G19','G23','G4','G56','G78']
LABEL={'G19':'sampling: stride 1, no caps (G1+G9)','G23':'sigma = tie parity on sign index (G2+G3)','G4':'classical = reversal fraction (G4)',
       'G56':'ownership OR + tie-free refuse (G5+G6)','G78':'T3-before-T2 precedence + strict floor (G7+G8)'}
