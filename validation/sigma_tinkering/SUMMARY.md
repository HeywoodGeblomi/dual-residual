# Tater sigma_tinker_v1 — summary (DS1 only, DS2 never touched)
DS1 candidate tries: 6 (T1v01–T1v06), stopped well under the 15 cap. T1v00 is a reproduction of the unmodified core, not a candidate. It matches Lucas's ds1_v1_exploratory exactly: flip 0.3310/0.2842, MW p 0.802/0.105, own_V 0.4223 vs shuffled 0.3378.
Result: NO variant passes all bars on DS1. There's no selection-rule pick from this track.

| ID | variant | flip 1024/4096 | MW p (|sd| V>None) 1024/4096 | top tier 1024/4096 | shuffle gap pts (McNemar p) 1024/4096 | owned-on-None 1024/4096 | all bars |
|---|---|---|---|---|---|---|---|
| T1v00 | BASELINE (not a candidate) | 0.331 / 0.284 | 0.8 / 0.11 | None 0.57 / None 0.57 | +8.5 (p=4e-10) / +8.6 (p=5e-05) | 0.43 / 0.43 | FAIL |
| T1v01 | Dwell parity | 0.028 / 0.200 | 0.18 / 0.02 | T3 0.78 / T3 0.65 | +11.3 (p=7e-41) / +11.2 (p=7e-21) | 0.95 / 0.96 | FAIL |
| T1v02 | Flat-turn parity | 0.024 / 0.242 | 0.27 / 0.00089 | T3 0.79 / T3 0.86 | +17.1 (p=1e-57) / +16.0 (p=5e-20) | 0.92 / 0.88 | FAIL |
| T1v03 | Zero-dwell runs | 0.013 / 0.497 | 0.71 / 1 | T3 0.82 / T3 0.48 | +76.2 (p=0) / +41.7 (p=1e-102) | 0.88 / 0.58 | FAIL |
| T1v04 | Dwell parity on the core's own events (crossings of s>0 = rising vs not-rising), ALL events, value = complete dwell length, normalized (me-mo)/(me+mo) | 0.022 / 0.221 | 1 / 1 | T3 0.55 / T3 0.76 | +12.5 (p=3e-56) / +7.9 (p=4e-10) | 0.98 / 0.97 | FAIL |
| T1v05 | Dwell parity (tie-held crossings) with dwell counted in non-tie steps only, normalized (me-mo)/(me+mo) | 0.031 / 0.212 | 0.14 / 0.0005 | T3 0.77 / T3 0.63 | +12.4 (p=1e-48) / +10.9 (p=4e-21) | 0.95 / 0.95 | FAIL |
| T1v06 | Plateau parity | 0.030 / 0.435 | 3e-05 / 0.007 | T2 0.50 / T2 0.72 | +14.0 (p=7e-54) / +11.6 (p=3e-15) | 0.96 / 0.93 | FAIL |

## Why they fail (D1 diagnostic in the log)
- At N=1024 the stride is 1, so a one-sample shift barely changes the sign stream. Every event-index variant is stable there (1.3–3.1% flips). T1v06 (plateau parity) passes all four bars at N=1024.
- At N=4096 the stride is 8, so a one-sample shift gives a completely different subsample. For the best variant (T1v05), |σ| at offset 0 vs offset 1 correlates only 0.85: across-window SD 0.052, shift-noise SD 0.029. With the 0.1 T2 cut inside the bulk and the 0.005 floor next to zero, about 15% of flips come from T2↔T3 and about 7% from None↔T3. T1v06 at 4096 is built from a few ties, so it barely correlates with itself under a shift (r=0.08) and flips 44%.
- So the 4096 flips are what you get from any σ read off the stride-8 stream. A fix would need to touch sampling, which is out of scope and frozen.
- Separation is weak or backwards for most readings. Only T1v06 separates V from None at both N.

## Interpretations made
1. Bar 1: "V" = dataset_v1 tier T2+T3 vs tier None (Purp bar 1 and Lucas's P2), not T3 alone. Test is |σ_Δ| one-sided Mann-Whitney (scipy, alternative='greater'), p<0.0167 at both N. T1 windows are excluded.
2. Bar 2: decision = (confirmed, talent) on window [start,end) vs [start+1,end+1). Windows with end+1 > record length are skipped, as in Lucas's run_v1.py (n=13892 / 3459). Threshold ≤10% at both N.
3. Bar 3: tier share = the core's output tier (None/T1/T2/T3, with None counted as a tier) over all DS1 windows at that N, intact and unshifted. Max must be ≤80% at both N.
4. Bar 4: "flag" = confirmed (owned), as in Lucas's P2. Shuffles use one np.random.default_rng(7) for the whole run, applied in CSV row order to T2+T3 windows only, N=1024 first and then 4096, exactly as in Lucas's run_v1.py, and re-seeded for each variant so every variant sees identical shuffles. Gap = own_V(intact) − own_V(shuffled) ≥ 0.10. "One-sided paired p" = exact one-sided McNemar (binomial sign test on discordant pairs, P(Bin(b+c, .5) ≥ b)) < 0.0167, at both N.
5. Bar 5: owned rate on dataset_v1 None-labelled windows, reported only.
6. Data: Toni's DS1 cache rec_*.i16 = MLII only, int16 LE, 650000 samples (1.3 MB files). The harness asserts each record is in meta ds1_records and not in the DS2/excluded denylists. The T1v00 exact reproduction of Lucas's wfdb-based numbers confirms the format.
7. σ is computed from the core's sign stream only. No raw amplitudes are used, so there's no new signal. The result is cast to float32 before the unchanged float32 comparisons.
