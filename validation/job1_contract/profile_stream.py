import wfdb, numpy as np, json, hashlib
recs=[l.strip() for l in open('data/mitdb/RECORDS')]
DS1=[101,106,108,109,112,114,115,116,118,119,122,124,201,203,205,207,208,209,215,220,223,230]
DS2=[100,103,105,111,113,117,121,123,200,202,210,212,213,214,219,221,222,228,231,232,233,234]
PACED=[102,104,107,217]
AAMI={'N':'N','L':'N','R':'N','e':'N','j':'N','A':'S','a':'S','J':'S','S':'S','V':'V','E':'V','F':'F','/':'Q','f':'Q','Q':'Q'}
Ns=[64,256,1024,4096,16384]
def stride(N): return 1 if N<=1024 else N//512
out={'records':{},'split':{'DS1':DS1,'DS2':DS2,'excluded_paced':PACED}}
for r in recs:
    rec=wfdb.rdrecord(f'data/mitdb/{r}',physical=False); ann=wfdb.rdann(f'data/mitdb/{r}','atr')
    if 'MLII' not in rec.sig_name: print('no MLII',r,rec.sig_name); continue
    x=rec.d_signal[:,rec.sig_name.index('MLII')].astype(np.int64)
    cls={}
    for s in ann.symbol:
        c=AAMI.get(s); 
        if c: cls[c]=cls.get(c,0)+1
    zr={}
    for N in Ns:
        s=stride(N); d=np.sign(x[s:]-x[:-s]); zr[N]=float((d==0).mean())
    out['records'][r]={'lead':'MLII','fs':rec.fs,'n':int(len(x)),'adc_gain':float(rec.adc_gain[0]),'aami':cls,'zero_rate_by_N':zr}
json.dump(out,open('stream_profile_v0.json','w'),indent=1)
def agg(ids):
    z={N:np.mean([out['records'][str(i)]['zero_rate_by_N'][N] for i in ids]) for N in Ns}
    c={}
    for i in ids:
        for k,v in out['records'][str(i)]['aami'].items(): c[k]=c.get(k,0)+v
    return z,c
for name,ids in [('DS1',DS1),('DS2',DS2)]:
    z,c=agg(ids); print(name,{k:round(v,4) for k,v in z.items()},c)
print(set(r['lead'] for r in out['records'].values()), set(r['adc_gain'] for r in out['records'].values()))
print(hashlib.sha256(open('stream_profile_v0.json','rb').read()).hexdigest())
