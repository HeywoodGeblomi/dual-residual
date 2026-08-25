# Dual Residual

**Secondary Parity dual-evidence primitive** — minimal single-header core.

**What:** Dual-key residual ownership rule — classical disorder + σ_Δ (even-indexed event parity) must jointly confirm before a residual path is owned and a talent (T1/T2/T3) is suggested.

**Who:** Engineers who already route residual / talent / adaptive menus with a single soft threshold and hit borderline selection failures.

**Next:** Clone → run independent verification to `ALL GREEN` → if production embed, request a paid commercial grant ([COMMERCIAL.md](COMMERCIAL.md)). AGPLv3 otherwise.

---

This is **not** a general-purpose library, high-performance utility, or industry tool.
It is a locked, deterministic, dual-evidence oracle that answers one narrow question:

> Given an array, do classical disorder + even-indexed event parity (σ_Δ) jointly own a residual path, and if so what talent (T1/T2/T3) is suggested?

**Novelty (protected):** classical disorder + σ_Δ must jointly confirm before the residual path is owned.

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
    // to   = confirmed   (dual_owned residual path)
    // in   = suggested   (T1 / T2 / T3)
    // from = classical   (polarity magnitude)
    // with = sigma_delta (σ_Δ)
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

## Relational preposition overlay (optional)

Semantic naming only. Zero change to computation or thresholds.

**Matrix:** `{[to, in]  [from, with]}`

| Token | Role | Maps to |
|-------|------|--------|
| **from** | Origin axis | `classical` (polarity magnitude) |
| **with** | Accompanying axis | `sigma_delta` (σ_Δ) |
| **to** | Ownership path | `confirmed` (dual_owned) |
| **in** | Container / result | `suggested` (Talent T1/T2/T3) |

Narrative:

> *from* classical *with* σ_Δ → dual_owned *to* residual path *in* talent

```cpp
#include "dual_residual_relational.hpp"

auto e = dual_residual::relational::evidence(a, n);
// e is bit-identical to dual_residual::evidence / prod::evidence
// Field names unchanged: classical, sigma_delta, confirmed, suggested
```

Core and production facade remain locked. This header only names the axes.

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

## Extensibility without unlocking the core

The decision table itself is immutable.  
Callers who need different thresholds pass them explicitly:

- `dual_residual::prod::evidence_with_floor(a, n, local_sigma_floor)`  
- or the full `dual_residual::evidence(a, n, max_events, classical_thresh, sigma_floor)`

This keeps the oracle hermetic while still allowing out-of-band reuse.  
Editing the locked constants is never required and is never the supported path.

## Independent verification

```bash
g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence && ./test_evidence
g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle && ./test_parity_oracle
g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases && ./test_borderline_cases
g++ -std=c++17 -O2 -I. -Itests tests/test_relational_facade.cpp -o test_relational_facade && ./test_relational_facade
```

All must print `ALL GREEN`.

Borderline case library (single-soft failure modes vs dual correct refuse/confirm): see `BORDERLINE.md`.

See `verify/independent_host.md` for the stranger path (<10 minutes).

## Non-claims

- Not a sorting algorithm.
- No soft@1.20 or performance claim (that gate lives on the PhotonicSort charged surface only).
- No photonic hardware, optical computing, or complexity-theoretic result.
- Worst-case behaviour of any consumer remains the consumer's responsibility.
- Production facade does not alter the oracle.
- Relational overlay is semantic naming only — no new computation.

## License

**Dual licensed.**

- Non-commercial / research / evaluation / non-production → [AGPLv3](LICENSE-AGPL)
- Commercial / production / embedding / SaaS / redistribution as product → requires a [paid proprietary Commercial License](LICENSE-COMMERCIAL)

See [LICENSE](LICENSE) for the dual statement and [COMMERCIAL.md](COMMERCIAL.md) for how to request a grant.

Until a commercial grant is issued in writing, AGPLv3 governs all use.
