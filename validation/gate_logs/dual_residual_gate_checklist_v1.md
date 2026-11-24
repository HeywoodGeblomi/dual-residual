# Dual Residual rollout — independent go/no-go checklist v1

## Provenance and freeze record

- **Document:** `dual_residual_gate_checklist_v1.md` (this file). Changes require a new version; do not overwrite this freeze.
- **Author:** Link — independent gate review for Blam (Heywood Geblomi).
- **Date:** 2026-11-23.
- **Timezone:** America/New_York (EST).
- **Inputs used:** Parent-relayed engineering directive and team-reported facts only, as supplied in the delegated brief. No Dual Residual repository, core header, decision table, facade, test, plot, dataset, or other implementation artifact was opened, hashed, or executed for this document.
- **Evidence label:** Authored specification and scoring rubric only. Nothing in this checklist is an execution result, a measured rate, a verified commit, or a stream lock. Team-reported mechanism and tip facts below are accepted as *reported, not verified here*.
- **Freeze statement:** Frozen read-only v1 before any gate scoring. No builds, tests, repository mutations, publishing, or external contact were performed.
- **Locked target (as specified, not verified here):** repo `HeywoodGeblomi/dual-residual`, tip `ba2ea57`. The provenance pack on every later deliverable must record the full commit hash that this short tip denotes.
- **Job owners (as assigned):** Purp Job 1 (Gate 1), Tater Job 2 (Gate 2), Lucas Job 3 (Gate 3), Toni Job 4 (Gate 4), Link independent gate review against this checklist.
- **Status:** Frozen v1. This document does not approve rollout.

## Verdict vocabulary

Every required check, and each gate, is scored as exactly one of:

| Verdict | Meaning |
|---|---|
| **GO** | The check or gate was scorable, and every required item passed. |
| **NO-GO** | The check or gate was scorable, and at least one required item failed with evidence. |
| **BLOCKED** | A required prerequisite is missing, unapproved, or leaked, so the check or gate cannot be scored honestly. |

BLOCKED is not a pass. A gate is GO only if every required check is GO and none are BLOCKED or NO-GO. Rollout is GO only if all four gates are GO and every cross-cutting constraint holds. If any gate is NO-GO or BLOCKED, halt rollout, write a failure-boundary log, and do not change the frozen core table or architecture until that log exists.

## Cross-cutting hard constraints

These bind every gate. Any breach is rollout **NO-GO**, even if a local metric looks favorable.

- **C1.** Do not modify the core header or decision table. Facades (`prod`, `relational`) are limited to guards and naming.
- **C2.** Decision constants stay immutable: `0.04` / `0.005` / `0.1` / `0.2`. They are cutoffs, not FPR/FNR SLA numbers.
- **C3.** No third signal, soft metric, or χ on the public path.
- **C4.** No deliverable may retune cutoffs, relabel states, or alter the held-out split after unblinding in order to obtain a pass.
- **C5.** Independent verification uses a named checker that does **not** share code with the core (no shared modules with the core header or decision table). Link grades deliverables against this checklist from reported results and artifacts, not by reusing core code. An "ALL GREEN" claim without that disjoint checker is **BLOCKED**.

## Failure-boundary log

A failure-boundary log is a dated, immutable record written **before** any architecture or core-table change after a NO-GO or a blocking gap that halts rollout. It must include at least:

1. Gate ID, check ID(s), and verdict.
2. The full provenance pack (below).
3. The preregistered rule or threshold, the observed statistic, and the side of the boundary that was crossed.
4. Where applicable: window length `N`, stride, zero rate, and event count.
5. Decision state(s) involved (`None` / `T1` / `T2` / `T3`).
6. Confirmation that the frozen core table was not modified in response to the failure.
7. A halt statement: no cutoff change, split change, or new public-path signal may be used to convert this result into a GO.

Missing or post-hoc logs cannot rehabilitate a NO-GO.

## Provenance pack (required on every gate deliverable)

Each of `SPEC_TARGET_CONTRACT.md`, the versioned labeled dataset, `REPORT_THRESHOLD_BOUNDS.md`, `REPORT_PARITY_MECHANISM.md`, `BENCHMARK_VS_BASELINES.md`, sweep scripts, plots, perturbation results, and benchmark CSVs must record:

- Core tip and full commit hash (directive lock: `ba2ea57`).
- Dataset identifier, version, and content hash.
- Held-out split definition and split hash.
- Exact quantization or deadband rule (the rule that produces exact zeros).
- Execution environment (OS, CPU, language/runtime versions, seed list, command or script hash).

A deliverable lacking this pack is **BLOCKED**, not GO.

## Preregistration

Before Jobs 2, 3, or 4 may score real or null data:

- **P1.** Gate 1 contract frozen, or any placeholders explicitly marked **and** approved by Blam in writing.
- **P2.** One real, non-synthetic stream locked. MIT-BIH Arrhythmia (11-bit integer ECG, cardiologist beat labels) is the team-reported candidate only, and is not a lock until the contract names it.
- **P3.** Quantization or deadband rule locked. Team-reported (unverified here): the core takes raw values and maps each sample versus the sample one stride ahead to `+1` / `-1` / `0`; only exact equality yields `0`. A centering rule is not a substitute for this lock. Tie-free streams force `σ_Δ ≡ 0` and refuse, so they are not an admissible target stream.
- **P4.** Held-out split sealed with a hash **before** Jobs 2–4 touch the data. Job 2 length/N work and Job 3 mechanism analysis must not use the held-out set. Job 4 uses only the sealed held-out set. Any touch or retune on held-out data before seal, or leakage of held-out labels into Jobs 2–3, is **BLOCKED** for Gates 2–4 and rollout **NO-GO**.
- **P5.** Per-state FPR and FNR SLA targets for `None`, `T1`, `T2`, and `T3` pinned in the contract. Using `0.04` / `0.005` / `0.1` / `0.2` as if they were those error-rate targets is invalid and leaves Gate 2 **BLOCKED**.
- **P6.** Job 3 shuffle-control statistic, inequality, and perturbation protocol preregistered (see G3).
- **P7.** Job 4 "beats or matches" tolerance and cost metric preregistered (see G4).
- **P8.** Independent checker named and confirmed code-disjoint from the core (see C5).

## Gate 1 — Target and actions

**Owner:** Purp. **Artifacts:** `SPEC_TARGET_CONTRACT.md` + versioned, labeled evaluation dataset.

| ID | Required check | GO | NO-GO | BLOCKED |
|---|---|---|---|---|
| G1-01 | One real, non-synthetic input stream locked in the contract, with source and version. | Named locked stream; not synthetic. | Synthetic, unspecified, or swapped after freeze without a new contract version. | Only a candidate (including unconfirmed MIT-BIH) is listed; Blam/contract lock absent. |
| G1-02 | Adjacent strided comparisons (`+1` / `-1` / `0`) can produce zero-dwell events on this stream. | Contract shows why natural ties exist under the locked rule. | Stream is tie-free under the locked rule (`σ_Δ` would refuse). | No evidence that zeros can occur; quantization rule not yet fixed. |
| G1-03 | Fixed upstream quantization or deadband rule documented and hashed. If raw inputs are already integer (e.g. 11-bit ECG), the contract still states whether raw equality is used or a coarser deadband is applied. | Rule is exact, frozen, and in the provenance pack. | Rule changed after freeze, or zeros are produced by an undeclared transform. | Rule missing, ambiguous, or deferred. |
| G1-04 | `None`, `T1`, `T2`, `T3` each bound to an executable downstream system action and an SLA. | All four states have actions and SLAs. | A state has no action, or actions contradict the frozen decision table. | Actions or SLAs left TBD with no approved placeholder. |
| G1-05 | Per-state FPR and FNR targets pinned (distinct from decision cutoffs). Placeholders allowed only if clearly marked and Blam-approved before freeze. | Numeric per-state targets frozen (or approved placeholders now frozen). | Cutoffs used as SLA stand-ins after freeze; or unapproved numbers treated as final. | Targets missing, or placeholders unmarked / not yet approved. |
| G1-06 | Versioned labeled dataset and sealed held-out split hash published with the contract. | Dataset version + split hash recorded; training/analysis vs held-out partition disjoint. | Split altered after publication; labels missing. | No split hash, or Jobs 2–4 already touched data before seal. |

**Gate 1 GO** iff G1-01…G1-06 are all GO. Gates 2–4 are **BLOCKED** until Gate 1 is GO.

## Gate 2 — Threshold proof

**Owner:** Tater. **Artifacts:** `REPORT_THRESHOLD_BOUNDS.md` + reproducible sweep script and plots.

Team-reported (unverified here), and binding on this gate if confirmed at scoring: above `N=1024`, stride = `N/512`, so at most 512 signs are seen (`DUAL_RESIDUAL_MAX_EVENTS = 512`; at `N=16384`, samples 32 apart). Zero rate therefore falls with `N`. `σ_Δ` is a mean over zero-crossing events, not over all `N` samples, so noise scales as `O(1/√event_count)`, not `O(1/√N)`. Sweeps must log **zero rate and event count at each N**. The facade operating window must guard on **event count**, not raw `N` alone. Long-window rows that hit the 512-event cap must not be scored as if they had more events.

| ID | Required check | GO | NO-GO | BLOCKED |
|---|---|---|---|---|
| G2-01 | Monte Carlo null streams **and** real negative controls at every `N ∈ {64, 256, 1024, 4096, 16384}`. | All five lengths run on both families; script reproducible. | A required `N` or control family omitted, or results not reproducible. | Sweep run before P1–P5, or on held-out data. |
| G2-02 | False-trigger rates reported for `classical > 0.04` and `|σ_Δ| > 0.005`, with zero rate and event count per `N`. | Both rates plus zero rate and event count logged for every `N`. | Rates missing, or cap/stride effects ignored so long-`N` rows are mis-measured. | Logs lack event count or zero rate, so the rates cannot be interpreted. |
| G2-03 | Facade guard states the exact operating window (min/max event count, and the corresponding `N` range under the locked stride rule) at which `|σ_Δ| > 0.005` holds a bounded false-positive rate. | Window defined on event count, enforced in the facade only, and justified by the sweep. | Guard uses raw `N` only, or the 0.005 floor is not bounded in the claimed window. | No guard, or window claimed without the G2-01/G2-02 logs. |
| G2-04 | Precision, recall, and confusion matrices on **non-held-out** labeled real data for `|σ_Δ| > 0.1 → T2`, `classical > 0.2 → T3`, and fallback `T1`. | Matrices and P/R reported for those frozen boundaries. | Boundaries relabeled or cutoffs moved to improve P/R. | Evaluation used held-out data, or labels/states not yet contracted. |
| G2-05 | FPR and FNR under those frozen cutoffs meet the **contract** per-state SLA targets (G1-05). | Each state's FPR and FNR meet the pinned SLA. | Any contracted SLA missed. Record the exact state, rate, and SLA in the failure-boundary log. | SLA targets not pinned (G1-05 not GO). Do not treat 0.04/0.005/0.1/0.2 as the SLA. |

## Gate 3 — Parity mechanism

**Owner:** Lucas. **Artifacts:** `REPORT_PARITY_MECHANISM.md` + perturbation test suite.

Shuffle control is mandatory and should be run before investing in Gates 2 and 4 scoring on the locked stream. Team-reported prior JHTDB result (unverified here): raw `σ_Δ ≡ 0`; after 32-bin quantization, parity ownership was 0.10 intact vs 0.45 shuffled, i.e. the parity signal failed its own noise control. That failure mode is a Gate 3 **NO-GO** if reproduced under the preregistered rule.

| ID | Required check | GO | NO-GO | BLOCKED |
|---|---|---|---|---|
| G3-01 | Preregistered shuffle (or symmetric-noise) control on the locked stream, scored only after preregistration. | Intact target events show the preregistered even-index minus odd-index mean asymmetry on zero-crossing events; background or shuffled controls stay symmetric under the same rule (intact signal not weaker than shuffled). | Shuffled or background asymmetry is equal or larger than intact (JHTDB-type failure), or no real generating cause is documented. | Control not preregistered, or run on held-out data, or quantization changed ad hoc to recover a pass. |
| G3-02 | Mechanism write-up: why target events in this stream produce non-zero even-minus-odd mean on zero-crossing events, while background stays symmetric. | Cause is stated for this stream and is consistent with G3-01. | Cause is only a synthetic fixture story, or contradicts the shuffle control. | Stream not locked, or write-up missing. |
| G3-03 | Perturbation stress: 1-step phase shift; random single-element insertion; random single-element deletion; jitter; quantization-step change. | All five families run; stability reported against a preregistered rule. | A required family omitted, or detection collapses under a preregistered fail condition. | Protocol not preregistered, or perturbations applied to held-out data. |
| G3-04 | Regression lock at tip `ba2ea57`: synthetic controls `sorted`, `reverse`, `equal`; traps `pairwise_swapped`, `alt_high_low`, `block_zigzag`, `moderate_local_disorder`; and `noisy_ramp_confirmed` all still pass, alongside the real-data tests. | All named controls and traps pass; core unmodified. | Any named regression fails, or a pass required a core or constant change. | Suite not run, or tip in the provenance pack is not the locked tip. |

A G3-01 NO-GO halts rollout even if later benchmarks look favorable.

## Gate 4 — Baseline benchmark

**Owner:** Toni. **Artifacts:** `BENCHMARK_VS_BASELINES.md` + raw benchmark CSVs.

Comparators, all required: Wald–Wolfowitz runs test; lag-1 autocorrelation; lag-2 autocorrelation; windowed sign-change / variance detector. Metrics, all required, on the **sealed held-out** real dataset only: F1, FPR, FNR, p99 latency, memory per window.

"Beats or matches on accuracy/FPR at strictly lower compute" is **BLOCKED** until the contract or a Job 4 protocol preregisters (P7): (a) which accuracy metric(s) are scored (at least F1, and FPR); (b) the numeric match tolerance ε; (c) the cost metric that must be strictly lower (p99 latency, memory per window, or a defined combination); (d) the comparison rule (e.g. Dual Residual F1 ≥ baseline − ε and Dual Residual FPR ≤ baseline + ε, and cost_core < cost_baseline, for each baseline, or a stated "match the best baseline / beat on cost" rule). No implicit tolerance is allowed.

| ID | Required check | GO | NO-GO | BLOCKED |
|---|---|---|---|---|
| G4-01 | Head-to-head on sealed held-out data vs all four baselines, with all five metrics and raw CSVs. | Complete, reproducible tables + CSVs; provenance pack present. | A baseline or metric missing, or evaluation not held-out. | Split not sealed, or held-out used in Jobs 2–3, or protocol not preregistered. |
| G4-02 | Frozen cutoffs and states only; no third signal or cutoff search on held-out data. | Public path unchanged; scoring uses the locked table. | Any held-out tuning or extra public-path feature. | Cannot confirm the path was frozen (provenance missing). |
| G4-03 | Beats or matches accuracy/FPR at strictly lower compute, under the preregistered tolerance and cost metric. | Preregistered rule satisfied vs every required baseline. | Rule missed for any required baseline. Log the baseline, metrics, tolerance, and cost numbers. | Tolerance or cost metric not predefined (P7). |
| G4-04 | Independent verification ALL GREEN: named code-disjoint checker (C5) plus this checklist all GO. | Disjoint checker reports all required checks green, and Gates 1–4 are GO under this rubric. | Checker finds a failure, or shares core code. | Checker unnamed, not shown to be code-disjoint, or earlier gates still BLOCKED. |

## Overall rollout rule

- **Rollout GO:** C1–C5 hold, P1–P8 were completed before scoring, Gates 1–4 are all GO, and the independent disjoint checker is ALL GREEN.
- **Rollout HALT:** any cross-cutting breach, any gate NO-GO, or any gate BLOCKED. Write the failure-boundary log first. Do not modify the frozen core table to clear the halt.

## Open blockers at v1 freeze (not yet scorable)

These items are **BLOCKED** at the moment this checklist is frozen. They are not failures of a run; they prevent a GO until resolved and approved as specified:

1. Per-state FPR/FNR SLA targets are not pinned; the directive's `0.04` / `0.005` / `0.1` / `0.2` values are decision cutoffs and must not be used as those SLAs (G1-05, G2-05, P5).
2. Held-out split is not yet sealed with a hash; Jobs 2–4 must not touch data until it is (G1-06, P4).
3. MIT-BIH is only a reported candidate stream, not a contract lock (G1-01, P2).
4. "Beats or matches at strictly lower compute" has no predefined tolerance or cost metric (G4-03, P7).
5. No named, code-disjoint independent checker is recorded for the ALL GREEN claim (C5, G4-04, P8).

End of frozen v1 checklist. Authored spec only; nothing executed.
