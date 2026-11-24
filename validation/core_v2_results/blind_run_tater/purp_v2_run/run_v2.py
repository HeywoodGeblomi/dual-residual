# Runs Purp's CORE_V2_CANDIDATES_v1.md (f2d87c61...) exactly: stride 1, no cap, at every N; sigma = C1/C2/C3 (Link frozen copy) or T1v06.
import sys, json, hashlib; sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/tater/dr_v2_both_v1'); sys.path.insert(0,'/workspace/tater/sigma_tinker_v1'); sys.path.insert(0,'/workspace/link/dr_sigma_candidates_frozen_v1')
import harness2 as H, variants_t1 as V, sigma_candidates as SC
P='/workspace/purp/dr-core-v2-prereg/CORE_V2_CANDIDATES_v1.md'
assert hashlib.sha256(open(P,'rb').read()).hexdigest()=='f2d87c61b0683a6f5e21212096621e3e91bc1ca5ae1f4da12d00190ab444ca33','Purp prereg changed -- STOP'
assert hashlib.sha256(open('/workspace/link/dr_sigma_candidates_frozen_v1/sigma_candidates.py','rb').read()).hexdigest().startswith('0b798952'),'C code changed -- STOP'
def wrap(f):
    def g(s): return f(s.tolist())
    g.__name__='list_'+f.__name__; return g
C={'V2-C1':(wrap(SC.c1_turns),SC.c1_turns,'stride 1 no cap + C1 turns (sample-position parity)'),
   'V2-C2':(wrap(SC.c2_flats),SC.c2_flats,'stride 1 no cap + C2 flat steps (sample-position parity)'),
   'V2-C3':(wrap(SC.c3_changes),SC.c3_changes,'stride 1 no cap + C3 any sign change (sample-position parity)'),
   'V2-T6':(V.v06_ties_inside_dwells,V.v06_ties_inside_dwells,'stride 1 no cap + T1v06 plateau parity')}
vid=sys.argv[1]; fn,src,defn=C[vid]
h=H.code_hash(src,H.samp_full); res=H.evaluate(fn,H.samp_full)
json.dump(dict(id=vid,definition=defn,code_sha256=h,prereg='f2d87c61',results=res),open(f'results/{vid}.json','w'),indent=1)
H.log_entry('VARIANTS_LOG.md',vid,defn,h,res)
