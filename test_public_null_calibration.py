"""
Unit tests for public_null_calibration.py

Verifies:
- Null quantiles under published generators are near zero
- Ownership rule refuses traps and confirms noisy_ramp
- Core functions return expected types and edge-case values

Run with: python -m pytest test_public_null_calibration.py -v
   or:    python test_public_null_calibration.py
"""

import os
import sys

import numpy as np

# Allow running from the repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from public_null_calibration import (
    alt_high_low,
    classical,
    compute_sigma,
    dwell_fraction,
    moderate_local_disorder,
    noisy_ramp,
    pairwise_swapped,
    polarity_stream,
    random_perm,
    sorted_arr,
)


def test_polarity_stream_basic():
    a = np.array([1, 2, 2, 0])
    stream = polarity_stream(a)
    assert list(stream) == [1.0, 0.0, -1.0]


def test_classical_all_positive():
    stream = np.array([1.0, 1.0, 1.0])
    assert classical(stream) == 1.0


def test_dwell_fraction_no_zeros():
    stream = np.array([1.0, -1.0, 1.0])
    assert dwell_fraction(stream) == 0.0


def test_dwell_fraction_some_zeros():
    stream = np.array([1.0, 0.0, -1.0, 0.0])
    assert dwell_fraction(stream) == 0.5


def test_compute_sigma_short_stream():
    assert compute_sigma(np.array([1.0, -1.0])) == 0.0


def test_generators_shapes():
    n = 16
    assert len(pairwise_swapped(n)) == n
    assert len(alt_high_low(n)) == n
    assert len(moderate_local_disorder(n)) == n
    assert len(sorted_arr(n)) == n
    assert len(random_perm(n, seed=1)) == n
    assert len(noisy_ramp(n=32)) == 32


def test_null_quantiles_near_zero():
    """Under the published null, both |σ_Δ| and dwell p99 must be ~0."""
    n = 128
    sigmas = []
    dwells = []
    for i in range(80):
        if i % 4 == 0:
            a = pairwise_swapped(n)
        elif i % 4 == 1:
            a = alt_high_low(n)
        elif i % 4 == 2:
            a = moderate_local_disorder(n, seed=i)
        else:
            a = random_perm(n, i)
        stream = polarity_stream(a)
        sigmas.append(abs(compute_sigma(stream)))
        dwells.append(dwell_fraction(stream))

    assert np.percentile(sigmas, 99) < 1e-6
    assert np.percentile(dwells, 99) < 1e-6


def test_ownership_table():
    """Traps and controls refuse; noisy_ramp confirms under the joint rule."""
    n = 256
    # Null floors (same rule as the artifact)
    dwell_p99 = 0.0
    sigma_floor = 0.005

    cases = {
        "pairwise": pairwise_swapped(n),
        "alt": alt_high_low(n),
        "mod_dis": moderate_local_disorder(n),
        "sorted": sorted_arr(n),
        "random": random_perm(n, 7),
        "noisy_ramp": noisy_ramp(),
    }

    for name, a in cases.items():
        stream = polarity_stream(a)
        s = abs(compute_sigma(stream))
        d = dwell_fraction(stream)
        owned = d > dwell_p99 and s >= sigma_floor
        if name == "noisy_ramp":
            assert owned, f"{name} should be owned"
        else:
            assert not owned, f"{name} should be refused"


def test_noisy_ramp_clears_both():
    stream = polarity_stream(noisy_ramp())
    assert abs(compute_sigma(stream)) >= 0.005
    assert dwell_fraction(stream) > 0.0


if __name__ == "__main__":
    # Simple runner if pytest is not available
    tests = [
        test_polarity_stream_basic,
        test_classical_all_positive,
        test_dwell_fraction_no_zeros,
        test_dwell_fraction_some_zeros,
        test_compute_sigma_short_stream,
        test_generators_shapes,
        test_null_quantiles_near_zero,
        test_ownership_table,
        test_noisy_ramp_clears_both,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
