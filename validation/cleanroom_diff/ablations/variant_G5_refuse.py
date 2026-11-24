"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_G5_refuse"

"""One-rule ablation: G5 only (drop the tie-free early refuse)."""


from _core_rules import polarity_stream, signs_int_from_stream, sigma_delta_ref, classical_ref, decide_ref

def tier(x):
    """Frozen ref, but no special-case refuse on tie-free streams (G5 only).

    The core has no such short-circuit: tie-free windows still get a classical
    score and a sigma_delta (often 0 when there are no crossings).
    """
    n = len(x)
    if n < 3:
        return "None", 0.0, 0.0
    stream = polarity_stream(x, stride=1, max_events=None)
    s = signs_int_from_stream(stream)
    if not s:
        return "None", 0.0, 0.0
    # G5 switch: do NOT return (None, 0, 0) when 0 not in s.
    sd = sigma_delta_ref(s)
    cl = classical_ref(s)
    return decide_ref(cl, sd), cl, sd
