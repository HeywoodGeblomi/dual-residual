#pragma once
// Fixed-seed generators for dual_residual verification.
// Borderline suite + control patterns. EXTERNAL-clean.
// The borderline generators exist to prove single-soft-signal failure modes
// against dual-ownership correctness. Core thresholds never change.
#include <cstdint>
#include <cstddef>
#include <vector>
#include <random>
#include <algorithm>

namespace dual_residual_test {

inline std::vector<int64_t> sorted(size_t n) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)i;
    return a;
}

inline std::vector<int64_t> reverse(size_t n) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)(n - 1 - i);
    return a;
}

inline std::vector<int64_t> equal_heavy(size_t n, int64_t mode = 42) {
    std::vector<int64_t> a(n, mode);
    if (n > 10) {
        a[0] = mode - 100;
        a[n/2] = mode + 100;
        a[n-1] = mode - 50;
    }
    return a;
}

// Borderline high-entropy: high unique + moderate inversions
inline std::vector<int64_t> borderline_he(size_t n, uint64_t seed = 0xD00D) {
    std::mt19937_64 rng(seed);
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)i;
    for (size_t i = 0; i + 1 < n; i += 3 + (rng() % 5)) {
        size_t j = i + 1 + (rng() % std::min<size_t>(16, n - i - 1));
        if (j < n) std::swap(a[i], a[j]);
    }
    return a;
}

inline std::vector<int64_t> pure_random(size_t n, uint64_t seed = 0xC0FFEE) {
    std::mt19937_64 rng(seed);
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)(rng() & 0xFFFFFFFF);
    return a;
}

// ---------------------------------------------------------------------------
// Borderline case library (honest single-soft failure modes)
// ---------------------------------------------------------------------------

// High classical, balanced events → |σ_Δ| ≈ 0.
// Single soft (classical > 0.04) would own residual; dual correctly refuses.
inline std::vector<int64_t> pairwise_swapped(size_t n) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)i;
    for (size_t i = 0; i + 1 < n; i += 2) std::swap(a[i], a[i + 1]);
    return a;
}

// Alternating high/low — classical = 1.0, σ_Δ = 0. Dual refuses.
inline std::vector<int64_t> alt_high_low(size_t n) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (i % 2 == 0) ? 100 : 0;
    return a;
}

// Block zigzag: local order, global disorder. Classical high, σ_Δ weak.
inline std::vector<int64_t> block_zigzag(size_t n, size_t block = 64) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) {
        size_t b = i / block;
        size_t off = i % block;
        a[i] = (b % 2 == 0) ? (int64_t)off : (int64_t)(block - off);
    }
    return a;
}

// Noisy ramp with fixed seed/amplitude that yields solid σ_Δ.
// Dual owns correctly; classical also high (both agree).
inline std::vector<int64_t> noisy_ramp_confirmed(size_t n = 1024, uint64_t seed = 42) {
    std::mt19937_64 rng(seed);
    std::vector<int64_t> a(n);
    const int amp = 15; // empirically dual-owned under this seed
    for (size_t i = 0; i < n; ++i)
        a[i] = (int64_t)i + (int64_t)(rng() % (2 * amp) - amp);
    return a;
}

// Moderate local disorder (partial swaps) — high classical, weak σ_Δ.
inline std::vector<int64_t> moderate_local_disorder(size_t n, uint64_t seed = 0xB0B0) {
    std::mt19937_64 rng(seed);
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)i;
    for (int k = 0; k < 120; ++k) {
        size_t i = rng() % (n - 1);
        std::swap(a[i], a[i + 1]);
    }
    return a;
}

} // namespace dual_residual_test
