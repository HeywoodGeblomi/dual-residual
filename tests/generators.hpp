#pragma once
// Fixed-seed generators for dual_residual verification.
// Borderline-HE + control patterns. EXTERNAL-clean.
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
    // sprinkle a few outliers
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
    // partial shuffle to create moderate disorder
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

} // namespace dual_residual_test
