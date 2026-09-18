// Table-lock assertion suite — dual-residual
// Pins the existing frozen decision table. Does not retune floors.
// Floors stay recited: 0.04 / 0.005 / 0.1 / 0.2.
// Compile:
//   g++ -std=c++17 -O2 -I. tests/test_table_lock.cpp -o test_table_lock
//   ./test_table_lock
// Expected: ALL GREEN (test_table_lock)
#include "../dual_residual.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cmath>
#include <cstdint>
#include <vector>

static int fails = 0;
#define CHECK(cond) do { \
    if (!(cond)) { \
        std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); \
        ++fails; \
    } \
} while (0)

static bool none_iff_unconfirmed(const dual_residual::Evidence& e) {
    return (e.suggested == dual_residual::Talent::None) == (!e.confirmed);
}

int main() {
    using namespace dual_residual;
    using namespace dual_residual_test;

    // ------------------------------------------------------------------
    // 0. Recited constants have not moved
    // ------------------------------------------------------------------
    CHECK(CLASSICAL_OWNED_THRESH == 0.04f);
    CHECK(SECOND_SOLID_FLOOR     == 0.005f);
    CHECK(TALENT2_SIGMA_THRESH   == 0.1f);
    CHECK(TALENT3_CLASSICAL      == 0.2f);
    CHECK(SAMPLE_SIZE            == 512);

    // ------------------------------------------------------------------
    // 1. Exact-floor cells on dual_confirm / compute_talent
    //    Mixed inequalities: C > 0.04, |σ_Δ| ≥ 0.005, |σ_Δ| > 0.1, C > 0.2
    // ------------------------------------------------------------------
    {
        // second-solid cut: ≥ 0.005 owns when classical already owned
        CHECK(detail::dual_confirm(true,  0.005f)    == true);
        CHECK(detail::dual_confirm(true, -0.005f)    == true);  // sign
        CHECK(detail::dual_confirm(true,  0.004999f) == false);
        CHECK(detail::dual_confirm(true, -0.004999f) == false);
        CHECK(detail::dual_confirm(false, 0.5f)      == false);
        CHECK(detail::dual_confirm(false, 0.005f)    == false);

        // classical cut lives in evidence(): C > 0.04, not ≥
        CHECK((0.04f  > CLASSICAL_OWNED_THRESH) == false);
        CHECK((0.0401f > CLASSICAL_OWNED_THRESH) == true);
        CHECK(detail::dual_confirm(0.04f  > CLASSICAL_OWNED_THRESH, 0.05f) == false);
        CHECK(detail::dual_confirm(0.0401f > CLASSICAL_OWNED_THRESH, 0.005f) == true);

        // not owned → None regardless of scores
        CHECK(detail::compute_talent(0.5f, 0.2f, false) == Talent::None);
        CHECK(detail::compute_talent(0.04f, 0.05f,
            detail::dual_confirm(0.04f > CLASSICAL_OWNED_THRESH, 0.05f)) == Talent::None);

        // |σ_Δ| == 0.1 → not T2 (strict >). C=0.1 ≤ 0.2 → T1
        CHECK(detail::compute_talent(0.1f,  0.1f,    true) == Talent::T1);
        CHECK(detail::compute_talent(0.1f, -0.1f,    true) == Talent::T1);
        CHECK(detail::compute_talent(0.1f,  0.1001f, true) == Talent::T2);
        CHECK(detail::compute_talent(0.1f, -0.15f,   true) == Talent::T2);

        // C == 0.2 and 0.005 ≤ |σ_Δ| ≤ 0.1 → T1, not T3 (strict >)
        CHECK(detail::compute_talent(0.2f,    0.05f, true) == Talent::T1);
        CHECK(detail::compute_talent(0.2001f, 0.05f, true) == Talent::T3);

        // just-owned T1 cell: C barely above 0.04, |σ_Δ| at floor
        CHECK(detail::compute_talent(0.0401f, 0.005f, true) == Talent::T1);
    }

    // ------------------------------------------------------------------
    // 2. Sign symmetry on the table
    // ------------------------------------------------------------------
    {
        CHECK(detail::compute_talent(0.15f,  0.2f, true) ==
              detail::compute_talent(0.15f, -0.2f, true));
        CHECK(detail::compute_talent(0.25f,  0.05f, true) ==
              detail::compute_talent(0.25f, -0.05f, true));
        CHECK(detail::dual_confirm(true, 0.01f) == detail::dual_confirm(true, -0.01f));
    }

    // ------------------------------------------------------------------
    // 3. Early returns on the core header (not only the prod facade)
    // ------------------------------------------------------------------
    {
        Evidence z = evidence<int64_t>(nullptr, 0);
        CHECK(!z.confirmed);
        CHECK(z.suggested == Talent::None);
        CHECK(z.classical == 0.f);
        CHECK(z.sigma_delta == 0.f);
        CHECK(none_iff_unconfirmed(z));
    }
    {
        int64_t two[2] = {1, 2};
        auto e = evidence(two, 2);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(none_iff_unconfirmed(e));
    }
    {
        int64_t three[3] = {1, 2, 3};
        auto e = evidence(three, 3);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(none_iff_unconfirmed(e));
    }
    {
        auto a = all_ties(64);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(e.classical == 0.f);
        CHECK(none_iff_unconfirmed(e));
    }
    {
        // max_events < 4 is an early return on the core path
        auto a = sorted(32);
        auto e = evidence(a.data(), a.size(), /*max_events=*/3);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(none_iff_unconfirmed(e));
    }

    // ------------------------------------------------------------------
    // 4. Length cliff: n=1024 stride=1 vs n=1025 stride=n/512
    //    Controls stay None on both sides. Do not "fix" stride.
    // ------------------------------------------------------------------
    {
        for (size_t n : {size_t(1024), size_t(1025)}) {
            auto s = sorted(n);
            auto e = evidence(s.data(), s.size());
            CHECK(!e.confirmed);
            CHECK(e.suggested == Talent::None);
            CHECK(none_iff_unconfirmed(e));

            auto r = reverse(n);
            e = evidence(r.data(), r.size());
            CHECK(!e.confirmed);
            CHECK(e.suggested == Talent::None);
            CHECK(none_iff_unconfirmed(e));

            auto q = equal_heavy(n);
            e = evidence(q.data(), q.size());
            CHECK(!e.confirmed);
            CHECK(e.suggested == Talent::None);
            CHECK(none_iff_unconfirmed(e));
        }
    }

    // ------------------------------------------------------------------
    // 5. End-to-end goldens through evidence() — measured, not hunted
    // ------------------------------------------------------------------
    {
        // T3-forcing confirm path
        auto a = noisy_ramp_confirmed(1024, 42);
        auto e = evidence(a.data(), a.size());
        CHECK(e.confirmed);
        CHECK(e.suggested == Talent::T3);
        CHECK(std::fabs(e.classical   - 0.962891f) < 1e-5f);
        CHECK(std::fabs(e.sigma_delta + 0.092215f) < 1e-4f);
        CHECK(none_iff_unconfirmed(e));
        CHECK(detail::compute_talent(e.classical, e.sigma_delta, e.confirmed) == e.suggested);
    }
    {
        // T2-forcing confirm path
        auto a = biased_walk_t2(1024, 8);
        auto e = evidence(a.data(), a.size());
        CHECK(e.confirmed);
        CHECK(e.suggested == Talent::T2);
        CHECK(std::fabs(e.classical   - 0.7832f) < 1e-3f);
        CHECK(std::fabs(e.sigma_delta - 0.1897f) < 1e-3f);
        CHECK(none_iff_unconfirmed(e));
        CHECK(detail::compute_talent(e.classical, e.sigma_delta, e.confirmed) == e.suggested);
    }
    {
        // Hard pin: drop the previous soft-if
        auto a = moderate_local_disorder(1024, 0xB0B0);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(std::fabs(e.classical - 1.0f) < 1e-6f);
        CHECK(std::fabs(e.sigma_delta) < SECOND_SOLID_FLOOR);
        CHECK(none_iff_unconfirmed(e));
    }
    {
        auto a = borderline_he(4096, 0xD00D);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(std::isfinite(e.classical));
        CHECK(std::isfinite(e.sigma_delta));
        CHECK(none_iff_unconfirmed(e));
    }
    {
        auto a = borderline_he(2048, 0xBEEF);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
        CHECK(none_iff_unconfirmed(e));
    }

    if (fails) {
        std::printf("%d FAIL(s) in table-lock suite\n", fails);
        return 1;
    }
    std::printf("ALL GREEN (test_table_lock)\n");
    return 0;
}
