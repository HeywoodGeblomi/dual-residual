# The Second Key for Residual Menus

Technical note · dual-residual · 2026-08-25  
Aimed at readers who already have a residual path and whose series can dwell.

---

## The problem you already have

Most adaptive residual menus decide with **one soft signal**.

Runs. Cardinality. Entropy. A CDF estimate. A learned classifier. A single disorder metric that routes to Counting, Radix, Quick, pdqsort, ska_sort, or a residual talent.

At the *borderline* — where the signal is weak, noisy, or near a threshold — that single key is not enough. You still open a residual path on evidence that would not survive a second check. Or you refuse a path that a second solid signal would have confirmed.

Single-signal residual ownership is the default in the field. It is also the failure mode at the edge.

---

## The second key

**Dual-evidence residual ownership:** classical disorder and a second solid signal must **jointly** confirm before the residual path is owned.

In this primitive the second signal is **σ_Δ** — even-indexed event parity. Not a soft score. Not a tunable weight. A solid axis that must agree with classical disorder before any talent (T1 / T2 / T3) is suggested.

The two maps read the same polarity stream. Separation on the borderline suite is empirical, not algebraic independence.

```
dual_owned = classical > 0.04 && |σ_Δ| >= 0.005
if (!dual_owned) → None
else if (|σ_Δ| > 0.1) → T2
else if (classical > 0.2) → T3
else → T1
```

Thresholds are **immutable**. That is the oracle property. Parameterizing them would turn the dual-key rule back into another soft menu.

This is not a sorter. It is not a claim about soft@1.20. It is a **locked decision primitive** that answers one question: do classical disorder and σ_Δ jointly own residual, and if so which talent?

On a tie-free polarity stream, σ_Δ is identically 0 and talent is None. Confirm can live only when the strided skeleton contains zeros.

---

## Who this is for

This primitive confirms only when the polarity stream can dwell (p = 0). Distinct-key / permutation arrays produce no zeros, so σ_Δ ≡ 0 and the oracle is silent. That is a property of the maps, not a routing miss.

- Maintainers who already have a residual path and whose series can repeat adjacent sampled values
- Readers of the borderline suite who want a second key that refuses single-soft traps when σ_Δ is dark

This is not a drop-in second key for unique-key sort routers (pdqsort / ska_sort / Counting / Radix on permutations). If your arrays are tie-free, do not expect confirm. If you do not already have a residual path, this note is not for you.

---

## Borderline case library (proof juice)

A small, honest suite lives in `tests/test_borderline_cases.cpp` + `BORDERLINE.md`.

It shows residual situations where **single soft-signal ownership would mis-route** while **dual ownership (classical + σ_Δ) correctly refuses or confirms**. Controls still refuse. EXTERNAL-clean. Core thresholds untouched.

```bash
g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases && ./test_borderline_cases
# → ALL GREEN (test_borderline_cases)
```

This is the evidence for that suite — not soft@ theater.

## How to verify (stranger path)

```bash
git clone https://github.com/HeywoodGeblomi/dual-residual.git
cd dual-residual
g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence && ./test_evidence
g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle && ./test_parity_oracle
g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases && ./test_borderline_cases
```

All must print `ALL GREEN`.  
See `verify/independent_host.md` for the full <10-minute path.

Core is one header: `dual_residual.hpp`. Zero third-party deps. C++17.

---

## License path

- **Evaluation / research / non-production** → AGPLv3
- **Production / embedding / SaaS / redistribution as product** → paid proprietary commercial license required

No free commercial grants. No verbal grants.  
Request: GitHub [@HeywoodGeblomi](https://github.com/HeywoodGeblomi) · subject exact: `dual-residual commercial license request`  
Serious inquiries answered within 2 business days. Details: [COMMERCIAL.md](COMMERCIAL.md).

Until a written grant is issued, AGPLv3 governs all use. The decision table stays locked under every license.

---

## What this is not

- Not a faster hybrid sort
- Not a residual router for distinct-key permutations
- Not a soft@ performance claim (that surface lives on PhotonicSort only)
- Not a configurable statistical filter
- Not an invitation to unlock or retune the table

If you need the exact dual-key residual ownership rule with independent verification, this is it.  
If you need something else, this is the wrong tree.

---

**dual-residual** · Secondary Parity dual-evidence primitive  
https://github.com/HeywoodGeblomi/dual-residual
