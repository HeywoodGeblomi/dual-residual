# Gate 3 phase-flip mechanism in core ba2ea57 (Tater, exploratory)
Header: dual_residual.hpp @ ba2ea5717863ae70497aed51514f9db2c0653b22 (file sha256 64fa3ca2da1655301ab64e4be704bbf34d975b8d690962d8fba93258b6d01ecf)
Probe: probe.cpp (compiled against the unmodified header), output probe_out.txt. Synthetic quantized random walks, 4000 trials per cell, seed 12345.

## Mechanism (read from detail::compute, L53-86)
- Events are crossings of stream[t] > 0, so they alternate up, down, up, down.
- even_idx takes events[0], events[2], ... : every one of them crosses in the SAME direction as events[0].
- If the first sign is <= 0 (first step flat or falling), events[0] is an up-crossing, every sampled value is +1, so even_mean = odd_mean = 1 and sigma_delta == 0 EXACTLY. dual_confirm fails, result is None.
- If the first sign is +1, every sampled crossing is a down-crossing landing on -1 or 0, and sigma_delta = (tie share among even-slot down-crossings) - (tie share among odd-slot down-crossings).
- So "owned" is gated by the direction of the window's first step, and sigma_delta measures a tie-landing imbalance, not parity of the signal.

## Probe results
- sigma_delta == 0 exactly in 100% of windows whose first sign is <= 0, in all 15 cells (N 64..16384, tie 5/20/40%).
- N <= 1024: 96-99.6% of one-sample-shift decision flips coincide with the first sign changing.
- N > 1024: first-sign change explains ~30-50% of flips; the rest come from the stride lattice moving (shift by 1 at stride N/512 re-samples every point).
- Null owned rate 0.27-0.42, matching the Job 2 ~40% false-trigger finding.

## Implication
Gate 3's flip boundary is in detail::compute (the even-index event selection) plus the stride lattice, both inside the locked header. A fix is an architecture change and needs Blam's call. It does not by itself address discrimination (Toni: p = 0.81 / 0.10).
