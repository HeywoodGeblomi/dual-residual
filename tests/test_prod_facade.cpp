/*
 * test_prod_facade.cpp — P0 production facade guards
 * Core dual_residual.hpp never modified. Decision table never touched.
 * g++ -std=c++17 -O2 -I. tests/test_prod_facade.cpp -o test_prod_facade
 * THE BEASTIE BOYZ 2026-08-23
 */
#include "dual_residual_prod.hpp"
#include <cassert>
#include <cstdio>
#include <cstdint>
#include <vector>
#include <numeric>

using dual_residual::Evidence;
using dual_residual::Talent;
using dual_residual::prod::evidence;
using dual_residual::prod::evidence_with_floor;

static int failures = 0;
#define CHECK(cond, msg) do { \
    if (!(cond)) { std::fprintf(stderr, "FAIL: %s\n", msg); ++failures; } \
} while (0)

static void test_null_pointer() {
    Evidence e = evidence<int32_t>(nullptr, 100);
    CHECK(!e.confirmed, "null+n>0 → not confirmed");
    CHECK(e.suggested == Talent::None, "null+n>0 → talent None");
    CHECK(e.classical == 0.f, "null+n>0 → classical 0");
    CHECK(e.sigma_delta == 0.f, "null+n>0 → sigma 0");
}

static void test_n_zero() {
    int32_t a[4] = {1, 2, 3, 4};
    Evidence e = evidence(a, 0);
    CHECK(!e.confirmed, "n=0 → not confirmed");
    CHECK(e.suggested == Talent::None, "n=0 → talent None");
}

static void test_n_one() {
    int32_t a[1] = {42};
    Evidence e = evidence(a, 1);
    CHECK(!e.confirmed, "n=1 → not confirmed");
    CHECK(e.suggested == Talent::None, "n=1 → talent None");
}

static void test_huge_n() {
    int32_t a[4] = {1, 2, 3, 4};
    // Do not actually allocate 1<<30; pass a fake large n with a valid small buffer.
    // Facade must reject before any dereference of out-of-range indices.
    Evidence e = evidence(a, (size_t(1) << 30) + 1);
    CHECK(!e.confirmed, "huge n → not confirmed");
    CHECK(e.suggested == Talent::None, "huge n → talent None");
}

static void test_sorted_matches_core() {
    std::vector<int32_t> a(4096);
    std::iota(a.begin(), a.end(), 0);
    Evidence facade = evidence(a.data(), a.size());
    Evidence core   = dual_residual::evidence(a.data(), a.size());
    CHECK(facade.confirmed == core.confirmed, "sorted confirmed match");
    CHECK(facade.suggested == core.suggested, "sorted talent match");
    CHECK(facade.classical == core.classical, "sorted classical match");
    CHECK(facade.sigma_delta == core.sigma_delta, "sorted sigma match");
    CHECK(!facade.confirmed, "sorted not dual_owned");
    CHECK(facade.suggested == Talent::None, "sorted talent None");
}

static void test_equal_heavy_matches_core() {
    std::vector<int32_t> a(4096, 42);
    Evidence facade = evidence(a.data(), a.size());
    Evidence core   = dual_residual::evidence(a.data(), a.size());
    CHECK(facade.confirmed == core.confirmed, "equal confirmed match");
    CHECK(facade.suggested == core.suggested, "equal talent match");
    CHECK(!facade.confirmed, "equal not dual_owned");
}

static void test_with_floor_opt_in() {
    std::vector<int32_t> a(4096);
    std::iota(a.begin(), a.end(), 0);
    // Opt-in floor path still applies guards and forwards
    Evidence e = evidence_with_floor(a.data(), a.size(), 0.005f);
    CHECK(!e.confirmed, "with_floor sorted not confirmed");
    CHECK(e.suggested == Talent::None, "with_floor sorted talent None");

    // null still safe under opt-in path
    Evidence bad = evidence_with_floor<int32_t>(nullptr, 50, 0.01f);
    CHECK(!bad.confirmed, "with_floor null safe");
    CHECK(bad.suggested == Talent::None, "with_floor null talent None");
}

int main() {
    test_null_pointer();
    test_n_zero();
    test_n_one();
    test_huge_n();
    test_sorted_matches_core();
    test_equal_heavy_matches_core();
    test_with_floor_opt_in();

    if (failures) {
        std::fprintf(stderr, "%d failure(s)\n", failures);
        return 1;
    }
    std::printf("test_prod_facade: ALL GREEN\n");
    return 0;
}
