# Dual Residual gate log v2 (Link, independent gate review)
2026-11-23 ~23:58 ET. Supersedes nothing: v1 (3a36a677...) stays frozen; this adds the refined failure boundary. Data/report artifacts only; I read no code.

## Gate 3: FAIL stands. Rollout: NO-GO. Core unmodified.

## Refined failure boundary (Tater, G3_MECHANISM_v1.md ac0962b2..., probe_out.txt 7f464818...)
Header Tater compiled: sha 64fa3ca2... = Lucas's prereg core hash (untouched copy).
- sigma_delta takes every other zero-crossing; crossings alternate direction, so it only ever samples one direction.
- First step flat/falling: sigma_delta == 0 exactly (100% of such windows, all 15 cells N 64..16384, tie 5/20/40%), so None.
- First step rising: sigma_delta = tie-share imbalance between even- and odd-slot down-crossings.
- One-sample flips coinciding with first-sign change: 96.1-99.6% at N<=1024; 30-50% at N>1024 (rest from the stride lattice).
- Null owned rate 0.27-0.42 on synthetic walks (consistent with Job 2/Job 3 ~40% ownership of None windows).
Synthetic walks only, seed 12345, 4000 trials per cell. Mechanism description is Tater's reading of detail::compute L53-86; I verified the data file, not the code.

## Consequence for the mechanism half (P2)
The core's sigma_delta measures a tie-landing imbalance gated by first-step direction, not signal parity.
So the P2 miss tests the coded sigma_delta, NOT the parity idea in Blam's directive.
Purp's clean-room sigma_delta also fails (p ~ 1), but it is a logged guess (spec gaps G3/G4) and flags 100% of windows.
Status: "parity can't see ventricular beats" is UNRESOLVED, not established.

## Exploratory (cannot pass the gate; DS1 spent, DS2 sealed)
- Lucas gate3_fix_v1 (prereg 09dd918d..., results b735b9e5...): 5-offset majority-vote guard: flips 33% -> 13% (N=1024), 28% -> 11% (N=4096). Misses 10%.
- Cheddar dr_gate3_ref_probe (rows 27fb7381...) and Lucas's literal-rule numbers: the reference flags ~100% of windows, so its ~0% flips are uninformative.
- Pending: Toni's sampling-only core variant (report tier mix with flip rates).

## Decisions only Blam can make
1. Unlock the header for a v2 that fixes the even-slot selection in detail::compute (and the stride lattice).
2. Only then can P2 be retested on a sigma_delta that actually measures parity, prereg first, scored once on DS2.
