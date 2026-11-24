"""Tater's sigma_delta variants. Input: core sign stream s (np int64 array of -1/0/+1). Output: sigma (float)."""
import numpy as np
def v00_core(s):  # BASELINE: ba2ea57 detail::compute, ported bit-exact (bridge_v1 sigma_core, nocap=False)
    f32=np.float32; T=len(s)
    if T<4: return f32(0)
    above=(s>0); ev=np.nonzero(above[1:]!=above[:-1])[0]+1; ev=ev[:512]
    if len(ev)<4: return f32(0)
    e=ev[0::2][:256]
    if len(e)<2: return f32(0)
    vals=s[e].astype(np.float64); ve=vals[0::2]; vo=vals[1::2]
    me=f32(ve.sum())/f32(len(ve)) if len(ve) else f32(0); mo=f32(vo.sum())/f32(len(vo)) if len(vo) else f32(0)
    return f32(me-mo)
VARIANTS={'T1v00':(v00_core,'BASELINE (not a candidate): unmodified ba2ea57 sigma, reproduction check only')}

def _held(s):
    """ties hold the previous nonzero sign; leading ties dropped. returns held array (+1/-1) and its positions"""
    nz=np.nonzero(s)[0]
    if len(nz)==0: return np.zeros(0,np.int64), nz
    h=s[nz]; return h, nz
def _crossings(s):
    """all direction crossings of the tie-held sign stream: positions (in s) of the first nonzero step after a direction change"""
    h,nz=_held(s)
    if len(h)<2: return np.zeros(0,np.int64), h, nz
    k=np.nonzero(h[1:]!=h[:-1])[0]+1     # index into nz
    return k, h, nz
def _norm_diff(ve,vo):
    if len(ve)<2 or len(vo)<2: return 0.0
    me=ve.mean(); mo=vo.mean()
    return 0.0 if me+mo==0 else (me-mo)/(me+mo)

def v01_dwell_hold(s):
    """dwell-length parity over ALL crossings (ties hold sign). value = length (steps in s) of each complete run between consecutive crossings."""
    k,h,nz=_crossings(s)
    if len(k)<5: return 0.0
    pos=nz[k]; d=np.diff(pos).astype(float)     # complete dwells
    return _norm_diff(d[0::2],d[1::2])
def v02_flat_turn(s):
    """over ALL crossings (ties hold sign), value = 1 if the turn passes through >=1 tie (flat peak/trough), else 0. even-odd by event index = peaks vs troughs. tie-free -> 0 exactly."""
    k,h,nz=_crossings(s)
    if len(k)<4: return 0.0
    gap=(nz[k]-nz[k-1])>1                         # a zero sat between the last step before and the first step after the turn
    v=gap.astype(float); ve=v[0::2]; vo=v[1::2]
    return ve.mean()-vo.mean()
def v03_tie_runs(s):
    """zero-dwell runs: events = maximal runs of ties, value = run length, even-odd by run index, normalized (me-mo)/(me+mo). fewer than 4 runs (incl. tie-free) -> 0."""
    z=np.concatenate(([0],(s==0).astype(np.int8),[0])); dz=np.diff(z)
    st=np.nonzero(dz==1)[0]; en=np.nonzero(dz==-1)[0]
    if len(st)<4: return 0.0
    L=(en-st).astype(float); return _norm_diff(L[0::2],L[1::2])
VARIANTS.update({
 'T1v01':(v01_dwell_hold,'Dwell parity: all crossings of the tie-held sign stream; value = complete dwell length; even-odd by event index (= rising-run vs falling-run length), normalized (me-mo)/(me+mo)'),
 'T1v02':(v02_flat_turn,'Flat-turn parity: all crossings (tie-held); value = 1 if the turn passes through a tie; even-odd by event index (= flat peaks vs flat troughs share); tie-free -> 0'),
 'T1v03':(v03_tie_runs,'Zero-dwell runs: events = maximal tie runs; value = run length; even-odd by run index, normalized (me-mo)/(me+mo); <4 runs -> 0'),
})

def v04_dwell_core_events(s):
    """core's own event definition (crossings of s>0, i.e. rising vs not-rising), but ALL events, value = complete dwell length, even-odd by event index, normalized."""
    above=(s>0); ev=np.nonzero(above[1:]!=above[:-1])[0]+1
    if len(ev)<5: return 0.0
    d=np.diff(ev).astype(float); return _norm_diff(d[0::2],d[1::2])
def v05_dwell_nonzero_steps(s):
    """dwell parity like T1v01 but dwell measured in non-tie steps only (ties neither extend nor break a run): pure rise/fall run-count asymmetry."""
    k,h,nz=_crossings(s)
    if len(k)<5: return 0.0
    d=np.diff(k).astype(float); return _norm_diff(d[0::2],d[1::2])
def v06_ties_inside_dwells(s):
    """all crossings (tie-held); value = number of ties inside each complete dwell; sigma = (sum even - sum odd)/(sum all) = rising-run vs falling-run share of plateau time. tie-free -> 0 exactly."""
    k,h,nz=_crossings(s)
    if len(k)<5: return 0.0
    pos=nz[k]; d=np.diff(pos)-np.diff(k)          # ties inside each complete dwell
    tot=d.sum()
    if tot==0: return 0.0
    return float(d[0::2].sum()-d[1::2].sum())/tot
VARIANTS.update({
 'T1v04':(v04_dwell_core_events,"Dwell parity on the core's own events (crossings of s>0 = rising vs not-rising), ALL events, value = complete dwell length, normalized (me-mo)/(me+mo)"),
 'T1v05':(v05_dwell_nonzero_steps,'Dwell parity (tie-held crossings) with dwell counted in non-tie steps only, normalized (me-mo)/(me+mo)'),
 'T1v06':(v06_ties_inside_dwells,'Plateau parity: all tie-held crossings; value = ties inside each complete dwell; (sum even - sum odd)/sum = rising- vs falling-run share of plateau time; tie-free -> 0'),
})
