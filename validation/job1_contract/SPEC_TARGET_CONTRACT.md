# SPEC_TARGET_CONTRACT.md — Dual Residual Job 1 (DRAFT v0, not frozen)

Owner: Purp. Core under test: HeywoodGeblomi/dual-residual @ ba2ea57 (unchanged; no core, header, decision-table or constant edits).
Status: DRAFT. Sections marked PROPOSED need Blam's sign-off before freeze. Research benchmark only; not a clinical or medical-device claim.

## 1. Target stream (locked candidate)
- Source: MIT-BIH Arrhythmia Database v1.0.0, PhysioNet (https://physionet.org/content/mitdb/1.0.0/), ODC-By 1.0.
- 48 records, 30 min each, 360 Hz, 11-bit ADC, gain 200 adu/mV. 144 .hea/.dat/.atr files verified against PhysioNet SHA256SUMS.txt.
- Lead: MLII selected by name (sig_name), never by channel index (record 114 stores V5 first).
- Labels: the database's expert beat annotations (.atr), mapped to AAMI EC57 classes N/S/V/F/Q.

## 2. Preprocessing / source of zeros (locked)
- Input to the core is the raw integer ADC value (physical=False). No filtering, no centering, no deadband, no resampling.
- Rationale: the core compares each sample with the one a stride ahead and emits +1/-1/0. Ties come from the native 11-bit quantization; no extra step is needed. Baseline drift largely cancels in the differences (confirmed with Lucas at ba2ea57).
- Measured tie rate (sign of x[i+s]-x[i] equal to 0, MLII, mean over records):

| N | stride | DS1 | DS2 |
|---|---|---|---|
| 64 / 256 / 1024 | 1 | 0.131 | 0.127 |
| 4096 | 8 | 0.042 | 0.043 |
| 16384 | 32 | 0.018 | 0.020 |

  These rates are MLII-only. Records 102 and 104 have no MLII and are paced, so they are excluded either way. The zero rate falls sharply above N=1024 because the stride grows; Job 2 must report it per N.

## 3. Windows and ground-truth tiers (locked)
- Non-overlapping windows of N samples, N ∈ {64, 256, 1024, 4096, 16384}, starting at sample 0; any trailing partial window is dropped.
- Window tier from the annotated beats inside it:
  - T3 (v1): the window overlaps any record-level run of 3 or more consecutive V-class beats. This fixes runs being split at window edges, which Cheddar found.
  - T2: at least 1 V-class beat, no run of 3.
  - T1: no V, but at least 1 S or F beat.
  - None: only N or Q beats, or no beats.
- Exclusion (v1): windows overlapping a `(VFL` rhythm episode or any `!` flutter wave are dropped. That affects only record 207, which is in DS1.
- Known limit (v0 wording; v1 counts in section 7): a 3-beat run lasts about 1.5–2 s (540–720 samples). That makes T3 rare at N ≤ 256 (DS1 has 4 fast runs at N=256, in records 203 and 205; DS2 has none) and uncommon everywhere (DS2: 14 / 17 / 18 windows at N = 1024 / 4096 / 16384). T3 confidence intervals will be wide, and Job 2 and Job 4 must report them, not hide them.

## 4. Held-out split (locked)
- Standard inter-patient split (de Chazal et al., 2004).
  - DS1 (tuning/exploration, for Jobs 2 and 3): 101 106 108 109 112 114 115 116 118 119 122 124 201 203 205 207 208 209 215 220 223 230.
  - DS2 (sealed held-out, Job 4 only, plus the final gate-2 check): 100 103 105 111 113 117 121 123 200 202 210 212 213 214 219 221 222 228 231 232 233 234.
- Excluded: paced records 102 104 107 217.
- Seal: honor-system. DS2 sits in the same readable folder, with no access log. It is protected by its hash (split_v0.json sha adf5ddcb…) and the logging rule below, not by an access control.
- Rule: no threshold, N-guard, perturbation choice or mechanism claim may be fitted or revised after any DS2 score is seen. DS2 is scored once per frozen configuration, and every run is logged.

## 5. Output-state → action contract (PROPOSED, needs Blam)
| Core state | Downstream action | Latency SLA (proposed) |
|---|---|---|
| None | no action; counted only | — |
| T1 | append to low-priority review log | ≤ 1 window |
| T2 | raise review flag on window | ≤ 1 window |
| T3 | raise alarm event | ≤ 1 window, p99 compute ≤ 1 ms per window |

## 6. Error targets per tier (PROPOSED placeholders, needs Blam)
These are window-level error rates on DS2. They are separate from the core's decision cutoffs 0.04 / 0.005 / 0.1 / 0.2.
| Tier | max FPR (proposed) | max FNR (proposed) |
|---|---|---|
| T3 (alarm) | 0.01 | 0.20 |
| T2 (flag) | 0.05 | 0.30 |
| T1 (log) | 0.10 | 0.50 |
Arithmetic floor: with 14–18 DS2 T3 windows, even 0 misses gives a 95% exact upper bound on FNR of about 0.15–0.19. Any T3 FNR target below about 0.20 can fail on sample size alone.
Gate 2 passes only if every tier meets its target, with a 95% upper bound computed on DS2 for each record-clustered tier.

## 7. Evaluation dataset (versioned)
- dataset_v0/{DS1,DS2}_N{N}.csv with columns record, lead, start, end, tier, n_beats. The hashes are in dataset_v0_manifest.json.
- Window tier counts:

| N | DS1 None/T1/T2/T3 | DS2 None/T1/T2/T3 |
|---|---|---|
| 64 | 218285 / 1359 / 3788 / 0 | 217986 / 2225 / 3221 / 0 |
| 256 | 51196 / 1084 / 3574 / 4 | 50508 / 2185 / 3165 / 0 |
| 1024 | 10909 / 562 / 2381 / 96 | 10653 / 958 / 2323 / 14 |
| 4096 | 2155 / 284 / 981 / 56 | 2138 / 321 / 1000 / 17 |
| 16384 | 370 / 109 / 340 / 39 | 415 / 106 / 319 / 18 |

## 7b. Dataset v1 (current; v0 is kept read-only)
- dataset_v1/ with manifest dataset_v1_manifest.json (sha 82f77b33…), built by build_labels_v1.py (sha 2042b064…).
- DS2 T3 windows by N: 162 / 58 / 29 / 21 / 18 for 64 / 256 / 1024 / 4096 / 16384. DS1 excluded VFL windows: 818 / 209 / 56 / 17 / 8.
- At small N, a T3 window may contain only part of a run.

## 7c. DS1 findings logged under the halt rule (from Jobs 3 and 4; the contract is not changed to fit them)
- On DS1 the core never emits T1, because classical is about 1 minus the tie rate, which is above 0.2 (Toni). The T1 tier is therefore unreachable on this stream as preprocessed.
- A one-sample phase shift flips 28–33% of decisions (Lucas, Gate 3 MISS).

## 8. Open items before freeze
1. Blam signs off on sections 5 and 6, or replaces the numbers.
2. Cheddar: second-check the stream choice and the AAMI mapping. Link: freeze and hash the document on sign-off.
