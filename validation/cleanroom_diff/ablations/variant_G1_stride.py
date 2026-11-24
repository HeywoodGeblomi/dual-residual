"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_G1_stride"

"""One-rule ablation: G1 only (core stride, including N/512 above N=1024)."""


from _core_rules import core_stride, polarity_stream, signs_int_from_stream, sigma_delta_ref, classical_ref, decide_ref

def tier(x):
    """Frozen ref, but signs are taken at the core stride (G1 only). No 512 cap."""
    n = len(x)
    if n < 3:
        return "None", 0.0, 0.0
    stride = core_stride(n)
    stream = polarity_stream(x, stride=stride, max_events=None)
    s = signs_int_from_stream(stream)
    if not s:
        return "None", 0.0, 0.0
    if 0 not in s:
        return "None", 0.0, 0.0
    sd = sigma_delta_ref(s)
    cl = classical_ref(s)
    return decide_ref(cl, sd), cl, sd
