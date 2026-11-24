# Bar 4 (shuffle null) pin v1 (Link) - 2026-11-24 ~00:38 ET. Clarifies FINAL_BARS_v1.md (7f233838...), which stays unchanged.
Why: "seed 7" left the generator and shuffle order open. On the ba2ea57 control at N=4096, Toni (RandomState(7)) got a 10.59-pt
gap (pass) and Tater (default_rng(7)) got 8.6 (fail). Everything else in their controls matched.
Pinned to the ORIGINAL convention (Lucas's Job 3 PREREG e9eb06e4 line 8 set the bar; its run_v1.py convention as described in
Tater's sigma_tinker_v1/SUMMARY.md line 25), not chosen against any v2 result:
- Generator: numpy np.random.default_rng(7) (PCG64); one stream per candidate, re-seeded for each candidate.
- Order: DS1 CSV row order; all N=1024 windows first, then N=4096, on that one stream.
- Windows: dataset_v1-labeled T2+T3 windows only; one within-window permutation of the raw samples per window per N.
- Flag: owned (AND ownership gate), as in Lucas's P2.
- Gap: owned rate intact minus owned rate shuffled >= 0.10.
- Test: exact one-sided McNemar. b = owned intact and not owned shuffled; c = the reverse; p = P(Bin(b+c, 0.5) >= b) < 0.0167.
- Both N must pass.
Disclosure: written after Tater posted his v2 verdicts (00:35 ET) and after Toni's sealed run (00:30 ET). Per Tater's posted
summary, no candidate failed on Bar 4 alone, so this pin cannot change the "no pick" outcome. Toni: re-score Bar 4 under this pin
for the cross-check and report your RandomState(7) numbers next to it. Finding to report either way: on the control, Bar 4 at
N=4096 sits near its threshold and flips pass/fail with the generator.
