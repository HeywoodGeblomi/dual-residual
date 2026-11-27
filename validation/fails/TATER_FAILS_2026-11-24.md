# Failure record: Tater's four graded tries (2026-11-24)

A plain-language write-up of four already-graded exploratory tries. No new numbers and no reruns. All four ideas were formed after E5 failed on records I42 and I43, so they are post-hoc and exploratory: not a gate, not a claim of efficacy, and not independent validation. Link graded each one from frozen files. Headline numbers below are taken from those frozen files and from Link's grades.

Sources (read only): Link's grades `link/xt_v1_grade_v1.md`, `link/xt2_latch_grade_v1.md`, `link/xt3_grade_and_ds2_incident_v1.md`, `link/e_pool_grade_v1.md` (sha256 `b3d568656d23d6ed431e9fefa55fca02957089721591ec58fddaea39210008e2`); Tater folders `tater/xt_v1/`, `xt_v1/xt2/latch_v1/`, `xt3_v1/`, `epool_recipe_v1/RECIPE_EPOOL.md`, `epool_primary_v1/`, `epool_stageB_v1/`. Times are America/New_York (EST/ET).

---

## 1. X-T1 — frozen early template (recipe F)

**Idea and why.** Keep E5 as it is, but build the template from only the first 30 eligible beats in time order, then freeze it. The hope, after E5 missed I42 and I43, was that early beats would be cleaner than a whole-record template, so ventricular beats would not be baked into the "normal" shape. This is a retrospective construction, not an online freeze: eligibility still used E5's `q`, which divides by the whole-record median RR (look-ahead), and scores were still divided by the record's own median distance.

**What was frozen.** Plan `tater_e2_dcl_exploratory_plan_v1.md` sha256 `fa7ec63d5d10a98a76b5650eef340290a1ae0ee9e59feefcbe5c11760df7a7cb`. Choices in `xt_v1/AMBIGUITIES.md` sha256 `0f3ab53faee8da0212e08d2a7df505c686fe7571289410461fd9a2df6f75a1bf`, hashed 13:12:15 EST, before any X-T1/X-T2 code. Base E5 harness `e5_blind_v1/HASHES.sha256` `b1b2e8692efc57605c7e2da001d9a8113aa26df21279000d9973f81860b68c1f`. Build `xt1/HASHES_BUILD.sha256` `6f14194f6b5394443a728cc528ce562b41f5d20cfe3cebc032fcb00412bc31b4`. Folder `xt_v1/HASHES.sha256` `71390f2363cc2062654642f71e476ba80f0545b2ea5f81d6d7b31be9ecb9ea94` (18/18 files OK). Link grade: `link/xt_v1_grade_v1.md`, 1:16 PM EST.

**The bar.** (a) I31+I42+I43 T3 windows missed at the 5% cutoff: ≤ 35 at N=1024 and ≤ 20 at N=4096 (half of E5's 40). (b) In every row: T3 misses no worse than E5 (73, 43, 8, 2); AUC no more than 0.01 below E5; fewer than 5 abstaining records. PASS needs (a) and (b). No near-miss rescue. One scoring run.

**Headline numbers** (from `xt1/TABLE.md` and Link's grade; one scoring run, E5 identity reproduced exactly; abstains 0 in every row):

| row | set | N | AUC F / E5 | caught F / E5 | T3 unflagged F / E5 | (b) T3 | (b) AUC |
|---|---|---|---|---|---|---|---|
| R1 | INCART_B2 | 1024 | 0.9120 / 0.9493 | 0.8054 / 0.7905 | 56 / 73 | ok | FAIL |
| R2 | INCART_B2 | 4096 | 0.9174 / 0.9442 | 0.7978 / 0.7993 | 44 / 43 | FAIL | FAIL |
| R3 | DS1 | 1024 | 0.9177 / 0.9480 | 0.8851 / 0.8706 | 48 / 8 | FAIL | FAIL |
| R4 | DS1 | 4096 | 0.9568 / 0.9719 | 0.9329 / 0.9125 | 10 / 2 | FAIL | FAIL |

Bar (a): I31+I42+I43 T3 unflagged at N=1024 is 15+29+3 = 47 vs bar ≤ 35 (E5 70); at N=4096 is 25+11+2 = 38 vs bar ≤ 20 (E5 40). Neither met. Link: AUC drop 0.015–0.037 in all rows (bar 0.01); T3 unflagged worse in 3 of 4 rows (43→44, 8→48, 2→10); INCART 1024 improved 73→56.

**Verdict.** FAIL.

**What it rules out.** This retrospective early-30-eligible-beat frozen template, scored with E5's whole-record eligibility and per-record normalization, does not clear I42/I43 on these rows and does not hold AUC or T3 misses to the bar. It does not test a truly online freeze, or a different rule for "early" or "clean."

**Report-only (after scoring).** V/E share of the 30 template beats: I42 0.50, I43 0.50, I31 0.00 (1 unmatched), I35 0.30, I53 0.033 (2 unmatched), I62 0.00, 208 0.00. I42 and I43 already had 15 of 30 V/E beats among their first 30 eligible beats, so freezing early did not keep V out of their template; both stayed fully missed (29/29 and 3/3 at N=1024; 11/11 and 2/2 at N=4096). I31 improved at N=1024 (38→15) but not enough. The early template cost elsewhere: DS1 T3 misses rose from 8 to 48 (N=1024) and 2 to 10 (N=4096), mostly record 207.

**Disclosures.** The synthetic build test was changed after one 9/10 run (noise added to a test signal because a noiseless V-majority made E5's median distance 0; core said unchanged). That was a build-stage change, before scoring. An earlier `score_f.py` start crashed at import (`ModuleNotFoundError e5_core`) before reading any data; that was not a scoring run. One scoring run followed, and it reproduced E5 exactly.

---

## 2. X-T2 — latch from a private repo's `dynamic_commitment_soft.h`

**Idea and why.** Run the DCL soft-header Schmitt anti-chatter latch on E5 window scores. The hope was to cut on/off chatter while still holding a true alarm. X-T2 was first BLOCKED, before any scoring: the named public repo `dcl-agent-memory-gate@a792c60e` has no latch. Heywood then approved a read-only read of `dynamic_commitment_soft.h` at a stated commit in a private Heywood repo. The scored try is that latch, not a generic substitute.

**What was frozen.** Source: `dynamic_commitment_soft.h` sha256 `abf98d4b6d90c42f27f06ec05c6983d5e6dcc1b516027981cb005ce1c855f28f` (Tater-reported; Link did not open the file; no source lines copied). Latch defaults used: `alpha_e` 0.35, `theta_hi` 0.70, `theta_lo` 0.30; start press 0, armed 0. Choices in `AMBIGUITIES_XT2.md` sha256 `b0c8083681dea79422d3a3cefeb2def54b75faf5d180752e05f6111b2c2bf9d2`, hashed 13:18:39 EST, before scoring code. Build `HASHES_BUILD.sha256` `8c0cb3903e50b1d0fe7b0705c9ee0fad7b403c7d0865bcafc279c6954ba8fe66` (port tests 10/10). Folder `latch_v1/HASHES.sha256` `29e4550ab7d9a32698d443c000e92870d4db2c39325071bfb438d507081ea158`. Link grade: `link/xt2_latch_grade_v1.md`, 1:21 PM EST.

**The bar.** PASS only if all four hold in all four rows: (1) toggle drop ≥ 50% vs plain E5; (2) share of normal (None) windows flagged ≤ 0.05; (3) T3 unflagged no worse than E5 (73, 43, 8, 2); (4) median delay on T3 runs ≤ E5's median + 1. No rescue. One scoring run.

**Headline numbers** (from `latch_v1/TABLE.md` and Link's grade):

| row | toggles E5 → latch (drop) | (1) | None share E5 / latch | (2) | T3 unfl E5 / latch | (3) | median delay E5 / latch | (4) | caught T2+T3 E5 / latch |
|---|---|---|---|---|---|---|---|---|---|
| INCART_B2 1024 | 8324 → 1081 (87.0%) | ok | 0.0500 / 0.0920 | FAIL | 73 / 113 | FAIL | 0 / 1 | ok | 0.791 / 0.497 |
| INCART_B2 4096 | 1943 → 290 (85.1%) | ok | 0.0499 / 0.0917 | FAIL | 43 / 68 | FAIL | 0 / 1 | ok | 0.799 / 0.367 |
| DS1 1024 | 2026 → 257 (87.3%) | ok | 0.0499 / 0.0672 | FAIL | 8 / 32 | FAIL | 0 / 1 | ok | 0.871 / 0.609 |
| DS1 4096 | 572 → 83 (85.5%) | ok | 0.0499 / 0.0839 | FAIL | 2 / 11 | FAIL | 0 / 0 | ok | 0.913 / 0.562 |

Bars (1) and (4) held in every row (toggle drop 85–87%; delay +1 or 0). Bars (2) and (3) failed in every row (normal-flag share 6.7–9.2%; T3 unflagged 73→113, 43→68, 8→32, 2→11).

**Verdict.** FAIL.

**What it rules out.** This Schmitt hold/rearm rule, driven by E5 scores with eligibility = "E5 score > the row's 5% cutoff," cuts chatter but raises false alarms and misses more T3 windows, so it fails the frozen bar on these rows. It does not test full DCL: the file's tension and correlation inputs were not available, so those gates were not simulated.

**Report-only / scope.** Step 0 is N/A: the header gives no synthetic case, so this is not "passed synthetic." Port unit tests were build checks only. The latch starts disarmed and needs a run of eligible windows to fire, then holds the alarm on after an excursion; short T3 runs were missed. T3 runs never flagged: E5 / latch = 19 / 41, 22 / 37, 0 / 14, 1 / 7.

**Disclosures.** The first X-T2 freeze, in `xt_v1/AMBIGUITIES.md` and `xt2/BLOCKED.md`, was BLOCKED because no latch was present in `dcl-agent-memory-gate`. The scored run was the later, approved private-repo read. One scoring run.

---

## 3. X-T3 — odd residuals only

**Idea and why.** On Heywood's ask (voice, 1:16 PM ET, relayed by Link): keep only the odd residual steps from the dual-residual core `03a010d1.py` (pairs of samples `(2ms, 2ms+s)`), and apply the 512-step cap to kept steps. The claim to test was that 512 odd steps would cover all 1024 samples (lifting the "513-sample cap"), and that even steps were a copy or a mirror of odd ones, so dropping them should not lose signal.

**What was frozen.** Choices in `xt3_v1/AMBIGUITIES_XT3.md` sha256 `030c88f1f98689b88d3932bbf8ec0926ac663f276d9d82ff7b685cd093c879d3`, hashed 13:20:43 EST, before any X-T3 code or real-data/label read. Core copy `core_03a010d1.py` sha256 `4f00d50de996e764227afca07692edb98eede66ae1318546f663febb3f88b6b7`. Build `HASHES_BUILD.sha256` `14827bce292bbcec96aa65b5ef6ab59a6e9ff0165d34dc202c605fd23065ad8d` (synth 10/10). Folder `xt3_v1/HASHES.sha256` `3417bb38d40c24579a0c980433c2146c3f47a15d9caa7d403115e4f1c46b2db2`. Link grade: `link/xt3_grade_and_ds2_incident_v1.md`, 1:25 PM EST. X-T3 does not re-grade X-T1 (that FAIL stands).

**The bar.** Premise: evens are a copy or a mirror of odds only if every row meets the copy or mirror thresholds (sign agreement or sign mirror ≥ 0.95, with matching correlation). Test D (ODD vs FULL on the core's `|sigma_delta|` if confirmed, else 0): in every row, ODD T3 unflagged ≤ FULL and AUC_ODD ≥ AUC_FULL − 0.01; INCART rows also need the I31+I42+I43 trio no worse. PASS only if all of that holds. No absolute efficacy bar. No rescue. One scoring run. E2, E5 and X-T1 recipe F were BLOCKED for an odd-only reading: their code has no cap or stride, and inventing one was not allowed.

**Headline numbers** (from `xt3_v1/TABLE.md` and Link's grade).

Premise: NEITHER in all four rows (sign agreement 0.608 / 0.551 / 0.545 / 0.544; sign mirror 0.153 / 0.338 / 0.236 / 0.377). Link's summary: sign agreement 0.54–0.61, mirror 0.15–0.38.

Test D:

| row | AUC ODD / FULL | caught ODD / FULL | T3 unfl ODD / FULL | trio I31+I42+I43 ODD / FULL | bar |
|---|---|---|---|---|---|
| INCART 1024 | 0.5153 / 0.5158 | 0.0572 / 0.0652 | 386 / 374 | 60+28+3=91 / 61+22+2=85 | FAIL (T3, trio) |
| INCART 4096 | 0.4941 / 0.4913 | 0.0298 / 0.0388 | 153 / 152 | 27+11+1=39 / 28+11+2=41 | FAIL (T3) |
| DS1 1024 | 0.4939 / 0.4948 | 0.0510 / 0.0417 | 129 / 130 | n/a | ok |
| DS1 4096 | 0.5137 / 0.5100 | 0.0369 / 0.0612 | 58 / 58 | n/a | ok |

Link: AUC 0.49–0.52 in both arms (chance). FAIL on INCART 1024 and 4096 under the frozen rule. FULL is also at chance, so the core's `sigma_delta` does not separate T3 here in either reading.

Cap / stride (geometry of every window at a given N): at N=1024, ODD removes the cap and covers all 1024 samples (FULL touched 513, spanned 513, cap binds; ODD touched 1024, spanned 1024, cap does not bind). At N=4096, ODD is worse: spanned 4089 → 2304, with 255 new interior gaps. Both versions leave 3584 samples untouched. Odd-only fixes the cap, not the stride.

**Verdict.** FAIL on test D. Premise does not hold. E2/E5/X-T1 under ODD remain BLOCKED.

**What it rules out.** On these rows, even residual steps are not a copy or a mirror of odd ones. Restricting the `03a010d1` evidence() score to odd steps does not improve on FULL; both arms are near chance. Odd-only lifts the N=1024 cap, but it does not fix N=4096 stride blind spots (coverage gets worse). It does not supply an odd-only version of E2, E5 or X-T1.

**Report-only.** Arm U (FULL with the cap lifted, all steps kept): at N=1024, INCART AUC 0.5173, caught 0.0631, T3 unflagged 379, trio 84; DS1 0.4990 / 0.0494 / 133. At N=4096, U is identical to FULL (the cap never binds). FULL vs ODD `|sigma|` Spearman 0.85 / 0.78 / 0.83 / 0.73; same talent 0.80 / 0.77 / 0.78 / 0.78. The off-parity lag control matched the odd/even sign-agreement numbers, so the odd/even pairing is not special.

**Disclosures.** The synthetic test was fixed after a 9/10 run (a float-equality bug in the test; test signals switched to integer residuals; core unchanged). Link logged this as the second build-stage test change of the day (X-T1 was the first). Allowed before scoring, and logged.

**X-T3 broad-search incident, as Link logged it.** About 13:17, Tater ran a content search for the string `03a010d1` across the shared workspace, which includes Purp's `DS2_N*.csv` (dataset_v0, v1), and filtered DS2 paths out of the output. No DS2 name, content or match result reached Tater, and nothing was saved or used. Ruling: the seal is intact (no information about DS2 left the files). Logged as a process breach. New rule: no recursive content search over the whole workspace or filesystem; search named folders only, with DS2 paths excluded before the scan, not after. Heywood may overrule.

---

## 4. E-pool — pooled cross-patient template, E5 per-record normalization kept

**Idea and why.** Change only the template: instead of each record's own eligible-beat median, use a leave-one-patient-out, lead-matched, amplitude-scaled median of other patients' record templates. Everything else stays E5, including dividing each beat's distance by the target record's own median distance (ruling O3). The hope, after I42 and I43, was that a template built from other patients would not be contaminated by a record whose own "normal" beats are half ventricular. That choice deliberately did not test a new scale: the record's own median remained the yardstick.

**What was frozen.** Recipe `epool_recipe_v1/RECIPE_EPOOL.md` sha256 `e9f6cb8a489946df0053cb76642e3ff0ca8c481c588a7c8cb14ce052fe376d4f`. Stage A choices `AMBIGUITIES_EPOOL.md` sha256 `4ca763e3dfba911bb6f0dddfb9378fc7c18a8f433195662e2bdcc670fc76712f`, hashed 14:23:34 ET, before any E-pool code or data. Build `HASHES_BUILD.sha256` `3c66d8c166735ed7b6e23c131f16d3627030883326f132358d2cd698b33fa307`. Stage A `HASHES_STAGEA.sha256` `2c17b4dbbd03378aca32280275bd68db58928c29a43e694048b0ff0745c398a9`. Stage B choices `AMBIG_B.md` sha256 `379d98b4892f143274647ce424fd98bff40ed92eab563671ea7cb15d0d56001e`, hashed 18:18:28 ET, before any label read. Primary results `tater/epool_stageB_v1/`, RESULTS OVERALL `ef9a3ff4a096266918a8bdf853efd5b1a7ab42b26e2137d67398d440b5e26e5c` (`head -n -1` convention; 8 files OK). Blind second, Toni, RESULTS OVERALL `0943874d0769715e9c75966f987615dece0e3a053e92e8e3bfb294adb48fea0a` (from Link's grade; that folder was not opened for this write-up). Link grade: `link/e_pool_grade_v1.md` (`b3d56865…`).

**The bar.** Screen bar (E2 PREREG lines 15–16, as Link applied it): catch at 5% ≥ 0.90 AND 0 truth-T3 unflagged, in all four rows. Recipe bars, mirroring X-T1: (a) I31+I42+I43 T3 unflagged ≤ 35 at N=1024 and ≤ 20 at N=4096; (b) in every row, T3 unflagged ≤ E5 (73, 43, 8, 2), AUC ≥ E5 AUC − 0.01, and abstaining records < 5. PASS needs (a) and (b). No near-miss rescue. One scoring run after a dry run. A PASS would have been a candidate only.

**Headline numbers** (identical in Tater's primary and Toni's blind run; both reproduce E5 exactly: T3 unflagged 73 / 43 / 8 / 2). From Link's grade table, with catch and T3 misses:

| row | AUC (E5) | catch@5% | T3 unflagged (E5) | abstain |
|---|---|---|---|---|
| INCART B2 N=1024 | 0.9263 (0.9493) | 0.694 | 169 (73) | 0 |
| INCART B2 N=4096 | 0.9061 (0.9442) | 0.611 | 70 (43) | 0 |
| DS1 N=1024 | 0.8908 (0.9480) | 0.828 | 50 (8) | 0 |
| DS1 N=4096 | 0.9146 (0.9719) | 0.832 | 11 (2) | 0 |

Bar (a): I31+I42+I43 T3 unflagged 78 at N=1024 (bar ≤ 35; E5 70) and 29 at N=4096 (bar ≤ 20; E5 40). Both fail. Bar (b) fails every row. E-pool is worse than E5 on AUC and on T3 misses in every row. The screen bar is not met on any row.

**Verdict.** FAIL. Link: all four queued recipes have now failed (E7, E6, gap-ratio, and E-pool). The queue is empty.

**What it rules out.** This pooled, leave-one-patient-out template, with E5's per-record median normalization kept, is worse than E5 on these rows. It does not test the idea that the record's own median scale is what blinds I42 and I43: that scale was left unchanged on purpose.

**Report-only** (T3 unflagged, E5 → E-pool; both harnesses agree, from Link's grade): I31 38→48 (N=1024), 27→16 (N=4096); I42 29→29, 11→11 (catch ~0 both); I43 3→1 (N=1024), 2→2 (N=4096); I62 1→9, 0→6 (new misses); I53 and 208 stayed 0→0.

Labeled observations, not a test, from Tater's frozen `epool_stageB_v1/results.json` named-record table:

- I42 was unchanged at 29 and 11 T3 misses, with per-record scaling kept. Catch was 0.0016 at N=1024 and 0 at N=4096.
- I43 catch of positives was 0.9920886075949367 at N=1024 (`n_pos` 632; T3 unflagged 3→1) versus 0 at N=4096 (`n_pos` 158; T3 unflagged stayed 2). That split is unexamined.

**Disclosures.** Tater, as Link accepted them: a dry run on synthetic random labels (`--dryrun`; no real label read; output only to `dry/`, and `dry/results.json` is not a result); one rebuild of `RESULTS.sha256`; harness_v2 report-only limits; data-only reads under `toni/`. Toni, as Link logged them: two aborted attempts before any scoring (load error, NaN label check), fixed and re-hashed, all kept; other blind-scope notes that did not change the agreed headlines. E5 identity passed on all four rows. No `.atr` contamination share was run.

---

## Open hypotheses, untested, Blam's call

No new recipe gets written unless Blam says so. E-pool did not test a change of scale. These remain hypotheses, not findings:

- **Per-record median scale blinding on high-V bigeminy (Lucas).** When about half the beats are ventricular, dividing by the record's own median distance makes V the norm, so the yardstick cannot see what it is measuring. I42 staying at 29 and 11 misses after E-pool changed only the template is consistent with this, but it is not a test.
- **Template-only median (Cheddar-Panama).** Keep the yardstick inside the record, but divide by the median distance of the template beats only, not all kept beats. Cheddar-Panama noted that gap-ratio already separates those beats on I42 and I43, so this would be a cheap next test if Blam wants one. Lucas has said this is the cheapest of the three, and that it would be post hoc and would count only on a fresh held-out set that Blam picks.
- **Outside-record fixed scale (Lucas).** Scale by something outside the record, such as a fixed population scale.
- **Record 223 is a separate blind spot (Purp).** Purp's report-only look found 223's VT running at about 100–133 bpm, which never crossed 0.6 times that record's own 75th-percentile gap, so a rate score can be zero in every T3 window. Its template is only about 4% V, so a template-median fix may leave 223 as it is even if it helps I42 and I43. That too is untested.

A held-out set, if any of these is to be tried, is Blam's to pick and Link's to freeze.
