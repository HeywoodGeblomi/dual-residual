#!/usr/bin/env python3
"""σ_Δ candidates C1-C3 (see SIGMA_CANDIDATES_v1.md). Input: the core's sign stream s (list of -1/0/+1). Imports nothing."""
def _parity(e):  # e: list of (position j, indicator)
    ev=[v for j,v in e if j%2==0]; od=[v for j,v in e if j%2==1]
    return (sum(ev)/len(ev) if ev else 0.0)-(sum(od)/len(od) if od else 0.0)
def c1_turns(s): return _parity([(j,1 if s[j-1]!=0 and s[j]!=0 and s[j-1]!=s[j] else 0) for j in range(1,len(s))])
def c2_flats(s): return _parity([(j,1 if s[j]==0 else 0) for j in range(len(s))])
def c3_changes(s): return _parity([(j,1 if s[j]!=s[j-1] else 0) for j in range(1,len(s))])
CANDIDATES={'C1':c1_turns,'C2':c2_flats,'C3':c3_changes}
if __name__=='__main__':
    tests={'tie-free alternating':[1,-1,1,-1,1,-1],'ties on even':[0,1,0,1,0,1],'monotone':[1,1,1,1],'mixed':[1,0,-1,1,0,0,-1]}
    for n,s in tests.items(): print(n, {k:round(f(s),4) for k,f in CANDIDATES.items()})
