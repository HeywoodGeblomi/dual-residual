# Validation record for ba2ea57

Core commit: `ba2ea5717863ae70497aed51514f9db2c0653b22`.

This folder is the crew's validation record for that commit.
The packaged files are unchanged.
This README is the only text added for publication.

The core header stays where it is.
It is not copied here.

## Status

Gate 3 FAILED for `ba2ea57`.
Rollout is NO-GO.

All results are exploratory.
They use the MIT-BIH DS1 split.
That split is the de Chazal inter-patient split.

DS2 is sealed on the honor system.
DS2 has not been read.
DS2 is reserved for one scoring run of a single frozen v2 candidate.

## Job 1 contract

Folder: `job1_contract/`.

This is the target contract for the stream.
The stream is MIT-BIH lead MLII, as raw ADC ints.
Tiers come from AAMI EC57 beat classes.
The split is recorded here.

FPR and FNR targets are still PROPOSED placeholders.
They await the owner's sign-off.

## Clean-room statement check

Folders: `cleanroom_statement_check/`, `cleanroom_diff/`, `edge_cases/`, and `bridge/`.

A reference rule was written from the directive text only, without reading the core.
It was frozen before comparison.
It logs 9 places where the directive is silent.

As frozen, it agrees with `ba2ea57` on 10.4% of DS1 windows.
Every disagreement traces to the gap rules.
The main gaps are the σ_Δ definition and the classical definition.
No disagreement is unexplained.

With the gap rules set to the core's behavior, the reference reproduces `ba2ea57` exactly.
That check covers all 329,176 DS1 and edge windows.

Verdict: no code bug was found.
The directive was underspecified.
The core is one faithful reading of it.

Caveat: the independence is on the honor system.
The method follows [2opremio/vp-vnp-statement-check](https://github.com/2opremio/vp-vnp-statement-check).

## Gate 3 mechanism

Folders: `gate3_mechanism/` and `job3_perturbation/`.

A one-sample shift flips 33% of decisions at N=1024.
It flips 28% at N=4096.
The bar is 10% or lower.

Cause: σ_Δ splits zero-crossing events by event index.
Crossings alternate up and down.
So σ_Δ only ever sees one direction.

σ_Δ is exactly 0 on 100% of DS1 windows whose first step is flat or falling.
About 98% of the N=1024 flips coincide with the first step changing.

A copy that only fixes sampling still misses the bar.
That copy reads every sample and drops the 512 cap.
It still flips 32.5% at N=1024 and 33.5% at N=4096.

## σ_Δ-only variants

Folder: `sigma_tinkering/`.

Six tries are logged.
Flips stay at or below 3.1% at N=1024.
At N=4096 they are 20% to 50%.
That spread is attributed to the stride-8 sampling lattice.
None passed every bar.

## Next step

Folders: `sigma_candidates/` and `core_v2_prereg/`.

The owner authorized changing σ_Δ and the sampling together.
Candidates and bars were frozen before any run.
Results are pending.
They are not in this record.

Running try count: 13.
With a further preregistered set, the count goes up to 17.
Any win must be reported with the try count.

## Limits

There is no claim that this detects arrhythmia.
This is not a medical device.
Edge cases are synthetic.

The mechanism test has not been fairly tested yet.
That test asks whether σ_Δ separates ventricular windows from normal windows.
The degeneracy above blocks a fair test.

Data source: MIT-BIH Arrhythmia Database on PhysioNet (Moody & Mark 2001; Goldberger et al. 2000).
https://physionet.org/content/mitdb/1.0.0/

The database is not redistributed here.

This work was prepared with AI assistants.

## Folder index

| Folder | What it holds |
| --- | --- |
| `bridge/` | A small CLI over the unmodified core, Python variants that swap gap rules, and the bridge result log. |
| `cleanroom_diff/` | Comparison harness, edge-window generator, and the written diff summary. Large result tables are not included. |
| `cleanroom_statement_check/` | Frozen clean-room spec, the reference rule, and the freeze hash list. |
| `core_v2_prereg/` | Preregistered v2 candidates. Sampling and σ_Δ change together. No results yet. |
| `edge_cases/` | Synthetic edge-case builder, a case index, and frozen reference outputs. The case waveform files are not included. |
| `gate3_mechanism/` | Mechanism note, the probe program, and the probe output. |
| `gate_logs/` | Gate checklist and the Gate 3 failure log. |
| `job1_contract/` | Target contract, split, stream profile, label builder, and dataset manifest. MIT-BIH waveform files are not included. |
| `job3_perturbation/` | Gate 3 preregistration, perturbation run, results, and one logged fix attempt. |
| `sigma_candidates/` | Three frozen σ_Δ candidates, the final bars, and the freeze hash list. No run results. |
| `sigma_tinkering/` | Six σ_Δ-only tries, the harness, and one result file per try. |

## What was left out

Hash lists were checked and not edited.
Every listed file that is present matches its hash.
Some list entries point at files that were left out on purpose.

Left out:

- MIT-BIH `.hea`, `.dat`, and `.atr` files named in `job1_contract/mitdb_files_v0.sha256` (144 files).
- Synthetic case waveforms named in `edge_cases/manifest.csv` (137 files).
- Large clean-room dumps and ablation scripts named in `cleanroom_diff/MANIFEST.sha256` (result CSVs, the edge suite, and ablation code).
- A second copy of the core header. `bridge/BRIDGE_v1.sha256` names `dual_residual.hpp`. That hash matches the header already in the repo. It is not copied into this folder.
