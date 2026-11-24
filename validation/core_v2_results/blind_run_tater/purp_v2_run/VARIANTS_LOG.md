# Purp CORE_V2_CANDIDATES_v1 (f2d87c61...) run by Tater's harness. IDs are Purp's. Run only after Link's freeze copy is found.

Link freeze copy found 00:33:39 ET at /workspace/link/dr_core_v2_prereg_frozen_v1/purp/CORE_V2_CANDIDATES_v1.md (f2d87c61...). Source sha re-verified by run_v2.py assert immediately before each run (00:34:09 ET start). Note: Toni also ran these four on DS1 (per Link NOTES.md); this is a second harness run of the SAME 4 frozen candidates, not new tries.

## V2-C1  (2026-11-24 00:34:20 ET)
- Definition: stride 1 no cap + C1 turns (sample-position parity)
- Code sha256: `771a134edf45cd7b7d7363926f6a22c5b65f891cbb67c2843c4daab376a350dc`
- N=1024 (n=13892): flip 0.0188 [PASS] | sep |sd| V med 0.0215 vs None med 0.0235, MW p=1 [FAIL] | tiers None 0.116, T1 0.000, T2 0.022, T3 0.862; top T3 0.862 [FAIL] | shuffle own_V 0.874 vs shuf 0.883, gap -0.9 pts, McNemar b=246 c=269 p=0.855 [FAIL] | owned-on-None 0.887
- N=4096 (n=3459): flip 0.0084 [PASS] | sep |sd| V med 0.0117 vs None med 0.0098, MW p=0.008 [PASS] | tiers None 0.260, T1 0.000, T2 0.004, T3 0.735; top T3 0.735 [PASS] | shuffle own_V 0.760 vs shuf 0.768, gap -0.8 pts, McNemar b=170 c=178 p=0.685 [FAIL] | owned-on-None 0.731
- ALL BARS: FAIL

## V2-C2  (2026-11-24 00:34:28 ET)
- Definition: stride 1 no cap + C2 flat steps (sample-position parity)
- Code sha256: `450b9a8b717767fec73ce9eac87e83aab55c549020ecbedf11d3b36df454b786`
- N=1024 (n=13892): flip 0.0166 [PASS] | sep |sd| V med 0.0135 vs None med 0.0140, MW p=1 [FAIL] | tiers None 0.181, T1 0.000, T2 0.000, T3 0.819; top T3 0.819 [FAIL] | shuffle own_V 0.812 vs shuf 0.411, gap +40.1 pts, McNemar b=1164 c=172 p=1.6e-181 [PASS] | owned-on-None 0.822
- N=4096 (n=3459): flip 0.0069 [PASS] | sep |sd| V med 0.0069 vs None med 0.0069, MW p=0.964 [FAIL] | tiers None 0.385, T1 0.000, T2 0.000, T3 0.615; top T3 0.615 [PASS] | shuffle own_V 0.605 vs shuf 0.081, gap +52.5 pts, McNemar b=568 c=28 p=3.56e-132 [PASS] | owned-on-None 0.626
- ALL BARS: FAIL

## V2-C3  (2026-11-24 00:34:37 ET)
- Definition: stride 1 no cap + C3 any sign change (sample-position parity)
- Code sha256: `cada4ca70531868a542ad060ca28ef9c4bf70139ee62a6eeff58e11cb720cbcb`
- N=1024 (n=13892): flip 0.0198 [PASS] | sep |sd| V med 0.0235 vs None med 0.0254, MW p=1 [FAIL] | tiers None 0.108, T1 0.000, T2 0.028, T3 0.864; top T3 0.864 [FAIL] | shuffle own_V 0.890 vs shuf 0.887, gap +0.2 pts, McNemar b=254 c=248 p=0.412 [FAIL] | owned-on-None 0.892
- N=4096 (n=3459): flip 0.0087 [PASS] | sep |sd| V med 0.0127 vs None med 0.0112, MW p=0.00513 [PASS] | tiers None 0.229, T1 0.000, T2 0.005, T3 0.766; top T3 0.766 [PASS] | shuffle own_V 0.801 vs shuf 0.776, gap +2.4 pts, McNemar b=188 c=163 p=0.1 [FAIL] | owned-on-None 0.758
- ALL BARS: FAIL

## V2-T6  (2026-11-24 00:34:39 ET)
- Definition: stride 1 no cap + T1v06 plateau parity
- Code sha256: `1078f4d0ef301b5b9eefcd7e8ba2b14e6611110c6a1ca9b7d39474a17373cda5`
- N=1024 (n=13892): flip 0.0186 [PASS] | sep |sd| V med 0.0769 vs None med 0.0732, MW p=0.0337 [FAIL] | tiers None 0.030, T1 0.000, T2 0.362, T3 0.608; top T3 0.608 [PASS] | shuffle own_V 0.967 vs shuf 0.874, gap +9.3 pts, McNemar b=302 c=72 p=6.52e-35 [FAIL] | owned-on-None 0.970
- N=4096 (n=3459): flip 0.0064 [PASS] | sep |sd| V med 0.0445 vs None med 0.0444, MW p=0.713 [FAIL] | tiers None 0.059, T1 0.000, T2 0.140, T3 0.802; top T3 0.802 [FAIL] | shuffle own_V 0.948 vs shuf 0.935, gap +1.4 pts, McNemar b=61 c=47 p=0.105 [FAIL] | owned-on-None 0.941
- ALL BARS: FAIL

## CLOSED 00:34:54 ET. No further tries.
