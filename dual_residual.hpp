// Copyright (c) 2026 Heywood Geblomi
// Dual licensed: AGPLv3 (non-commercial) or Commercial License (see LICENSE)

#pragma once
/*
 * dual_residual.hpp — Secondary Parity dual-evidence primitive
 * Minimal single-header core. C++17. Zero dependencies beyond std.
 * EXTERNAL-clean. No sort. No residual menu. No branding.
 *
 * The transferable contribution: classical disorder score + second solid
 * signal (σ_Δ from even-indexed event parity) jointly decide whether a
 * residual path is owned, and emit a talent suggestion (T1/T2/T3).
 *
 * Extracted from the locked Field-Level surface. Independent verification
 * suite lives in tests/ + verify/.
 */
#include <cstddef>
#include <cstdint>
#include <cmath>
#include <algorithm>

#ifndef DUAL_RESIDUAL_MAX_EVENTS
#define DUAL_RESIDUAL_MAX_EVENTS 512
#endif

namespace dual_residual {

// Named constants (locked decision table)
constexpr float CLASSICAL_OWNED_THRESH = 0.04f;
constexpr float SECOND_SOLID_FLOOR     = 0.005f;
constexpr float TALENT2_SIGMA_THRESH   = 0.1f;
constexpr float TALENT3_CLASSICAL      = 0.2f;
constexpr size_t SAMPLE_SIZE           = 512;

enum class Talent : int { None = 0, T1 = 1, T2 = 2, T3 = 3 };

struct Evidence {
    bool   confirmed   = false;   // dual_owned
    float  sigma_delta = 0.f;     // σ_Δ
    float  classical   = 0.f;     // polarity magnitude
    Talent suggested   = Talent::None;
};

namespace detail {

struct Sigma {
    float even_mean = 0.f;
    float odd_mean  = 0.f;
    float delta     = 0.f;
    int   n_events  = 0;
};

inline Sigma compute(const float* stream, int T, float c = 0.f) {
    Sigma s;
    if (T < 4) return s;
    int events[DUAL_RESIDUAL_MAX_EVENTS];
    int ne = 0;
    bool above = stream[0] > c;
    for (int t = 1; t < T && ne < DUAL_RESIDUAL_MAX_EVENTS; ++t) {
        bool now = stream[t] > c;
        if (now != above) {
            events[ne++] = t;
            above = now;
        }
    }
    if (ne < 4) return s;
    int even_idx[DUAL_RESIDUAL_MAX_EVENTS / 2];
    int no = 0;
    for (int i = 0; i < ne; i += 2) {
        if (no < (int)(sizeof(even_idx)/sizeof(even_idx[0])))
            even_idx[no++] = events[i];
    }
    if (no < 2) return s;
    float sum_even = 0.f, sum_odd = 0.f;
    int n_even = 0, n_odd = 0;
    for (int i = 0; i < no; ++i) {
        float val = stream[even_idx[i]];
        if ((i % 2) == 0) { sum_even += val; ++n_even; }
        else              { sum_odd  += val; ++n_odd;  }
    }
    s.even_mean = n_even ? sum_even / n_even : 0.f;
    s.odd_mean  = n_odd  ? sum_odd  / n_odd  : 0.f;
    s.delta     = s.even_mean - s.odd_mean;
    s.n_events  = no;
    return s;
}

template <class T>
inline int polarity_stream_strided(const T* a, size_t n, size_t stride,
                                   float* out, int max_out) {
    int Tlen = 0;
    if (stride < 1) stride = 1;
    for (size_t i = 0; i + stride < n && Tlen < max_out; i += stride) {
        if (a[i + stride] > a[i])      out[Tlen++] = 1.f;
        else if (a[i + stride] < a[i]) out[Tlen++] = -1.f;
        else                           out[Tlen++] = 0.f;
    }
    return Tlen;
}

inline bool dual_confirm(bool classical, float sigma_delta,
                         float floor = SECOND_SOLID_FLOOR) {
    if (!classical) return false;
    if (std::fabs(sigma_delta) < floor) return false;
    return true;
}

inline Talent compute_talent(float classical_score, float sigma_delta, bool dual_owned) {
    if (!dual_owned) return Talent::None;
    if (std::fabs(sigma_delta) > TALENT2_SIGMA_THRESH) return Talent::T2;
    if (classical_score > TALENT3_CLASSICAL) return Talent::T3;
    return Talent::T1;
}

} // namespace detail

/** First-class dual evidence.
 *  polarity stream → σ_Δ → dual_confirm → talent suggestion.
 */
template <typename T>
inline Evidence evidence(const T* a, size_t n,
                         size_t max_events = DUAL_RESIDUAL_MAX_EVENTS,
                         float classical_thresh = CLASSICAL_OWNED_THRESH,
                         float sigma_floor = SECOND_SOLID_FLOOR) {
    Evidence de;
    if (n < 2 || max_events < 4) return de;
    float stream[DUAL_RESIDUAL_MAX_EVENTS];
    size_t stride = (n > 1024) ? (n / SAMPLE_SIZE) : 1;
    if (stride < 1) stride = 1;
    int Tlen = detail::polarity_stream_strided(a, n, stride, stream,
        (int)std::min(max_events, (size_t)DUAL_RESIDUAL_MAX_EVENTS));
    if (Tlen < 4) return de;
    detail::Sigma sig = detail::compute(stream, Tlen, 0.f);
    de.sigma_delta = sig.delta;
    float sum = 0.f;
    for (int i = 0; i < Tlen; ++i) sum += std::fabs(stream[i]);
    de.classical = sum / (float)Tlen;
    bool classical = de.classical > classical_thresh;
    de.confirmed = detail::dual_confirm(classical, de.sigma_delta, sigma_floor);
    de.suggested = detail::compute_talent(de.classical, de.sigma_delta, de.confirmed);
    return de;
}

} // namespace dual_residual
