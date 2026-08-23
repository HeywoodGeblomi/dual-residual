// Unit tests for dual_residual::evidence
// Compile: g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence && ./test_evidence
#include "../dual_residual.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>

static int fails = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); ++fails; } } while(0)

int main() {
    using namespace dual_residual;
    using namespace dual_residual_test;

    // Controls: sorted → not dual_owned
    {
        auto a = sorted(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Controls: reverse → not dual_owned (monotonic)
    {
        auto a = reverse(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Controls: equal_heavy → low classical, not dual_owned
    {
        auto a = equal_heavy(1024);
        auto e = evidence(a.data(), a.size());
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Empty / short
    {
        int64_t one = 1;
        auto e = evidence(&one, 1);
        CHECK(!e.confirmed);
        CHECK(e.suggested == Talent::None);
    }
    // Talent decision table (synthetic)
    {
        CHECK(detail::compute_talent(0.5f, 0.2f, false) == Talent::None);
        CHECK(detail::compute_talent(0.1f, 0.15f, true) == Talent::T2);
        CHECK(detail::compute_talent(0.25f, 0.05f, true) == Talent::T3);
        CHECK(detail::compute_talent(0.1f, 0.05f, true) == Talent::T1);
    }
    // Borderline HE — finite metrics, talent in range
    {
        auto a = borderline_he(4096, 0xD00D);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(std::isfinite(e.sigma_delta));
        CHECK((int)e.suggested >= 0 && (int)e.suggested <= 3);
    }
    // Pure random: classical high
    {
        auto a = pure_random(2048);
        auto e = evidence(a.data(), a.size());
        CHECK(std::isfinite(e.classical));
        CHECK(e.classical > 0.f);
    }

    if (fails) {
        std::printf("%d FAIL(s)\n", fails);
        return 1;
    }
    std::printf("ALL GREEN (test_evidence)\n");
    return 0;
}
