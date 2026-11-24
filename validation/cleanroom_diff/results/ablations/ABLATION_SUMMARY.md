# Ablation results (exploratory, core-informed, not clean-room)

Each variant switches exactly one frozen-ref assumption to the behavior
in `dual_residual.hpp` at ba2ea57, except `all_switched` (every rule) and
`fullsample` (core math, stride 1, no 512 cap). The frozen reference
files were not modified. Rollout remains halted. DS1 only.

Baseline is the already-computed frozen-ref vs core comparison.

## all_switched vs core (exact-reproduction check)

- DS1 tier mismatches: 0 / 297572
- DS1 feature mismatches (|Δ| > 1e-06): 0 / 297572
- Edge tier mismatches: 0 / 31604
- Edge feature mismatches (|Δ| > 1e-06): 0 / 31604

all_switched reproduced the core on every DS1 and edge window (tiers and features). No UNEXPLAINED residual.

## DS1 agreement with the core, by N

| variant | N=64 rate (Δ vs frozen) | N=256 rate (Δ vs frozen) | N=1024 rate (Δ vs frozen) | N=4096 rate (Δ vs frozen) | N=16384 rate (Δ vs frozen) | all |
|---|---|---|---|---|---|---|
| frozen_ref (baseline) | 0.0702 (15696/223432) | 0.1793 (10017/55858) | 0.2625 (3662/13948) | 0.3777 (1313/3476) | 0.3671 (315/858) | 0.1042 (31003/297572) |
| G1_stride | 0.0702 (+0.0000) | 0.1793 (+0.0000) | 0.2625 (+0.0000) | 0.3976 (+0.0199) | 0.3834 (+0.0163) | 0.1045 (+0.0003) 31086/297572 |
| G9_cap | 0.0702 (+0.0000) | 0.1793 (+0.0000) | 0.2534 (-0.0091) | 0.3458 (-0.0319) | 0.3368 (-0.0303) | 0.1033 (-0.0009) 30739/297572 |
| G2G3_sigma | 0.1674 (+0.0971) | 0.2213 (+0.0420) | 0.2693 (+0.0067) | 0.3780 (+0.0003) | 0.3671 (+0.0000) | 0.1853 (+0.0811) 55145/297572 |
| G4_classical | 0.0628 (-0.0074) | 0.2104 (+0.0311) | 0.2888 (+0.0262) | 0.3979 (+0.0201) | 0.3834 (+0.0163) | 0.1060 (+0.0018) 31536/297572 |
| G5_refuse | 0.0646 (-0.0056) | 0.1793 (+0.0000) | 0.2625 (+0.0000) | 0.3777 (+0.0000) | 0.3671 (+0.0000) | 0.0999 (-0.0042) 29742/297572 |
| G6_ownership | 0.1326 (+0.0623) | 0.2082 (+0.0288) | 0.3158 (+0.0533) | 0.4563 (+0.0785) | 0.5163 (+0.1492) | 0.1602 (+0.0561) 47683/297572 |
| G7_precedence | 0.1011 (+0.0309) | 0.1789 (-0.0004) | 0.2626 (+0.0001) | 0.3777 (+0.0000) | 0.3671 (+0.0000) | 0.1273 (+0.0231) 37872/297572 |
| G8_inclusive | 0.0702 (+0.0000) | 0.1793 (+0.0000) | 0.2625 (+0.0000) | 0.3777 (+0.0000) | 0.3671 (+0.0000) | 0.1042 (+0.0000) 31003/297572 |
| all_switched | 1.0000 (+0.9298) | 1.0000 (+0.8207) | 1.0000 (+0.7375) | 1.0000 (+0.6223) | 1.0000 (+0.6329) | 1.0000 (+0.8958) 297572/297572 |
| fullsample | 1.0000 (+0.9298) | 1.0000 (+0.8207) | 0.8354 (+0.5728) | 0.6016 (+0.2238) | 0.5711 (+0.2040) | 0.9864 (+0.8822) 293523/297572 |

## Edge-suite agreement with the core, by class

| variant | a_exhaustive | b_strict_alt | b_strict_dec | b_strict_inc | c_constant | c_tie50 | c_tie80 | c_tie95 | d_boundary_len | d_half_free_then_tie | d_half_tie_then_free | e_nonzero_signs | e_zero_signs | f_random_small | f_random_wide | all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frozen_ref | 0.070 | 1.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.962 | 0.1072 (3389/31604) |
| G1_stride | 0.070 | 1.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.998 | 0.1084 (+0.0011) 3425/31604 |
| G9_cap | 0.070 | 1.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.993 | 0.1082 (+0.0010) 3420/31604 |
| G2G3_sigma | 0.155 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.962 | 0.1866 (+0.0794) 5898/31604 |
| G4_classical | 0.052 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.600 | 0.000 | 0.000 | 0.000 | 0.000 | 0.283 | 0.962 | 0.0898 (-0.0174) 2839/31604 |
| G5_refuse | 0.018 | 0.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 0.800 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.003 | 0.0283 (-0.0790) 893/31604 |
| G6_ownership | 0.308 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.346 | 0.997 | 0.3326 (+0.2254) 10512/31604 |
| G7_precedence | 0.158 | 1.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.285 | 0.962 | 0.1899 (+0.0827) 6003/31604 |
| G8_inclusive | 0.070 | 1.000 | 1.000 | 1.000 | 1.000 | 0.750 | 0.500 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.283 | 0.962 | 0.1072 (+0.0000) 3389/31604 |
| all_switched | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.0000 (+0.8928) 31604/31604 |
| fullsample | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.819 | 0.994 | 0.9941 (+0.8868) 31417/31604 |

## One-sample-shift flip rates on DS1 (N=1024 and N=4096)

A flip is a change in the suggested tier when the window starts one sample later.
First-step sign is `sign(x[stride]-x[0])` at that variant's stride: core and
all_switched use the core stride (`1` if N<=1024 else `N/512`); fullsample uses stride 1.

| variant | N=1024 flips (rate) | N=1024 flips with first-step change (share) | N=4096 flips (rate) | N=4096 flips with first-step change (share) |
|---|---:|---:|---:|---:|
| core (ba2ea57) | 4620/13948 (0.331230) | 4526/4620 (0.979654) | 987/3476 (0.283947) | 407/987 (0.412361) |
| frozen_ref | 27/13948 (0.001936) | n/a | 1/3476 (0.000288) | n/a |
| G1_stride | 27/13948 (0.001936) | 19/27 (0.703704) | 0/3476 (0.000000) | 0/0 (0.000000) |
| G9_cap | 72/13948 (0.005162) | 41/72 (0.569444) | 15/3476 (0.004315) | 4/15 (0.266667) |
| G2G3_sigma | 102/13948 (0.007313) | 94/102 (0.921569) | 4/3476 (0.001151) | 0/4 (0.000000) |
| G4_classical | 0/13948 (0.000000) | 0/0 (0.000000) | 0/3476 (0.000000) | 0/0 (0.000000) |
| G5_refuse | 27/13948 (0.001936) | 19/27 (0.703704) | 1/3476 (0.000288) | 0/1 (0.000000) |
| G6_ownership | 249/13948 (0.017852) | 155/249 (0.622490) | 25/3476 (0.007192) | 5/25 (0.200000) |
| G7_precedence | 27/13948 (0.001936) | 19/27 (0.703704) | 1/3476 (0.000288) | 0/1 (0.000000) |
| G8_inclusive | 27/13948 (0.001936) | 19/27 (0.703704) | 1/3476 (0.000288) | 0/1 (0.000000) |
| all_switched | 4620/13948 (0.331230) | 4526/4620 (0.979654) | 987/3476 (0.283947) | 407/987 (0.412361) |
| fullsample | 4528/13948 (0.324634) | 4486/4528 (0.990724) | 1166/3476 (0.335443) | 1166/1166 (1.000000) |

## σ_Δ == 0 vs first-step direction (unshifted DS1)

Claim: σ_Δ is exactly 0 whenever the first step is flat or falling, because
the core averages only every other crossing and so sees only one crossing
direction. Also, 96–99.6% of flips at N<=1024 coincide with a first-step change.

| variant | N | first-step | windows | sigma_delta == 0 | rate |
|---|---:|---|---:|---:|---:|
| core | 1024 | flat or falling (<=0) | 7598 | 7598 | 1.000000 |
| core | 1024 | rising (>0) | 6350 | 310 | 0.048819 |
| core | 4096 | flat or falling (<=0) | 1705 | 1705 | 1.000000 |
| core | 4096 | rising (>0) | 1771 | 130 | 0.073405 |
| all_switched | 1024 | flat or falling (<=0) | 7598 | 7598 | 1.000000 |
| all_switched | 1024 | rising (>0) | 6350 | 310 | 0.048819 |
| all_switched | 4096 | flat or falling (<=0) | 1705 | 1705 | 1.000000 |
| all_switched | 4096 | rising (>0) | 1771 | 130 | 0.073405 |
| fullsample | 1024 | flat or falling (<=0) | 7598 | 7598 | 1.000000 |
| fullsample | 1024 | rising (>0) | 6350 | 217 | 0.034173 |
| fullsample | 4096 | flat or falling (<=0) | 1886 | 1886 | 1.000000 |
| fullsample | 4096 | rising (>0) | 1590 | 78 | 0.049057 |

### Claim check

- **core, N=1024:** already reported in DIFF_SUMMARY.md: σ_Δ == 0 on every flat/falling first step, and 4526/4620 (0.979654) of flips coincide with a first-step change.
- **fullsample, N=1024:** σ_Δ == 0 on flat/falling first step: 7598/7598 (YES, always). Rising: 217/6350. Flip-with-first-step-change share: 4486/4528 (0.990724); in 96–99.6% band: YES.
- **fullsample, N=4096** (stride 1, full window): σ_Δ == 0 on flat/falling: 1886/1886. Rising: 78/1590. Flip rate 0.335443; first-step-change share of flips 1.000000.

Which single rule causes the phase fragility: see the flip-rate table above.
A rule that, switched alone, moves the frozen-ref's near-zero flip rate up to
the core's ~33% / ~28% is the one that introduces the fragility.

## Cheddar-Panama hard-case set (read-only, exploratory)

- `manifest.csv` sha256 `521989c70d2852b92aab4a9026b9459055defb997a0394d2487a7dc2d007a129` (verified)
- `ref_v1_outputs.csv` sha256 `6a23d63486871e9ed14980f95b126b0424f4c8514270e5dc6d0be94a261c0a00` (verified)
- Windows: 137 (manifest rows 137)
- Frozen ref vs Cheddar `ref_v1_outputs.csv`: 137/137 match on tier and on features (their CSV prints 6 decimals; every value reprints identically with `%.6f`, and no pair differs by more than 1e-6). No real mismatches. An earlier 6-decimal string compare had flagged 77 typographic-only diffs; those are not disagreements.
- Frozen ref vs core on Cheddar windows: 53/137 agree (0.3869)

Core vs frozen-ref tiers on the 137 windows:

```
core\ref |   None |     T1 |     T2 |     T3
    None |     37 |      9 |     32 |     37
      T1 |      0 |      0 |      0 |      0
      T2 |      0 |      1 |      0 |      2
      T3 |      0 |      3 |      0 |     16
```

- Shift pairs found: 60
- Core flips on Cheddar shift pairs: 11/60 (0.1833)
- Frozen-ref flips on Cheddar shift pairs: 0/60 (0.0000)

Pairs that flip (core or ref):

| case | N | core | core_shift | ref | ref_shift |
|---|---:|---|---|---|---|
| ramp_jitter | 64 | T2 | None | T3 | T3 |
| ramp_jitter | 256 | None | T3 | T3 | T3 |
| walk_tie02 | 256 | T3 | None | T3 | T3 |
| walk_tie02 | 1024 | T3 | None | T3 | T3 |
| walk_tie02 | 16384 | T3 | None | T3 | T3 |
| walk_tie05 | 64 | T2 | None | T3 | T3 |
| walk_tie05 | 256 | T3 | None | T3 | T3 |
| walk_tie05 | 1024 | T3 | None | T3 | T3 |
| walk_tie13 | 256 | None | T3 | T3 | T3 |
| walk_tie30 | 64 | T2 | None | T1 | T1 |
| walk_tie60 | 4096 | None | T3 | T1 | T1 |

