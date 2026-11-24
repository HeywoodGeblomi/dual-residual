## Tater T2 tries (prereg 26953107 + errata ff54d531, frozen by Link 00:33 ET)
| ID | definition | flip 1024/4096 | MW p 1024/4096 | top tier 1024/4096 | shuffle gap pts (p) 1024/4096 | owned-on-None | all |
|---|---|---|---|---|---|---|---|
| T2v01 | (a) lag-not-decimate + T1v05 dwell parity (non-tie steps) | 0.016 / 0.003 | 0.0034 / 3.3e-06 | T3 0.816 / T3 0.665 | +19.0 (p=4e-92) / +41.4 (p=1e-108) | 0.95 / 0.95 | FAIL |
| T2v02 | (a) lag-not-decimate + T1v06 plateau parity | 0.019 / 0.006 | 0.034 / 0.096 | T3 0.608 / T3 0.671 | +9.3 (p=7e-35) / +4.4 (p=4e-06) | 0.97 / 0.96 | FAIL |
| T2v03 | (b) block-mean decimation + T1v05 dwell parity (non-tie steps) | 0.016 / 0.145 | 0.0034 / 0.025 | T3 0.816 / T3 0.552 | +19.0 (p=4e-92) / +13.7 (p=4e-30) | 0.95 / 0.96 | FAIL |
| T2v04 | (b) block-mean decimation + T1v06 plateau parity | 0.019 / 0.348 | 0.034 / 0.11 | T3 0.608 / T2 0.771 | +9.3 (p=7e-35) / +29.7 (p=6e-42) | 0.97 / 0.78 | FAIL |

## Purp V2 candidates (prereg f2d87c61, frozen by Link 00:33 ET), run by Tater's harness
| ID | definition | flip 1024/4096 | MW p 1024/4096 | top tier 1024/4096 | shuffle gap pts (p) 1024/4096 | owned-on-None | all |
|---|---|---|---|---|---|---|---|
| V2-C1 | stride 1 no cap + C1 turns (sample-position parity) | 0.019 / 0.008 | 1 / 0.008 | T3 0.862 / T3 0.735 | -0.9 (p=0.9) / -0.8 (p=0.7) | 0.89 / 0.73 | FAIL |
| V2-C2 | stride 1 no cap + C2 flat steps (sample-position parity) | 0.017 / 0.007 | 1 / 0.96 | T3 0.819 / T3 0.615 | +40.1 (p=2e-181) / +52.5 (p=4e-132) | 0.82 / 0.63 | FAIL |
| V2-C3 | stride 1 no cap + C3 any sign change (sample-position parity) | 0.020 / 0.009 | 1 / 0.0051 | T3 0.864 / T3 0.766 | +0.2 (p=0.4) / +2.4 (p=0.1) | 0.89 / 0.76 | FAIL |
| V2-T6 | stride 1 no cap + T1v06 plateau parity | 0.019 / 0.006 | 0.034 / 0.71 | T3 0.608 / T3 0.802 | +9.3 (p=7e-35) / +1.4 (p=0.1) | 0.97 / 0.94 | FAIL |
