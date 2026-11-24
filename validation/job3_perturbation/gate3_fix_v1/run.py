import sys, ctypes, numpy as np, wfdb, csv, json, collections
from scipy.stats import mannwhitneyu
sys.dont_write_bytecode=True; sys.path.insert(0,'/workspace/link/dr_cleanroom_frozen_v1')
from ref import tier as ref_tier
L=ctypes.CDLL('/workspace/dr_job3/ds1/libdr.so'); D='/workspace/purp/dual-residual-job1/'
cache={}
def sig(r):
    if r not in cache:
        rec=wfdb.rdrecord(D+f'data/mitdb/{r}',physical=False); cache[r]=rec.d_signal[:,rec.sig_name.index('MLII')].astype(np.int64)
    return cache[r]
def ev(a):
    a=np.ascontiguousarray(a,dtype=np.int64); c=ctypes.c_int(); t=ctypes.c_int(); s=ctypes.c_float(); k=ctypes.c_float()
    L.ev(a.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),ctypes.c_ulong(len(a)),ctypes.byref(c),ctypes.byref(t),ctypes.byref(s),ctypes.byref(k))
    return (c.value,t.value),s.value
def phaselock(x,st,en,base):
    votes=collections.Counter(ev(x[st+base+o:en+base+o])[0] for o in range(5))
    d,n=votes.most_common(1)[0]; return d if n>=3 else 'HOLD'
out={}; rng=np.random.default_rng(7)
for N in (1024,4096):
    rows=list(csv.DictReader(open(D+f'dataset_v1/DS1_N{N}.csv')))
    n=0; fA=0; covA=0; fB=0; sV=[]; sN=[]; oV=0; oVs=0; nV=0
    for r in rows:
        x=sig(r['record']); st=int(r['start']); en=int(r['end'])
        if en+6>len(x): continue
        n+=1
        a0=phaselock(x,st,en,0); a1=phaselock(x,st,en,1); fA+=a0!=a1; covA+=a0!='HOLD'
        w0=list(map(int,x[st:en])); w1=list(map(int,x[st+1:en+1]))
        b0=ref_tier(w0); b1=ref_tier(w1); fB+=b0[0]!=b1[0]
        if r['tier'] in ('T2','T3'):
            sV.append(abs(b0[2])); nV+=1; oV+=b0[0]!='None'; w=np.array(w0); rng.shuffle(w); oVs+=ref_tier(list(map(int,w)))[0]!='None'
        elif r['tier']=='None': sN.append(abs(b0[2]))
    p=float(mannwhitneyu(sV,sN,alternative='greater').pvalue)
    out[N]=dict(windows=n,A_flip=fA/n,A_coverage=covA/n,B_flip=fB/n,B_V=nV,B_None=len(sN),B_mean_absS_V=float(np.mean(sV)),B_mean_absS_None=float(np.mean(sN)),B_mw_p=p,B_own_V=oV/nV,B_own_V_shuffled=oVs/nV)
    out[N]['A_P1']='HIT' if out[N]['A_flip']<=0.10 else 'MISS'
    out[N]['B_P1']='HIT' if out[N]['B_flip']<=0.10 else 'MISS'
    out[N]['B_P2']='HIT' if (p<0.01 and out[N]['B_own_V']-out[N]['B_own_V_shuffled']>=0.10) else 'MISS'
json.dump(out,open('results.json','w'),indent=1); print(json.dumps(out,indent=1))
