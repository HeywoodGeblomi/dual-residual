import wfdb, numpy as np, csv, hashlib, json, os
DS1=[101,106,108,109,112,114,115,116,118,119,122,124,201,203,205,207,208,209,215,220,223,230]
DS2=[100,103,105,111,113,117,121,123,200,202,210,212,213,214,219,221,222,228,231,232,233,234]
AAMI={'N':'N','L':'N','R':'N','e':'N','j':'N','A':'S','a':'S','J':'S','S':'S','V':'V','E':'V','F':'F','/':'Q','f':'Q','Q':'Q'}
Ns=[64,256,1024,4096,16384]
os.makedirs('dataset_v1',exist_ok=True)
summary={};excl={}
def prep(r):
    rec=wfdb.rdrecord(f'data/mitdb/{r}',physical=False); ann=wfdb.rdann(f'data/mitdb/{r}','atr')
    samp=np.array(ann.sample); sym=list(ann.symbol); aux=list(ann.aux_note)
    # record-level V runs >=3 over AAMI-classified beat sequence
    beats=[(s,AAMI[c]) for s,c in zip(samp,sym) if c in AAMI]
    runs=[];i=0
    while i<len(beats):
        if beats[i][1]=='V':
            j=i
            while j+1<len(beats) and beats[j+1][1]=='V': j+=1
            if j-i+1>=3: runs.append((beats[i][0],beats[j][0]))
            i=j+1
        else: i+=1
    # VFL episodes from rhythm marks
    vfl=[];cur=None
    for s,c,a in zip(samp,sym,aux):
        if c=='+':
            a=a.strip('\x00')
            if a.startswith('(VFL'): cur=s
            elif cur is not None: vfl.append((cur,s)); cur=None
    if cur is not None: vfl.append((cur,rec.sig_len))
    flut=samp[np.array(sym)=='!'] if '!' in sym else np.array([])
    return rec.sig_len,samp,sym,runs,vfl,flut
P={r:prep(r) for r in DS1+DS2}
for split,ids in [('DS1',DS1),('DS2',DS2)]:
    for N in Ns:
        cnt={'None':0,'T1':0,'T2':0,'T3':0,'excluded_VFL':0}
        with open(f'dataset_v1/{split}_N{N}.csv','w',newline='') as f:
            w=csv.writer(f); w.writerow(['record','lead','start','end','tier','n_beats'])
            for r in ids:
                L,samp,sym,runs,vfl,flut=P[r]
                for st in range(0,L-N+1,N):
                    en=st+N
                    if any(a<en and b>=st for a,b in vfl) or ((flut>=st)&(flut<en)).any():
                        cnt['excluded_VFL']+=1; continue
                    m=(samp>=st)&(samp<en); cl=[AAMI[s] for s in np.array(sym)[m] if s in AAMI]
                    if any(a<en and b>=st for a,b in runs): t='T3'
                    elif 'V' in cl: t='T2'
                    elif 'S' in cl or 'F' in cl: t='T1'
                    else: t='None'
                    cnt[t]+=1; w.writerow([r,'MLII',st,en,t,len(cl)])
        summary[f'{split}_N{N}']=cnt
print('VFL episodes', {r:P[r][4] for r in P if P[r][4]}, 'flutter waves', {r:len(P[r][5]) for r in P if len(P[r][5])})
print('DS2 runs>=3', sum(len(P[r][3]) for r in DS2))
man={fn:hashlib.sha256(open('dataset_v1/'+fn,'rb').read()).hexdigest() for fn in sorted(os.listdir('dataset_v1'))}
json.dump({'tier_counts':summary,'sha256':man,'rules':'T3 if window overlaps any record-level run of >=3 consecutive AAMI V beats; windows overlapping a (VFL episode or any ! flutter wave excluded'},open('dataset_v1_manifest.json','w'),indent=1)
for k,v in summary.items(): print(k,v)
