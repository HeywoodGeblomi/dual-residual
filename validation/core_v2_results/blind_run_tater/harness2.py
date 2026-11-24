"""Tater dr_v2_both_v1 harness: sigma_tinker_v1 harness generalised to a pluggable sampler. Decision path otherwise identical
(four constants, AND gate, talent order, classical = mean|s|, refusal n<2 or len(s)<4, float32 compares). DS1 only."""
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
def _L(n): return max(n//512 if n>1024 else 1,1)
def samp_core(x):   # ba2ea57 polarity_stream_strided (reference only)
    n=len(x); L=_L(n); idx=np.arange(0,n,L); idx=idx[idx+L<n][:512]
    return np.sign(x[idx+L]-x[idx]).astype(np.int64)
def samp_lag(x):    # (a) lag-not-decimate
    n=len(x); L=_L(n); return np.sign(x[L:]-x[:-L]).astype(np.int64) if n>L else np.zeros(0,np.int64)
def samp_block(x):  # (b) block-mean (exact block sums) decimation
    n=len(x); L=_L(n); nb=n//L; b=x[:nb*L].reshape(nb,L).sum(1)
    return np.sign(b[1:]-b[:-1]).astype(np.int64)
def samp_full(x):   # Purp V2: stride 1, no cap
    return np.sign(x[1:]-x[:-1]).astype(np.int64)
def decide(x, sigma_fn, sampler):
    if len(x)<2: return (0,0,0.0)
    s=sampler(x)
    if len(s)<4: return (0,0,0.0)
    sd=f32(sigma_fn(s))
    cl=f32(np.abs(s).sum())/f32(len(s))
    conf=(cl>f32(0.04)) and not (abs(sd)<f32(0.005))
    if not conf: return (0,0,float(sd))
    if abs(sd)>f32(0.1): t=2
    elif cl>f32(0.2): t=3
    else: t=1
    return (1,t,float(sd))
def evaluate(sigma_fn, sampler):
    rng=np.random.default_rng(7); out={}
    for N in (1024,4096):
        rows=list(csv.DictReader(open(LAB+f'DS1_N{N}.csv')))
        n=flips=0; tiers=np.zeros(4,int); sV=[]; sN=[]; oI=[]; oS=[]; ownNone=[]
        for r in rows:
            x=sig(r['record']); st=int(r['start']); en=int(r['end'])
            if en+1>len(x): continue
            d0=decide(x[st:en],sigma_fn,sampler); d1=decide(x[st+1:en+1],sigma_fn,sampler)
            n+=1; flips+=(d0[0],d0[1])!=(d1[0],d1[1]); tiers[d0[1]]+=1
            if r['tier'] in ('T2','T3'):
                sV.append(abs(d0[2])); w=x[st:en].copy(); rng.shuffle(w)
                oI.append(d0[0]); oS.append(decide(w,sigma_fn,sampler)[0])
            elif r['tier']=='None':
                sN.append(abs(d0[2])); ownNone.append(d0[0])
        oI=np.array(oI); oS=np.array(oS)
        b=int(((oI==1)&(oS==0)).sum()); c=int(((oI==0)&(oS==1)).sum())
        p_shuf=float(binom.sf(b-1,b+c,0.5)) if b+c>0 else 1.0
        try: p_mw=float(mannwhitneyu(sV,sN,alternative='greater').pvalue)
        except ValueError: p_mw=1.0
        gap=float(oI.mean()-oS.mean()); top=float(tiers.max()/n)
        out[N]=dict(windows=n,flip=flips/n,tier_share={k:float(v/n) for k,v in zip(['None','T1','T2','T3'],tiers)},
            top_tier=['None','T1','T2','T3'][int(tiers.argmax())],top_share=top,V=len(sV),Nn=len(sN),
            medS_V=float(np.median(sV)),medS_None=float(np.median(sN)),mw_p=p_mw,own_V=float(oI.mean()),own_V_shuf=float(oS.mean()),
            shuf_gap=gap,mcnemar_b=b,mcnemar_c=c,shuf_p=p_shuf,own_None=float(np.mean(ownNone)),
            bar1=p_mw<0.0167,bar2=flips/n<=0.10,bar3=top<=0.80,bar4=(gap>=0.10 and p_shuf<0.0167))
    out['PASS_ALL']=all(out[N][k] for N in (1024,4096) for k in ('bar1','bar2','bar3','bar4'))
    return out
def code_hash(*objs):
    src=''.join(inspect.getsource(o) for o in objs)+open(__file__).read()
    return hashlib.sha256(src.encode()).hexdigest()
def log_entry(path, vid, defn, h, res):
    import datetime
    L=[f"\n## {vid}  ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')})",f"- Definition: {defn}",f"- Code sha256: `{h}`"]
    for N in (1024,4096):
        r=res[N]; ts=', '.join(f"{k} {v:.3f}" for k,v in r['tier_share'].items())
        P=lambda k:'PASS' if r[k] else 'FAIL'
        L.append(f"- N={N} (n={r['windows']}): flip {r['flip']:.4f} [{P('bar2')}] | sep |sd| V med {r['medS_V']:.4f} vs None med {r['medS_None']:.4f}, MW p={r['mw_p']:.3g} [{P('bar1')}] | tiers {ts}; top {r['top_tier']} {r['top_share']:.3f} [{P('bar3')}] | shuffle own_V {r['own_V']:.3f} vs shuf {r['own_V_shuf']:.3f}, gap {r['shuf_gap']*100:+.1f} pts, McNemar b={r['mcnemar_b']} c={r['mcnemar_c']} p={r['shuf_p']:.3g} [{P('bar4')}] | owned-on-None {r['own_None']:.3f}")
    L.append(f"- ALL BARS: {'PASS' if res['PASS_ALL'] else 'FAIL'}")
    open(path,'a').write('\n'.join(L)+'\n'); print('\n'.join(L))
