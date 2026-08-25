// Borderline case library — dual-residual
// Honest suite: single soft-signal residual ownership mis-routes;
// dual ownership (classical + σ_Δ) refuses or confirms correctly.
// EXTERNAL-clean. Core decision table never touched.
// Compile:
//   g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases
//   ./test_borderline_cases
// Expected: ALL GREEN (test_borderline_cases)
#include "../dual_residual.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cmath>
#include <vector>

static int fails = 0;
#define CHECK(cond) do { \
    if (!(cond)) { \
        std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); \
        ++fails; \
    } \
} while (0)

// Single-soft decision: classical alone above locked threshold.
static bool single_soft_would_own(float classical) {
    return classical > dual_residual::CLASSICAL_OWNED_THRESH;
}

int main() {
    using namespace dual_residual;
    using namespace dual_residual_test;

    // ------------------------------------------------------------------
    // A. Single-soft trap cases
    //    classical high → single would own residual
    //    |σ_Δ| weak → dual correctly refuses
    // ------------------------------------------------------------------
    {
        auto a = pairwise_swapped(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(e.classical > 0.5f);                 // strong classical
        CHECK(single_soft_would_own(e.classical)); // single soft would own
        CHECK(std::fabs(e.sigma_delta) < SECOND_SOLID_FLOOR);
        CHECK(!e.confirmed);                       // dual correctly refuses
        CHECK(e.suggested == Talent::None);
    }
    {
        auto a = alt_high_low(512);
        auto e = evidence(a.data(), a.size());
        CHECK(e.classical > 0.9f);
        CHECK(single_soft_would_own(e.classical));
        CHECK(std::fabs(e.sigma_delta) < SECOND_SOLID_FLOOR);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    {
        auto a = block_zigzag(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(e.classical > 0.5f);
        CHECK(single_soft_would_own(e.classical));
        CHECK(std::fabs(e.sigma_delta) < SECOND_SOLID_FLOOR);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    {
        auto a = moderate_local_disorder(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(single_soft_would_own(e.classical));
        // Most moderate local swaps stay under the solid floor
        if (std::fabs(e.sigma_delta) < SECOND_SOLID_FLOOR) {
            CHECK(!e.confirmed);
            CHECK(e.suggested == Talent::None);
        }
    }

    // ------------------------------------------------------------------
    // B. Dual-owned confirmation cases
    //    both axes solid → dual confirms; talent in range
    // ------------------------------------------------------------------
    {
        auto a = noisy_ramp_confirmed(1024, 42);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(std::isfinite(e.sigma_delta));
        CHECK(e.classical > CLASSICAL_OWNED_THRESH);
        CHECK(std::fabs(e.sigma_delta) >= SECOND_SOLID_FLOOR);
        CHECK(e.confirmed);                        // dual owns correctly
        CHECK((int)e.suggested >= 1 && (int)e.suggested <= 3);
    }

    // ------------------------------------------------------------------
    // C. Control cases still refuse (no false positive ownership)
    // ------------------------------------------------------------------
    {
        auto a = sorted(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    {
        auto a = reverse(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    {
        auto a = equal_heavy(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }

    // ------------------------------------------------------------------
    // D. Existing borderline_he remains finite and talent-ranged
    // ------------------------------------------------------------------
    {
        auto a = borderline_he(4096, 0xD00D);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(std::isfinite(e.sigma_delta));
        CHECK((int)e.suggested >= 0 && (int)e.suggested <= 3);
    }

    if (fails) {
        std::printf("%d FAIL(s) in borderline case library\n", fails);
        return 1;
    }
    std::printf("ALL GREEN (test_borderline_cases)\n");
    return 0;
}
