#!/usr/bin/env python3
"""Clean-room Dual Residual reference v1. Reads whitespace-separated raw ints (one window) on stdin, prints tier.
Written from the directive text only; see CLEANROOM_SPEC_v1.md for gaps G1-G9 and assumptions A1-A9."""
import sys
def tier(x):
    n=len(x)
    if n<3: return 'None',0.0,0.0
    s=[(x[i+1]>x[i])-(x[i+1]<x[i]) for i in range(n-1)]          # A1
    if 0 not in s: return 'None',0.0,0.0                           # A5
    ev=[1 if s[i]==0 else 0 for i in range(0,len(s),2)]
    od=[1 if s[i]==0 else 0 for i in range(1,len(s),2)]
    sd=(sum(ev)/len(ev) if ev else 0.0)-(sum(od)/len(od) if od else 0.0)   # A3
    pairs=len(s)-1
    rev=sum(1 for i in range(pairs) if s[i]!=0 and s[i+1]!=0 and s[i]!=s[i+1])
    cl=rev/pairs if pairs else 0.0                                  # A4
    if cl>0.2: t='T3'                                               # A7, A8
    elif abs(sd)>0.1: t='T2'
    elif cl>0.04 or abs(sd)>0.005: t='T1'                           # A6
    else: t='None'
    return t,cl,sd
if __name__=='__main__':
    x=[int(v) for v in sys.stdin.read().split()]
    t,cl,sd=tier(x)
    print(t) if '--verbose' not in sys.argv else print(t,f'classical={cl:.6f}',f'sigma_delta={sd:.6f}')
