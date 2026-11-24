# Diagnostic on ALREADY-LOGGED variants only (no new sigma definition): N=4096 shift behaviour.
import sys, csv, numpy as np; sys.dont_write_bytecode=True
import harness as H, variants_t1 as V
for vid in sys.argv[1:]:
    fn=V.VARIANTS[vid][0]; a=[];b=[];trans={}
    for r in csv.DictReader(open(H.LAB+'DS1_N4096.csv')):
        x=H.sig(r['record']); st=int(r['start']); en=int(r['end'])
        if en+1>len(x): continue
        d0=H.decide(x[st:en],fn); d1=H.decide(x[st+1:en+1],fn); a.append(abs(d0[2])); b.append(abs(d1[2]))
        if d0[1]!=d1[1]: k=tuple(sorted((d0[1],d1[1]))); trans[k]=trans.get(k,0)+1
    a=np.array(a);b=np.array(b)
    print(vid,'corr|sd| off0/off1 =%.3f'%np.corrcoef(a,b)[0,1],'sd(|sd|)=%.4f'%a.std(),'sd(diff)=%.4f'%(a-b).std(),'flip transitions (0=None,2=T2,3=T3):',trans)
