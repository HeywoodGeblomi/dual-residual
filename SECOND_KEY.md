# The Second Key for Residual Menus

Technical note · dual-residual · 2026-08-25  
Aimed at engineers who already maintain adaptive residual, talent, or hybrid sort routers.

---

## The problem you already have

Most adaptive residual menus decide with **one soft signal**.

Runs. Cardinality. Entropy. A CDF estimate. A learned classifier. A single disorder metric that routes to Counting, Radix, Quick, pdqsort, ska_sort, or a residual talent.

At the *borderline* — where the signal is weak, noisy, or near a threshold — that single key is not enough. You still open a residual path on evidence that would not survive a second independent check. Or you refuse a path that a second solid signal would have confirmed.

Single-signal residual ownership is the default in the field. It is also the failure mode at the edge.

---

## The second key

**Dual-evidence residual ownership:** classical disorder and a second independent solid signal must **jointly** confirm before the residual path is owned.

In this primitive the second signal is **σ_Δ** — even-indexed event parity. Not a soft score. Not a tunable weight. A solid axis that must agree with classical disorder before any talent (T1 / T2 / T3) is suggested.

```
dual_owned = classical > 0.04 && |σ_Δ| >= 0.005
if (!dual_owned) → None
else if (|σ_Δ| > 0.1) → T2
else if (classical > 0.2) → T3
else → T1
```

Thresholds are **immutable**. That is the oracle property. Parameterizing them would turn the dual-key rule back into another soft menu.

This is not a sorter. It is not a claim about soft@1.20. It is a **locked decision primitive** that answers one question: do two independent signals jointly own residual, and if so which talent?

---

## Who this is for

- Maintainers of adaptive residual / talent menus inside database kernels, HPC libraries, or hybrid policy layers
- Anyone already routing to pdqsort / ska_sort / vergesort / Counting / Radix with a **single** threshold or classifier and hitting borderline mis-routes
- Engineers who want a second solid key they can drop in without adopting a full sort stack

If you do not already have a residual path, this note is not for you.

---

## How to verify (stranger path)

```bash
git clone https://github.com/HeywoodGeblomi/dual-residual.git
cd dual-residual
g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence && ./test_evidence
g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle && ./test_parity_oracle
```

Both must print `ALL GREEN`.  
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
- Not a soft@ performance claim (that surface lives on PhotonicSort only)
- Not a configurable statistical filter
- Not an invitation to unlock or retune the table

If you need the exact dual-key residual ownership rule with independent verification, this is it.  
If you need something else, this is the wrong tree.

---

**dual-residual** · Secondary Parity dual-evidence primitive  
https://github.com/HeywoodGeblomi/dual-residual
