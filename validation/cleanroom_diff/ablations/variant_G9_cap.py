"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_G9_cap"

"""One-rule ablation: G9 only (512-sign cap / half-window read at N=1024)."""


from _core_rules import polarity_stream, signs_int_from_stream, sigma_delta_ref, classical_ref, decide_ref, DUAL_RESIDUAL_MAX_EVENTS

def tier(x):
    """Frozen ref, but the polarity stream is capped at 512 signs (G9 only).

    Stride stays 1 (ref A1). At N=1024 this is the half-window read: only the
    first 512 adjacent signs, i.e. samples 0..512, are used.
    """
    n = len(x)
    if n < 3:
        return "None", 0.0, 0.0
    stream = polarity_stream(x, stride=1, max_events=DUAL_RESIDUAL_MAX_EVENTS)
    s = signs_int_from_stream(stream)
    if not s:
        return "None", 0.0, 0.0
    if 0 not in s:
        return "None", 0.0, 0.0
    sd = sigma_delta_ref(s)
    cl = classical_ref(s)
    return decide_ref(cl, sd), cl, sd
