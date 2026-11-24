# Dual Residual validation: a process record

**Author:** Heywood Geblomi
**Date:** 24 November 2026 (America/New_York)
**Status:** draft research record, v7. Not published. v1 (`af7ce94e…`), v2 (`3a857a24…`), v3 (`80c88628…`), v4 (`b82b8b20…`), v5 (`1be25db4…`), and v6 (`05a43ac7…`) stay on disk unchanged.

This is not a clinical, safety, or efficacy claim. It is a record of how a small frozen rule was tested, and of the method used to test it. Every number below is tied to a file path and a short sha256 checked with `sha256sum` on this box. If a number could not be checked from a file, it is marked unverified or left out.

## 1. What the core is

The locked core is commit `ba2ea57` (`ba2ea5717863ae70497aed51514f9db2c0653b22`). It is a short C++ rule. For a window of samples it computes two scores:

- **classical** — a polarity, or disorder, score for the window.
- **σ_Δ** (sigma-delta) — a score of even-versus-odd event imbalance in the up-and-down crossings of the window.

The window is "owned" only if both scores pass fixed cutoffs. If owned, it is given a tier: T1, T2, or T3. The cutoffs do not change.

σ_Δ was exactly 0 on every sign stream, after sampling, that is period-2 from its first step, checked for lengths 4–1,200 (`/workspace/lucas_dr_beat_timing_v1/PERIOD2.sha256`, `31d09c1b…`). Written derivations by Cheddar-Panama (`/workspace/link/dr_v4_ceiling_escrow_v1/cheddar_O1/O1_DERIV.sha256`, `1c20cd1f…`) and Toni (`/workspace/toni/dual-residual-job4/sigma_period2_proof_v1/MANIFEST.sha256`, `3e21466b…`) agree, and they are not blind to Lucas's posted proof. Link has not re-derived any of them. A lead-in, including one created by the lag sampler from a flat hold, can make it nonzero (0.091; 1/128). Lucas's check gives the 0.091 case: a lead-in of 1, 0, 0, −1, 0, 0 followed by alternation (`/workspace/lucas_dr_beat_timing_v1/period2_proof_check_out.txt`, `f4ae8680…`). Toni's write-up gives the 1/128 hand example: under `stream_lag`, a leading low hold then a period-2 window of length 1,536 returns 0.0078125, which is 1/128 (`/workspace/toni/dual-residual-job4/sigma_period2_proof_v1/PROOF.md`, `6d71773a…`, lines 250–252). Toni's results file gives the 40 of 100,000 random cases at 0.0078125 (`/workspace/toni/dual-residual-job4/sigma_period2_proof_v1/results.txt`, `05e79713…`; that file is in the package listed by `MANIFEST.sha256` `3e21466b…`; also `/workspace/link/dr_v4_explore_log_v10.md`, `6b32ddd7…`, `/workspace/link/dr_v4_explore_log_v11.md`, `9a064bbf…`, and `/workspace/link/dr_v4_explore_log_v13.md`, `1bc1b7b6…`). An earlier three-case dump — a bigeminy beat-gap window, the same window shifted by one beat, and a plain ±1 alternation — also returned exactly 0 (`/workspace/lucas_dr_beat_timing_v1/DUMP.sha256`, `cbed848e…`). Lucas's checks were run on Tater's copy of the core, which Tater describes as a bit-exact port of `ba2ea57` (`/workspace/tater/sigma_tinker_v1/VARIANTS_LOG.md`, `3120c67b…`).

The crew tested this rule on public heart-recording windows from the MIT-BIH Arrhythmia Database, using the de Chazal DS1 split. DS2, the usual second half of that split, was sealed and was not read. This is a research test of a frozen rule. It is not a medical device. There is no claim that the rule detects arrhythmia.

A clean-room check — a second rule written from the written text only, and frozen before comparison — found no code bug in `ba2ea57`. The written directive was underspecified. A one-sample shift of each window flipped 33% of decisions at window length N=1024, and 28% at N=4096. The pre-set bar was 10% or lower. Gate 3 therefore failed, and rollout was no-go.

These facts are from the public validation README on `main`, fetched on 24 November 2026 from `https://raw.githubusercontent.com/HeywoodGeblomi/dual-residual/main/validation/README.md` (sha256 `91df9af7…`), and from merged pull request https://github.com/HeywoodGeblomi/dual-residual/pull/6. A local package of the same record sits at `/workspace/purp/dr-public-package/`.

## 2. Core v2

A change to σ_Δ and to how the window is sampled was authorized, together. Candidates were written down and frozen before the blind run.

On DS1, no candidate passed every pre-set bar at both N=1024 and N=4096. No candidate was picked. DS2 stayed sealed.

The sampling fix worked. Reading every sample (stride 1), or using a lag without decimation (decimation means shrinking the window by averaging blocks of samples), cut **tier flips** — the assigned tier changing when the window is shifted by one sample — to 2.0% or less at both lengths. That held in all six tries that used it. Block-mean decimation still flipped 14.5% and 34.8% at N=4096.

Two independently built scoring programs (**harnesses**) agreed on all 32 pass-or-fail calls (4 bars, 4 candidates, 2 lengths). One harness ran before the freeze, against the unchanged prereg file, and stayed sealed until the blind run was posted.

Sources: `/workspace/link/dual_residual_gate_log_v3.md` (`f5c10e80…`); `/workspace/tater/dr_v2_both_v1/SUMMARY.md` (`76ab95dd…`); `/workspace/purp/dr-public-package/handoff/v2/crosscheck_toni/V2_DS1_SUMMARY.md` (`8dcc423a…`).

## 3. Core v3 plan

Link froze a single **prereg** (a written plan locked before any v3 score): freeze v2 (`4d0d9e6f…`), then v3 (`cd1e23b1…`), then v4 (`4648d36c…`). Those hashes are of the freeze lists themselves, under `/workspace/link/dr_core_v3_prereg_frozen_v2/`, `_v3/`, and `_v4/`.

The practice set was a build of the public INCART database (St. Petersburg Institute of Cardiological Technics), converted toward MIT-BIH's 360 Hz rate and voltage steps. The build was picked by a **label-free tie-rate rule**: choose the variant whose median share of flat steps is closer to DS1's, without using labels. One disclosed fix was allowed before the pick. Values exceed the 11-bit range in 33 of 75 records (the file's count is records with more than 1% of samples beyond ±5.12 mV). Removing the median offset doesn't change that (still 33). 27 of 75 records sit more than 2 mV off zero. Link reproduced these counts. Source: `/workspace/lucas_dr_incart_offset_v1/offset_out.csv` (`e1cb1cda…`); hash list `/workspace/lucas_dr_incart_offset_v1/OFFSET.sha256` (`ea9c0845…`). Toni counted the same lead-II offsets independently, before opening Lucas's files, and got matching numbers: 27 of 75 and 33 of 75, with the same records (`/workspace/toni/dual-residual-job4/upstream_wfdb_v1/lucas_agreement.md`, `95e595bf…`). 12.1% of raw lead II samples fall outside the 11-bit range (4,196,356 of 34,695,000; the file's exact share is 12.095%). After removing each record's median offset, 6.71% remain outside (2,327,428 of 34,695,000). Across all 12 leads the shares are 8.44% raw and 4.31% centered. So "about 12%" holds only for raw lead II. The all-lead extremes of ±107 mV come from I02 V6 sitting at the 16-bit rail (header init −32767), which is not physiology (`/workspace/toni/dual-residual-job4/upstream_wfdb_v1/incart_ranges_summary.json`, `c31b2f74…`; `/workspace/toni/dual-residual-job4/upstream_wfdb_v1/README.md`, `b3176bbc…`; hash list `/workspace/toni/dual-residual-job4/upstream_wfdb_v1/MANIFEST.sha256`, `21c25164…`). INCART headers show gains of 240–1063 adu/mV on all 12 leads (docs say 250–1100); five records sit at 240 and two at 248 (`/workspace/toni/dual-residual-job4/upstream_wfdb_v1/incart_ranges_per_lead.csv`, `3f868856…`; documented range: `/workspace/toni/dual-residual-job4/upstream_wfdb_v1/gain_vs_docs.md`, `56a26935…`). wfdb itself doesn't clip: `adc()` doesn't clamp, and `wrsamp` with format 212 raises an error instead (`/workspace/toni/dual-residual-job4/upstream_wfdb_v1/wfdb_repro.md`, `5c7002d3…`). Our own 11-bit clamp did the clipping in the conversion: a check against `wfdb.rdrecord` differed by 0 on the records checked, and the clamp to 0…2047 was the only step that discarded amplitude (`/workspace/link/dr_v3_practice_set_pick_v2/RERUN_RULE.md`, `24de5dd7…`; same bytes at `/workspace/toni/dual-residual-job4/dsdev/RERUN_RULE.md`). The cause is not established; baseline wander and a gain issue are candidate explanations, unproved.
The clamp was then removed (build B2). B2 won the pick.

Sources for the pick: `/workspace/link/dr_v3_practice_set_pick_v2/NOTES.md` (`eade78e7…`) and the `RERUN_RULE.md` cited above. The rule file is not inside the `B2_360mitbih_fixed/` folder.

Error limits were written with a cushion (tighter than a stated "need" level). Link recorded the project owner's approval, after the proposal was posted, in the owner's words: "Link -- you have my OK." Sources: `/workspace/link/dr_core_v3_prereg_frozen_v3/NOTES.md` (`be581d27…`); `/workspace/link/dr_core_v3_prereg_frozen_v3/link/ERROR_LIMITS_v3_APPROVED.md` (`ef80900a…`). At each length, at most 5% of normal windows may be flagged, at most 1% may be flagged at the top alarm tier, at most 10% of problem windows may be missed, and no top-tier window may be missed. Both an exact 95% bound and a record-cluster bootstrap must pass. Freeze v4 added a stricter **patient-cluster** bootstrap on INCART (32 patients, not only 75 records). That only adds a condition. It cannot loosen a limit (`/workspace/link/dr_core_v3_prereg_frozen_v4/NOTES.md`, `1eb2130d…`).

## 4. Core v3 result

**No pick.** DS2 stayed sealed and was never opened.

Two harnesses ran blind to each other and sent tables only to Link. They agreed on all 160 pass-or-fail calls. That is 20 rows — two selectable candidates on INCART and DS1, plus six report-only reruns on INCART, at two lengths — with four bars and four limits on each row. Source: `/workspace/link/dual_residual_gate_log_v4.md` (`4260bb11…`).

**P1 held.** The six reruns of earlier candidates kept INCART flips at or below 2.7% at both lengths. The pre-registered bar was 10%. The sampling fix from v2 held on a second database.

**P2's outcome held, but not for the reason written in the freeze.** The prereg predicted that nothing would qualify, "because separation is the weak spot on DS1" (`/workspace/link/dr_core_v3_prereg_frozen_v3/purp/CORE_V3_PREREG_DRAFT_v3.md`, `0e21468b…`). Nothing qualified. The main reason was false alarms: the bound on normal windows flagged was 0.94–0.99 against a 5% limit. Only the 10% miss limit (L3) passed, and only because almost every window was flagged. That is not detection skill. The zero-T3-miss limit (L4) failed in every scored row of the two selectable candidates. T3v18 missed 11 of 414 T3 windows on INCART at N=1024, 2 of 159 at N=4096, 7 of 139 on DS1 at N=1024, and 1 of 59 at N=4096. T3v19 missed 17 of 414, 5 of 159, 5 of 139, and 1 of 59 (`/workspace/link/dual_residual_gate_log_v4.md`, `4260bb11…`). Separation was secondary. The expected 5% false-alarm failure had also been written in freeze v3 before scoring.

The `ba2ea57` baseline on INCART flipped 0.26 / 0.28 at the two lengths. Gate log v4 records that rounding. Toni's table gives 0.2632 / 0.2785 (`/workspace/toni/dual-residual-job4/v3_run1/report_only/TABLES.md`, `96a217c3…`). That figure is **report-only and from one harness**. It was not cross-checked. It should not be read as a cross-checked "tenfold" drop.

The rank score of |σ_Δ| — how often that score ranks a ventricular window above a normal one — is 0.4561 to 0.5493 across 22 rows, a coin flip. Source: `/workspace/link/dr_v3_sigma_rank_check_v1.md` (`fa47c8cc…`), computed from the stored U statistics in Toni's run1 results.

## 5. Lessons: the method, and corrections

The method is the piece worth keeping, even though no candidate was picked.

1. **Freeze before scoring.** Candidates, bars, limits, and the practice-set pick were locked first.
2. **A try ledger.** v2 logged 17 tries. v3 added two (T3v18 and T3v19). The running total is 19. Harness fixes are not tries (`4260bb11…`; try count 17 also in `f5c10e80…`).
3. **Two harnesses, blind.** Agreement was required on every pass-or-fail call (32/32 in v2; 160/160 in v3) before a pick could be named.
4. **A sealed holdout.** DS2 was never opened.
5. **Label-free selection** for the practice-set build (tie rate, no labels).
6. **Corrections recorded in the open:**
   - Purp's room line "my prediction was wrong" was itself wrong as to the frozen v2 text. The frozen prediction was that at least one v2 candidate would pass the flip bar at both lengths. It held. All four did (`/workspace/link/dual_residual_gate_log_v3.md`, `f5c10e80…`).
   - Link's 80→81 erratum: an earlier pick note said the build manifests had 80 entries. The correct count is 81 (75 signals, 5 label files, and `meta.json`). No hash or verdict changed (`/workspace/link/dr_v3_practice_set_pick_v2/NOTES.md`, `eade78e7…`).
   - **float32 honesty.** The frozen rule compares 32-bit floating-point values to 32-bit constants (**float32**). Link ruled that float32 is the rule (`/workspace/link/dr_v3_harness_rulings_v1/RULINGS.md`, `deabbfa4…`). Toni's v2 harness compared scores against 64-bit constants (**float64**), so windows exactly on a cutoff could have been given a different tier (`/workspace/toni/dual-residual-job4/v3_harness/SPEC_TRACE.md`, `650c83e4…`).
   - v2 used float64 constants; on these windows that changed no call. On DS1 at both sizes, for all five v2 cross-check candidates (`ba2ea57`, V2-C1, V2-C2, V2-C3, and V2-T6), no window sits exactly on the 0.04, 0.2, or 0.005 cutoffs. Only V2-T6 has windows at exactly |σ_Δ| = 0.1 (48 at N=1024, 4 at N=4096). All of them are already T3 and stay T3, since T2 uses a strict `>`. That gives zero tier or ownership differences, unshifted, shifted, or shuffled. No v2 verdict changes. Source: `/workspace/toni/dual-residual-job4/v2_float32_erratum_v1/V2_FLOAT32_ERRATUM.md` (`dd736ac8…`); hash list `/workspace/toni/dual-residual-job4/v2_float32_erratum_v1/MANIFEST.sha256` (`baf40979…`).
   - For v3, gate log v4 notes that float32 was used. Tater's float64 counterfactual moved at most 12 of 47,400 windows and no verdict (`/workspace/link/dual_residual_gate_log_v4.md`, `4260bb11…`).

## 6. What is next (plans only; no claims)

A ceiling check on `classical` alone is planned, to see whether that other input carries any ranking signal. A per-record shape template, and a gate that uses beat timing from an off-the-shelf beat detector (never from the label files), are also on the table. A fresh test set is still needed. Lucas's ST Change set was not scored and remains available for a later freeze. DS2 stays sealed until a new freeze and an explicit go from the project owner.
