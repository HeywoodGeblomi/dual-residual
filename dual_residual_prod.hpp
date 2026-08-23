// Copyright (c) 2026 Heywood Geblomi
// Dual licensed: AGPLv3 (non-commercial) or Commercial License (see LICENSE)

#pragma once
/*
 * dual_residual_prod.hpp — Thin production facade over dual_residual.hpp
 *
 * Core remains locked. Decision table remains immutable.
 * This facade adds only production guards (P0) and optional hooks (P1/P2).
 * It never re-implements polarity, σ_Δ, dual_confirm, or compute_talent.
 *
 * Call flow:
 *   Caller → facade guards → dual_residual::evidence(...) → Evidence unchanged
 *
 * THE BEASTIE BOYZ 2026-08-23
 * Production Hardening Plan — chassis only. Math stays fierce.
 */
#include "dual_residual.hpp"
#include <cstddef>
#include <cstdint>
#include <limits>

namespace dual_residual {
namespace prod {

// Reasonable upper bound for size sanity (plan §3.1)
constexpr size_t kMaxReasonableN = (size_t(1) << 30);

/** P0 mandatory production entry.
 *  - null / invalid pointer + n > 0 → zeroed Evidence (no dereference)
 *  - n == 0 or n > kMaxReasonableN → safe None
 *  - otherwise forward to dual_residual::evidence with original signatures
 *  - return-by-value only
 */
template <typename T>
inline Evidence evidence(const T* a, size_t n,
                         size_t max_events = DUAL_RESIDUAL_MAX_EVENTS,
                         float classical_thresh = CLASSICAL_OWNED_THRESH,
                         float sigma_floor = SECOND_SOLID_FLOOR) {
    Evidence safe;  // zero-initialized: confirmed=false, Talent::None

    // P0-1: null / invalid pointer
    if (a == nullptr && n > 0) {
        return safe;
    }

    // P0-2: size sanity
    if (n == 0 || n > kMaxReasonableN) {
        return safe;
    }

    // Core already handles n < 2; facade makes the contract explicit above.
    // Forward unchanged — decision table and core math never touched.
    return dual_residual::evidence(a, n, max_events, classical_thresh, sigma_floor);
}

/** P1 opt-in: evidence with an explicit sigma_floor override.
 *  Default path remains the locked SECOND_SOLID_FLOOR.
 *  Callers who want a local adaptive floor compute it themselves and pass it here.
 *  Never the default.
 */
template <typename T>
inline Evidence evidence_with_floor(const T* a, size_t n,
                                    float sigma_floor,
                                    size_t max_events = DUAL_RESIDUAL_MAX_EVENTS,
                                    float classical_thresh = CLASSICAL_OWNED_THRESH) {
    Evidence safe;
    if (a == nullptr && n > 0) return safe;
    if (n == 0 || n > kMaxReasonableN) return safe;
    return dual_residual::evidence(a, n, max_events, classical_thresh, sigma_floor);
}

} // namespace prod
} // namespace dual_residual
