# Dual Residual core v2 candidates, prereg v1 (Purp). Exploratory; Link to freeze before any run.

## Authority
- Blam, Nov 24 00:12 ET: "Full unlock" for the core header, after the σ_Δ-only unlock.
- `ba2ea57` stays on record as the version that failed Gate 3.

## What changes (only what the DS1 diagnostics point at)
1. **Sampling.** Every sample is read: stride 1, no 512 cap, at every N.
   - Why: Tater's diagnostic found the stride-8 lattice causes the remaining flips at N=4096.
2. **σ_Δ.** Each candidate uses one σ_Δ definition, all splitting by sample-position parity:
   - **V2-C1:** C1 (turns), from `/workspace/link/dr_sigma_candidates_frozen_v1/`.
   - **V2-C2:** C2 (flat steps), same source.
   - **V2-C3:** C3 (any sign change), same source.
   - **V2-T6:** Tater's T1v06 (plateau parity), exactly as defined in `/workspace/tater/sigma_tinker_v1/` (hash list b2585ac9…).

## What stays as `ba2ea57`
- The four constants: 0.04 / 0.005 / 0.1 / 0.2.
- The decision table and precedence.
- The AND ownership gate.
- The classical formula.
- The refusal rule.

These are not changed even though the unlock allows it. Changing them after seeing DS1 would add tries without a diagnostic reason.

## Bars and selection
- Bars: Link's `FINAL_BARS_v1.md` unchanged, at both N=1024 and N=4096, with the tier mix and owned-on-None rate reported.
- Selection: of the candidates passing every bar on DS1, the lowest N=1024 flip rate goes to DS2, which is scored once.
- If none passes, that is the result, with no fifth candidate.

## Try count (must be reported with any win)
- C1–C3: 3 tries (σ_Δ-only; still to be run).
- Tater's T1v01–T1v06: 6 tries.
- V2-C1, V2-C2, V2-C3 and V2-T6: 4 tries.
- Total: 13.

## Prediction logged before the run
- At least one V2 candidate passes the flip bar at both N.
- If none does, the stride explanation for the N=4096 flips is wrong.

## Still sealed
DS2 stays sealed until one candidate and this prereg are frozen.
