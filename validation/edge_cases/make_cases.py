#!/usr/bin/env python3
"""Hard-case input windows for the Dual Residual clean-room vs core comparison (v1, Cheddar-Panama).
Inputs only: no spec, no core code read or imported. Seed fixed. Each case file = one window of
whitespace-separated raw ints. Pairs named *_shift1 are the same series moved one sample later."""
import random, hashlib, os, csv
R=random.Random(20261123)
Ns=[64,256,1024,4096,16384]
cases=[]
def add(name,N,x,desc):
    fn=f'cases/{name}_N{N}.txt'; open(fn,'w').write(' '.join(map(str,x))+'\n')
    cases.append((fn,name,N,len(x),desc))
def pair(name,N,y,desc):            # y has length N+1
    add(name,N,y[:N],desc); add(name+'_shift1',N,y[1:N+1],desc+' (shifted one sample)')
def walk(L,p0,start=1024):
    x=[start]
    for _ in range(L-1):
        r=R.random(); x.append(x[-1] if r<p0 else x[-1]+(1 if R.random()<.5 else -1))
    return x
for N in Ns:
    pair('flat',N,[1000]*(N+1),'all samples equal: every comparison ties')
    pair('ramp',N,list(range(N+1)),'strictly increasing: no ties')
    pair('alternate',N,[i%2 for i in range(N+1)],'0,1,0,1: every step reverses, no ties')
    pair('ramp_jitter',N,[i+R.choice((-1,0,1)) for i in range(N+1)],'ramp plus +/-1 jitter (Lucas false-alarm case)')
    # ties only on even-indexed steps vs only odd-indexed steps: maximal parity imbalance, flips under a 1-sample shift
    y=[0];
    for i in range(N): y.append(y[-1] if i%2==0 else y[-1]+1)
    pair('ties_even_steps',N,y,'ties on every even-indexed step only')
    y=[0]
    for i in range(N): y.append(y[-1] if i%2==1 else y[-1]+1)
    pair('ties_odd_steps',N,y,'ties on every odd-indexed step only')
    y=[0]
    for i in range(N): y.append(y[-1] if i%4==0 else y[-1]+1)
    pair('ties_every4',N,y,'tie on every 4th step (parity-balanced period-4)')
    for p0 in (0.02,0.05,0.13,0.30,0.60):
        pair(f'walk_tie{int(p0*100):02d}',N,walk(N+1,p0),f'random +/-1 walk, tie probability {p0} (MIT-BIH spans ~0.02-0.13)')
# event-count edges around the 512 cap, at N=1024 (stride 1 regime)
N=1024
for k in (510,511,512,513,514):
    # exactly k tied steps, placed at random positions in an otherwise strictly rising series
    pos=set(R.sample(range(N-1),k)); x=[0]
    for i in range(N-1): x.append(x[-1] if i in pos else x[-1]+1)
    add(f'ties_exact{k}',N,x,f'exactly {k} tied steps, rest rising')
    # exactly k sign reversals among nonzero steps, no ties
    pos=set(R.sample(range(1,N-1),k)); d=1; x=[0,1]
    for i in range(1,N-1):
        if i in pos: d=-d
        x.append(x[-1]+d)
    add(f'reversals_exact{k}',N,x,f'exactly {k} sign reversals, no ties')
# window-length edges (half-window read Tater found at 514-1024 samples)
for L in (511,512,513,514,1023,1025,2048):
    add(f'walk_tie13_len{L}',L,walk(L,0.13),f'tie-13% walk, odd length {L}')
with open('manifest.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['file','case','N','length','sha256','description'])
    for fn,name,N,L,desc in cases:
        w.writerow([fn,name,N,L,hashlib.sha256(open(fn,'rb').read()).hexdigest(),desc])
print(len(cases),'cases')
