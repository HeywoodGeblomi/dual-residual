# Tater sigma_tinker_v1 - VARIANTS_LOG (append-only)
Scope: only sigma_delta swapped in a bit-exact port of ba2ea57 (harness.py). DS1 only (dataset_v1 labels, Toni's DS1 int16 cache). DS2 never touched.
Bars: FINAL_BARS_v1.md + Purp bars 1-3. Each entry is appended automatically by run.py before the next variant is run. Cap: 15 DS1 candidate variants (T1v01..). T1v00 is the unmodified-core reproduction check, disclosed here, not a candidate.

## T1v00  (2026-11-24 00:06 ET)
- Definition: BASELINE (not a candidate): unmodified ba2ea57 sigma, reproduction check only
- Code sha256 (variant fn source + harness): `73e3b3d586f779d3d828aeacc028ce3c42747d4d928b1abd7a1443f5e41a8865`
- N=1024 (n=13892): flip 0.3310 [FAIL] | sep |sd| V med 0.0000 vs None med 0.0000, MW p=0.802 [FAIL] | tiers None 0.569, T1 0.000, T2 0.142, T3 0.289; top None 0.569 [PASS] | shuffle own_V 0.422 vs shuf 0.338, gap +8.5 pts, McNemar b=680 c=471 p=3.94e-10 [FAIL] | owned-on-None 0.432
- N=4096 (n=3459): flip 0.2842 [FAIL] | sep |sd| V med 0.0000 vs None med 0.0000, MW p=0.105 [FAIL] | tiers None 0.567, T1 0.000, T2 0.035, T3 0.398; top None 0.567 [PASS] | shuffle own_V 0.440 vs shuf 0.355, gap +8.6 pts, McNemar b=293 c=205 p=4.65e-05 [FAIL] | owned-on-None 0.427
- ALL BARS: FAIL

## T1v01  (2026-11-24 00:07 ET)
- Definition: Dwell parity: all crossings of the tie-held sign stream; value = complete dwell length; even-odd by event index (= rising-run vs falling-run length), normalized (me-mo)/(me+mo)
- Code sha256 (variant fn source + harness): `e977c3b64ceb764ecd59e163cf507059de9f181110232d59fc97167da43fcd3a`
- N=1024 (n=13892): flip 0.0284 [PASS] | sep |sd| V med 0.0521 vs None med 0.0514, MW p=0.176 [FAIL] | tiers None 0.050, T1 0.000, T2 0.174, T3 0.776; top T3 0.776 [PASS] | shuffle own_V 0.952 vs shuf 0.839, gap +11.3 pts, McNemar b=372 c=93 p=7.32e-41 [PASS] | owned-on-None 0.949
- N=4096 (n=3459): flip 0.2001 [FAIL] | sep |sd| V med 0.0730 vs None med 0.0648, MW p=0.0204 [FAIL] | tiers None 0.037, T1 0.000, T2 0.309, T3 0.655; top T3 0.655 [PASS] | shuffle own_V 0.973 vs shuf 0.861, gap +11.2 pts, McNemar b=140 c=25 p=6.74e-21 [PASS] | owned-on-None 0.956
- ALL BARS: FAIL

## T1v02  (2026-11-24 00:07 ET)
- Definition: Flat-turn parity: all crossings (tie-held); value = 1 if the turn passes through a tie; even-odd by event index (= flat peaks vs flat troughs share); tie-free -> 0
- Code sha256 (variant fn source + harness): `affde40b3f0d65160fc8f9e81b5516741b9658dc3943f1af8d683a3cfddc77db`
- N=1024 (n=13892): flip 0.0239 [PASS] | sep |sd| V med 0.0444 vs None med 0.0432, MW p=0.268 [FAIL] | tiers None 0.084, T1 0.000, T2 0.122, T3 0.793; top T3 0.793 [PASS] | shuffle own_V 0.906 vs shuf 0.735, gap +17.1 pts, McNemar b=583 c=160 p=1.33e-57 [PASS] | owned-on-None 0.918
- N=4096 (n=3459): flip 0.2417 [FAIL] | sep |sd| V med 0.0256 vs None med 0.0225, MW p=0.000891 [PASS] | tiers None 0.120, T1 0.000, T2 0.016, T3 0.864; top T3 0.864 [FAIL] | shuffle own_V 0.880 vs shuf 0.720, gap +16.0 pts, McNemar b=252 c=87 p=4.72e-20 [PASS] | owned-on-None 0.881
- ALL BARS: FAIL

## T1v03  (2026-11-24 00:07 ET)
- Definition: Zero-dwell runs: events = maximal tie runs; value = run length; even-odd by run index, normalized (me-mo)/(me+mo); <4 runs -> 0
- Code sha256 (variant fn source + harness): `7b2aeeab30a21859519ef586c56694fc04b76e1e8c00aeb2b0cf802bb3ae9b1d`
- N=1024 (n=13892): flip 0.0127 [PASS] | sep |sd| V med 0.0345 vs None med 0.0349, MW p=0.712 [FAIL] | tiers None 0.127, T1 0.000, T2 0.051, T3 0.822; top T3 0.822 [FAIL] | shuffle own_V 0.852 vs shuf 0.091, gap +76.2 pts, McNemar b=1910 c=27 p=0 [PASS] | owned-on-None 0.879
- N=4096 (n=3459): flip 0.4973 [FAIL] | sep |sd| V med 0.0000 vs None med 0.0323, MW p=1 [FAIL] | tiers None 0.462, T1 0.000, T2 0.057, T3 0.481; top T3 0.481 [PASS] | shuffle own_V 0.478 vs shuf 0.061, gap +41.7 pts, McNemar b=455 c=26 p=1.15e-102 [PASS] | owned-on-None 0.576
- ALL BARS: FAIL

## T1v04  (2026-11-24 00:08 ET)
- Definition: Dwell parity on the core's own events (crossings of s>0 = rising vs not-rising), ALL events, value = complete dwell length, normalized (me-mo)/(me+mo)
- Code sha256 (variant fn source + harness): `b7973ec99f0425182d2eaa5e522b4a853d1136c77b9fcfbc64ebff88251dec77`
- N=1024 (n=13892): flip 0.0216 [PASS] | sep |sd| V med 0.0677 vs None med 0.0949, MW p=1 [FAIL] | tiers None 0.023, T1 0.000, T2 0.428, T3 0.549; top T3 0.549 [PASS] | shuffle own_V 0.971 vs shuf 0.846, gap +12.5 pts, McNemar b=367 c=58 p=2.76e-56 [PASS] | owned-on-None 0.979
- N=4096 (n=3459): flip 0.2215 [FAIL] | sep |sd| V med 0.0499 vs None med 0.0648, MW p=1 [FAIL] | tiers None 0.040, T1 0.000, T2 0.200, T3 0.761; top T3 0.761 [PASS] | shuffle own_V 0.949 vs shuf 0.871, gap +7.9 pts, McNemar b=128 c=47 p=3.67e-10 [FAIL] | owned-on-None 0.967
- ALL BARS: FAIL

## T1v05  (2026-11-24 00:08 ET)
- Definition: Dwell parity (tie-held crossings) with dwell counted in non-tie steps only, normalized (me-mo)/(me+mo)
- Code sha256 (variant fn source + harness): `07ba052698f1ded97a93ce799bbbdce37c229c39683660355f7db40a9ca8450e`
- N=1024 (n=13892): flip 0.0307 [PASS] | sep |sd| V med 0.0551 vs None med 0.0534, MW p=0.14 [FAIL] | tiers None 0.048, T1 0.000, T2 0.179, T3 0.773; top T3 0.773 [PASS] | shuffle own_V 0.960 vs shuf 0.836, gap +12.4 pts, McNemar b=391 c=84 p=1.11e-48 [PASS] | owned-on-None 0.950
- N=4096 (n=3459): flip 0.2122 [FAIL] | sep |sd| V med 0.0769 vs None med 0.0655, MW p=0.000501 [PASS] | tiers None 0.040, T1 0.000, T2 0.326, T3 0.634; top T3 0.634 [PASS] | shuffle own_V 0.971 vs shuf 0.862, gap +10.9 pts, McNemar b=134 c=22 p=4.35e-21 [PASS] | owned-on-None 0.953
- ALL BARS: FAIL

## T1v06  (2026-11-24 00:08 ET)
- Definition: Plateau parity: all tie-held crossings; value = ties inside each complete dwell; (sum even - sum odd)/sum = rising- vs falling-run share of plateau time; tie-free -> 0
- Code sha256 (variant fn source + harness): `12883e336d4b2e108b39bde9db1f8ab8e8d307657c6236473e6ed16b944837f5`
- N=1024 (n=13892): flip 0.0299 [PASS] | sep |sd| V med 0.1070 vs None med 0.0980, MW p=3.02e-05 [PASS] | tiers None 0.043, T1 0.000, T2 0.497, T3 0.460; top T2 0.497 [PASS] | shuffle own_V 0.952 vs shuf 0.813, gap +14.0 pts, McNemar b=442 c=97 p=6.84e-54 [PASS] | owned-on-None 0.958
- N=4096 (n=3459): flip 0.4351 [FAIL] | sep |sd| V med 0.2000 vs None med 0.2000, MW p=0.00697 [PASS] | tiers None 0.073, T1 0.000, T2 0.719, T3 0.208; top T2 0.719 [PASS] | shuffle own_V 0.925 vs shuf 0.810, gap +11.6 pts, McNemar b=179 c=60 p=3.08e-15 [PASS] | owned-on-None 0.930
- ALL BARS: FAIL

## DIAGNOSTIC D1 (no new variant; re-runs logged T1v01/T1v05/T1v06 at N=4096 to see why flips happen)
```
T1v05 corr|sd| off0/off1 =0.849 sd(|sd|)=0.0523 sd(diff)=0.0288 flip transitions (0=None,2=T2,3=T3): {(0, 3): 226, (2, 3): 508}
T1v06 corr|sd| off0/off1 =0.080 sd(|sd|)=0.1741 sd(diff)=0.2354 flip transitions (0=None,2=T2,3=T3): {(2, 3): 1008, (0, 2): 386, (0, 3): 111}
T1v01 corr|sd| off0/off1 =0.827 sd(|sd|)=0.0515 sd(diff)=0.0304 flip transitions (0=None,2=T2,3=T3): {(0, 3): 208, (2, 3): 483, (0, 2): 1}
```

## CLOSED 2026-11-24 00:09 ET — 6 DS1 candidate tries (T1v01–T1v06), none passes all bars. No further variants.
