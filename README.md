# Dual Residual

**Secondary Parity dual-evidence primitive** — minimal single-header core.

This is **not** a general-purpose library, high-performance utility, or industry tool.
It is a locked, deterministic, dual-evidence oracle that answers one narrow question:

> Given an array, do classical disorder + even-indexed event parity (σ_Δ) jointly own a residual path, and if so what talent (T1/T2/T3) is suggested?

The decision table and thresholds (0.04 / 0.005 / 0.1 / 0.2) are **immutable**.  
That is the point. Parameterizing them would break the oracle property.

- Zero third-party dependencies
- C++17, single header
- Independent verification suite (ALL GREEN required)
- Production facade exists for null/size guards only — core is never modified

If you need a configurable, adaptive, or high-throughput statistical filter, this is the wrong repository.  
If you need the exact dual-evidence primitive with a frozen decision table, this is it.

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

Constants are immutable: `0.04 / 0.005 / 0.1 / 0.2`.

## Production facade (optional)

For production call sites that need pointer/size guards:

```cpp
#include "dual_residual_prod.hpp"

auto e = dual_residual::prod::evidence(a, n);  // null + size sanity, then core
```

- Core header is never modified.
- Decision table is never modified.
- Facade only: guards → `dual_residual::evidence(...)` → result unchanged.
- Opt-in floor override: `evidence_with_floor(a, n, local_floor)`.
- Independent verification of the core remains the product gate.

```bash
g++ -std=c++17 -O2 -I. tests/test_prod_facade.cpp -o test_prod_facade && ./test_prod_facade
# → test_prod_facade: ALL GREEN
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
- Production facade does not alter the oracle.

## License

MIT
