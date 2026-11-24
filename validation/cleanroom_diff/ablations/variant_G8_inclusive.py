"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_G8_inclusive"

"""One-rule ablation: G8 only (inclusive |sd| >= 0.005 floor)."""


from _core_rules import polarity_stream, signs_int_from_stream, sigma_delta_ref, classical_ref

def tier(x):
    """Frozen ref, but the ownership floor is inclusive |sd| >= 0.005 (G8 only).

    Other cutoffs (classical > 0.04, > 0.2, |sd| > 0.1) are already strict in
    both the core and the frozen ref.
    """
    n = len(x)
    if n < 3:
        return "None", 0.0, 0.0
    stream = polarity_stream(x, stride=1, max_events=None)
    s = signs_int_from_stream(stream)
    if not s:
        return "None", 0.0, 0.0
    if 0 not in s:
        return "None", 0.0, 0.0
    sd = sigma_delta_ref(s)
    cl = classical_ref(s)
    if cl > 0.2:
        t = "T3"
    elif abs(sd) > 0.1:
        t = "T2"
    elif cl > 0.04 or abs(sd) >= 0.005:
        t = "T1"
    else:
        t = "None"
    return t, cl, sd
