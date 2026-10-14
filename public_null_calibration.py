#!/usr/bin/env python3
"""
Public null-calibration artifact for Dual Residual.
Facade only — does not touch the locked decision table.

Shows:
- |σ_Δ| null p99 = 0 under published generators; locked 0.005 is the practical floor above it.
- dwell_fraction proxy: null p99 = 0; noisy_ramp clears it; traps refuse.
- Ownership table for both signals.

Anyone can rerun and verify that the floors are outputs of the null.
"""
import numpy as np

def polarity_stream(a, stride=1, max_out=512):
    n = len(a)
    out = []
    for i in range(0, n - stride, stride):
        if a[i + stride] > a[i]: out.append(1.0)
        elif a[i + stride] < a[i]: out.append(-1.0)
        else: out.append(0.0)
        if len(out) >= max_out: break
    return np.array(out)

def compute_sigma(stream, c=0.0):
    T = len(stream)
    if T < 4: return 0.0
    events = []
    above = stream[0] > c
    for t in range(1, T):
        now = stream[t] > c
        if now != above:
            events.append(t)
            above = now
        if len(events) >= 512: break
    ne = len(events)
    if ne < 4: return 0.0
    even_idx = [events[i] for i in range(0, ne, 2)]
    if len(even_idx) < 2: return 0.0
    vals = [stream[idx] for idx in even_idx]
    sum_even = sum(vals[::2])
    sum_odd = sum(vals[1::2])
    n_even = len(vals[::2])
    n_odd = len(vals[1::2])
    even_mean = sum_even / n_even if n_even else 0.0
    odd_mean = sum_odd / n_odd if n_odd else 0.0
    return even_mean - odd_mean

def classical(stream):
    return float(np.mean(np.abs(stream))) if len(stream) else 0.0

def dwell_fraction(stream):
    if len(stream) == 0: return 0.0
    return float(np.mean(np.abs(stream) < 1e-6))

def pairwise_swapped(n):
    a = np.arange(n, dtype=np.int64)
    for i in range(0, n-1, 2):
        a[i], a[i+1] = a[i+1], a[i]
    return a

def alt_high_low(n):
    a = np.zeros(n, dtype=np.int64)
    a[::2] = 100
    return a

def moderate_local_disorder(n, seed=0xB0B0, k=120):
    rng = np.random.RandomState(seed)
    a = np.arange(n, dtype=np.int64)
    for _ in range(k):
        i = rng.randint(0, n-1)
        a[i], a[i+1] = a[i+1], a[i]
    return a

def noisy_ramp(n=1024, seed=42, amp=15):
    rng = np.random.RandomState(seed)
    return np.arange(n, dtype=np.int64) + rng.randint(-amp, amp+1, n)

def random_perm(n, seed):
    rng = np.random.RandomState(seed)
    a = np.arange(n, dtype=np.int64)
    rng.shuffle(a)
    return a

def sorted_arr(n):
    return np.arange(n, dtype=np.int64)

def main():
    n = 512
    sigmas, dwells = [], []
    for i in range(400):
        if i % 5 == 0: a = pairwise_swapped(n)
        elif i % 5 == 1: a = alt_high_low(n)
        elif i % 5 == 2: a = moderate_local_disorder(n, seed=i)
        elif i % 5 == 3: a = sorted_arr(n)
        else: a = random_perm(n, i)
        stream = polarity_stream(a)
        sigmas.append(abs(compute_sigma(stream)))
        dwells.append(dwell_fraction(stream))

    print("=== Public null-calibration artifact ===")
    print(f"Null samples: {len(sigmas)}")
    print(f"|σ_Δ|  p99 = {np.percentile(sigmas, 99):.6f}")
    print(f"dwell p99 = {np.percentile(dwells, 99):.6f}")
    print("Locked 0.005 is the practical floor above the |σ_Δ| null p99.")
    print()

    cases = [
        ("pairwise_swapped", pairwise_swapped(n)),
        ("alt_high_low", alt_high_low(n)),
        ("moderate_local_disorder", moderate_local_disorder(n)),
        ("sorted", sorted_arr(n)),
        ("random", random_perm(n, 7)),
        ("noisy_ramp", noisy_ramp()),
    ]
    print("Ownership table (dwell > null_p99 and |σ_Δ| >= 0.005):")
    print(f"{'case':<28} {'classical':>10} {'|σ_Δ|':>10} {'dwell':>8} {'owned'}")
    for name, a in cases:
        stream = polarity_stream(a)
        c = classical(stream)
        s = abs(compute_sigma(stream))
        d = dwell_fraction(stream)
        owned = d > np.percentile(dwells, 99) and s >= 0.005
        print(f"{name:<28} {c:10.4f} {s:10.6f} {d:8.4f} {'YES' if owned else 'no'}")

if __name__ == "__main__":
    main()
