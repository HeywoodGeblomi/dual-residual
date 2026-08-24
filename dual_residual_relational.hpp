// Copyright (c) 2026 Heywood Geblomi
// Dual licensed: AGPLv3 (non-commercial) or Commercial License (see LICENSE)

#pragma once
/*
 * dual_residual_relational.hpp — Relational preposition overlay
 *
 * Pure semantic / documentation layer over dual_residual_prod.hpp.
 * Zero arithmetic. Zero branching. Zero change to decision logic.
 *
 * Relational matrix:  {[to, in]  [from, with]}
 *
 *   from  → classical     (polarity magnitude / classical disorder)
 *   with  → sigma_delta   (σ_Δ from even-indexed event parity)
 *   to    → confirmed     (dual_owned residual path)
 *   in    → suggested     (Talent T1 / T2 / T3)
 *
 * Narrative:
 *   from classical  with  σ_Δ  →  dual_owned  to  residual path  in  talent
 *
 * Core dual_residual.hpp remains locked.
 * Production guards remain in dual_residual_prod.hpp.
 * This header only names the axes.
 */

#include "dual_residual_prod.hpp"

namespace dual_residual {
namespace relational {

/*
 * Field aliases (documentation only — Evidence layout unchanged):
 *
 *   e.classical   == from   (origin axis)
 *   e.sigma_delta == with   (accompanying axis)
 *   e.confirmed   == to     (ownership path)
 *   e.suggested   == in     (container / result talent)
 */

/** Pure forward to production facade (P0 guards + core evidence).
 *  Returns identical Evidence to dual_residual::prod::evidence(...).
 */
template <typename T>
inline Evidence evidence(const T* a, size_t n,
                         size_t max_events = DUAL_RESIDUAL_MAX_EVENTS,
                         float classical_thresh = CLASSICAL_OWNED_THRESH,
                         float sigma_floor = SECOND_SOLID_FLOOR) {
    return dual_residual::prod::evidence(a, n, max_events, classical_thresh, sigma_floor);
}

/** Opt-in floor override — same as prod::evidence_with_floor. */
template <typename T>
inline Evidence evidence_with_floor(const T* a, size_t n,
                                    float sigma_floor,
                                    size_t max_events = DUAL_RESIDUAL_MAX_EVENTS,
                                    float classical_thresh = CLASSICAL_OWNED_THRESH) {
    return dual_residual::prod::evidence_with_floor(a, n, sigma_floor, max_events, classical_thresh);
}

} // namespace relational
} // namespace dual_residual
