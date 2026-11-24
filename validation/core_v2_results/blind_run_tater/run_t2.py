import sys, json; sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/tater/sigma_tinker_v1')
import harness2 as H, variants_t1 as V
TRIES={'T2v01':(H.samp_lag,'T1v05','(a) lag-not-decimate + T1v05 dwell parity (non-tie steps)'),
       'T2v02':(H.samp_lag,'T1v06','(a) lag-not-decimate + T1v06 plateau parity'),
       'T2v03':(H.samp_block,'T1v05','(b) block-mean decimation + T1v05 dwell parity (non-tie steps)'),
       'T2v04':(H.samp_block,'T1v06','(b) block-mean decimation + T1v06 plateau parity')}
vid=sys.argv[1]; samp,sv,defn=TRIES[vid]; fn=V.VARIANTS[sv][0]
h=H.code_hash(fn,samp); res=H.evaluate(fn,samp)
json.dump(dict(id=vid,definition=defn,code_sha256=h,results=res),open(f'results/{vid}.json','w'),indent=1)
H.log_entry('VARIANTS_LOG.md',vid,defn,h,res)
