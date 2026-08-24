// Copyright (c) 2026 Heywood Geblomi
// Dual licensed: AGPLv3 (non-commercial) or Commercial License (see LICENSE)
//
// Parity test: relational facade must return bit-identical Evidence vs core.
#include "dual_residual_relational.hpp"
#include "generators.hpp"
#include <cstdio>
#include <cmath>
#include <vector>
#include <cstdint>

static bool same_evidence(const dual_residual::Evidence& a,
                          const dual_residual::Evidence& b) {
    if (a.confirmed != b.confirmed) return false;
    if (a.suggested != b.suggested) return false;
    if (std::fabs(a.sigma_delta - b.sigma_delta) > 1e-7f) return false;
    if (std::fabs(a.classical - b.classical) > 1e-7f) return false;
    return true;
}

int main() {
    int fails = 0;
    const size_t n = 4096;

    // Sorted control
    {
        auto a = dual_residual_test::sorted(n);
        auto core = dual_residual::evidence(a.data(), n);
        auto rel  = dual_residual::relational::evidence(a.data(), n);
        if (!same_evidence(core, rel)) {
            std::printf("FAIL sorted parity\n");
            ++fails;
        }
    }

    // Borderline HE
    {
        auto a = dual_residual_test::borderline_he(n);
        auto core = dual_residual::evidence(a.data(), n);
        auto rel  = dual_residual::relational::evidence(a.data(), n);
        if (!same_evidence(core, rel)) {
            std::printf("FAIL borderline_he parity\n");
            ++fails;
        }
    }

    // Pure random
    {
        auto a = dual_residual_test::pure_random(n);
        auto core = dual_residual::evidence(a.data(), n);
        auto rel  = dual_residual::relational::evidence(a.data(), n);
        if (!same_evidence(core, rel)) {
            std::printf("FAIL pure_random parity\n");
            ++fails;
        }
    }

    // Equal-heavy
    {
        auto a = dual_residual_test::equal_heavy(n);
        auto core = dual_residual::evidence(a.data(), n);
        auto rel  = dual_residual::relational::evidence(a.data(), n);
        if (!same_evidence(core, rel)) {
            std::printf("FAIL equal_heavy parity\n");
            ++fails;
        }
    }

    // Null / empty via relational (prod guards)
    {
        auto e0 = dual_residual::relational::evidence<int64_t>(nullptr, 0);
        if (e0.confirmed || e0.suggested != dual_residual::Talent::None) {
            std::printf("FAIL empty guard\n");
            ++fails;
        }
        auto e1 = dual_residual::relational::evidence<int64_t>(nullptr, 10);
        if (e1.confirmed || e1.suggested != dual_residual::Talent::None) {
            std::printf("FAIL null guard\n");
            ++fails;
        }
    }

    // Mapping field access (layout unchanged)
    {
        auto a = dual_residual_test::borderline_he(n, 99);
        auto e = dual_residual::relational::evidence(a.data(), n);
        (void)e.classical;    // from
        (void)e.sigma_delta;  // with
        (void)e.confirmed;    // to
        (void)e.suggested;    // in
    }

    if (fails == 0) {
        std::printf("ALL GREEN (test_relational_facade)\n");
        return 0;
    }
    std::printf("FAILED %d checks\n", fails);
    return 1;
}
