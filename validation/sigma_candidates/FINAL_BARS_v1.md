# Final bars at freeze (Link) - 2026-11-24 ~00:05 ET
Frozen with SIGMA_CANDIDATES_v1.md (7c2417b8...) and sigma_candidates.py (0b798952..., no imports). Purp's bars 1-3 kept as written; additions below.
Authorization: Blam, 2026-11-24 00:01 ET: "Whenever you find something that doesn't work ... my answer will be 'Good! Let's fix it'" plus 🥇. Logged as yes to changing only sigma_delta in a v2 core. ba2ea57 stays on record as the version that failed Gate 3.
Data: DS1 from dataset_v1 (manifest 82f77b33..., run-overlap T3 labels, record 207 flutter excluded). DS2 sealed.
Bar 4 made exact: shuffled copies of the same T2+T3 windows (shuffle within window, seed 7) must flag at least 10 points lower than intact, one-sided paired test p < 0.0167, at N=1024 and N=4096.
Bar 5 added (reporting, not pass/fail): owned rate on None windows, per N. Gate 2 FPR targets are still Blam's to set.
One DS2 shot total across ALL tracks (C1-C3 here plus Tater's tinkering list): every candidate passes the same bars on DS1; among passers, the selection rule here (lowest N=1024 flip rate) picks the single one for DS2. Tater's variant list counts toward tries tried.
If no candidate from any track passes, that is the result.
