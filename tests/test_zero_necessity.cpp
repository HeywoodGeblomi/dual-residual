// Zero-necessity + classical identity — dual-residual
// Pins Galil L2 and Knuth L1 as assertions. Does not retune floors.
// Does not edit dual_residual.hpp. No new talent.
// Floors stay recited: 0.04 / 0.005 / 0.1 / 0.2.
//
// Model (Lynch): one process, evidence(a,n). Default output is None.
// L3 skeleton / stride cliff is already pinned in tests/test_table_lock.cpp §4.
//
// Compile:
//   g++ -std=c++17 -O2 -I. tests/test_zero_necessity.cpp -o test_zero_necessity
//   ./test_zero_necessity
// Expected: ALL GREEN (test_zero_necessity)
#include "../dual_residual.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cmath>
#include <cstdint>
#include <vector>
#include <random>
#include <algorithm>

static int fails = 0;
#define CHECK(cond) do { \
    if (!(cond)) { \
        std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); \
        ++fails; \
    } \
} while (0)

static size_t evidence_stride(size_t n) {
    size_t stride = (n > 1024) ? (n / dual_residual::SAMPLE_SIZE) : 1;
    if (stride < 1) stride = 1;
    return stride;
}

struct PolarityCount {
    int T = 0;
    int z = 0;
};

static PolarityCount count_polarity(const int64_t* a, size_t n) {
    float stream[DUAL_RESIDUAL_MAX_EVENTS];
    size_t stride = evidence_stride(n);
    int T = dual_residual::detail::polarity_stream_strided(
        a, n, stride, stream, DUAL_RESIDUAL_MAX_EVENTS);
    int z = 0;
    for (int i = 0; i < T; ++i) {
        if (stream[i] == 0.f) ++z;
    }
    PolarityCount pc;
    pc.T = T;
    pc.z = z;
    return pc;
}

static std::vector<int64_t> permutation(size_t n, uint64_t seed) {
    std::vector<int64_t> a(n);
    for (size_t i = 0; i < n; ++i) a[i] = (int64_t)i;
    std::mt19937_64 rng(seed);
    std::shuffle(a.begin(), a.end(), rng);
    return a;
}

static void check_injective(const int64_t* a, size_t n, const char* tag) {
    using namespace dual_residual;
    auto e = evidence(a, n);
    PolarityCount pc = count_polarity(a, n);

    CHECK(pc.T >= 4);
    CHECK(pc.z == 0);
    CHECK(std::fabs(e.sigma_delta) < 1e-6f);
    CHECK(!e.confirmed);
    CHECK(e.suggested == Talent::None);

    // Named falsifier: injective + |σ_Δ| >= 0.005 + confirmed must FAIL
    // the suite, not retune 0.04 / 0.005 / 0.1 / 0.2.
    const bool forbidden = (std::fabs(e.sigma_delta) >= SECOND_SOLID_FLOOR) && e.confirmed;
    CHECK(!forbidden);

    std::printf("  L2 %s n=%zu T=%d z=%d C=%.6f σ_Δ=%.6f confirmed=%d talent=%d\n",
                tag, n, pc.T, pc.z, e.classical, e.sigma_delta,
                (int)e.confirmed, (int)e.suggested);
}

int main() {
    using namespace dual_residual;
    using namespace dual_residual_test;

    // Recite floors only. Do not write new numbers into the header.
    CHECK(CLASSICAL_OWNED_THRESH == 0.04f);
    CHECK(SECOND_SOLID_FLOOR     == 0.005f);
    CHECK(TALENT2_SIGMA_THRESH   == 0.1f);
    CHECK(TALENT3_CLASSICAL      == 0.2f);

    // ------------------------------------------------------------------
    // Galil L2 — zero-necessity
    // Injective input ⇒ polarity has no zeros at any stride
    // ⇒ σ_Δ == 0 (float noise) and default None.
    // ------------------------------------------------------------------
    const size_t ns[] = {32, 128, 1024, 2048};
    for (size_t n : ns) {
        {
            auto a = sorted(n);
            check_injective(a.data(), a.size(), "identity");
        }
        {
            auto a = reverse(n);
            check_injective(a.data(), a.size(), "reverse");
        }
        for (int k = 0; k < 8; ++k) {
            auto a = permutation(n, 0xA11CEull + (uint64_t)k);
            char tag[32];
            std::snprintf(tag, sizeof(tag), "shuffle[%d]", k);
            check_injective(a.data(), a.size(), tag);
        }
    }

    // ------------------------------------------------------------------
    // Knuth L1 — classical identity
    // On this alphabet, classical = 1 - z/T exactly.
    // Equality in the existing formula, not a new score.
    // ------------------------------------------------------------------
    {
        auto a = all_ties(64);
        auto e = evidence(a.data(), a.size());
        PolarityCount pc = count_polarity(a.data(), a.size());
        const float ident = 1.f - (float)pc.z / (float)pc.T;
        std::printf("  L1 all_ties T=%d z=%d classical=%.6f identity=%.6f\n",
                    pc.T, pc.z, e.classical, ident);
        CHECK(pc.T > 0);
        CHECK(pc.z == pc.T);
        CHECK(std::fabs(e.classical - ident) < 1e-6f);
        CHECK(std::fabs(e.classical) < 1e-6f);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    {
        // Mixed zeros: sea of ties + a few outliers (existing generator).
        auto a = equal_heavy(64);
        auto e = evidence(a.data(), a.size());
        PolarityCount pc = count_polarity(a.data(), a.size());
        const float ident = 1.f - (float)pc.z / (float)pc.T;
        std::printf("  L1 equal_heavy T=%d z=%d classical=%.6f identity=%.6f\n",
                    pc.T, pc.z, e.classical, ident);
        CHECK(pc.T > 0);
        CHECK(pc.z > 0);
        CHECK(pc.z < pc.T);
        CHECK(std::fabs(e.classical - ident) < 1e-6f);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }

    if (fails) {
        std::printf("%d FAIL(s) in zero-necessity suite\n", fails);
        return 1;
    }
    std::printf("ALL GREEN (test_zero_necessity)\n");
    return 0;
}
