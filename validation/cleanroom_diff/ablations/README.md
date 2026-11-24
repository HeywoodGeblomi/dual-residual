# Ablation variants (derived, core-informed — not clean-room)

These files are **not** a clean-room reference. Each one starts from the
Link-frozen `ref.py` (`effc85ac…`) and switches one assumed rule to the
behavior in `core/dual_residual.hpp` at `ba2ea57`. The frozen files under
`/workspace/link/dr_cleanroom_frozen_v1/` and `/workspace/purp/dr-cleanroom/`
were not edited.

Exploratory only. Rollout remains halted. DS1 only.

| file | rule switched |
|---|---|
| `variant_G1_stride.py` | Core stride (`1` if N<=1024, else `N/512`). No cap. |
| `variant_G9_cap.py` | 512-sign cap (half-window read at N=1024). Stride stays 1. |
| `variant_G2G3_sigma.py` | Core event definition and σ_Δ average (every other crossing of `stream[t] > 0`; even-odd mean of stream values). |
| `variant_G4_classical.py` | Core classical = mean(\|sign\|). |
| `variant_G5_refuse.py` | Drop the tie-free early refuse. |
| `variant_G6_ownership.py` | Ownership = `classical > 0.04 AND \|σ_Δ\| >= 0.005`. |
| `variant_G7_precedence.py` | T2 before T3. |
| `variant_G8_inclusive.py` | Inclusive floor `\|σ_Δ\| >= 0.005`. |
| `variant_all_switched.py` | All of the above; should reproduce the core. |
| `variant_fullsample.py` | Core math on the full window (stride 1, no cap). |
