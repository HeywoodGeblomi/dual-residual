# Job 3 DS1 prereg (Lucas), written before any scoring
Core: dual-residual ba2ea57, dual_residual.hpp sha 64fa3ca2…ecf, constants untouched.
Data: Purp dataset_v0 DS1 only (DS2 sealed, not read). MIT-BIH MLII raw 11-bit ints, no extra quantization.
Windows: DS1_N1024.csv and DS1_N4096.csv as listed. Score once.
P1 phase stability: evidence(window) vs evidence(window shifted +1 sample). Decision = (confirmed, talent).
  HIT if flip rate <= 10% at both N.
P2 mechanism: |sigma_delta| higher on labeled V windows (T2+T3) than on None windows, one-sided Mann-Whitney p < 0.01 at both N,
  AND ownership rate on V windows (intact) exceeds the same windows with samples shuffled within window (seed 7) by >= 10 points.
  HIT only if both parts hold at both N.
Anything else reported as exploratory.
