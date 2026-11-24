# V2_DS1_SUMMARY

Exploratory independent cross-check of the four core-v2 candidates on DS1
from dataset_v1. Rollout remains halted. DS2 was not opened.

## Authority and hashes

- Blam: "Full unlock" for the core header (prereg).
- Prereg `/workspace/purp/dr-core-v2-prereg/CORE_V2_CANDIDATES_v1.md` sha256 `f2d87c61b0683a6f5e21212096621e3e91bc1ca5ae1f4da12d00190ab444ca33` (verified, matches f2d87c61… as posted).
- No newer Link freeze of this prereg with a different hash was found under `/workspace/link/`.
- dataset_v1 manifest `82f77b3324123fbd11643c9949f4131795b355aa06875dfd0fc81220cea79502` (full sha; expected 82f77b33…).
- Link σ freeze `FROZEN_v1.sha256` `ce6c15043bb6bed191fec0e5542f35ea2e50573f239925fe418f71fa9b0436fb`; payload files matched the list.
- Tater hash list `/workspace/tater/sigma_tinker_v1/HASHES.sha256` `b2585ac9732b6bb19cd0da6f3ecf4393f71d2dd9199df82328e58e65f595c4e9` (verified b2585ac9…; listed files OK).
- T1v06 was ported from `variants_t1.py` (definition only). His harness was not used.
- Bars were implemented from `FINAL_BARS_v1.md` and `SIGMA_CANDIDATES_v1.md`, not from Tater's code.

## Sampling and what was held fixed

Every V2 candidate uses stride 1, every sample, no 512 cap, at every N.
Constants 0.04 / 0.005 / 0.1 / 0.2, the ba2ea57 decision table and T2-before-T3
precedence, the AND ownership gate, the classical formula (mean |sign|), and the
refusal rule (not owned → None) are unchanged. Only σ_Δ is swapped.
The ba2ea57 control keeps the locked stride (`N/512` above 1024) and 512-sign cap.

## Fullsample confirmation

The all_switched port with stride 1, no cap, and the core's own σ_Δ was compared
to `variant_fullsample` on every DS1 v1 window at N=1024 and N=4096:
**17351 / 17351 match**, mismatches=0.

## Window set (dataset_v1, DS1 only)

Windows and labels rebuilt from `dataset_v1/DS1_N*.csv` (hashes checked against
the manifest). Raw MLII samples reused from the existing Job 4 DS1 int16 cache
(same records; v0 vs v1 differs in labels and in VFL/flutter exclusions, not in
the cached ADU values). Record 207 remains in DS1; windows overlapping a VFL
episode or a `!` flutter wave are already omitted from the v1 CSVs.

| N | windows | None | T1 | T2 | T3 |
|---:|---:|---:|---:|---:|---:|
| 64 | 222614 | 216320 | 1359 | 3331 | 1604 |
| 256 | 55649 | 50925 | 1084 | 3207 | 433 |
| 1024 | 13892 | 10858 | 562 | 2333 | 139 |
| 4096 | 3459 | 2146 | 284 | 970 | 59 |
| 16384 | 850 | 368 | 109 | 336 | 37 |

Alpha for bars 1 and 4 is 0.05/3 ≈ 0.0167, as written (Bonferroni over the
original three C candidates). Bar 5 is reported, not pass/fail.

Shuffle convention: `np.random.RandomState(7)`, one stream, windows in CSV
order (record, start); `rng.shuffle` of a copy of the raw samples inside each
truth-T2-or-T3 window. Flag = owned (suggested tier ≠ None). Paired test =
one-sided exact McNemar (binomial on discordant pairs, alternative: more
intact-owned/shuffled-not than the reverse). Gap bar: ≥ 10 percentage points.

## Per-N results

### N=1024

| candidate | windows | flip | flip bar | chance flip 1−Σp² | kappa | None | T1 | T2 | T3 | top share | degen bar | sep med \|σ_Δ\| V vs None | MW p | sep bar | shuf owned vs shuf | gap pts | McNemar p | shuf bar | owned-on-None |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---:|---|---:|
| ba2ea57 | 13892 | 0.330982 | FAIL | 0.572583 | 0.421950 | 0.5690 | 0.0000 | 0.1420 | 0.2890 | None 0.5690 | PASS | 0.000000 vs 0.000000 | 0.802296 | FAIL | 0.4223 vs 0.3325 | 8.98 | 1.080e-10 | FAIL | 0.4324 |
| V2-C1 | 13892 | 0.018788 | PASS | 0.243198 | 0.922747 | 0.1163 | 0.0000 | 0.0219 | 0.8619 | T3 0.8619 | FAIL | 0.021526 vs 0.023483 | 0.999967 | FAIL | 0.8742 vs 0.8888 | -1.46 | 0.947703 | FAIL | 0.8866 |
| V2-C2 | 13892 | 0.016556 | PASS | 0.296856 | 0.944228 | 0.1811 | 0.0000 | 0.0001 | 0.8187 | T3 0.8187 | FAIL | 0.013494 vs 0.014018 | 0.999929 | FAIL | 0.8119 vs 0.3908 | 42.11 | 1.647e-185 | PASS | 0.8215 |
| V2-C3 | 13892 | 0.019796 | PASS | 0.240443 | 0.917671 | 0.1078 | 0.0000 | 0.0278 | 0.8644 | T3 0.8644 | FAIL | 0.023483 vs 0.025440 | 0.999858 | FAIL | 0.8896 vs 0.8900 | -0.04 | 0.535953 | FAIL | 0.8922 |
| V2-T6 | 13892 | 0.018644 | PASS | 0.498523 | 0.962602 | 0.0302 | 0.0000 | 0.3617 | 0.6080 | T3 0.6080 | PASS | 0.076923 vs 0.073171 | 0.033659 | FAIL | 0.9668 vs 0.8750 | 9.18 | 2.748e-34 | FAIL | 0.9703 |

### N=4096

| candidate | windows | flip | flip bar | chance flip 1−Σp² | kappa | None | T1 | T2 | T3 | top share | degen bar | sep med \|σ_Δ\| V vs None | MW p | sep bar | shuf owned vs shuf | gap pts | McNemar p | shuf bar | owned-on-None |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---:|---|---:|
| ba2ea57 | 3459 | 0.284186 | FAIL | 0.518893 | 0.452322 | 0.5669 | 0.0000 | 0.0350 | 0.3981 | None 0.5669 | PASS | 0.000000 vs 0.000000 | 0.105445 | FAIL | 0.4402 vs 0.3343 | 10.59 | 8.531e-07 | PASS | 0.4268 |
| V2-C1 | 3459 | 0.008384 | PASS | 0.391637 | 0.978593 | 0.2605 | 0.0000 | 0.0043 | 0.7352 | T3 0.7352 | PASS | 0.011724 vs 0.009770 | 0.008216 | PASS | 0.7600 vs 0.7609 | -0.10 | 0.541564 | FAIL | 0.7307 |
| V2-C2 | 3459 | 0.006938 | PASS | 0.473321 | 0.985341 | 0.3845 | 0.0000 | 0.0000 | 0.6155 | T3 0.6155 | PASS | 0.006885 vs 0.006921 | 0.964198 | FAIL | 0.6054 vs 0.0690 | 53.64 | 3.892e-141 | PASS | 0.6258 |
| V2-C3 | 3459 | 0.008673 | PASS | 0.361493 | 0.976008 | 0.2290 | 0.0000 | 0.0055 | 0.7655 | T3 0.7655 | PASS | 0.012702 vs 0.011236 | 0.005068 | PASS | 0.8008 vs 0.7570 | 4.37 | 0.010221 | FAIL | 0.7582 |
| V2-T6 | 3459 | 0.006360 | PASS | 0.334372 | 0.980979 | 0.0587 | 0.0000 | 0.1396 | 0.8017 | T3 0.8017 | FAIL | 0.044534 vs 0.044445 | 0.713026 | FAIL | 0.9485 vs 0.9456 | 0.29 | 0.422685 | FAIL | 0.9408 |

### Other N (descriptive; bars are only at 1024 and 4096)

| candidate | N | windows | flip | chance flip | kappa | None | T1 | T2 | T3 | owned-on-None |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ba2ea57 | 64 | 222614 | 0.314724 | 0.509064 | 0.381759 | 0.6184 | 0.0000 | 0.3245 | 0.0571 | 0.3820 |
| ba2ea57 | 256 | 55649 | 0.336035 | 0.578068 | 0.418694 | 0.5764 | 0.0000 | 0.2132 | 0.2105 | 0.4210 |
| ba2ea57 | 16384 | 850 | 0.223529 | 0.476299 | 0.530695 | 0.6129 | 0.0000 | 0.0024 | 0.3847 | 0.3614 |
| V2-C1 | 64 | 222614 | 0.141572 | 0.541619 | 0.738612 | 0.1331 | 0.0000 | 0.2533 | 0.6136 | 0.8676 |
| V2-C1 | 256 | 55649 | 0.049165 | 0.266207 | 0.815312 | 0.0588 | 0.0000 | 0.0915 | 0.8497 | 0.9413 |
| V2-C1 | 16384 | 850 | 0.002353 | 0.498893 | 0.995284 | 0.5235 | 0.0000 | 0.0000 | 0.4765 | 0.4429 |
| V2-C2 | 64 | 222614 | 0.092986 | 0.474207 | 0.803912 | 0.1125 | 0.0000 | 0.1995 | 0.6880 | 0.8905 |
| V2-C2 | 256 | 55649 | 0.040109 | 0.181766 | 0.779340 | 0.0765 | 0.0000 | 0.0224 | 0.9010 | 0.9240 |
| V2-C2 | 16384 | 850 | 0.008235 | 0.448044 | 0.981619 | 0.6612 | 0.0000 | 0.0000 | 0.3388 | 0.3207 |
| V2-C3 | 64 | 222614 | 0.182765 | 0.560419 | 0.673878 | 0.1185 | 0.0000 | 0.3048 | 0.5768 | 0.8821 |
| V2-C3 | 256 | 55649 | 0.062715 | 0.292842 | 0.785842 | 0.0518 | 0.0000 | 0.1171 | 0.8311 | 0.9489 |
| V2-C3 | 16384 | 850 | 0.004706 | 0.499723 | 0.990583 | 0.4882 | 0.0000 | 0.0000 | 0.5118 | 0.4810 |
| V2-T6 | 64 | 222614 | 0.055423 | 0.310253 | 0.821361 | 0.1432 | 0.0000 | 0.8171 | 0.0397 | 0.8601 |
| V2-T6 | 256 | 55649 | 0.047386 | 0.506404 | 0.906426 | 0.0638 | 0.0000 | 0.6283 | 0.3079 | 0.9378 |
| V2-T6 | 16384 | 850 | 0.002353 | 0.277738 | 0.991528 | 0.0906 | 0.0000 | 0.0671 | 0.8424 | 0.8913 |

## Pass/fail at both bar N

| candidate | N=1024 bars (sep/flip/degen/shuf) | N=4096 bars | every bar both N |
|---|---|---|---|
| ba2ea57 | N,N,Y,N | N,N,Y,Y | FAIL |
| V2-C1 | N,Y,N,N | Y,Y,Y,N | FAIL |
| V2-C2 | N,Y,N,Y | N,Y,Y,Y | FAIL |
| V2-C3 | N,Y,N,N | Y,Y,Y,N | FAIL |
| V2-T6 | N,Y,Y,N | N,Y,N,N | FAIL |

## Selection rule

Among V2 candidates (not the ba2ea57 control) that pass every bar at both N,
pick the lowest N=1024 flip rate. If none pass, that is the result.

**None of the four V2 candidates passed every bar at both N.** The selection
rule therefore picks nobody. DS2 stays sealed.

## Logged prediction

Purp, logged before the run: at least one V2 candidate passes the flip bar
at both N. If none does, the stride explanation for the N=4096 flips is wrong.

**Prediction held:** V2-C1, V2-C2, V2-C3, V2-T6 passed the flip bar at both N=1024 and N=4096.

## Try count (from the prereg, to be reported with any win)

- C1–C3: 3 tries (σ_Δ-only).
- Tater T1v01–T1v06: 6 tries.
- V2-C1, V2-C2, V2-C3, V2-T6: 4 tries.
- Total: 13.

