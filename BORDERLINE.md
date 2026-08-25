# Borderline Case Library

dual-residual · honest single-soft failure modes · 2026-08-25

Small, EXTERNAL-clean suite that demonstrates why dual-evidence ownership matters.

## The claim this suite proves

A single soft residual signal (classical disorder alone) will **own residual paths it should not** at the borderline.  
Dual ownership (classical + σ_Δ) correctly **refuses** those paths while still **confirming** when both axes are solid.

No soft@ theater. No new metric. No unlocked table. Core thresholds remain 0.04 / 0.005 / 0.1 / 0.2.

## Cases

### A. Single-soft traps (dual correctly refuses)

| Generator | What it produces | Single soft | Dual |
|-----------|------------------|-------------|------|
| `pairwise_swapped` | Every adjacent pair swapped | would own (classical high) | refuses (σ_Δ ≈ 0) |
| `alt_high_low` | Strict alternation | would own | refuses |
| `block_zigzag` | Local order, global zigzag | would own | refuses |
| `moderate_local_disorder` | Limited adjacent swaps | would own | refuses when σ_Δ weak |

### B. Dual-owned confirmation

| Generator | What it produces | Dual |
|-----------|------------------|------|
| `noisy_ramp_confirmed` | Ramp + controlled noise (seed 42, amp 15) | confirms, talent in {T1,T2,T3} |

### C. Controls (still refuse)

`sorted`, `reverse`, `equal_heavy` — dual remains silent. No false ownership.

## How to run

```bash
g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases
./test_borderline_cases
# → ALL GREEN (test_borderline_cases)
```

Also covered by the existing stranger path in `verify/independent_host.md` once the new test is added to the compile list.

## Non-goals

- Does not change the decision table.
- Does not add a third signal or soft metric.
- Does not claim performance (soft@ lives on PhotonicSort only).
- Does not expand into a residual menu.

This library exists so adaptive-menu engineers can see, in <30 seconds, why the second solid key is not optional at the edge.

**dual-residual** · Secondary Parity dual-evidence primitive
