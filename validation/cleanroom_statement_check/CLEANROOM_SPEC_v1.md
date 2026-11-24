# Dual Residual clean-room reference spec v1 (Purp)

## Source and taint log
- Only source: Blam's "Engineering Directive: Dual Residual Core Validation & Rollout" text, as posted in Cul De Sac on Nov 23 at 2:50 PM ET, plus its gate screenshots.
- I have never opened `dual_residual.hpp` or any dual-residual source file.
- Taint: I have read room messages describing the core: the stride N/512 above N=1024, the 512-sign cap, classical ≈ 1 − tie rate, and comparison with a sample a stride ahead. None of these is used below. Wherever the directive is silent, I log a gap (G#) and state the assumption (A#) I made instead of using what the room reported.

## What the directive states
- D1: Input is a stream. "Adjacent strided comparisons (+1 / -1 / 0)" produce "zero-dwell events".
- D2: "Tie-free streams force σ_Δ ≡ 0 and refuse."
- D3: σ_Δ is the "even-index mean − odd-index mean on zero-crossing events".
- D4: The cutoffs are classical > 0.04, |σ_Δ| > 0.005, |σ_Δ| > 0.1 → T2, classical > 0.2 → T3, with a fallback to T1.
- D5: Output states are None, T1, T2 and T3.

## Gaps and assumptions
- G1, the stride ("strided" is undefined). A1: stride 1, so s_i = sign(x[i+1] − x[i]) for i = 0..N−2.
- G2, what a zero-dwell or zero-crossing event is. A2: an event is any position i where s_i = 0.
- G3, what σ_Δ averages over. A3: z_i = 1 if s_i = 0, else 0, and σ_Δ = mean(z_i over even i) − mean(z_i over odd i).
- G4, the formula for "classical" (undefined). A4: classical = the fraction of adjacent sign pairs (s_i, s_{i+1}) with both nonzero and opposite, i.e. direction reversals, over all N−2 pairs.
- G5, what "refuse" maps to. A5: if no s_i = 0, the output is None.
- G6, the ownership gate. A6: owned if classical > 0.04 OR |σ_Δ| > 0.005.
- G7, precedence when the T2 and T3 conditions both hold. A7: T3 wins.
- G8, comparison direction (strict or inclusive). A8: strict >, as written.
- G9, window length and any cap. A9: all N samples are used, with no cap.

## Decision procedure
1. s_i = sign(x[i+1] − x[i]). If no s_i = 0, return None.
2. Compute σ_Δ (A3) and classical (A4).
3. If classical > 0.2, return T3. Else if |σ_Δ| > 0.1, return T2. Else if classical > 0.04 or |σ_Δ| > 0.005, return T1. Else return None.

## Expected use
Toni runs `ref.py` against `ba2ea57` on DS1. Every disagreement is attributed to a G# assumption or flagged as unexplained. Agreement on ordinary windows proves the least, so per Link, tie-heavy windows, N=1024, and inputs with exactly 512 events should be included.
