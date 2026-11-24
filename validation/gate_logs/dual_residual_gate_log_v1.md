# Dual Residual gate log v1 (Link, independent gate review)
Date: 2026-11-23 15:10 ET. Graded against dual_residual_gate_checklist_v1.md (sha d5959b02...). Data/report artifacts only; no code read.

## Gate 3: FAIL (halt rule triggered)
Source: /workspace/dr_job3/ds1/ (Lucas). Hashes verified by me:
- PREREG.md e9eb06e467047743b53bb3aedcfa42c3a894d863fe8b132a234cd0ae726f8622
- results.json df3e73f41c71a83e65a35e3a8ed5c0ff6c12064298aa53db32a7f43151b36ad6
Core: ba2ea57, reported unchanged (self-asserted).
Failure boundary (label-independent, so the 207 flutter leak doesn't affect it):
- P1 phase stability, bar <= 10% flips under +1 sample shift:
  N=1024: 0.3312 (13,948 windows); N=4096: 0.2839 (3,476 windows).
Also missed (label-dependent, exploratory once labels are fixed):
- P2 |sigma_delta| V vs None: MW p 0.811 (N=1024), 0.098 (N=4096); bar p < 0.01.
- Ownership by tier is flat (~0.42-0.49 at 1024; 0.375-0.454 at 4096).
Caveats: prereg-before-scoring ordering is self-asserted (file mtimes 14:57 vs 14:58); DS1 only, DS2 not read.

## Other findings logged (not gate verdicts)
- Toni DS1: core never emits T1 at any N (classical = 1 - tie rate > 0.2). Bears on G1/G2.
- Toni DS1: ~38% of None windows owned at N=64.
- Cheddar: run-splitting at window edges (6/20 DS2 V-runs at N=1024, 2 at 4096) and record 207 VFL unlabeled.
- Toni prereg v2 (827bc8e2...) fixes G4-03 tolerance; G4-04 independent baselines claimed (MANIFEST 7e51f1e3...), not yet graded.

## Status
Rollout: NO-GO. Per directive, halt; core is not modified. Any further runs are exploratory only.
DS2 should stay unread: no gate result can turn this into a pass.
