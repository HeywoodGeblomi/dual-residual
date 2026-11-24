"""DERIVED, CORE-INFORMED — NOT A CLEAN-ROOM REFERENCE.

This file starts from the frozen clean-room `tier()` logic (Link freeze v1,
ref.py sha256 effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f)
and switches one or more assumptions to the locked Dual Residual core's
actual behavior, as read from core/dual_residual.hpp at ba2ea57.

It is not independent of the core. Do not treat it as a clean-room spec.
Exploratory only. Rollout remains halted. DS1 only.
"""
VARIANT = "variant_fullsample"

"""Fullsample: core math, stride 1, no 512 cap. Derived, not clean-room."""


from _core_rules import evidence_core

def tier(x):
    """Core feature and decision rules on every adjacent sign of the full window.

    Stride is forced to 1 and the 512-sign cap is removed. Everything else
    (events, sigma_delta, classical, ownership, precedence) follows the core.
    Used to isolate the every-other-crossing sigma_delta phase fragility from
    the half-window / stride effects.
    """
    return evidence_core(x, stride=1, max_events=10**9)
