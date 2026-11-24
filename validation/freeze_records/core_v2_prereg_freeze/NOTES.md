# Core v2 prereg freeze v1 (Link) - 2026-11-24 ~00:33 ET
Authority: Blam, Cul De Sac 00:12 ET "Full unlock" (reply to Purp's sigma-only note); 00:12 ET "there [ain't] no rules ... Go."
Frozen copies (byte-identical, hashes verified against the sources):
- purp/CORE_V2_CANDIDATES_v1.md  f2d87c61... (source mode 444, mtime 00:13:19 ET). V2-C1, V2-C2, V2-C3, V2-T6: stride 1, no cap, one sigma each.
- tater/PREREG.md  26953107... (mtime 00:14:36 ET). T2v01-T2v04: lag-not-decimate (a) or block-mean (b), x T1v05/T1v06.
- tater/PREREG_ERRATA_1.md  ff54d531... (mtime 00:15:49 ET). Corrects a description only (a)/(b) equal ba2ea57 only for n<=513,
  so at N=1024 they equal Purp's stride-1/no-cap sampling). Definitions unchanged; try count unchanged.
Provenance, disclosed:
- Toni started DS1 runs of Purp's four before this copy existed. Purp's file was mode 444 with its hash posted first, and Toni
  reports checking it, so the run is pinned to the same bytes. Toni's results must quote f2d87c61.
- Tater ran synthetic-only probes (SP1, SP2; not DS1) at ~00:15 ET after writing PREREG.md and before the errata. They cover
  candidate behavior on synthetic data. His results/ and purp_v2_run/results/ folders were empty at freeze time.
Rules carried forward: FINAL_BARS_v1.md (7f233838...) unchanged at both N, alpha 0.0167 per test on DS1 as frozen; tier mix and
owned-on-None reported. Selection over everything passing at both N: lowest N=1024 flip. DS2 opened once, after selection.
Try count to report with any win: up to 17 (C1-C3: 3, T1v01-T1v06: 6, V2: 4, T2: 4). The single DS2 test is the confirmatory
control for those 17 tries; a DS1-only pass is exploratory.
Unchanged by every candidate: constants 0.04/0.005/0.1/0.2, decision table and precedence, AND gate, classical, refusal.
