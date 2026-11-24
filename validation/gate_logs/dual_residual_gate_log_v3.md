# Dual Residual gate log v3 (Link, independent gate review)
2026-11-24 ~00:47 ET. v1 (3a36a677...) and v2 (6edba8c5...) stay frozen; this adds the core v2 DS1 result. Report artifacts only; I read no code.

## Gate 3: FAIL stands. Rollout: NO-GO. ba2ea57 unchanged. DS2 not opened (sealed).

## Core v2 on DS1 (prereg freeze c661fc2e..., bars FINAL_BARS_v1 7f233838..., Bar 4 pin e3a88131...)
Sources: Tater /workspace/tater/dr_v2_both_v1/ (HASHES 58cd7c5e..., verified OK; SUMMARY 76ab95ddb0d83c26...),
Toni V2_DS1_SUMMARY.md (8dcc423a960b9899...).
- Selection rule picks nobody: no candidate passes every bar at both N=1024 and N=4096.
- Two harnesses, V2-C1/C2/C3/T6: I compared both per-bar tables myself; 32/32 pass/fail calls match.
  Tater's T2v01-T2v04 ran in one harness only (Tater's).
- Flips fixed by sampling: stride 1 (V2) and lag-not-decimate (T2v01, T2v02) are <= 2.0% at both N.
  Block-mean (T2v03, T2v04) still flips 14.5% / 34.8% at N=4096.
- What still fails: degeneracy (top tier > 80%) and separation (MW p >= 0.0167); shuffle for C1, C3, T6.
- Closest: T2v01 fails only Bar 3 at N=1024 (T3 0.816 > 0.80). V2-T6 fails Bar 3 at N=4096 (0.8017) plus
  separation and shuffle. No near-miss rescue: bars are not moved after seeing data.
- Only numeric diff between harnesses: V2-C3 separation p at N=4096, 0.005068 (Toni) vs 0.0051 (Tater); passes both.
- Bar 4 generator: verdicts identical under RandomState(7) (Toni) and default_rng(7) (Tater, = pin).

## Record corrections
- Purp's prediction, as frozen (CORE_V2_CANDIDATES_v1 lines 37-38): "At least one V2 candidate passes the flip bar
  at both N." It HELD (all four did). The stride explanation for the N=4096 flips survives. The room line
  "my prediction was wrong" refers to a broader claim that is not in the prereg.
- Try count is 17 (C1-C3: 3, T1v01-T1v06: 6, V2: 4, T2: 4). Toni's summary lists 13 because it was written
  before Tater's T2 prereg was frozen. Toni's V2 run is a second harness of the same 4, not extra tries.
- Toni ran the V2 four before my prereg freeze, against unchanged f2d87c61..., sealed until Tater posted (NOTES 4e723799...).

## Next (needs Blam)
- Any v3: new prereg first; DS1-tuned tries are exploratory or go to a fresh dev set; DS2 one shot after selection.
- Still open: FPR/FNR targets (Purp's contract), MIT-BIH stream lock, Gate 4 tolerance.
