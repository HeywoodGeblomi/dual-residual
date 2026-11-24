# Synthetic-only probes (no DS1). Seeded.
import sys, time, numpy as np; sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/tater/sigma_tinker_v1'); sys.path.insert(0,'/workspace/link/dr_sigma_candidates_frozen_v1')
import harness2 as H, harness as H1, variants_t1 as V, sigma_candidates as SC
rng=np.random.default_rng(123)
def ecgish(n):  # quantized smooth wave + spikes + noise, 360Hz-like
    t=np.arange(n+8); x=40*np.sin(2*np.pi*t/300+rng.uniform(0,6))+rng.normal(0,1.2,len(t)).cumsum()*0.3
    for p in range(rng.integers(0,300),len(t)-10,300): x[p:p+10]+=np.hanning(10)*rng.uniform(150,300)
    return np.round(x).astype(np.int64)
# P1 equivalence
ok=0
for _ in range(300):
    n=int(rng.choice([64,256,1000,1024])); x=ecgish(n)[:n]
    a=H.samp_core(x); ok+= np.array_equal(a,H.samp_lag(x)) and np.array_equal(a,H.samp_block(x)) and np.array_equal(a,H1.signs(x))
    assert H.decide(x,V.v05_dwell_nonzero_steps,H.samp_core)==H1.decide(x,V.v05_dwell_nonzero_steps)
print('P1 samplers identical to ba2ea57 at n<=1024, and harness2(core sampler)==sigma_tinker harness:',ok,'/300')
x=ecgish(4096); print('P1 lengths at 4096: core',len(H.samp_core(x[:4096])),'lag',len(H.samp_lag(x[:4096])),'block',len(H.samp_block(x[:4096])),'full',len(H.samp_full(x[:4096])))
# P2 synthetic flip rates at N=4096
wrap=lambda f:(lambda s:f(s.tolist()))
sig={'T1v05':V.v05_dwell_nonzero_steps,'T1v06':V.v06_ties_inside_dwells,'C1':wrap(SC.c1_turns),'C2':wrap(SC.c2_flats),'C3':wrap(SC.c3_changes)}
W=[ecgish(4097) for _ in range(300)]
for sn,sampler in (('core',H.samp_core),('lag',H.samp_lag),('block',H.samp_block),('full',H.samp_full)):
    for k,f in sig.items():
        t0=time.time(); fl=0; tiers=np.zeros(4,int)
        for x in W:
            d0=H.decide(x[:4096],f,sampler); d1=H.decide(x[1:4097],f,sampler); fl+=d0[:2]!=d1[:2]; tiers[d0[1]]+=1
        print(f'P2 synth N=4096 sampler={sn:5s} sigma={k}: flip {fl/len(W):.3f} tiers(None,T1,T2,T3) {tiers.tolist()}  {1000*(time.time()-t0)/len(W)/2:.2f} ms/window')
