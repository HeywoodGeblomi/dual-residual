# Dual Residual

**Secondary Parity dual-evidence primitive** — minimal single-header core.

A classical disorder score (visible polarity magnitude) plus a second solid signal (σ_Δ from even-indexed event parity) jointly decide whether a residual path is owned, and emit a talent suggestion (T1 / T2 / T3).

This is the transferable core. It does not sort. It does not claim soft@1.20. It does not depend on any residual menu or library.

## Use

```cpp
#include "dual_residual.hpp"

int64_t a[n] = { /* ... */ };
auto e = dual_residual::evidence(a, n);

if (e.confirmed) {
    // dual_owned — residual path is jointly confirmed
    // e.suggested is T1, T2, or T3
    // e.sigma_delta and e.classical are the visible metrics
}
```

C++17. Zero dependencies beyond the standard library. One header.

## Decision table (locked)

```
dual_owned = classical > 0.04 && |σ_Δ| >= 0.005
if (!dual_owned) → None
else if (|σ_Δ| > 0.1) → T2
else if (classical > 0.2) → T3
else → T1
```

## Independent verification

```bash
g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence && ./test_evidence
g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle && ./test_parity_oracle
```

Both must print `ALL GREEN`.

See `verify/independent_host.md` for the stranger path (<10 minutes).

## Non-claims

- Not a sorting algorithm.
- No soft@1.20 or performance claim.
- No photonic hardware, optical computing, or complexity-theoretic result.
- Worst-case behaviour of any consumer remains the consumer's responsibility.

## License

MIT
