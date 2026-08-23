// Parity oracle: Evidence construction must be deterministic and match
// the locked event-parity definition.
// Compile: g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle && ./test_parity_oracle
#include "../dual_residual.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cmath>
#include <vector>

static int fails = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); ++fails; } } while(0)

int main() {
    using namespace dual_residual;
    using namespace dual_residual_test;

    // Determinism: same input → same Evidence
    {
        auto a = borderline_he(2048, 0xBEEF);
        auto e1 = evidence(a.data(), a.size());
        auto e2 = evidence(a.data(), a.size());
        CHECK(e1.confirmed == e2.confirmed);
        CHECK(e1.suggested == e2.suggested);
        CHECK(std::fabs(e1.classical - e2.classical) < 1e-6f);
        CHECK(std::fabs(e1.sigma_delta - e2.sigma_delta) < 1e-6f);
    }
    // Sorted: monotonic polarity → not dual_owned
    {
        auto a = sorted(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Reverse: same
    {
        auto a = reverse(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Equal-heavy
    {
        auto a = equal_heavy(512);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // dual_confirm floor
    {
        CHECK(detail::dual_confirm(true, 0.01f) == true);
        CHECK(detail::dual_confirm(true, 0.001f) == false);
        CHECK(detail::dual_confirm(false, 0.5f) == false);
    }
    // Talent table exact
    {
        CHECK(detail::compute_talent(0.5f, 0.2f, false) == Talent::None);
        CHECK(detail::compute_talent(0.1f, 0.15f, true) == Talent::T2);
        CHECK(detail::compute_talent(0.25f, 0.05f, true) == Talent::T3);
        CHECK(detail::compute_talent(0.1f, 0.05f, true) == Talent::T1);
    }

    if (fails) {
        std::printf("%d FAIL(s)\n", fails);
        return 1;
    }
    std::printf("ALL GREEN (test_parity_oracle)\n");
    return 0;
}
