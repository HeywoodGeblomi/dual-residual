import ctypes, numpy as np, wfdb, csv, json
from scipy.stats import mannwhitneyu
L=ctypes.CDLL('./libdr.so'); D='/workspace/purp/dual-residual-job1/'
cache={}
def sig(r):
    if r not in cache:
        rec=wfdb.rdrecord(D+f'data/mitdb/{r}',physical=False); cache[r]=rec.d_signal[:,rec.sig_name.index('MLII')].astype(np.int64)
    return cache[r]
def ev(a):
    a=np.ascontiguousarray(a,dtype=np.int64); c=ctypes.c_int(); t=ctypes.c_int(); s=ctypes.c_float(); k=ctypes.c_float()
    L.ev(a.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),ctypes.c_ulong(len(a)),ctypes.byref(c),ctypes.byref(t),ctypes.byref(s),ctypes.byref(k))
    return c.value,t.value,s.value,k.value
out={}
rng=np.random.default_rng(7)
for N in (1024,4096):
    rows=list(csv.DictReader(open(D+f'dataset_v0/DS1_N{N}.csv')))
    flips=0;n=0;sV=[];sN=[];oV=0;oVs=0;nV=0;own_tab={}
    for r in rows:
        x=sig(r['record']); st=int(r['start']); en=int(r['end'])
        if en+1>len(x): continue
        e0=ev(x[st:en]); e1=ev(x[st+1:en+1]); n+=1; flips+= (e0[0],e0[1])!=(e1[0],e1[1])
        own_tab.setdefault(r['tier'],[0,0]); own_tab[r['tier']][0]+=e0[0]; own_tab[r['tier']][1]+=1
        if r['tier'] in ('T2','T3'):
            sV.append(abs(e0[2])); nV+=1; oV+=e0[0]; w=x[st:en].copy(); rng.shuffle(w); oVs+=ev(w)[0]
        elif r['tier']=='None': sN.append(abs(e0[2]))
    p=mannwhitneyu(sV,sN,alternative='greater').pvalue
    out[N]=dict(windows=n,flip_rate=flips/n,V_windows=nV,None_windows=len(sN),mean_absS_V=float(np.mean(sV)),mean_absS_None=float(np.mean(sN)),mw_p=float(p),own_V=oV/nV,own_V_shuffled=oVs/nV,own_by_tier={k:v[0]/v[1] for k,v in own_tab.items()},tier_n={k:v[1] for k,v in own_tab.items()})
json.dump(out,open('results.json','w'),indent=1); print(json.dumps(out,indent=1))
