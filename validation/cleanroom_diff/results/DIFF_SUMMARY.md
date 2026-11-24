# DIFF_SUMMARY

Exploratory G4-04-style spec-vs-code check. Rollout remains halted. DS1 only.

## Hashes verified at startup

- Frozen dir: `/workspace/link/dr_cleanroom_frozen_v1`
- `CLEANROOM_SPEC_v1.md`: `fe1fa84dcdf82410b596c2aff05a8d6890c157e02daf02913efb3c277f67c897`
- `ref.py`: `effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f`
- `FROZEN_v1.sha256`: `932fd233f1a426d8dc973ca896e3aafe9a558a75406737c4dddfc57982277976`
- Core dump DS1: `5341a8440543e5a18d82a2a46e2a4f0a9bedd2b325b0bd11743872bd620f86cd`
- Core dump edge: `24855f80e40002aaf0c758865344ade04c67799e5c2595a04d5790f83d42ec20`
- Edge suite: `76bb1c8a35a3e867d5a1d2005ebf5448e377bf10efec882660dfe0f453c93c01`

## DS1 agreement by N

| N | agree | total | rate |
|---:|---:|---:|---:|
| 64 | 15696 | 223432 | 0.070250 |
| 256 | 10017 | 55858 | 0.179330 |
| 1024 | 3662 | 13948 | 0.262547 |
| 4096 | 1313 | 3476 | 0.377733 |
| 16384 | 315 | 858 | 0.367133 |
| all | 31003 | 297572 | 0.104187 |

## DS1 confusion matrix (core rows, ref columns)

```
core\ref |   None |     T1 |     T2 |     T3 |  total
---------|--------|--------|--------|--------|------
    None |   1351 |  43016 |   8291 | 128132 | 180790
      T1 |      0 |      0 |      0 |      0 |      0
      T2 |     23 |  23978 |   4768 |  57766 |  86535
      T3 |      0 |   4666 |    697 |  24884 |  30247
   total |   1374 |  71660 |  13756 | 210782 | 297572
```

## Edge-suite agreement by class

| class | agree | total | rate |
|---|---:|---:|---:|
| a_exhaustive | 2056 | 29511 | 0.069669 |
| b_strict_alt | 9 | 9 | 1.000000 |
| b_strict_dec | 9 | 9 | 1.000000 |
| b_strict_inc | 9 | 9 | 1.000000 |
| c_constant | 4 | 4 | 1.000000 |
| c_tie50 | 3 | 4 | 0.750000 |
| c_tie80 | 2 | 4 | 0.500000 |
| c_tie95 | 2 | 4 | 0.500000 |
| d_boundary_len | 30 | 30 | 1.000000 |
| d_half_free_then_tie | 1 | 1 | 1.000000 |
| d_half_tie_then_free | 1 | 1 | 1.000000 |
| e_nonzero_signs | 9 | 9 | 1.000000 |
| e_zero_signs | 9 | 9 | 1.000000 |
| f_random_small | 283 | 1000 | 0.283000 |
| f_random_wide | 962 | 1000 | 0.962000 |
| all | 3389 | 31604 | 0.107233 |

## Edge confusion matrix (core rows, ref columns)

```
core\ref |   None |     T1 |     T2 |     T3 |  total
---------|--------|--------|--------|--------|------
    None |   2972 |   1255 |   6781 |  16637 |  27645
      T1 |      0 |      0 |      0 |      0 |      0
      T2 |      0 |     22 |    133 |   3518 |   3673
      T3 |      2 |      0 |      0 |    284 |    286
   total |   2974 |   1277 |   6914 |  20439 |  31604
```

## Disagreement gap attribution

A disagreement may carry more than one gap. UNEXPLAINED means no heuristic fired.

### DS1

| gap | disagreements tagged |
|---|---:|
| G4 | 266569 |
| G2 | 266569 |
| G3 | 266569 |
| G1 | 12992 |
| G9 | 12992 |
| (disagreements) | 266569 |

### Edge

| gap | disagreements tagged |
|---|---:|
| G4 | 28169 |
| G2 | 23495 |
| G3 | 23495 |
| G1 | 389 |
| G9 | 389 |
| G5 | 2 |
| (disagreements) | 28215 |

## UNEXPLAINED disagreements

DS1: 0  |  edge: 0

No UNEXPLAINED DS1 disagreements.

No UNEXPLAINED edge disagreements.

## Gate 3 one-sample-shift phase test (DS1, N=1024 and N=4096)

Each window is compared with the same record starting one sample later,
only when the shifted window fits in the signal. A flip is a change in the
suggested tier. First-step sign is `sign(x[stride] - x[0])` at the *core*
stride (`1` when N<=1024, else `N/512`). A first-step change means that
sign differs between the unshifted and shifted windows.

| N | pairs | core flips | core flip rate | ref flips | ref flip rate | core flips with first-step change | share |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 13948 | 4620 | 0.331230 | 27 | 0.001936 | 4526 | 0.979654 |
| 4096 | 3476 | 987 | 0.283947 | 1 | 0.000288 | 407 | 0.412361 |

### sigma_delta == 0 vs first-step direction (core, unshifted DS1 windows)

Claim under test: σ_Δ is exactly 0 whenever the first step is flat or falling,
and 96–99.6% of flips at N<=1024 coincide with the first step changing.

| N | first-step | windows | sigma_delta == 0 | rate |
|---:|---|---:|---:|---:|
| 1024 | flat or falling (<=0) | 7598 | 7598 | 1.000000 |
| 1024 | rising (>0) | 6350 | 310 | 0.048819 |
| 4096 | flat or falling (<=0) | 1705 | 1705 | 1.000000 |
| 4096 | rising (>0) | 1771 | 130 | 0.073405 |

Claim check (core, N=1024):
- σ_Δ exactly 0 on every flat/falling first step at N=1024: **YES**
  (7598/7598). Rising first step: 310/6350 have σ_Δ == 0.
- Share of N=1024 core flips coinciding with a first-step change: **0.979654** (4526/4620); in the claimed 96–99.6% band: **YES**.

## Runtime

- Ref (or stub) DS1: wall 7.507s, sum of per-window eval 18.589s, mean 0.000062s/window
- Ref (or stub) edge: wall 2.063s, sum of per-window eval 2.177s, mean 0.000069s/window
- Ref (or stub) shift: wall 2.883s, sum of per-window eval 7.438s
- Workers: 8

