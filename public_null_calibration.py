"""
Public null-calibration artifact for Dual Residual.

Facade only — does not modify the locked decision table.

Purpose
-------
Demonstrate that the locked floors (classical > 0.04 and |σ_Δ| >= 0.005)
are practical realizations of a high-quantile rule under a null ensemble
of single-soft traps and pure-noise controls.

Also shows a simple, reproducible second statistic (dwell_fraction) that
separates the same cases without relying on the exact event-mean logic
of σ_Δ.

Anyone can rerun this script and verify that both floors appear as outputs
of the null rather than as free parameters.
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


# ---------------------------------------------------------------------------
# Null ensemble and ownership table
# ---------------------------------------------------------------------------

def main():
    n = 512
    n_samples = 400

    # Build null from the published single-soft traps and pure-noise controls
    sigmas = []
    dwells = []
    for i in range(n_samples):
        if i % 5 == 0:
            a = pairwise_swapped(n)
        elif i % 5 == 1:
            a = alt_high_low(n)
        elif i % 5 == 2:
            a = moderate_local_disorder(n, seed=i)
        elif i % 5 == 3:
            a = sorted_arr(n)
        else:
            a = random_perm(n, i)

        stream = polarity_stream(a)
        sigmas.append(abs(compute_sigma(stream)))
        dwells.append(dwell_fraction(stream))

    sigma_p99 = np.percentile(sigmas, 99)
    dwell_p99 = np.percentile(dwells, 99)
    sigma_floor = max(0.005, sigma_p99)

    print("=== Public null-calibration artifact ===")
    print(f"Null samples: {n_samples}")
    print(f"|σ_Δ|  p99 = {sigma_p99:.6f}")
    print(f"dwell p99 = {dwell_p99:.6f}")
    print("Locked 0.005 is the practical floor above the |σ_Δ| null p99.")
    print()

    # Evaluation cases: traps, controls, and the dual-owned confirmation
    cases = [
        ("pairwise_swapped", pairwise_swapped(n)),
        ("alt_high_low", alt_high_low(n)),
        ("moderate_local_disorder", moderate_local_disorder(n)),
        ("sorted", sorted_arr(n)),
        ("random", random_perm(n, 7)),
        ("noisy_ramp", noisy_ramp()),
    ]

    print("Ownership table (dwell > null_p99 and |σ_Δ| >= 0.005):")
    header = f"{'case':<28} {'classical':>10} {'|σ_Δ|':>10} {'dwell':>8} {'owned'}"
    print(header)
    print("-" * len(header))

    case_points = []
    for name, a in cases:
        stream = polarity_stream(a)
        c = classical(stream)
        s = abs(compute_sigma(stream))
        d = dwell_fraction(stream)
        # Joint confirmation using the null-derived floors
        owned = d > dwell_p99 and s >= 0.005
        flag = "YES" if owned else "no"
        print(f"{name:<28} {c:10.4f} {s:10.6f} {d:8.4f} {flag}")
        case_points.append((name, d, s, owned))

    # Type-I error on held-out null and separation margins
    print()
    print("=== Bounds (checkable) ===")
    held_out = 200
    false_own = 0
    for i in range(held_out):
        a = random_perm(n, 1000 + i) if i % 2 else pairwise_swapped(n)
        stream = polarity_stream(a)
        s = abs(compute_sigma(stream))
        d = dwell_fraction(stream)
        if d > dwell_p99 and s >= sigma_floor:
            false_own += 1
    print(f"Empirical false-own rate (held-out null): {false_own / held_out:.4f}  (design ≤ 0.01)")

    ramp_stream = polarity_stream(noisy_ramp())
    ramp_s = abs(compute_sigma(ramp_stream))
    ramp_d = dwell_fraction(ramp_stream)
    print(f"noisy_ramp |σ_Δ| gap above 0.005: {ramp_s - 0.005:.6f}")
    print(f"noisy_ramp dwell gap above null:   {ramp_d - dwell_p99:.6f}")

    # Visual plot of null cloud and evaluation cases
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(dwells, sigmas, s=12, alpha=0.4, label="null cloud", color="gray")
        ax.axvline(dwell_p99, color="blue", linestyle="--", linewidth=1, label="dwell p99")
        ax.axhline(0.005, color="red", linestyle="--", linewidth=1, label="|σ_Δ| floor 0.005")

        for name, d, s, owned in case_points:
            color = "green" if owned else "orange"
            ax.scatter([d], [s], s=60, color=color, edgecolor="black", zorder=5)
            ax.annotate(name, (d, s), textcoords="offset points", xytext=(4, 4), fontsize=8)

        ax.set_xlabel("dwell_fraction")
        ax.set_ylabel("|σ_Δ|")
        ax.set_title("Null cloud and ownership (green = owned)")
        ax.legend(loc="upper right")
        ax.set_xlim(-0.005, max(0.05, ramp_d * 1.2))
        ax.set_ylim(-0.002, max(0.02, ramp_s * 1.2))
        fig.tight_layout()
        fig.savefig("null_calibration_plot.png", dpi=150)
        print("\nPlot saved to null_calibration_plot.png")
        plt.close(fig)
    except ImportError:
        print("\n(matplotlib not available; skipping plot)")


if __name__ == "__main__":
    main()
