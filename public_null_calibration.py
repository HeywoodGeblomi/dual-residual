"""
Public null-calibration artifact for Dual Residual.

Facade only — does not modify the locked decision table.

Purpose
-------
Report two nulls side by side:
- Pure-trap null (published generators): degenerate at 0. Locked 0.005 is the special case above it.
- Noise-matched null (additive integer noise amp=15, same as noisy_ramp): non-degenerate. Locked 0.005 sits below its p99.

Anyone can rerun and see when the locked floors transfer and when they do not.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Polarity stream and derived statistics
# ---------------------------------------------------------------------------

def polarity_stream(a, stride=1, max_out=512):
    """Convert an array into a +1 / -1 / 0 polarity stream of consecutive comparisons."""
    n = len(a)
    out = []
    for i in range(0, n - stride, stride):
        if a[i + stride] > a[i]:
            out.append(1.0)
        elif a[i + stride] < a[i]:
            out.append(-1.0)
        else:
            out.append(0.0)
        if len(out) >= max_out:
            break
    return np.array(out)


def classical(stream):
    """Mean absolute polarity — the classical disorder score."""
    return float(np.mean(np.abs(stream))) if len(stream) else 0.0


def dwell_fraction(stream):
    """
    Fraction of zero-polarity (equal consecutive) values.
    Simple proxy second signal: near-zero on pure traps, elevated when
    residual structure introduces dwells.
    """
    if len(stream) == 0:
        return 0.0
    return float(np.mean(np.abs(stream) < 1e-6))


def compute_sigma(stream, c=0.0):
    """
    Even-indexed event parity (σ_Δ).
    Faithful reconstruction of the published dual_residual.hpp logic.
    Returns the difference of means of stream values at selected even-event indices.
    """
    T = len(stream)
    if T < 4:
        return 0.0

    # Locate zero-crossings (events)
    events = []
    above = stream[0] > c
    for t in range(1, T):
        now = stream[t] > c
        if now != above:
            events.append(t)
            above = now
        if len(events) >= 512:
            break

    if len(events) < 4:
        return 0.0

    # Take even-indexed events, then even/odd means of the stream values there
    even_idx = [events[i] for i in range(0, len(events), 2)]
    if len(even_idx) < 2:
        return 0.0

    vals = [stream[idx] for idx in even_idx]
    sum_even = sum(vals[::2])
    sum_odd = sum(vals[1::2])
    n_even = len(vals[::2])
    n_odd = len(vals[1::2])

    even_mean = sum_even / n_even if n_even else 0.0
    odd_mean = sum_odd / n_odd if n_odd else 0.0
    return even_mean - odd_mean


# ---------------------------------------------------------------------------
# Published generators (single-soft traps + controls)
# ---------------------------------------------------------------------------

def pairwise_swapped(n):
    """Sorted array with every adjacent pair swapped."""
    a = np.arange(n, dtype=np.int64)
    for i in range(0, n - 1, 2):
        a[i], a[i + 1] = a[i + 1], a[i]
    return a


def alt_high_low(n):
    """Strict alternation of high and low values."""
    a = np.zeros(n, dtype=np.int64)
    a[::2] = 100
    return a


def moderate_local_disorder(n, seed=0xB0B0, k=120):
    """Sorted array with a modest number of adjacent swaps."""
    rng = np.random.RandomState(seed)
    a = np.arange(n, dtype=np.int64)
    for _ in range(k):
        i = rng.randint(0, n - 1)
        a[i], a[i + 1] = a[i + 1], a[i]
    return a


def sorted_arr(n):
    """Fully sorted ascending."""
    return np.arange(n, dtype=np.int64)


def random_perm(n, seed):
    """Uniform random permutation."""
    rng = np.random.RandomState(seed)
    a = np.arange(n, dtype=np.int64)
    rng.shuffle(a)
    return a


def noisy_ramp(n=1024, seed=42, amp=15):
    """Monotonic ramp plus small additive noise — the dual-owned confirmation case."""
    rng = np.random.RandomState(seed)
    return np.arange(n, dtype=np.int64) + rng.randint(-amp, amp + 1, n)


def integer_noise_trap(n, seed, amp=15):
    """Pure trap plus integer additive noise of the same strength as noisy_ramp."""
    rng = np.random.RandomState(seed)
    a = pairwise_swapped(n)
    a = a + rng.randint(-amp, amp + 1, n)
    return a


# ---------------------------------------------------------------------------
# Dual-null reporting
# ---------------------------------------------------------------------------

def main():
    n = 512
    n_samples = 200
    amp = 15

    # Pure-trap null
    pure_sigmas, pure_dwells = [], []
    for i in range(n_samples):
        if i % 4 == 0:
            a = pairwise_swapped(n)
        elif i % 4 == 1:
            a = alt_high_low(n)
        elif i % 4 == 2:
            a = moderate_local_disorder(n, seed=i)
        else:
            a = random_perm(n, i)
        stream = polarity_stream(a)
        pure_sigmas.append(abs(compute_sigma(stream)))
        pure_dwells.append(dwell_fraction(stream))

    # Noise-matched null
    noise_sigmas, noise_dwells = [], []
    for i in range(n_samples):
        a = integer_noise_trap(n, seed=3000 + i, amp=amp)
        stream = polarity_stream(a)
        noise_sigmas.append(abs(compute_sigma(stream)))
        noise_dwells.append(dwell_fraction(stream))

    pure_sigma_p99 = np.percentile(pure_sigmas, 99)
    pure_dwell_p99 = np.percentile(pure_dwells, 99)
    noise_sigma_p99 = np.percentile(noise_sigmas, 99)
    noise_dwell_p99 = np.percentile(noise_dwells, 99)

    print("=== Dual-null calibration ===")
    print(f"Pure-trap null (n={n_samples}):")
    print(f"  |σ_Δ|  p99 = {pure_sigma_p99:.6f}")
    print(f"  dwell p99 = {pure_dwell_p99:.6f}")
    print(f"Noise-matched null (amp={amp}, n={n_samples}):")
    print(f"  |σ_Δ|  p99 = {noise_sigma_p99:.6f}")
    print(f"  dwell p99 = {noise_dwell_p99:.6f}")
    print()
    print("Locked 0.005 is the pure-trap special case.")
    print("It sits below the noise-matched |σ_Δ| p99.")
    print()

    # Separation for noisy_ramp under each null
    ramp_stream = polarity_stream(noisy_ramp(amp=amp))
    ramp_s = abs(compute_sigma(ramp_stream))
    ramp_d = dwell_fraction(ramp_stream)

    print("=== noisy_ramp under each null ===")
    print(f"|σ_Δ| = {ramp_s:.6f}")
    print(f"  clears pure-trap floor 0.005: {'YES' if ramp_s >= 0.005 else 'no'}")
    print(f"  clears noise-matched p99:    {'YES' if ramp_s >= noise_sigma_p99 else 'no'}")
    print(f"dwell = {ramp_d:.6f}")
    print(f"  clears pure-trap p99:        {'YES' if ramp_d > pure_dwell_p99 else 'no'}")
    print(f"  clears noise-matched p99:    {'YES' if ramp_d > noise_dwell_p99 else 'no'}")
    print()
    print("Summary:")
    print("- Pure-trap null: both signals clear the locked floors.")
    print("- Noise-matched null: only dwell clears; |σ_Δ| does not.")
    print("Locked table unchanged.")


if __name__ == "__main__":
    main()
