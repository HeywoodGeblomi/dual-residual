
"""DERIVED, CORE-INFORMED primitives copied from dual_residual.hpp at ba2ea57.

NOT a clean-room reference. Used by ablation variants and the all-switched
reproduction. Exploratory only.
"""
from __future__ import annotations

import numpy as np

# Locked constants from the header.
DUAL_RESIDUAL_MAX_EVENTS = 512
CLASSICAL_OWNED_THRESH = 0.04
SECOND_SOLID_FLOOR = 0.005
TALENT2_SIGMA_THRESH = 0.1
TALENT3_CLASSICAL = 0.2
SAMPLE_SIZE = 512

F32 = np.float32


def core_stride(n: int) -> int:
    """G1: stride = n/512 when n > 1024, else 1. (integer division.)"""
    stride = (n // SAMPLE_SIZE) if n > 1024 else 1
    return stride if stride >= 1 else 1


def sign_int(a, b) -> int:
    return (a > b) - (a < b)


def polarity_stream(x, stride: int = 1, max_events: int | None = None) -> list:
    """Adjacent (or strided) +1/-1/0 signs. max_events caps Tlen (G9, default no cap)."""
    n = len(x)
    if stride < 1:
        stride = 1
    out = []
    i = 0
    cap = max_events if max_events is not None else n
    while i + stride < n and len(out) < cap:
        d = sign_int(x[i + stride], x[i])
        out.append(F32(d))
        i += stride
    return out


def compute_sigma_delta_core(stream) -> F32:
    """G2/G3 from detail::compute.

    Events are indices t where (stream[t] > 0) flips relative to the previous
    above-ness, starting from stream[0]. Even-indexed events only (every other
    crossing) are kept. sigma_delta is the mean of stream values at the even
    positions of that even-event list, minus the mean at the odd positions.
    Returns 0 if T < 4, fewer than 4 events, or fewer than 2 even-index events.
    """
    T = len(stream)
    if T < 4:
        return F32(0)
    c = F32(0)
    events = []
    above = bool(stream[0] > c)
    for t in range(1, T):
        if len(events) >= DUAL_RESIDUAL_MAX_EVENTS:
            break
        now = bool(stream[t] > c)
        if now != above:
            events.append(t)
            above = now
    if len(events) < 4:
        return F32(0)
    even_idx = []
    for i in range(0, len(events), 2):
        if len(even_idx) < (DUAL_RESIDUAL_MAX_EVENTS // 2):
            even_idx.append(events[i])
    if len(even_idx) < 2:
        return F32(0)
    sum_even = F32(0)
    sum_odd = F32(0)
    n_even = 0
    n_odd = 0
    for i, idx in enumerate(even_idx):
        val = F32(stream[idx])
        if (i % 2) == 0:
            sum_even = F32(sum_even + val)
            n_even += 1
        else:
            sum_odd = F32(sum_odd + val)
            n_odd += 1
    even_mean = F32(sum_even / F32(n_even)) if n_even else F32(0)
    odd_mean = F32(sum_odd / F32(n_odd)) if n_odd else F32(0)
    return F32(even_mean - odd_mean)


def classical_core(stream) -> F32:
    """G4: mean of |sign|, i.e. one minus the tie rate on the polarity stream."""
    T = len(stream)
    if T <= 0:
        return F32(0)
    s = F32(0)
    for v in stream:
        s = F32(s + np.abs(F32(v)))
    return F32(s / F32(T))


def classical_ref(s_int) -> float:
    """Frozen-ref A4: fraction of adjacent sign pairs that are opposite and nonzero."""
    pairs = len(s_int) - 1
    if pairs <= 0:
        return 0.0
    rev = sum(
        1
        for i in range(pairs)
        if s_int[i] != 0 and s_int[i + 1] != 0 and s_int[i] != s_int[i + 1]
    )
    return rev / pairs


def sigma_delta_ref(s_int) -> float:
    """Frozen-ref A2/A3: event = s_i==0; sd = mean(even z) - mean(odd z)."""
    ev = [1 if s_int[i] == 0 else 0 for i in range(0, len(s_int), 2)]
    od = [1 if s_int[i] == 0 else 0 for i in range(1, len(s_int), 2)]
    return (sum(ev) / len(ev) if ev else 0.0) - (sum(od) / len(od) if od else 0.0)


def signs_int_from_stream(stream) -> list[int]:
    return [int(v) for v in stream]


def decide_ref(cl: float, sd: float) -> str:
    """Frozen-ref decision: T3 first, then T2, then OR-gate T1, all strict >."""
    if cl > 0.2:
        return "T3"
    if abs(sd) > 0.1:
        return "T2"
    if cl > 0.04 or abs(sd) > 0.005:
        return "T1"
    return "None"


def decide_core(cl: float, sd: float) -> tuple[str, bool]:
    """Locked table: owned = classical>0.04 AND |sd|>=0.005; T2 before T3."""
    confirmed = (cl > CLASSICAL_OWNED_THRESH) and (abs(sd) >= SECOND_SOLID_FLOOR)
    if not confirmed:
        return "None", False
    if abs(sd) > TALENT2_SIGMA_THRESH:
        return "T2", True
    if cl > TALENT3_CLASSICAL:
        return "T3", True
    return "T1", True


def evidence_core(x, stride=None, max_events=DUAL_RESIDUAL_MAX_EVENTS):
    """Full core evidence() reproduction (float32 features)."""
    n = len(x)
    if n < 2 or max_events < 4:
        return "None", 0.0, 0.0
    if stride is None:
        stride = core_stride(n)
    stream = polarity_stream(x, stride=stride, max_events=max_events)
    if len(stream) < 4:
        return "None", 0.0, 0.0
    sd = float(compute_sigma_delta_core(stream))
    cl = float(classical_core(stream))
    t, _ = decide_core(cl, sd)
    return t, cl, sd
