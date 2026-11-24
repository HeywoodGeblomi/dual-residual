"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_G6_ownership"

"""One-rule ablation: G6 only (ownership = classical>0.04 AND |sd|>=0.005)."""


from _core_rules import polarity_stream, signs_int_from_stream, sigma_delta_ref, classical_ref, CLASSICAL_OWNED_THRESH, SECOND_SOLID_FLOOR

def tier(x):
    """Frozen ref, but ownership is the core AND-gate (G6 only).

    owned = classical > 0.04 AND |sigma_delta| >= 0.005.
    If not owned, return None even when classical > 0.2 or |sd| > 0.1.
    When owned, keep the frozen-ref T3-before-T2 precedence (G7 not switched).
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
    owned = (cl > CLASSICAL_OWNED_THRESH) and (abs(sd) >= SECOND_SOLID_FLOOR)
    if not owned:
        return "None", cl, sd
    if cl > 0.2:
        return "T3", cl, sd
    if abs(sd) > 0.1:
        return "T2", cl, sd
    return "T1", cl, sd
