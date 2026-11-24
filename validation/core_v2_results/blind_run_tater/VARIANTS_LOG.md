# Tater dr_v2_both_v1 - VARIANTS_LOG (append-only). Prereg PREREG.md sha 26953107f6caae4c26506f9637ac8a2a0c15696534aa3abe92a021a533647fdb (00:14:36 ET).
DS1 tries T2v01-T2v04 only, each run only after Link's freeze copy of PREREG.md is found under /workspace/link/.

## Synthetic probes (not DS1, not tries)
- SP1 (00:15 ET, synth_probe.py, seed 123, synthetic ECG-like quantized waves, no DS1): sampler-equivalence check found (a)/(b) match ba2ea57 only for n<=513; at 513<n<=1024 the core caps at 512 and (a)/(b) do not -> PREREG_ERRATA_1.md. harness2 with the ba2ea57 sampler == sigma_tinker_v1 harness on all 300 windows (assert passed).
- SP2 synthetic N=4096 one-sample-shift flips (300 windows):
```
P1 samplers identical to ba2ea57 at n<=1024, and harness2(core sampler)==sigma_tinker harness: 143 /300
P1 lengths at 4096: core 511 lag 4088 block 511 full 4095
P2 synth N=4096 sampler=core  sigma=T1v05: flip 0.020 tiers(None,T1,T2,T3) [5, 0, 0, 295]  0.02 ms/window
P2 synth N=4096 sampler=core  sigma=T1v06: flip 0.437 tiers(None,T1,T2,T3) [24, 0, 215, 61]  0.02 ms/window
P2 synth N=4096 sampler=core  sigma=C1: flip 0.353 tiers(None,T1,T2,T3) [87, 0, 0, 213]  0.08 ms/window
P2 synth N=4096 sampler=core  sigma=C2: flip 0.443 tiers(None,T1,T2,T3) [90, 0, 0, 210]  0.06 ms/window
P2 synth N=4096 sampler=core  sigma=C3: flip 0.327 tiers(None,T1,T2,T3) [64, 0, 0, 236]  0.09 ms/window
P2 synth N=4096 sampler=lag   sigma=T1v05: flip 0.003 tiers(None,T1,T2,T3) [6, 0, 2, 292]  0.04 ms/window
P2 synth N=4096 sampler=lag   sigma=T1v06: flip 0.000 tiers(None,T1,T2,T3) [7, 0, 137, 156]  0.04 ms/window
P2 synth N=4096 sampler=lag   sigma=C1: flip 0.000 tiers(None,T1,T2,T3) [0, 0, 0, 300]  0.82 ms/window
P2 synth N=4096 sampler=lag   sigma=C2: flip 0.000 tiers(None,T1,T2,T3) [253, 0, 0, 47]  0.53 ms/window
P2 synth N=4096 sampler=lag   sigma=C3: flip 0.000 tiers(None,T1,T2,T3) [27, 0, 0, 273]  0.52 ms/window
P2 synth N=4096 sampler=block sigma=T1v05: flip 0.063 tiers(None,T1,T2,T3) [4, 0, 11, 285]  0.03 ms/window
P2 synth N=4096 sampler=block sigma=T1v06: flip 0.333 tiers(None,T1,T2,T3) [83, 0, 217, 0]  0.03 ms/window
P2 synth N=4096 sampler=block sigma=C1: flip 0.267 tiers(None,T1,T2,T3) [61, 0, 0, 239]  0.09 ms/window
P2 synth N=4096 sampler=block sigma=C2: flip 0.433 tiers(None,T1,T2,T3) [207, 0, 0, 93]  0.07 ms/window
P2 synth N=4096 sampler=block sigma=C3: flip 0.263 tiers(None,T1,T2,T3) [59, 0, 0, 241]  0.07 ms/window
P2 synth N=4096 sampler=full  sigma=T1v05: flip 0.017 tiers(None,T1,T2,T3) [37, 0, 0, 263]  0.04 ms/window
P2 synth N=4096 sampler=full  sigma=T1v06: flip 0.003 tiers(None,T1,T2,T3) [30, 0, 8, 262]  0.04 ms/window
P2 synth N=4096 sampler=full  sigma=C1: flip 0.010 tiers(None,T1,T2,T3) [108, 0, 0, 192]  0.60 ms/window
P2 synth N=4096 sampler=full  sigma=C2: flip 0.017 tiers(None,T1,T2,T3) [72, 0, 0, 228]  0.51 ms/window
P2 synth N=4096 sampler=full  sigma=C3: flip 0.017 tiers(None,T1,T2,T3) [84, 0, 0, 216]  0.54 ms/window
```

## Freeze found 00:33:57 ET: /workspace/link/dr_core_v2_prereg_frozen_v1/ (tater/PREREG.md 26953107..., tater/PREREG_ERRATA_1.md ff54d531..., FROZEN_v1.sha256). DS1 tries start now.
## DS1 tries

## T2v01  (2026-11-24 00:33:59 ET)
- Definition: (a) lag-not-decimate + T1v05 dwell parity (non-tie steps)
- Code sha256: `02b40f748e444bc5cbf3900a285ecde9f5e06f89d77056d43b18408c43d16606`
- N=1024 (n=13892): flip 0.0160 [PASS] | sep |sd| V med 0.0543 vs None med 0.0505, MW p=0.00343 [PASS] | tiers None 0.046, T1 0.000, T2 0.138, T3 0.816; top T3 0.816 [FAIL] | shuffle own_V 0.964 vs shuf 0.775, gap +19.0 pts, McNemar b=536 c=67 p=4e-92 [PASS] | owned-on-None 0.950
- N=4096 (n=3459): flip 0.0026 [PASS] | sep |sd| V med 0.0769 vs None med 0.0619, MW p=3.29e-06 [PASS] | tiers None 0.037, T1 0.000, T2 0.298, T3 0.665; top T3 0.665 [PASS] | shuffle own_V 0.977 vs shuf 0.563, gap +41.4 pts, McNemar b=443 c=17 p=1.35e-108 [PASS] | owned-on-None 0.954
- ALL BARS: FAIL

## T2v02  (2026-11-24 00:34:00 ET)
- Definition: (a) lag-not-decimate + T1v06 plateau parity
- Code sha256: `8b1e91c233c8244ed0d771e28959a068098618935d7746e9d3e9b6246ca2ea1b`
- N=1024 (n=13892): flip 0.0186 [PASS] | sep |sd| V med 0.0769 vs None med 0.0732, MW p=0.0337 [FAIL] | tiers None 0.030, T1 0.000, T2 0.362, T3 0.608; top T3 0.608 [PASS] | shuffle own_V 0.967 vs shuf 0.874, gap +9.3 pts, McNemar b=302 c=72 p=6.52e-35 [FAIL] | owned-on-None 0.970
- N=4096 (n=3459): flip 0.0061 [PASS] | sep |sd| V med 0.0638 vs None med 0.0617, MW p=0.0956 [FAIL] | tiers None 0.038, T1 0.000, T2 0.291, T3 0.671; top T3 0.671 [PASS] | shuffle own_V 0.972 vs shuf 0.928, gap +4.4 pts, McNemar b=73 c=28 p=4.32e-06 [FAIL] | owned-on-None 0.956
- ALL BARS: FAIL

## T2v03  (2026-11-24 00:34:02 ET)
- Definition: (b) block-mean decimation + T1v05 dwell parity (non-tie steps)
- Code sha256: `3f5e1c9ecf469b735f9d4cbbc06dfe410207b4aa25e71565a280b27687497238`
- N=1024 (n=13892): flip 0.0160 [PASS] | sep |sd| V med 0.0543 vs None med 0.0505, MW p=0.00343 [PASS] | tiers None 0.046, T1 0.000, T2 0.138, T3 0.816; top T3 0.816 [FAIL] | shuffle own_V 0.964 vs shuf 0.775, gap +19.0 pts, McNemar b=536 c=67 p=4e-92 [PASS] | owned-on-None 0.950
- N=4096 (n=3459): flip 0.1454 [FAIL] | sep |sd| V med 0.0917 vs None med 0.0816, MW p=0.0253 [FAIL] | tiers None 0.030, T1 0.000, T2 0.418, T3 0.552; top T3 0.552 [PASS] | shuffle own_V 0.976 vs shuf 0.839, gap +13.7 pts, McNemar b=158 c=17 p=3.98e-30 [PASS] | owned-on-None 0.964
- ALL BARS: FAIL

## T2v04  (2026-11-24 00:34:04 ET)
- Definition: (b) block-mean decimation + T1v06 plateau parity
- Code sha256: `603813f9e82114e2a63cf6db6b4831c83fcf7a33b235e88798f15cf16219967e`
- N=1024 (n=13892): flip 0.0186 [PASS] | sep |sd| V med 0.0769 vs None med 0.0732, MW p=0.0337 [FAIL] | tiers None 0.030, T1 0.000, T2 0.362, T3 0.608; top T3 0.608 [PASS] | shuffle own_V 0.967 vs shuf 0.874, gap +9.3 pts, McNemar b=302 c=72 p=6.52e-35 [FAIL] | owned-on-None 0.970
- N=4096 (n=3459): flip 0.3484 [FAIL] | sep |sd| V med 0.3333 vs None med 0.3333, MW p=0.105 [FAIL] | tiers None 0.221, T1 0.000, T2 0.771, T3 0.007; top T2 0.771 [PASS] | shuffle own_V 0.765 vs shuf 0.467, gap +29.7 pts, McNemar b=423 c=117 p=5.97e-42 [PASS] | owned-on-None 0.782
- ALL BARS: FAIL

## CLOSED 00:34:54 ET. No further tries.
