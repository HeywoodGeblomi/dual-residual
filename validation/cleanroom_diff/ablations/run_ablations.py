#!/usr/bin/env python3
"""Run derived (core-informed) ablation variants against the ba2ea57 core dumps.

NOT a clean-room comparison by itself: the variants peek at the core. The
baseline frozen-ref numbers are read from the already-computed
cleanroom_diff/results/diff_*.csv and phase_shift_ds1.csv, which are not
altered. Exploratory, DS1 only. Rollout remains halted.
"""
from __future__ import annotations

import csv
import hashlib
import importlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DIFF = HERE.parent
JOB4 = DIFF.parent
CACHE = JOB4 / "cache"
RESULTS = DIFF / "results"
OUT = RESULTS / "ablations"
CHEDDAR_DIR = Path("/workspace/cheddar/dr_edgecases_v1")
CHEDDAR_OUT = RESULTS / "cheddar"

EXPECTED_CHEDDAR = {
    "manifest.csv": "521989c70d2852b92aab4a9026b9459055defb997a0394d2487a7dc2d007a129",
    "ref_v1_outputs.csv": "6a23d63486871e9ed14980f95b126b0424f4c8514270e5dc6d0be94a261c0a00",
}

VARIANT_SPECS = [
    ("G1_stride", "variant_G1_stride"),
    ("G9_cap", "variant_G9_cap"),
    ("G2G3_sigma", "variant_G2G3_sigma"),
    ("G4_classical", "variant_G4_classical"),
    ("G5_refuse", "variant_G5_refuse"),
    ("G6_ownership", "variant_G6_ownership"),
    ("G7_precedence", "variant_G7_precedence"),
    ("G8_inclusive", "variant_G8_inclusive"),
    ("all_switched", "variant_all_switched"),
    ("fullsample", "variant_fullsample"),
]
NS = (64, 256, 1024, 4096, 16384)
PHASE_NS = (1024, 4096)
FEAT_TOL = 1e-6


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def load_meta(cache: Path) -> dict:
    return json.loads((cache / "meta.json").read_text())


def load_signals(cache: Path, meta: dict) -> dict[int, np.memmap]:
    deny = set(meta["ds2_denylist"]) | set(meta["excluded_denylist"])
    sigs = {}
    for r in meta["ds1_records"]:
        r = int(r)
        if r in deny:
            raise RuntimeError(f"DS2_SEAL_VIOLATION: {r}")
        sigs[r] = np.memmap(cache / f"rec_{r}.i16", dtype="<i2", mode="r")
    return sigs


def window_list(sigs, record, start, n):
    x = sigs[int(record)]
    end = int(start) + int(n)
    if end > len(x):
        raise RuntimeError(f"window past end record={record} start={start} N={n}")
    return [int(v) for v in x[int(start):end]]


def first_step_sign(values, stride):
    if stride < 1 or stride >= len(values):
        return 0
    d = values[stride] - values[0]
    return (d > 0) - (d < 0)


def core_stride(n: int) -> int:
    return (n // 512) if n > 1024 else 1


# ---- workers --------------------------------------------------------------

_W = {}


def _init_worker(which: str):
    """which: 'ds1' or 'edge'."""
    sys.path.insert(0, str(HERE))
    tiers = {}
    for name, mod in VARIANT_SPECS:
        m = importlib.import_module(mod)
        tiers[name] = m.tier
    _W["tiers"] = tiers
    if which == "ds1":
        meta = load_meta(CACHE)
        _W["sigs"] = load_signals(CACHE, meta)
        _W["edges"] = None
    else:
        edges = {}
        with (DIFF / "edge" / "edge_suite.jsonl").open() as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    edges[rec["id"]] = rec["values"]
        _W["edges"] = edges
        _W["sigs"] = None


def _eval_chunk(jobs):
    tiers = _W["tiers"]
    out = []
    for j in jobs:
        if j["kind"] in ("ds1", "shift"):
            values = window_list(_W["sigs"], j["record"], j["start"], j["N"])
        elif j["kind"] == "edge":
            values = _W["edges"][j["id"]]
        elif j["kind"] == "values":
            values = j["values"]
        else:
            raise RuntimeError(j["kind"])
        rec = {"kind": j["kind"], "key": j["key"], "N": j.get("N", len(values))}
        rec["values_head_stride"] = None  # filled by caller if needed
        rec["_len"] = len(values)
        # first-step signs at core stride and at stride 1 (fullsample)
        rec["fs_core"] = first_step_sign(values, core_stride(len(values)))
        rec["fs_full"] = first_step_sign(values, 1)
        for name, fn in tiers.items():
            t, cl, sd = fn(values)
            rec[f"{name}_tier"] = t
            rec[f"{name}_cl"] = float(cl)
            rec[f"{name}_sd"] = float(sd)
        out.append(rec)
    return out


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def run_jobs(jobs, which, n_jobs=8, chunk_size=400, label="jobs"):
    if not jobs:
        return []
    t0 = time.perf_counter()
    results = []
    with ProcessPoolExecutor(max_workers=n_jobs, initializer=_init_worker, initargs=(which,)) as ex:
        futs = [ex.submit(_eval_chunk, ch) for ch in chunks(jobs, chunk_size)]
        done = 0
        for fut in futs:
            results.extend(fut.result())
            done += 1
            if done == 1 or done == len(futs) or done % 25 == 0:
                sys.stderr.write(f"  {label}: chunks {done}/{len(futs)} rows={len(results)}\n")
                sys.stderr.flush()
    sys.stderr.write(f"  {label}: {len(results)} windows wall={time.perf_counter()-t0:.3f}s\n")
    return results


def agree_counts(rows, core_key, var_key, n_key="N"):
    by = {n: [0, 0] for n in NS}  # agree, total
    all_a = all_t = 0
    for r in rows:
        n = int(r[n_key])
        if n not in by:
            by[n] = [0, 0]
        hit = int(r[core_key] == r[var_key])
        by[n][0] += hit
        by[n][1] += 1
        all_a += hit
        all_t += 1
    return by, all_a, all_t


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CHEDDAR_OUT.mkdir(parents=True, exist_ok=True)

    ds1_core = read_csv(RESULTS / "core_ds1_dump.csv")
    edge_core = read_csv(RESULTS / "core_edge_dump.csv")
    shift_core = read_csv(RESULTS / "core_ds1_shift1.csv")
    base_ds1 = read_csv(RESULTS / "diff_ds1.csv")
    base_edge = read_csv(RESULTS / "diff_edge.csv")
    base_phase = read_csv(RESULTS / "phase_shift_ds1.csv")

    # Baseline frozen-ref agreement per N / class
    base_ds1_by_n = {}
    for n in NS:
        sub = [r for r in base_ds1 if int(r["N"]) == n]
        a = sum(int(r["agree"]) for r in sub)
        base_ds1_by_n[n] = (a, len(sub), a / len(sub) if sub else 0.0)
    base_ds1_all = (
        sum(int(r["agree"]) for r in base_ds1),
        len(base_ds1),
        sum(int(r["agree"]) for r in base_ds1) / len(base_ds1),
    )
    base_edge_by_c = {}
    for r in base_edge:
        c = r["class"]
        a, t = base_edge_by_c.get(c, (0, 0))
        base_edge_by_c[c] = (a + int(r["agree"]), t + 1)
    base_edge_all = (
        sum(int(r["agree"]) for r in base_edge),
        len(base_edge),
        sum(int(r["agree"]) for r in base_edge) / len(base_edge),
    )
    base_flip = {}
    for n in PHASE_NS:
        sub = [r for r in base_phase if int(r["N"]) == n]
        cf = sum(int(r["core_flip"]) for r in sub)
        rf = sum(int(r["ref_flip"]) for r in sub)
        base_flip[n] = {"pairs": len(sub), "core": cf, "ref": rf}

    ds1_jobs = [
        {
            "kind": "ds1",
            "key": (int(r["N"]), int(r["record"]), int(r["window_start"])),
            "N": int(r["N"]),
            "record": int(r["record"]),
            "start": int(r["window_start"]),
        }
        for r in ds1_core
    ]
    shift_jobs = [
        {
            "kind": "shift",
            "key": (int(r["N"]), int(r["record"]), int(r["orig_start"])),
            "N": int(r["N"]),
            "record": int(r["record"]),
            "start": int(r["window_start"]),
        }
        for r in shift_core
        if r.get("skipped", "0") != "1"
    ]
    edge_jobs = [{"kind": "edge", "id": r["id"], "key": r["id"], "N": int(r["N"])} for r in edge_core]

    n_jobs = max(1, min(8, os.cpu_count() or 8))
    ds1_res = run_jobs(ds1_jobs, "ds1", n_jobs=n_jobs, chunk_size=400, label="ablate-ds1")
    shift_res = run_jobs(shift_jobs, "ds1", n_jobs=n_jobs, chunk_size=400, label="ablate-shift")
    edge_res = run_jobs(edge_jobs, "edge", n_jobs=n_jobs, chunk_size=400, label="ablate-edge")

    ds1_map = {r["key"]: r for r in ds1_res}
    shift_map = {r["key"]: r for r in shift_res}
    edge_map = {r["id"] if "id" in r else r["key"]: r for r in edge_res}
    # edge keys
    edge_map = {r["key"]: r for r in edge_res}

    # ---- all_switched exactness ------------------------------------------
    def check_match(core_rows, pred_map, kind):
        tier_mm = []
        feat_mm = []
        for cr in core_rows:
            if kind == "ds1":
                key = (int(cr["N"]), int(cr["record"]), int(cr["window_start"]))
            else:
                key = cr["id"]
            pr = pred_map[key]
            if pr["all_switched_tier"] != cr["core_tier"]:
                tier_mm.append((kind, key, cr["core_tier"], pr["all_switched_tier"],
                                cr["classical"], pr["all_switched_cl"],
                                cr["sigma_delta"], pr["all_switched_sd"]))
            if (abs(pr["all_switched_cl"] - float(cr["classical"])) > FEAT_TOL
                    or abs(pr["all_switched_sd"] - float(cr["sigma_delta"])) > FEAT_TOL):
                feat_mm.append((kind, key, cr["core_tier"], pr["all_switched_tier"],
                                float(cr["classical"]), pr["all_switched_cl"],
                                float(cr["sigma_delta"]), pr["all_switched_sd"]))
        return tier_mm, feat_mm

    ds1_tmm, ds1_fmm = check_match(ds1_core, ds1_map, "ds1")
    edge_tmm, edge_fmm = check_match(edge_core, edge_map, "edge")
    sys.stderr.write(
        f"all_switched DS1 tier_mm={len(ds1_tmm)} feat_mm={len(ds1_fmm)} "
        f"edge tier_mm={len(edge_tmm)} feat_mm={len(edge_fmm)}\n"
    )

    # ---- per-variant agreement -------------------------------------------
    lines = []
    a = lines.append
    a("# Ablation results (exploratory, core-informed, not clean-room)")
    a("")
    a("Each variant switches exactly one frozen-ref assumption to the behavior")
    a("in `dual_residual.hpp` at ba2ea57, except `all_switched` (every rule) and")
    a("`fullsample` (core math, stride 1, no 512 cap). The frozen reference")
    a("files were not modified. Rollout remains halted. DS1 only.")
    a("")
    a("Baseline is the already-computed frozen-ref vs core comparison.")
    a("")

    a("## all_switched vs core (exact-reproduction check)")
    a("")
    a(f"- DS1 tier mismatches: {len(ds1_tmm)} / {len(ds1_core)}")
    a(f"- DS1 feature mismatches (|Δ| > {FEAT_TOL}): {len(ds1_fmm)} / {len(ds1_core)}")
    a(f"- Edge tier mismatches: {len(edge_tmm)} / {len(edge_core)}")
    a(f"- Edge feature mismatches (|Δ| > {FEAT_TOL}): {len(edge_fmm)} / {len(edge_core)}")
    a("")
    residual = ds1_tmm + edge_tmm + ds1_fmm + edge_fmm
    if not residual:
        a("all_switched reproduced the core on every DS1 and edge window (tiers and features). No UNEXPLAINED residual.")
    else:
        a("UNEXPLAINED residual mismatches (up to 20):")
        a("")
        for row in residual[:20]:
            a(f"- `{row}`")
    a("")

    # Build agreement tables
    variant_names = [n for n, _ in VARIANT_SPECS]
    a("## DS1 agreement with the core, by N")
    a("")
    header = "| variant | " + " | ".join(f"N={n} rate (Δ vs frozen)" for n in NS) + " | all |"
    a(header)
    a("|" + "---|" * (2 + len(NS)))
    # frozen baseline row
    cells = []
    for n in NS:
        ag, tot, rate = base_ds1_by_n[n]
        cells.append(f"{rate:.4f} ({ag}/{tot})")
    a("| frozen_ref (baseline) | " + " | ".join(cells) + f" | {base_ds1_all[2]:.4f} ({base_ds1_all[0]}/{base_ds1_all[1]}) |")

    ds1_agree_rows = []
    for vname in variant_names:
        cells = []
        all_a = all_t = 0
        per = {}
        for n in NS:
            ag = tot = 0
            for cr in (r for r in ds1_core if int(r["N"]) == n):
                key = (int(cr["N"]), int(cr["record"]), int(cr["window_start"]))
                hit = int(ds1_map[key][f"{vname}_tier"] == cr["core_tier"])
                ag += hit
                tot += 1
            rate = ag / tot if tot else 0.0
            base = base_ds1_by_n[n][2]
            cells.append(f"{rate:.4f} ({rate-base:+.4f})")
            per[n] = (ag, tot, rate, rate - base)
            all_a += ag
            all_t += tot
        all_rate = all_a / all_t if all_t else 0.0
        cells.append(f"{all_rate:.4f} ({all_rate-base_ds1_all[2]:+.4f}) {all_a}/{all_t}")
        a(f"| {vname} | " + " | ".join(cells) + " |")
        ds1_agree_rows.append({"variant": vname, "per": per, "all": (all_a, all_t, all_rate)})
    a("")

    a("## Edge-suite agreement with the core, by class")
    a("")
    classes = sorted({r["class"] for r in edge_core})
    a("| variant | " + " | ".join(classes) + " | all |")
    a("|" + "---|" * (2 + len(classes)))
    base_cells = []
    for c in classes:
        ag, tot = base_edge_by_c[c]
        base_cells.append(f"{ag/tot:.3f}" if tot else "n/a")
    a("| frozen_ref | " + " | ".join(base_cells) + f" | {base_edge_all[2]:.4f} ({base_edge_all[0]}/{base_edge_all[1]}) |")
    for vname in variant_names:
        cells = []
        all_a = all_t = 0
        for c in classes:
            ag = tot = 0
            for cr in (r for r in edge_core if r["class"] == c):
                hit = int(edge_map[cr["id"]][f"{vname}_tier"] == cr["core_tier"])
                ag += hit
                tot += 1
            cells.append(f"{ag/tot:.3f}" if tot else "n/a")
            all_a += ag
            all_t += tot
        all_rate = all_a / all_t if all_t else 0.0
        cells.append(f"{all_rate:.4f} ({all_rate-base_edge_all[2]:+.4f}) {all_a}/{all_t}")
        a(f"| {vname} | " + " | ".join(cells) + " |")
    a("")

    # ---- phase flips ------------------------------------------------------
    a("## One-sample-shift flip rates on DS1 (N=1024 and N=4096)")
    a("")
    a("A flip is a change in the suggested tier when the window starts one sample later.")
    a("First-step sign is `sign(x[stride]-x[0])` at that variant's stride: core and")
    a("all_switched use the core stride (`1` if N<=1024 else `N/512`); fullsample uses stride 1.")
    a("")
    a("| variant | N=1024 flips (rate) | N=1024 flips with first-step change (share) | N=4096 flips (rate) | N=4096 flips with first-step change (share) |")
    a("|---|---:|---:|---:|---:|")

    # Core from baseline
    def fs_share_core(n):
        sub = [r for r in base_phase if int(r["N"]) == n]
        flips = [r for r in sub if int(r["core_flip"])]
        with_fs = sum(int(r["first_step_changed"]) for r in flips)
        return len(sub), len(flips), with_fs

    phase_stats = {}
    p1024 = fs_share_core(1024)
    p4096 = fs_share_core(4096)
    a(
        f"| core (ba2ea57) | {p1024[1]}/{p1024[0]} ({p1024[1]/p1024[0]:.6f}) | "
        f"{p1024[2]}/{p1024[1]} ({(p1024[2]/p1024[1] if p1024[1] else 0):.6f}) | "
        f"{p4096[1]}/{p4096[0]} ({p4096[1]/p4096[0]:.6f}) | "
        f"{p4096[2]}/{p4096[1]} ({(p4096[2]/p4096[1] if p4096[1] else 0):.6f}) |"
    )
    a(
        f"| frozen_ref | {base_flip[1024]['ref']}/{base_flip[1024]['pairs']} "
        f"({base_flip[1024]['ref']/base_flip[1024]['pairs']:.6f}) | n/a | "
        f"{base_flip[4096]['ref']}/{base_flip[4096]['pairs']} "
        f"({base_flip[4096]['ref']/base_flip[4096]['pairs']:.6f}) | n/a |"
    )

    # Need orig values' first-step already in ds1_res / shift_res
    phase_detail_rows = []
    for vname in variant_names:
        phase_stats[vname] = {}
        cells = []
        for n in PHASE_NS:
            pairs = flips = flips_fs = 0
            stride_kind = "full" if vname == "fullsample" else "core"
            for cr in ds1_core:
                if int(cr["N"]) != n:
                    continue
                key = (int(cr["N"]), int(cr["record"]), int(cr["window_start"]))
                if key not in shift_map:
                    continue
                pairs += 1
                t0 = ds1_map[key][f"{vname}_tier"]
                t1 = shift_map[key][f"{vname}_tier"]
                flip = t0 != t1
                fs0 = ds1_map[key]["fs_full" if stride_kind == "full" else "fs_core"]
                fs1 = shift_map[key]["fs_full" if stride_kind == "full" else "fs_core"]
                fs_changed = fs0 != fs1
                if flip:
                    flips += 1
                    if fs_changed:
                        flips_fs += 1
                if vname in ("fullsample", "all_switched"):
                    phase_detail_rows.append({
                        "variant": vname,
                        "N": n,
                        "record": cr["record"],
                        "orig_start": cr["window_start"],
                        "tier": t0,
                        "tier_shift": t1,
                        "flip": int(flip),
                        "first_step": fs0,
                        "first_step_shift": fs1,
                        "first_step_changed": int(fs_changed),
                        "sigma_delta": ds1_map[key][f"{vname}_sd"],
                        "sigma_delta_shift": shift_map[key][f"{vname}_sd"],
                    })
            phase_stats[vname][n] = {
                "pairs": pairs, "flips": flips, "flips_fs": flips_fs,
                "rate": flips / pairs if pairs else 0.0,
                "fs_share": flips_fs / flips if flips else 0.0,
            }
            cells.append(
                f"{flips}/{pairs} ({flips/pairs if pairs else 0:.6f}) | "
                f"{flips_fs}/{flips} ({(flips_fs/flips if flips else 0):.6f})"
            )
        a(f"| {vname} | " + " | ".join(cells) + " |")
    a("")

    # First-step vs sigma_delta for core (already in DIFF_SUMMARY) and fullsample + all_switched
    a("## σ_Δ == 0 vs first-step direction (unshifted DS1)")
    a("")
    a("Claim: σ_Δ is exactly 0 whenever the first step is flat or falling, because")
    a("the core averages only every other crossing and so sees only one crossing")
    a("direction. Also, 96–99.6% of flips at N<=1024 coincide with a first-step change.")
    a("")
    a("| variant | N | first-step | windows | sigma_delta == 0 | rate |")
    a("|---|---:|---|---:|---:|---:|")

    def sd_by_fs(pred_map, vname, fs_key, n):
        n_le = z_le = n_gt = z_gt = 0
        for cr in ds1_core:
            if int(cr["N"]) != n:
                continue
            key = (int(cr["N"]), int(cr["record"]), int(cr["window_start"]))
            pr = pred_map[key]
            fs = pr[fs_key]
            sd = pr[f"{vname}_sd"]
            if fs <= 0:
                n_le += 1
                if sd == 0.0:
                    z_le += 1
            else:
                n_gt += 1
                if sd == 0.0:
                    z_gt += 1
        return n_le, z_le, n_gt, z_gt

    # core features from the dump, first-step from ds1_map
    for n in PHASE_NS:
        n_le = z_le = n_gt = z_gt = 0
        for cr in ds1_core:
            if int(cr["N"]) != n:
                continue
            key = (int(cr["N"]), int(cr["record"]), int(cr["window_start"]))
            fs = ds1_map[key]["fs_core"]
            sd = float(cr["sigma_delta"])
            if fs <= 0:
                n_le += 1
                if sd == 0.0:
                    z_le += 1
            else:
                n_gt += 1
                if sd == 0.0:
                    z_gt += 1
        a(f"| core | {n} | flat or falling (<=0) | {n_le} | {z_le} | {z_le/n_le if n_le else 0:.6f} |")
        a(f"| core | {n} | rising (>0) | {n_gt} | {z_gt} | {z_gt/n_gt if n_gt else 0:.6f} |")

    for vname, fs_key in (("all_switched", "fs_core"), ("fullsample", "fs_full")):
        for n in PHASE_NS:
            n_le, z_le, n_gt, z_gt = sd_by_fs(ds1_map, vname, fs_key, n)
            a(f"| {vname} | {n} | flat or falling (<=0) | {n_le} | {z_le} | {z_le/n_le if n_le else 0:.6f} |")
            a(f"| {vname} | {n} | rising (>0) | {n_gt} | {z_gt} | {z_gt/n_gt if n_gt else 0:.6f} |")
    a("")

    # Claim summary
    a("### Claim check")
    a("")
    # fullsample N=1024
    fs = phase_stats["fullsample"][1024]
    n_le, z_le, n_gt, z_gt = sd_by_fs(ds1_map, "fullsample", "fs_full", 1024)
    a(
        f"- **core, N=1024:** already reported in DIFF_SUMMARY.md: σ_Δ == 0 on every "
        f"flat/falling first step, and {p1024[2]}/{p1024[1]} "
        f"({p1024[2]/p1024[1] if p1024[1] else 0:.6f}) of flips coincide with a first-step change."
    )
    a(
        f"- **fullsample, N=1024:** σ_Δ == 0 on flat/falling first step: "
        f"{z_le}/{n_le} ({'YES, always' if z_le==n_le and n_le else 'NO'}). "
        f"Rising: {z_gt}/{n_gt}. Flip-with-first-step-change share: "
        f"{fs['flips_fs']}/{fs['flips']} ({fs['fs_share']:.6f}); "
        f"in 96–99.6% band: {'YES' if 0.96 <= fs['fs_share'] <= 0.996 else 'NO'}."
    )
    n_le4, z_le4, n_gt4, z_gt4 = sd_by_fs(ds1_map, "fullsample", "fs_full", 4096)
    fs4 = phase_stats["fullsample"][4096]
    a(
        f"- **fullsample, N=4096** (stride 1, full window): σ_Δ == 0 on flat/falling: "
        f"{z_le4}/{n_le4}. Rising: {z_gt4}/{n_gt4}. "
        f"Flip rate {fs4['rate']:.6f}; first-step-change share of flips {fs4['fs_share']:.6f}."
    )
    a("")
    a("Which single rule causes the phase fragility: see the flip-rate table above.")
    a("A rule that, switched alone, moves the frozen-ref's near-zero flip rate up to")
    a("the core's ~33% / ~28% is the one that introduces the fragility.")
    a("")

    # Write compact per-variant CSVs of agreement only (not all 297k x 10)
    summary_rows = []
    for item in ds1_agree_rows:
        row = {"variant": item["variant"], "split": "ds1_all",
               "agree": item["all"][0], "total": item["all"][1], "rate": f"{item['all'][2]:.6f}",
               "delta_vs_frozen": f"{item['all'][2]-base_ds1_all[2]:.6f}"}
        summary_rows.append(row)
        for n in NS:
            ag, tot, rate, delta = item["per"][n]
            summary_rows.append({
                "variant": item["variant"], "split": f"ds1_N{n}",
                "agree": ag, "total": tot, "rate": f"{rate:.6f}", "delta_vs_frozen": f"{delta:.6f}",
            })
    write_csv(OUT / "agreement_summary.csv", summary_rows,
              ["variant", "split", "agree", "total", "rate", "delta_vs_frozen"])
    write_csv(OUT / "phase_fullsample_allswitched.csv", phase_detail_rows,
              ["variant", "N", "record", "orig_start", "tier", "tier_shift", "flip",
               "first_step", "first_step_shift", "first_step_changed",
               "sigma_delta", "sigma_delta_shift"])

    # ---- Cheddar hard-case set -------------------------------------------
    a("## Cheddar-Panama hard-case set (read-only, exploratory)")
    a("")
    mismatches_hash = []
    cheddar_hashes = {}
    for name, expected in EXPECTED_CHEDDAR.items():
        digest = sha256_file(CHEDDAR_DIR / name)
        cheddar_hashes[name] = digest
        if digest != expected:
            mismatches_hash.append((name, digest, expected))
        a(f"- `{name}` sha256 `{digest}`" + (" **MISMATCH**" if digest != expected else " (verified)"))
    if mismatches_hash:
        a("")
        a("Hash mismatch: aborting Cheddar comparison.")
        (OUT / "ABLATION_SUMMARY.md").write_text("\n".join(lines) + "\n")
        return 3

    # Load frozen ref
    import importlib.util
    ref_path = Path("/workspace/link/dr_cleanroom_frozen_v1/ref.py")
    spec = importlib.util.spec_from_file_location("frozen_ref_cheddar", str(ref_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    frozen_tier = mod.tier

    man = read_csv(CHEDDAR_DIR / "manifest.csv")
    their_ref = read_csv(CHEDDAR_DIR / "ref_v1_outputs.csv")
    their_by_file = {r["file"]: r for r in their_ref}
    core_ch = read_csv(RESULTS / "core_cheddar_dump.csv")
    core_by_file = {r["file"]: r for r in core_ch}

    cheddar_rows = []
    ref_cross_mm = []
    for m in man:
        fn = m["file"]
        path = CHEDDAR_DIR / fn
        values = [int(v) for v in path.read_text().split()]
        # verify listed sha
        got = sha256_file(path)
        if got != m["sha256"]:
            raise RuntimeError(f"Cheddar case file hash mismatch: {fn}")
        t, cl, sd = frozen_tier(values)
        tr = their_by_file[fn]
        # cross-check
        if t != tr["ref_tier"] or abs(cl - float(tr["ref_classical"])) > 1e-9 or abs(sd - float(tr["ref_sigma_delta"])) > 1e-9:
            ref_cross_mm.append((fn, t, tr["ref_tier"], cl, tr["ref_classical"], sd, tr["ref_sigma_delta"]))
        cc = core_by_file[fn]
        cheddar_rows.append({
            "file": fn,
            "case": m["case"],
            "N": int(m["N"]),
            "length": int(m["length"]),
            "core_tier": cc["core_tier"],
            "core_classical": cc["classical"],
            "core_sigma_delta": cc["sigma_delta"],
            "ref_tier": t,
            "ref_classical": f"{cl:.17g}",
            "ref_sigma_delta": f"{sd:.17g}",
            "their_ref_tier": tr["ref_tier"],
            "agree": int(cc["core_tier"] == t),
            "is_shift1": int(m["case"].endswith("_shift1")),
        })
    write_csv(CHEDDAR_OUT / "diff_cheddar.csv", cheddar_rows,
              ["file", "case", "N", "length", "core_tier", "core_classical", "core_sigma_delta",
               "ref_tier", "ref_classical", "ref_sigma_delta", "their_ref_tier", "agree", "is_shift1"])

    n_ch = len(cheddar_rows)
    n_ag = sum(r["agree"] for r in cheddar_rows)
    a(f"- Windows: {n_ch} (manifest rows {len(man)})")
    a(f"- Frozen ref vs Cheddar `ref_v1_outputs.csv`: {n_ch - len(ref_cross_mm)}/{n_ch} match, mismatches={len(ref_cross_mm)}")
    if ref_cross_mm:
        a("  Cross-check mismatches (up to 10):")
        for row in ref_cross_mm[:10]:
            a(f"  - `{row}`")
    a(f"- Frozen ref vs core on Cheddar windows: {n_ag}/{n_ch} agree ({n_ag/n_ch:.4f})")
    a("")
    # confusion
    from collections import Counter as C
    cm = C((r["core_tier"], r["ref_tier"]) for r in cheddar_rows)
    a("Core vs frozen-ref tiers on the 137 windows:")
    a("")
    a("```")
    tiers = ("None", "T1", "T2", "T3")
    a("core\\ref | " + " | ".join(f"{t:>6}" for t in tiers))
    for t in tiers:
        a(f"{t:>8} | " + " | ".join(f"{cm[(t,u)]:6d}" for u in tiers))
    a("```")
    a("")

    # 60 shift pairs: case FOO and FOO_shift1 at same N
    by_pair = {}
    for r in cheddar_rows:
        c = r["case"]
        base = c[:-7] if c.endswith("_shift1") else c
        by_pair.setdefault((base, r["N"]), {})[c] = r
    pairs = []
    for (base, n), d in sorted(by_pair.items()):
        keys = list(d)
        if base in d and (base + "_shift1") in d:
            a0 = d[base]
            a1 = d[base + "_shift1"]
            pairs.append((base, n, a0, a1))
    a(f"- Shift pairs found: {len(pairs)}")
    core_flips = sum(1 for _, _, a0, a1 in pairs if a0["core_tier"] != a1["core_tier"])
    ref_flips = sum(1 for _, _, a0, a1 in pairs if a0["ref_tier"] != a1["ref_tier"])
    a(f"- Core flips on Cheddar shift pairs: {core_flips}/{len(pairs)} ({core_flips/len(pairs) if pairs else 0:.4f})")
    a(f"- Frozen-ref flips on Cheddar shift pairs: {ref_flips}/{len(pairs)} ({ref_flips/len(pairs) if pairs else 0:.4f})")
    a("")
    if pairs:
        a("Pairs that flip (core or ref):")
        a("")
        a("| case | N | core | core_shift | ref | ref_shift |")
        a("|---|---:|---|---|---|---|")
        for base, n, a0, a1 in pairs:
            if a0["core_tier"] != a1["core_tier"] or a0["ref_tier"] != a1["ref_tier"]:
                a(f"| {base} | {n} | {a0['core_tier']} | {a1['core_tier']} | {a0['ref_tier']} | {a1['ref_tier']} |")
        a("")

    text = "\n".join(lines) + "\n"
    (OUT / "ABLATION_SUMMARY.md").write_text(text)
    # also copy a pointer into cheddar out
    (CHEDDAR_OUT / "CHEDDAR_NOTES.md").write_text(
        "See ../ablations/ABLATION_SUMMARY.md for the Cheddar section. "
        "Exploratory, read-only, DS1-unrelated synthetic windows.\n"
    )
    sys.stderr.write(f"wrote {OUT / 'ABLATION_SUMMARY.md'}\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
