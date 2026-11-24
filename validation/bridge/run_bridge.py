import sys, json, subprocess, hashlib, glob, os, csv
import numpy as np
sys.path.insert(0,'/workspace/link/dr_cleanroom_frozen_v1'); import ref as REF
from variants import tier, RULES, LABEL
rng=np.random.default_rng(20261123)
def walk(n,tie):
    r=rng.random(n); step=np.where(r<tie,0,np.where(r<tie+(1-tie)/2,1,-1)); return np.cumsum(step).astype(np.int64)
# ---- synthetic set: windows of length N+1 so x[0:N] and x[1:N+1] form a one-sample-shift pair
syn=[]
for tie in (0.05,0.2,0.4):
    for N in (64,256,1024,4096):
        for k in range(250): syn.append((tie,N,walk(N+1,tie)))
# ---- step 1: verify the Python core port is bit-exact against the compiled unmodified header
lines=[]
for tie,N,w in syn: lines.append(' '.join(map(str,w[:N]))); lines.append(' '.join(map(str,w[1:N+1])))
out=subprocess.run(['./core_cli'],input='\n'.join(lines)+'\n',capture_output=True,text=True).stdout.split('\n')
names={0:'None',1:'T1',2:'T2',3:'T3'}
cpp=[names[int(l.split()[0])] for l in out if l.strip()]
py=[]
for tie,N,w in syn: py.append(tier(w[:N])); py.append(tier(w[1:N+1]))
port_mismatch=sum(a!=b for a,b in zip(cpp,py)); assert len(cpp)==len(py)
# ---- edge-case set (Cheddar, read-only)
edge=[]
for row in csv.DictReader(open('/workspace/cheddar/dr_edgecases_v1/manifest.csv')):
    x=[int(v) for v in open('/workspace/cheddar/dr_edgecases_v1/'+row['file']).read().split()]
    edge.append((row['case'],x))
edge_pairs=[(c,x) for c,x in edge]; ed=dict(edge)
pairs=[(ed[c],ed[c.replace('_shift1','',1)]) for c in ed if '_shift1' in c and c.replace('_shift1','',1) in ed]
def configs():
    yield 'core',{}
    for r in RULES: yield 'core+'+r,{r:True}            # one rule alone
    acc={}
    for r in RULES:
        acc=dict(acc); acc[r]=True; yield 'chain..'+r,acc  # cumulative toward ref
res={'port_check':{'windows':len(cpp),'mismatches':port_mismatch},'labels':LABEL,'synthetic':{},'edge':{}}
refsyn=[REF.tier(list(map(int,w[:N])))[0] for tie,N,w in syn]
refedge=[REF.tier(x)[0] for c,x in edge]
coresyn=[tier(w[:N]) for tie,N,w in syn]; coreedge=[tier(x) for c,x in edge]
for name,cfg in configs():
    a=[tier(w[:N],**cfg) for tie,N,w in syn]; b=[tier(w[1:N+1],**cfg) for tie,N,w in syn]
    byN={}
    for (tie,N,w),t0,t1 in zip(syn,a,b):
        d=byN.setdefault(N,[0,0]); d[0]+=1; d[1]+=(t0!=t1)
    mix={t:a.count(t)/len(a) for t in ('None','T1','T2','T3')}
    ea=[tier(x,**cfg) for c,x in edge]
    ep=sum(tier(p,**cfg)!=tier(q,**cfg) for p,q in pairs)
    res['synthetic'][name]={'agree_core':float(np.mean([x==y for x,y in zip(a,coresyn)])),'agree_ref':float(np.mean([x==y for x,y in zip(a,refsyn)])),
        'flip_rate_by_N':{str(k):round(v[1]/v[0],3) for k,v in sorted(byN.items())},'tier_mix':{k:round(v,3) for k,v in mix.items()}}
    res['edge'][name]={'agree_core':float(np.mean([x==y for x,y in zip(ea,coreedge)])),'agree_ref':float(np.mean([x==y for x,y in zip(ea,refedge)])),'pair_flips':f'{ep}/{len(pairs)}'}
json.dump(res,open('bridge_results_v1.json','w'),indent=1)
print(json.dumps(res['port_check']))
for name in res['synthetic']:
    s=res['synthetic'][name]; e=res['edge'][name]
    print(f"{name:14s} agree_core={s['agree_core']:.3f} agree_ref={s['agree_ref']:.3f} flips={s['flip_rate_by_N']} mix={s['tier_mix']} | edge core={e['agree_core']:.3f} ref={e['agree_ref']:.3f} pairflips={e['pair_flips']}")
