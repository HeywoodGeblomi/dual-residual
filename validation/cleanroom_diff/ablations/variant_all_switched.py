"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_all_switched"

"""All-switched reproduction of dual_residual::evidence at ba2ea57."""


from _core_rules import evidence_core

def tier(x):
    """All assumptions switched to the core. Should reproduce ba2ea57 evidence().

    Includes core stride, 512-sign cap, event/sigma definition, classical
    formula, no tie-free refuse, AND ownership with inclusive floor, and T2
    before T3. Features are computed in float32 to match the C++ `float`.
    """
    return evidence_core(x)
