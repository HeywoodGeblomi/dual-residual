// Job 2 — Monte Carlo NULL half only.
// Links the locked header. Does not modify it, the decision table,
// the constants 0.04 / 0.005 / 0.1 / 0.2, or either facade.
// No third signal is computed for a decision. Zero-rate, stride,
// event count, and window coverage are diagnostics.
//
// RW step selection (tie rates only, applied by select_rw_step.py
// to the pilot CSV before the official grid is locked):
//   score(q) = (tie_1024 - 0.13)^2 + (tie_4096 - 0.04)^2 + (tie_16384 - 0.02)^2
//   Those three targets are reported MIT-BIH contract figures, used
//   only as a tie-rate band. This program does not read ECG.
//   Prefer q whose official-N tie rates all lie in [0.015, 0.20].
//   Break score ties toward the smaller q.
//   Official rw_q steps = winner and its two candidate neighbors.
// Gauss steps 0.5, 1, 2 and unif alphabets 2, 4, 8 are fixed a priori.
//
// Build from the repo root:
//   g++ -std=c++17 -O2 -Wall -Wextra -I. validation/job2_null_sweep/sweep_null.cpp -o /tmp/job2_sweep_null

#include "dual_residual.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {

constexpr uint64_t kMasterSeed = 0xD0A15EED20261123ull;
constexpr int kBurnIn = 4096;
constexpr int kOfficialTrials = 4000;
constexpr int kPilotTrials = 500;

constexpr size_t kOfficialN[] = {64, 256, 1024, 4096, 16384};
constexpr size_t kCoverageN[] = {
    64, 256, 512, 513, 514, 768, 1024, 1025, 2048, 4096, 16384};

enum Kind { kGauss = 0, kUnif = 1, kRw = 2 };

struct Spec {
    const char* family;
    const char* step_label;
    double step;
    Kind kind;
};

// Official grid. rw_q steps are the tie-rate rule's winner (0.3) and its
// two candidate neighbors (0.2, 0.35). See select_rw_step.py.
const Spec kOfficial[] = {
    {"gauss_q", "0.5", 0.5, kGauss},
    {"gauss_q", "1", 1.0, kGauss},
    {"gauss_q", "2", 2.0, kGauss},
    {"unif_k", "2", 2.0, kUnif},
    {"unif_k", "4", 4.0, kUnif},
    {"unif_k", "8", 8.0, kUnif},
    {"rw_q", "0.2", 0.2, kRw},
    {"rw_q", "0.3", 0.3, kRw},  // focus: tie-rate SSE winner
    {"rw_q", "0.35", 0.35, kRw},
};

const double kPilotRw[] = {
    0.2, 0.3, 0.35, 0.4, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0};

struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed) {}
    uint64_t next() {
        s += 0x9E3779B97F4A7C15ull;
        uint64_t z = s;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
        return z ^ (z >> 31);
    }
    // (0, 1]
    double u01() {
        return static_cast<double>((next() >> 11) + 1ull) / 9007199254740992.0;
    }
    double normal() {
        const double u1 = u01();
        const double u2 = u01();
        constexpr double kTwoPi = 6.28318530717958647692;
        return std::sqrt(-2.0 * std::log(u1)) * std::cos(kTwoPi * u2);
    }
};

uint64_t mix(uint64_t x) {
    x += 0x9E3779B97F4A7C15ull;
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull;
    x = (x ^ (x >> 27)) * 0x94D049BB133111EBull;
    return x ^ (x >> 31);
}

uint64_t trial_seed(uint32_t fam_tag, uint32_t step_milli, uint32_t n, uint32_t trial) {
    uint64_t x = kMasterSeed;
    x = mix(x ^ fam_tag);
    x = mix(x ^ step_milli);
    x = mix(x ^ (n * 0x9E3779B9u));
    x = mix(x ^ trial);
    return x;
}

uint32_t step_milli(double step) {
    return static_cast<uint32_t>(std::llround(step * 1000.0));
}

uint32_t fam_tag(const char* family) {
    // Stable small tags. Not a hash of a decision.
    if (std::strcmp(family, "gauss_q") == 0) return 1;
    if (std::strcmp(family, "unif_k") == 0) return 2;
    if (std::strcmp(family, "rw_q") == 0) return 3;
    return 9;
}

void fill_series(Rng& rng, Kind kind, double step, int64_t* a, size_t n) {
    if (kind == kGauss) {
        for (size_t i = 0; i < n; ++i) a[i] = std::llround(rng.normal() / step);
        return;
    }
    if (kind == kUnif) {
        const auto k = static_cast<uint64_t>(std::llround(step));
        for (size_t i = 0; i < n; ++i) a[i] = static_cast<int64_t>(rng.next() % k);
        return;
    }
    double s = 0.0;
    for (int i = 0; i < kBurnIn; ++i) s += rng.normal();
    for (size_t i = 0; i < n; ++i) {
        s += rng.normal();
        a[i] = std::llround(s / step);
    }
}

size_t core_stride(size_t n) {
    size_t stride = (n > 1024) ? (n / dual_residual::SAMPLE_SIZE) : 1;
    if (stride < 1) stride = 1;
    return stride;
}

int count_crossings(const float* stream, int tlen) {
    if (tlen < 1) return 0;
    int ne = 0;
    bool above = stream[0] > 0.f;
    for (int t = 1; t < tlen && ne < DUAL_RESIDUAL_MAX_EVENTS; ++t) {
        const bool now = stream[t] > 0.f;
        if (now != above) {
            ++ne;
            above = now;
        }
    }
    return ne;
}

const char* talent_name(dual_residual::Talent t) {
    using dual_residual::Talent;
    switch (t) {
        case Talent::None: return "None";
        case Talent::T1: return "T1";
        case Talent::T2: return "T2";
        case Talent::T3: return "T3";
    }
    return "?";
}

// ---------------------------------------------------------------------------
// Coverage probe. The element type records every index the core compares.
// evidence() is called unmodified; operator> / operator< are the only
// reads the polarity loop performs.
// ---------------------------------------------------------------------------

struct Tap {
    volatile uint8_t* seen;
    size_t idx;
    int val;
    friend bool operator>(const Tap& x, const Tap& y) {
        x.seen[x.idx] = 1;
        y.seen[y.idx] = 1;
        return x.val > y.val;
    }
    friend bool operator<(const Tap& x, const Tap& y) {
        x.seen[x.idx] = 1;
        y.seen[y.idx] = 1;
        return x.val < y.val;
    }
};

struct Coverage {
    size_t n = 0;
    size_t stride = 0;
    int tlen = 0;
    size_t last_index = 0;
    size_t samples_touched = 0;
    double fraction_window_read = 0;
    double fraction_samples_touched = 0;
    bool cap_binds = false;
    bool prefix_truncation = false;
    bool matches_lattice = false;
};

Coverage probe_coverage(size_t n) {
    std::vector<uint8_t> seen(n, 0);
    std::vector<Tap> a(n);
    for (size_t i = 0; i < n; ++i) {
        a[i].seen = seen.data();
        a[i].idx = i;
        a[i].val = static_cast<int>(i);  // strictly increasing; values do not affect the index set
    }
    const auto e = dual_residual::evidence(a.data(), n);
    (void)e;

    Coverage c;
    c.n = n;
    c.stride = core_stride(n);
    size_t touched = 0;
    size_t last = 0;
    bool any = false;
    for (size_t i = 0; i < n; ++i) {
        if (seen[i]) {
            ++touched;
            last = i;
            any = true;
        }
    }
    c.samples_touched = touched;
    c.last_index = any ? last : 0;

    float stream[DUAL_RESIDUAL_MAX_EVENTS];
    c.tlen = dual_residual::detail::polarity_stream_strided(
        a.data(), n, c.stride, stream, DUAL_RESIDUAL_MAX_EVENTS);
    // polarity_stream_strided walks the same pairs. Touch set must be unchanged
    // in extent: call it on a fresh buffer and require the same indices.
    std::vector<uint8_t> seen2(n, 0);
    for (size_t i = 0; i < n; ++i) a[i].seen = seen2.data();
    const int tlen2 = dual_residual::detail::polarity_stream_strided(
        a.data(), n, c.stride, stream, DUAL_RESIDUAL_MAX_EVENTS);
    if (tlen2 != c.tlen) {
        std::fprintf(stderr, "tlen mismatch n=%zu %d vs %d\n", n, c.tlen, tlen2);
        std::exit(1);
    }
    if (seen != seen2) {
        std::fprintf(stderr, "evidence() and polarity_stream_strided touch different indices at n=%zu\n", n);
        std::exit(1);
    }

    const size_t uncapped = (n - 1) / c.stride;
    c.cap_binds = uncapped > static_cast<size_t>(DUAL_RESIDUAL_MAX_EVENTS);
    c.fraction_window_read = static_cast<double>(c.last_index + 1) / static_cast<double>(n);
    c.fraction_samples_touched =
        static_cast<double>(c.samples_touched) / static_cast<double>(n);
    c.prefix_truncation = (c.stride == 1 && c.last_index + 1 < n);

    bool lattice = true;
    for (size_t i = 0; i < n; ++i) {
        const bool expect = (i % c.stride == 0) && (i <= c.last_index);
        if (static_cast<bool>(seen[i]) != expect) lattice = false;
    }
    // Expected last index from the loop: Tlen * stride, with Tlen = min(cap, floor((n-1)/stride)).
    const size_t expect_tlen = std::min(uncapped, static_cast<size_t>(DUAL_RESIDUAL_MAX_EVENTS));
    const size_t expect_last = expect_tlen * c.stride;
    if (static_cast<size_t>(c.tlen) != expect_tlen || c.last_index != expect_last) lattice = false;
    c.matches_lattice = lattice;
    return c;
}

int cmd_coverage(const char* path) {
    FILE* fp = std::fopen(path, "w");
    if (!fp) {
        std::perror(path);
        return 1;
    }
    std::fprintf(fp,
                 "n,stride,tlen,last_index,samples_touched,fraction_window_read,"
                 "fraction_samples_touched,cap_binds,prefix_truncation,matches_lattice\n");
    std::printf("n,stride,tlen,last,touched,fraction_window_read,fraction_samples_touched,cap,prefix_truncation,lattice_ok\n");
    int bad = 0;
    for (size_t n : kCoverageN) {
        const Coverage c = probe_coverage(n);
        std::fprintf(fp, "%zu,%zu,%d,%zu,%zu,%.10f,%.10f,%d,%d,%d\n",
                     c.n, c.stride, c.tlen, c.last_index, c.samples_touched,
                     c.fraction_window_read, c.fraction_samples_touched,
                     c.cap_binds ? 1 : 0, c.prefix_truncation ? 1 : 0,
                     c.matches_lattice ? 1 : 0);
        std::printf("%zu,%zu,%d,%zu,%zu,%.10f,%.10f,%d,%d,%d\n",
                    c.n, c.stride, c.tlen, c.last_index, c.samples_touched,
                    c.fraction_window_read, c.fraction_samples_touched,
                    c.cap_binds ? 1 : 0, c.prefix_truncation ? 1 : 0,
                    c.matches_lattice ? 1 : 0);
        if (!c.matches_lattice) ++bad;
    }
    std::fclose(fp);
    if (bad) {
        std::fprintf(stderr, "coverage probe: %d lengths did not match the lattice formula\n", bad);
        return 1;
    }
    return 0;
}

struct TrialDiag {
    int tlen = 0;
    int n_zeros = 0;
    int n_crossings = 0;
    int n_events = 0;
    float classical = 0.f;
    float sigma = 0.f;
    bool confirmed = false;
    dual_residual::Talent talent = dual_residual::Talent::None;
    bool classical_gt = false;
    bool sigma_gt = false;
    bool sigma_ge = false;
    bool sigma_eq_0 = false;
};

TrialDiag run_one(const int64_t* a, size_t n) {
    const auto e = dual_residual::evidence(a, n);
    const size_t stride = core_stride(n);
    float stream[DUAL_RESIDUAL_MAX_EVENTS];
    const int tlen = dual_residual::detail::polarity_stream_strided(
        a, n, stride, stream, DUAL_RESIDUAL_MAX_EVENTS);
    if (tlen < 4) {
        std::fprintf(stderr, "unexpected short stream n=%zu tlen=%d\n", n, tlen);
        std::exit(1);
    }
    float sum = 0.f;
    int zeros = 0;
    for (int i = 0; i < tlen; ++i) {
        sum += std::fabs(stream[i]);
        if (stream[i] == 0.f) ++zeros;
    }
    const float classical = sum / static_cast<float>(tlen);
    const auto sig = dual_residual::detail::compute(stream, tlen, 0.f);
    const int crossings = count_crossings(stream, tlen);
    if (classical != e.classical || sig.delta != e.sigma_delta) {
        std::fprintf(stderr, "diagnostic diverged from evidence() n=%zu\n", n);
        std::exit(1);
    }
    if (crossings < 4) {
        if (sig.n_events != 0 || sig.delta != 0.f) {
            std::fprintf(stderr, "early-return sigma mismatch n=%zu\n", n);
            std::exit(1);
        }
    } else if (sig.n_events != (crossings + 1) / 2) {
        std::fprintf(stderr, "n_events mismatch n=%zu crossings=%d n_events=%d\n",
                     n, crossings, sig.n_events);
        std::exit(1);
    }
    const bool confirmed = e.confirmed;
    const bool none = e.suggested == dual_residual::Talent::None;
    if (confirmed == none) {
        std::fprintf(stderr, "talent/confirmed mismatch n=%zu\n", n);
        std::exit(1);
    }
    const bool sigma_ge = !(std::fabs(e.sigma_delta) < dual_residual::SECOND_SOLID_FLOOR);
    const bool classical_gt = e.classical > dual_residual::CLASSICAL_OWNED_THRESH;
    if (confirmed != (classical_gt && sigma_ge)) {
        std::fprintf(stderr, "confirm predicate mismatch n=%zu\n", n);
        std::exit(1);
    }
    if (e.sigma_delta == 0.f && confirmed) {
        std::fprintf(stderr, "identical-zero sigma was confirmed n=%zu\n", n);
        std::exit(1);
    }
    if (!confirmed) {
        if (e.suggested != dual_residual::Talent::None) {
            std::fprintf(stderr, "unconfirmed talent n=%zu\n", n);
            std::exit(1);
        }
    } else if (std::fabs(e.sigma_delta) > dual_residual::TALENT2_SIGMA_THRESH) {
        if (e.suggested != dual_residual::Talent::T2) {
            std::fprintf(stderr, "T2 mismatch n=%zu\n", n);
            std::exit(1);
        }
    } else if (e.classical > dual_residual::TALENT3_CLASSICAL) {
        if (e.suggested != dual_residual::Talent::T3) {
            std::fprintf(stderr, "T3 mismatch n=%zu\n", n);
            std::exit(1);
        }
    } else if (e.suggested != dual_residual::Talent::T1) {
        std::fprintf(stderr, "T1 mismatch n=%zu\n", n);
        std::exit(1);
    }

    TrialDiag d;
    d.tlen = tlen;
    d.n_zeros = zeros;
    d.n_crossings = crossings;
    d.n_events = sig.n_events;
    d.classical = e.classical;
    d.sigma = e.sigma_delta;
    d.confirmed = confirmed;
    d.talent = e.suggested;
    d.classical_gt = e.classical > dual_residual::CLASSICAL_OWNED_THRESH;
    d.sigma_gt = std::fabs(e.sigma_delta) > dual_residual::SECOND_SOLID_FLOOR;
    d.sigma_ge = !(std::fabs(e.sigma_delta) < dual_residual::SECOND_SOLID_FLOOR);
    d.sigma_eq_0 = (e.sigma_delta == 0.f);
    return d;
}

void check_locked_constants() {
    using namespace dual_residual;
    if (CLASSICAL_OWNED_THRESH != 0.04f || SECOND_SOLID_FLOOR != 0.005f ||
        TALENT2_SIGMA_THRESH != 0.1f || TALENT3_CLASSICAL != 0.2f ||
        SAMPLE_SIZE != 512 || DUAL_RESIDUAL_MAX_EVENTS != 512) {
        std::fprintf(stderr, "locked constants are not 0.04/0.005/0.1/0.2 with caps 512\n");
        std::exit(1);
    }
}

int cmd_pilot(const char* path) {
    FILE* fp = std::fopen(path, "w");
    if (!fp) {
        std::perror(path);
        return 1;
    }
    std::fprintf(fp,
                 "family,step,n,trials,stride,tlen,fraction_window_read,"
                 "fraction_samples_touched,mean_zero_rate,mean_n_events,mean_n_crossings\n");

    std::vector<Spec> specs;
    for (const auto& s : kOfficial) {
        if (s.kind != kRw) specs.push_back(s);
    }
    for (double q : kPilotRw) {
        Spec s;
        s.family = "rw_q";
        s.step_label = nullptr;
        s.step = q;
        s.kind = kRw;
        specs.push_back(s);
    }

    std::vector<int64_t> buf(*std::max_element(std::begin(kOfficialN), std::end(kOfficialN)));
    char label[32];
    for (const Spec& spec : specs) {
        const char* step_label = spec.step_label;
        if (!step_label) {
            std::snprintf(label, sizeof(label), "%.4g", spec.step);
            step_label = label;
        }
        for (size_t n : kOfficialN) {
            const Coverage cov = probe_coverage(n);
            if (!cov.matches_lattice) {
                std::fprintf(stderr, "lattice mismatch during pilot n=%zu\n", n);
                return 1;
            }
            double zsum = 0, esum = 0, csum = 0;
            for (int trial = 0; trial < kPilotTrials; ++trial) {
                Rng rng(trial_seed(fam_tag(spec.family), step_milli(spec.step),
                                   static_cast<uint32_t>(n), static_cast<uint32_t>(trial)));
                fill_series(rng, spec.kind, spec.step, buf.data(), n);
                const TrialDiag d = run_one(buf.data(), n);
                zsum += static_cast<double>(d.n_zeros) / static_cast<double>(d.tlen);
                esum += d.n_events;
                csum += d.n_crossings;
            }
            const double inv = 1.0 / static_cast<double>(kPilotTrials);
            std::fprintf(fp, "%s,%s,%zu,%d,%zu,%d,%.10f,%.10f,%.6f,%.4f,%.4f\n",
                         spec.family, step_label, n, kPilotTrials, cov.stride, cov.tlen,
                         cov.fraction_window_read, cov.fraction_samples_touched,
                         zsum * inv, esum * inv, csum * inv);
            std::printf("pilot %s step=%s N=%zu tie=%.4f events=%.2f\n",
                        spec.family, step_label, n, zsum * inv, esum * inv);
            std::fflush(stdout);
        }
    }
    std::fclose(fp);
    return 0;
}

int cmd_run(const char* path, int n_trials) {
    for (const auto& s : kOfficial) {
        if (s.step <= 0) {
            std::fprintf(stderr, "official step not locked: %s\n", s.family);
            return 1;
        }
    }
    FILE* fp = std::fopen(path, "w");
    if (!fp) {
        std::perror(path);
        return 1;
    }
    static char iobuf[1 << 20];
    std::setvbuf(fp, iobuf, _IOFBF, sizeof iobuf);
    std::fprintf(fp,
                 "family,step,n,trial,seed,stride,tlen,last_index,fraction_window_read,"
                 "fraction_samples_touched,n_zeros,zero_rate,n_crossings,n_events,"
                 "classical,sigma_delta,confirmed,talent,classical_gt_004,"
                 "abs_sigma_gt_0005,abs_sigma_ge_0005,sigma_eq_0\n");

    std::vector<int64_t> buf(*std::max_element(std::begin(kOfficialN), std::end(kOfficialN)));
    Coverage cov_by_n[5];
    for (size_t i = 0; i < 5; ++i) {
        cov_by_n[i] = probe_coverage(kOfficialN[i]);
        if (!cov_by_n[i].matches_lattice) {
            std::fprintf(stderr, "lattice mismatch n=%zu\n", kOfficialN[i]);
            return 1;
        }
    }

    const int n_spec = static_cast<int>(sizeof(kOfficial) / sizeof(kOfficial[0]));
    for (int si = 0; si < n_spec; ++si) {
        const Spec& spec = kOfficial[si];
        for (size_t ni = 0; ni < 5; ++ni) {
            const size_t n = kOfficialN[ni];
            const Coverage& cov = cov_by_n[ni];
            for (int trial = 0; trial < n_trials; ++trial) {
                const uint64_t seed = trial_seed(fam_tag(spec.family), step_milli(spec.step),
                                                 static_cast<uint32_t>(n),
                                                 static_cast<uint32_t>(trial));
                Rng rng(seed);
                fill_series(rng, spec.kind, spec.step, buf.data(), n);
                const TrialDiag d = run_one(buf.data(), n);
                if (d.tlen != cov.tlen) {
                    std::fprintf(stderr, "tlen drifted\n");
                    return 1;
                }
                const double zero_rate =
                    static_cast<double>(d.n_zeros) / static_cast<double>(d.tlen);
                std::fprintf(fp,
                             "%s,%s,%zu,%d,%016llx,%zu,%d,%zu,%.10f,%.10f,%d,%.6f,%d,%d,"
                             "%.8e,%.8e,%d,%s,%d,%d,%d,%d\n",
                             spec.family, spec.step_label, n, trial,
                             static_cast<unsigned long long>(seed),
                             cov.stride, d.tlen, cov.last_index,
                             cov.fraction_window_read, cov.fraction_samples_touched,
                             d.n_zeros, zero_rate, d.n_crossings, d.n_events,
                             static_cast<double>(d.classical), static_cast<double>(d.sigma),
                             d.confirmed ? 1 : 0, talent_name(d.talent),
                             d.classical_gt ? 1 : 0, d.sigma_gt ? 1 : 0,
                             d.sigma_ge ? 1 : 0, d.sigma_eq_0 ? 1 : 0);
            }
            std::fprintf(stderr, "done %s step=%s N=%zu trials=%d\n",
                         spec.family, spec.step_label, n, n_trials);
        }
    }
    std::fclose(fp);
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    check_locked_constants();
    if (argc < 3) {
        std::fprintf(stderr,
                     "usage:\n"
                     "  sweep_null coverage <coverage.csv>\n"
                     "  sweep_null pilot <pilot_tie_rates.csv>\n"
                     "  sweep_null run <null_trials.csv> [n_trials]\n");
        return 2;
    }
    const std::string cmd = argv[1];
    if (cmd == "coverage") return cmd_coverage(argv[2]);
    if (cmd == "pilot") return cmd_pilot(argv[2]);
    if (cmd == "run") {
        int n_trials = kOfficialTrials;
        if (argc >= 4) n_trials = std::atoi(argv[3]);
        if (n_trials < 1) return 2;
        return cmd_run(argv[2], n_trials);
    }
    std::fprintf(stderr, "unknown command %s\n", argv[1]);
    return 2;
}
