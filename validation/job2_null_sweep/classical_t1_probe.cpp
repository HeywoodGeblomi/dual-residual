// Confirms the classical formula and whether evidence() can emit T1.
// Does not modify the locked header. Not a real-data result.
//
//   g++ -std=c++17 -O2 -Wall -Wextra -I. validation/job2_null_sweep/classical_t1_probe.cpp -o /tmp/job2_classical_t1
//   /tmp/job2_classical_t1

#include "dual_residual.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

namespace {

float ratio_classical(int nnz, int tlen) {
    return static_cast<float>(nnz) / static_cast<float>(tlen);
}

float knuth_classical(int zeros, int tlen) {
    return 1.f - static_cast<float>(zeros) / static_cast<float>(tlen);
}

void print_window(int tlen) {
    int z_lo = -1;
    int z_hi = -1;
    float c_at_lo = 0.f;
    float c_at_hi = 0.f;
    for (int z = 0; z <= tlen; ++z) {
        const float c = ratio_classical(tlen - z, tlen);
        const bool owned_band = c > dual_residual::CLASSICAL_OWNED_THRESH;
        const bool not_t3 = !(c > dual_residual::TALENT3_CLASSICAL);
        if (owned_band && not_t3) {
            if (z_lo < 0) {
                z_lo = z;
                c_at_lo = c;
            }
            z_hi = z;
            c_at_hi = c;
        }
    }
    if (z_lo < 0) {
        std::printf("T=%d  no integer tie count puts classical in (0.04, 0.2]\n", tlen);
        return;
    }
    std::printf("T=%d  tie count z in [%d, %d]  tie rate [%.6f, %.6f]  "
                "classical [%.8f, %.8f]\n",
                tlen, z_lo, z_hi,
                static_cast<double>(z_lo) / tlen,
                static_cast<double>(z_hi) / tlen,
                static_cast<double>(c_at_hi),
                static_cast<double>(c_at_lo));
    const float c_just_below = ratio_classical(tlen - (z_lo - 1), tlen);
    const float c_just_above = ratio_classical(tlen - (z_hi + 1), tlen);
    std::printf("         just outside: z=%d classical=%.8f (above 0.2)  "
                "z=%d classical=%.8f (not above 0.04)\n",
                z_lo - 1, static_cast<double>(c_just_below),
                z_hi + 1, static_cast<double>(c_just_above));
    // Knuth expression can differ by an ulp from the ratio the core stores.
    int knuth_mismatch = 0;
    float max_gap = 0.f;
    for (int z = 0; z <= tlen; ++z) {
        const float ratio = ratio_classical(tlen - z, tlen);
        const float knuth = knuth_classical(z, tlen);
        const float gap = std::fabs(ratio - knuth);
        if (gap > max_gap) max_gap = gap;
        if (ratio != knuth) ++knuth_mismatch;
    }
    std::printf("         float32 (T-z)/T vs 1-z/T mismatches %d / %d, max abs gap %.3e\n",
                knuth_mismatch, tlen + 1, static_cast<double>(max_gap));
}

struct Built {
    std::vector<int64_t> a;
    int zeros = 0;
    int tlen = 0;
};

Built build_from_signs(const std::vector<int>& signs) {
    Built b;
    b.tlen = static_cast<int>(signs.size());
    b.a.assign(signs.size() + 1, 0);
    for (size_t i = 0; i < signs.size(); ++i) {
        if (signs[i] == 0) ++b.zeros;
        if (signs[i] > 0) b.a[i + 1] = b.a[i] + 1;
        else if (signs[i] < 0) b.a[i + 1] = b.a[i] - 1;
        else b.a[i + 1] = b.a[i];
    }
    return b;
}

// Start positive. Each leave is 0, except leaves whose index is in `neg`.
// Extra zeros after each leave raise the tie rate without adding crossings.
std::vector<int> signs_negative_leaves(int tlen, int n_leaves,
                                      const std::vector<int>& neg, int pad) {
    std::vector<int> s;
    s.reserve(static_cast<size_t>(tlen));
    for (int leave = 0; leave < n_leaves && static_cast<int>(s.size()) < tlen; ++leave) {
        s.push_back(1);
        bool is_neg = false;
        for (int slot : neg) {
            if (slot == leave) is_neg = true;
        }
        s.push_back(is_neg ? -1 : 0);
        for (int k = 0; k < pad && static_cast<int>(s.size()) < tlen; ++k) s.push_back(0);
    }
    while (static_cast<int>(s.size()) < tlen) s.push_back(0);
    if (static_cast<int>(s.size()) > tlen) s.resize(static_cast<size_t>(tlen));
    return s;
}

}  // namespace

int main() {
    std::printf("classical formula window on the sign-stream lengths the core uses\n");
    for (int tlen : {63, 255, 511, 512}) print_window(tlen);

    std::printf("\nconstructed evidence() search for T1\n");
    int found = 0;
    for (int n : {64, 256, 512, 513}) {
        const size_t stride = (n > 1024) ? (n / dual_residual::SAMPLE_SIZE) : 1;
        const int tlen = static_cast<int>(std::min(
            (n - 1) / (stride < 1 ? 1 : stride),
            static_cast<size_t>(DUAL_RESIDUAL_MAX_EVENTS)));
        if (stride != 1) continue;
        for (int n_leaves = 4; n_leaves <= 24; ++n_leaves) {
            for (int pad = 0; pad <= 8; ++pad) {
                for (int neg_a = 0; neg_a < n_leaves; ++neg_a) {
                    for (int neg_b = neg_a; neg_b < n_leaves; ++neg_b) {
                        std::vector<int> neg_slots;
                        neg_slots.push_back(neg_a);
                        if (neg_b != neg_a) neg_slots.push_back(neg_b);
                        auto signs = signs_negative_leaves(tlen, n_leaves, neg_slots, pad);
                        if (static_cast<int>(signs.size()) + 1 != n) continue;
                        Built built = build_from_signs(signs);
                        auto e = dual_residual::evidence(built.a.data(), built.a.size());
                        const float expect = ratio_classical(built.tlen - built.zeros, built.tlen);
                        if (e.classical != expect) {
                            std::printf("IDENTITY FAIL n=%d classical=%a expect=%a\n",
                                        n, static_cast<double>(e.classical),
                                        static_cast<double>(expect));
                            return 1;
                        }
                        if (e.suggested == dual_residual::Talent::T1) {
                            const double tie = static_cast<double>(built.zeros) / built.tlen;
                            std::printf("T1 n=%d T=%d tie=%.6f classical=%.8f sigma=% .8f "
                                        "leaves=%d neg=%d,%d pad=%d\n",
                                        n, built.tlen, tie,
                                        static_cast<double>(e.classical),
                                        static_cast<double>(e.sigma_delta),
                                        n_leaves, neg_a, neg_b, pad);
                            ++found;
                            goto next_n;
                        }
                    }
                }
            }
        }
        std::printf("no T1 at stride-1 n=%d within this pad/leave grid\n", n);
    next_n:
        ;
    }
    std::printf("constructed T1 hits: %d\n", found);
    return found > 0 ? 0 : 2;
}
