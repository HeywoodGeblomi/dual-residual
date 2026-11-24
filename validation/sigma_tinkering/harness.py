"""Tater sigma_tinker_v1 harness. DS1 only. Core decision path = bit-exact port of ba2ea57 (bridge_v1/variants.py),
with ONLY sigma_delta swapped. Sampling, classical, dual_confirm, compute_talent and the four constants unchanged."""
import sys, json, csv, hashlib, inspect, numpy as np
from scipy.stats import mannwhitneyu, binom
sys.dont_write_bytecode=True
f32=np.float32
CACHE='/workspace/toni/dual-residual-job4/cache/'
LAB='/workspace/purp/dual-residual-job1/dataset_v1/'
META=json.load(open(CACHE+'meta.json'))
DS1=set(META['ds1_records']); DENY=set(META['ds2_denylist'])|set(META['excluded_denylist'])
_sig={}
def sig(r):
    r=int(r); assert r in DS1 and r not in DENY, f'record {r} not DS1 -- STOP'
    if r not in _sig: _sig[r]=np.fromfile(CACHE+f'rec_{r}.i16',dtype='<i2').astype(np.int64)
    return _sig[r]
def signs(x):  # core polarity_stream_strided, byte-identical semantics
    n=len(x); stride=n//512 if n>1024 else 1; stride=max(stride,1)
    idx=np.arange(0,n,stride); idx=idx[idx+stride<n][:512]
    return np.sign(x[idx+stride]-x[idx]).astype(np.int64)
def decide(x, sigma_fn):
    """returns (confirmed, talent, sigma). Talent 0..3 = None,T1,T2,T3"""
    if len(x)<2: return (0,0,0.0)
    s=signs(x)
    if len(s)<4: return (0,0,0.0)
    sd=f32(sigma_fn(s))
    cl=f32(np.abs(s).sum())/f32(len(s))                 # classical, unchanged
    classical= cl>f32(0.04)
    conf = classical and not (abs(sd)<f32(0.005))       # dual_confirm, unchanged
    if not conf: return (0,0,float(sd))
    if abs(sd)>f32(0.1): t=2                            # compute_talent, unchanged order
    elif cl>f32(0.2): t=3
    else: t=1
    return (1,t,float(sd))
def evaluate(sigma_fn):
    rng=np.random.default_rng(7)   # one generator over N=1024 then 4096, in row order (matches Lucas run_v1.py)
    out={}
    for N in (1024,4096):
        rows=list(csv.DictReader(open(LAB+f'DS1_N{N}.csv')))
        n=flips=0; tiers=np.zeros(4,int); sV=[]; sN=[]; oI=[]; oS=[]; ownNone=[]
        for r in rows:
            x=sig(r['record']); st=int(r['start']); en=int(r['end'])
            if en+1>len(x): continue
            d0=decide(x[st:en],sigma_fn); d1=decide(x[st+1:en+1],sigma_fn)
            n+=1; flips+= (d0[0],d0[1])!=(d1[0],d1[1]); tiers[d0[1]]+=1
            if r['tier'] in ('T2','T3'):
                sV.append(abs(d0[2])); w=x[st:en].copy(); rng.shuffle(w)
                oI.append(d0[0]); oS.append(decide(w,sigma_fn)[0])
            elif r['tier']=='None':
                sN.append(abs(d0[2])); ownNone.append(d0[0])
        oI=np.array(oI); oS=np.array(oS)
        b=int(((oI==1)&(oS==0)).sum()); c=int(((oI==0)&(oS==1)).sum())
        p_shuf=float(binom.sf(b-1,b+c,0.5)) if b+c>0 else 1.0   # exact one-sided McNemar (sign test on discordant pairs)
        try: p_mw=float(mannwhitneyu(sV,sN,alternative='greater').pvalue)
        except ValueError: p_mw=1.0
        gap=float(oI.mean()-oS.mean()); top=float(tiers.max()/n)
        out[N]=dict(windows=n,flip=flips/n,tier_share={k:float(v/n) for k,v in zip(['None','T1','T2','T3'],tiers)},
            top_tier=['None','T1','T2','T3'][int(tiers.argmax())],top_share=top,
            V=len(sV),Nn=len(sN),medS_V=float(np.median(sV)),medS_None=float(np.median(sN)),
            meanS_V=float(np.mean(sV)),meanS_None=float(np.mean(sN)),mw_p=p_mw,
            own_V=float(oI.mean()),own_V_shuf=float(oS.mean()),shuf_gap=gap,mcnemar_b=b,mcnemar_c=c,shuf_p=p_shuf,
            own_None=float(np.mean(ownNone)),
            bar1=p_mw<0.0167, bar2=flips/n<=0.10, bar3=top<=0.80, bar4=(gap>=0.10 and p_shuf<0.0167))
    out['PASS_ALL']=all(out[N][k] for N in (1024,4096) for k in ('bar1','bar2','bar3','bar4'))
    return out
def code_hash(fn):
    src=inspect.getsource(fn)+open(__file__).read()
    return hashlib.sha256(src.encode()).hexdigest()
