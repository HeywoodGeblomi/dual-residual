# Dual Residual core v2, Tater track, prereg v1. Written before any DS1 run of these tries. Link freezes it before DS1.
Written: 2026-11-24 ~00:15 ET. Authority: Blam "Full unlock" (00:12 ET), as cited in Purp's CORE_V2_CANDIDATES_v1.md (f2d87c61...).
ba2ea57 stays on record as the version that failed Gate 3.

## Scope
Exactly 4 DS1 tries, T2v01–T2v04. Each changes the sampling (one of two schemes below) and the sigma_delta (T1v05 or T1v06, exactly as defined in /workspace/tater/sigma_tinker_v1/variants_t1.py, hash list b2585ac9...).
Unchanged from ba2ea57: the four constants (0.04 / 0.005 / 0.1 / 0.2), the decision table and precedence (T2 if |sd|>0.1, else T3 if classical>0.2, else T1), the AND ownership gate (classical>0.04 AND not |sd|<0.005), the classical formula (mean |s| over the stream), the refusal rule (n<2 or stream length <4 gives None), and float32 comparisons.
Purp's "stride 1, no cap" sampling is NOT run here; it is his prereg (V2-C1/C2/C3/T6).

## Sampling schemes (L = ba2ea57 stride = n//512 if n>1024 else 1; at N<=1024 both are identical to ba2ea57)
- (a) Lag-not-decimate: s[i] = sign(x[i+L] - x[i]) for EVERY i = 0..n-L-1 (no decimation, no 512 cap). At N=4096, L=8 and the stream has 4088 entries.
- (b) Block-mean decimation: split x into consecutive non-overlapping blocks of L samples from the window start (a trailing partial block is dropped), take each block's sum (an exact integer, which is equivalent to its mean), and s[k] = sign(sum[k+1] - sum[k]). At N=4096 that gives 511 entries, under the 512 cap.

## Tries
- T2v01 = (a) + T1v05 sigma (dwell parity, non-tie steps)
- T2v02 = (a) + T1v06 sigma (plateau parity)
- T2v03 = (b) + T1v05 sigma
- T2v04 = (b) + T1v06 sigma
At N=1024 each one reproduces T1v05/T1v06 exactly; reported anyway.

## Bars and selection (identical to all tracks)
Link's FINAL_BARS_v1.md plus Purp's bars 1-3, at both N=1024 and N=4096, computed by the same harness and interpretations as sigma_tinker_v1/SUMMARY.md (V = T2+T3 vs None, one-sided MW p<0.0167; flip <=10% on (confirmed,talent) with a +1 shift; top tier <=80%; shuffle gap >=10 pts with exact one-sided McNemar p<0.0167, seed 7; owned-on-None reported).
These tries compete with Purp's V2 candidates and the C1-C3 track under the same bars and the SAME single DS2 selection rule: among everything passing all bars at both N, lowest N=1024 flip goes to DS2, scored once. If none passes, that is the result; no fifth T2 try.

## Try count
Counted on top of Purp's 13 (C1-C3: 3, T1v01-T1v06: 6, V2-C1/C2/C3/T6: 4), for a running total of up to 17.

## Prediction before any run
(a) and (b) cut N=4096 flips well below the stride-8 decimated stream (~20% for T1v05). I expect at least one T2 try to pass the flip bar at both N; T1v06's ties at 4096 may still flip under (b) because block sums rarely tie.

## Still sealed
DS2 stays sealed. Not opened, read, hashed or listed.
