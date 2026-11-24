#!/usr/bin/env python3
"""Differential test: locked Dual Residual core (ba2ea57) vs Link-frozen clean-room ref.

Exploratory, G4-04-style spec-vs-code check. Rollout remains halted. DS1 only.

Loads the frozen reference ONLY from
  /workspace/link/dr_cleanroom_frozen_v1/{ref.py,CLEANROOM_SPEC_v1.md,FROZEN_v1.sha256}
and re-verifies all three sha256 values at startup, refusing to run on mismatch.

--stub uses a self-written STUB tier function (NOT the frozen reference) to
smoke-test joins and outputs on a small subset.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
JOB4 = HERE.parent
DEFAULT_FROZEN = Path("/workspace/link/dr_cleanroom_frozen_v1")
DEFAULT_CACHE = JOB4 / "cache"
DEFAULT_RESULTS = HERE / "results"

EXPECTED_SHA256 = {
    "CLEANROOM_SPEC_v1.md": "fe1fa84dcdf82410b596c2aff05a8d6890c157e02daf02913efb3c277f67c897",
    "ref.py": "effc85ac5363403cfe52724e248f68c346d14b6b9dbeca2bb152fe2a5085922f",
    "FROZEN_v1.sha256": "932fd233f1a426d8dc973ca896e3aafe9a558a75406737c4dddfc57982277976",
}

TIERS = ("None", "T1", "T2", "T3")
NS = (64, 256, 1024, 4096, 16384)
PHASE_NS = (1024, 4096)
FEAT_TOL = 1e-9

# ---------------------------------------------------------------------------
# Hash gate
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen(frozen_dir: Path) -> dict[str, str]:
    got = {}
    mismatches = []
    for name, expected in EXPECTED_SHA256.items():
        path = frozen_dir / name
        if not path.is_file():
            mismatches.append(f"{name}: missing at {path}")
            continue
        digest = sha256_file(path)
        got[name] = digest
        if digest != expected:
            mismatches.append(f"{name}: got {digest}, expected {expected}")
    if mismatches:
        sys.stderr.write("FATAL: frozen-reference hash check failed:\n")
        for m in mismatches:
            sys.stderr.write("  " + m + "\n")
        sys.exit(3)
    return got


# ---------------------------------------------------------------------------
# STUB tier (smoke tests only)
# ---------------------------------------------------------------------------

def stub_tier(x):
    """STUB tier function for smoke-testing compare.py only.

    NOT Purp's clean-room reference and NOT the frozen copy. Deterministic
    and intentionally unlike both the core table and the clean-room rule.
    Used only with --stub.
    """
    n = len(x)
    if n < 3:
        return "None", 0.0, 0.0
    s = [(x[i + 1] > x[i]) - (x[i + 1] < x[i]) for i in range(n - 1)]
    cl = sum(abs(v) for v in s) / len(s)
    sd = (s[0] - s[-1]) / 2.0
    if cl > 0.9 and abs(sd) > 0.1:
        t = "T2"
    elif cl > 0.7:
        t = "T3"
    elif cl > 0.4:
        t = "T1"
    else:
        t = "None"
    return t, float(cl), float(sd)


def load_frozen_tier(ref_path: Path):
    spec = importlib.util.spec_from_file_location("dr_cleanroom_frozen_v1_ref", str(ref_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen ref from {ref_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "tier"):
        raise RuntimeError(f"{ref_path} has no tier()")
    return mod.tier


# ---------------------------------------------------------------------------
# Cache I/O (DS1 only)
# ---------------------------------------------------------------------------

def load_meta(cache: Path) -> dict:
    meta = json.loads((cache / "meta.json").read_text())
    if set(meta["ds2_denylist"]) & set(meta["ds1_records"]):
        raise RuntimeError("meta.json lists a record in both DS1 and the DS2 denylist")
    return meta


def assert_ds1(meta: dict, record: int, context: str) -> None:
    if record in meta["ds2_denylist"]:
        raise RuntimeError(f"DS2_SEAL_VIOLATION: refused record {record} ({context})")
    if record in meta["excluded_denylist"]:
        raise RuntimeError(f"Refused excluded record {record} ({context})")
    if record not in meta["ds1_records"]:
        raise RuntimeError(f"Record {record} is not in DS1 allowlist ({context})")


def load_signals(cache: Path, meta: dict) -> dict[int, np.memmap]:
    sigs = {}
    for r in meta["ds1_records"]:
        assert_ds1(meta, int(r), "load_signals")
        path = cache / f"rec_{int(r)}.i16"
        sigs[int(r)] = np.memmap(path, dtype="<i2", mode="r")
    return sigs


def window_list(sigs: dict[int, np.memmap], record: int, start: int, n: int) -> list[int]:
    x = sigs[int(record)]
    end = int(start) + int(n)
    if end > len(x):
        raise RuntimeError(f"window past end of signal record {record}: start={start} N={n} len={len(x)}")
    return [int(v) for v in x[int(start):end]]


def first_step_sign(values: list[int], stride: int) -> int:
    if stride < 1 or stride >= len(values):
        return 0
    d = values[stride] - values[0]
    return (d > 0) - (d < 0)


def core_stride(n: int) -> int:
    return (n // 512) if n > 1024 else 1


# ---------------------------------------------------------------------------
# Attribution
# ---------------------------------------------------------------------------

def is_tie_free(values: list[int]) -> bool:
    if len(values) < 2:
        return True
    return all(values[i + 1] != values[i] for i in range(len(values) - 1))


def near(a: float, b: float, tol: float = FEAT_TOL) -> bool:
    return abs(a - b) <= tol


def attribute(n: int, values: list[int], core_tier: str, ref_tier: str,
              core_cl: float, ref_cl: float, core_sd: float, ref_sd: float) -> list[str]:
    """Return gap labels for a disagreement. Multiple labels allowed."""
    gaps: list[str] = []
    cl_diff = not near(core_cl, ref_cl)
    sd_diff = not near(core_sd, ref_sd)
    feat_equal = (not cl_diff) and (not sd_diff)
    tie_free = is_tie_free(values)

    if tie_free and (cl_diff or sd_diff):
        gaps.append("G5")
    if cl_diff:
        gaps.append("G4")
        if n >= 1024:
            if "G1" not in gaps:
                gaps.append("G1")
            if "G9" not in gaps:
                gaps.append("G9")
    if sd_diff:
        gaps.append("G2")
        gaps.append("G3")
        if n >= 1024:
            if "G1" not in gaps:
                gaps.append("G1")
            if "G9" not in gaps:
                gaps.append("G9")

    if feat_equal and core_tier != ref_tier:
        # Use the shared feature values (they match).
        cl, sdabs = core_cl, abs(core_sd)
        classical_hi = cl > 0.04
        sd_strict = sdabs > 0.005
        sd_incl = sdabs >= 0.005
        # G6: AND vs OR would disagree when exactly one of the two conditions holds.
        and_strict = classical_hi and sd_strict
        or_strict = classical_hi or sd_strict
        if and_strict != or_strict:
            gaps.append("G6")
        # G7: both T2 and T3 conditions hold; precedence decides T2 vs T3.
        if cl > 0.2 and sdabs > 0.1:
            gaps.append("G7")
        # G8: value exactly at a cutoff, or inclusive vs strict floor would differ.
        if sd_incl != sd_strict:
            gaps.append("G8")
        at_cutoff = (
            near(cl, 0.04) or near(cl, 0.2)
            or near(sdabs, 0.005) or near(sdabs, 0.1)
        )
        if at_cutoff and "G8" not in gaps:
            gaps.append("G8")

    if not gaps:
        gaps.append("UNEXPLAINED")
    return gaps


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

_W = {}


def _init_worker(frozen_dir: str, cache_dir: str, edge_path: str, use_stub: bool):
    _W["stub"] = use_stub
    if use_stub:
        _W["tier"] = stub_tier
    else:
        _W["tier"] = load_frozen_tier(Path(frozen_dir) / "ref.py")
    meta = load_meta(Path(cache_dir))
    _W["meta"] = meta
    _W["sigs"] = load_signals(Path(cache_dir), meta)
    edges = {}
    if edge_path:
        with open(edge_path) as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                edges[rec["id"]] = rec["values"]
    _W["edges"] = edges


def _eval_chunk(jobs: list[dict]) -> list[dict]:
    tier = _W["tier"]
    out = []
    t0 = time.perf_counter()
    for j in jobs:
        kind = j["kind"]
        if kind in ("ds1", "shift"):
            assert_ds1(_W["meta"], int(j["record"]), kind)
            values = window_list(_W["sigs"], j["record"], j["start"], j["N"])
        elif kind == "edge":
            values = _W["edges"][j["id"]]
        elif kind == "values":
            values = j["values"]
        else:
            raise RuntimeError(f"unknown job kind {kind}")
        t1 = time.perf_counter()
        t, cl, sd = tier(values)
        t2 = time.perf_counter()
        rec = {
            "kind": kind,
            "key": j.get("key"),
            "id": j.get("id"),
            "N": j.get("N", len(values)),
            "record": j.get("record"),
            "start": j.get("start"),
            "tier": t,
            "classical": float(cl),
            "sigma_delta": float(sd),
            "eval_s": t2 - t1,
            "wall_s": t2 - t1,  # filled per-item; chunk wall added below
        }
        rec["_values"] = values  # needed for attribution / first-step on small jobs? too heavy
        out.append(rec)
        # Never ship raw values back for DS1 (memory). Re-load in parent if needed.
        if kind in ("ds1", "shift"):
            rec.pop("_values", None)
        # For edge, parent can reload from jsonl; drop values.
        rec.pop("_values", None)
    elapsed = time.perf_counter() - t0
    if out:
        share = elapsed / len(out)
        for rec in out:
            rec["chunk_share_s"] = share
    return out


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def run_jobs(jobs, frozen_dir, cache, edge_path, use_stub, n_jobs, chunk_size, label):
    if not jobs:
        return []
    t0 = time.perf_counter()
    results = []
    init_args = (str(frozen_dir), str(cache), str(edge_path) if edge_path else "", use_stub)
    if n_jobs <= 1 or len(jobs) < 32:
        _init_worker(*init_args)
        for ch in chunks(jobs, chunk_size):
            results.extend(_eval_chunk(ch))
    else:
        # Fork so workers inherit nothing sensitive; they reload from paths.
        ctx_ok = True
        try:
            import multiprocessing as mp
            # Default fork on Linux is fine; be explicit.
            mp.set_start_method("fork", force=False)
        except RuntimeError:
            ctx_ok = True  # already set
        with ProcessPoolExecutor(
            max_workers=n_jobs,
            initializer=_init_worker,
            initargs=init_args,
        ) as ex:
            futs = [ex.submit(_eval_chunk, ch) for ch in chunks(jobs, chunk_size)]
            done = 0
            total = len(futs)
            for fut in futs:
                results.extend(fut.result())
                done += 1
                if done == 1 or done == total or done % 20 == 0:
                    sys.stderr.write(f"  {label}: chunks {done}/{total} rows={len(results)}\n")
                    sys.stderr.flush()
    wall = time.perf_counter() - t0
    eval_sum = sum(r["eval_s"] for r in results)
    sys.stderr.write(
        f"  {label}: windows={len(results)} wall={wall:.3f}s "
        f"sum_eval={eval_sum:.3f}s mean_eval={eval_sum / max(len(results), 1):.6f}s "
        f"jobs={n_jobs} stub={use_stub}\n"
    )
    sys.stderr.flush()
    return results, wall, eval_sum


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def ffloat(s) -> float:
    return float(s)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def confusion(rows, a="core_tier", b="ref_tier"):
    m = {t: {u: 0 for u in TIERS} for t in TIERS}
    for r in rows:
        m[r[a]][r[b]] += 1
    return m


def fmt_matrix(m) -> str:
    lines = ["core\\ref | " + " | ".join(f"{t:>6}" for t in TIERS) + " |  total"]
    lines.append("---------|-" + "-|-".join(["------"] * 4) + "-|------")
    for t in TIERS:
        row = [m[t][u] for u in TIERS]
        lines.append(f"{t:>8} | " + " | ".join(f"{v:6d}" for v in row) + f" | {sum(row):6d}")
    totals = [sum(m[t][u] for t in TIERS) for u in TIERS]
    lines.append(f"{'total':>8} | " + " | ".join(f"{v:6d}" for v in totals) + f" | {sum(totals):6d}")
    return "\n".join(lines)


def agree_rate(rows) -> tuple[int, int, float]:
    n = len(rows)
    ok = sum(1 for r in rows if r["core_tier"] == r["ref_tier"])
    return ok, n, (ok / n if n else 0.0)


def write_summary(path: Path, ctx: dict) -> None:
    lines = []
    a = lines.append
    a("# DIFF_SUMMARY")
    a("")
    a("Exploratory G4-04-style spec-vs-code check. Rollout remains halted. DS1 only.")
    if ctx.get("stub"):
        a("")
        a("**STUB RUN.** Outputs in this directory were produced with a self-written")
        a("stub `tier()` function, not the frozen clean-room reference. Do not use")
        a("these numbers as the real comparison.")
    a("")
    a("## Hashes verified at startup")
    a("")
    a(f"- Frozen dir: `{ctx['frozen_dir']}`")
    for name, digest in ctx["hashes"].items():
        a(f"- `{name}`: `{digest}`")
    a(f"- Core dump DS1: `{ctx['sha_ds1']}`")
    a(f"- Core dump edge: `{ctx['sha_edge']}`")
    a(f"- Edge suite: `{ctx['sha_edge_suite']}`")
    a("")
    a("## DS1 agreement by N")
    a("")
    a("| N | agree | total | rate |")
    a("|---:|---:|---:|---:|")
    for n in NS:
        sub = ctx["ds1_by_n"][n]
        ok, tot, rate = agree_rate(sub)
        a(f"| {n} | {ok} | {tot} | {rate:.6f} |")
    ok, tot, rate = agree_rate(ctx["ds1"])
    a(f"| all | {ok} | {tot} | {rate:.6f} |")
    a("")
    a("## DS1 confusion matrix (core rows, ref columns)")
    a("")
    a("```")
    a(fmt_matrix(confusion(ctx["ds1"])))
    a("```")
    a("")
    a("## Edge-suite agreement by class")
    a("")
    a("| class | agree | total | rate |")
    a("|---|---:|---:|---:|")
    classes = sorted({r["class"] for r in ctx["edge"]})
    for cls in classes:
        sub = [r for r in ctx["edge"] if r["class"] == cls]
        ok, tot, rate = agree_rate(sub)
        a(f"| {cls} | {ok} | {tot} | {rate:.6f} |")
    ok, tot, rate = agree_rate(ctx["edge"])
    a(f"| all | {ok} | {tot} | {rate:.6f} |")
    a("")
    a("## Edge confusion matrix (core rows, ref columns)")
    a("")
    a("```")
    a(fmt_matrix(confusion(ctx["edge"])))
    a("```")
    a("")
    a("## Disagreement gap attribution")
    a("")
    a("A disagreement may carry more than one gap. UNEXPLAINED means no heuristic fired.")
    a("")
    a("### DS1")
    a("")
    a("| gap | disagreements tagged |")
    a("|---|---:|")
    for g, c in ctx["ds1_gap_counts"].most_common():
        a(f"| {g} | {c} |")
    a(f"| (disagreements) | {ctx['ds1_n_disagree']} |")
    a("")
    a("### Edge")
    a("")
    a("| gap | disagreements tagged |")
    a("|---|---:|")
    for g, c in ctx["edge_gap_counts"].most_common():
        a(f"| {g} | {c} |")
    a(f"| (disagreements) | {ctx['edge_n_disagree']} |")
    a("")
    a("## UNEXPLAINED disagreements")
    a("")
    un_ds1 = ctx["ds1_unexplained"]
    un_edge = ctx["edge_unexplained"]
    a(f"DS1: {len(un_ds1)}  |  edge: {len(un_edge)}")
    a("")
    if un_ds1:
        a("DS1 examples (up to 20):")
        a("")
        a("| N | record | window_start | core_tier | ref_tier | core_classical | ref_classical | core_sigma_delta | ref_sigma_delta |")
        a("|---:|---:|---:|---|---|---:|---:|---:|---:|")
        for r in un_ds1[:20]:
            a(
                f"| {r['N']} | {r['record']} | {r['window_start']} | {r['core_tier']} | {r['ref_tier']} "
                f"| {r['core_classical']} | {r['ref_classical']} | {r['core_sigma_delta']} | {r['ref_sigma_delta']} |"
            )
        a("")
    else:
        a("No UNEXPLAINED DS1 disagreements.")
        a("")
    if un_edge:
        a("Edge examples (up to 20):")
        a("")
        a("| id | class | N | core_tier | ref_tier | core_classical | ref_classical | core_sigma_delta | ref_sigma_delta |")
        a("|---|---|---:|---|---|---:|---:|---:|---:|")
        for r in un_edge[:20]:
            a(
                f"| {r['id']} | {r['class']} | {r['N']} | {r['core_tier']} | {r['ref_tier']} "
                f"| {r['core_classical']} | {r['ref_classical']} | {r['core_sigma_delta']} | {r['ref_sigma_delta']} |"
            )
        a("")
    else:
        a("No UNEXPLAINED edge disagreements.")
        a("")
    a("## Gate 3 one-sample-shift phase test (DS1, N=1024 and N=4096)")
    a("")
    a("Each window is compared with the same record starting one sample later,")
    a("only when the shifted window fits in the signal. A flip is a change in the")
    a("suggested tier. First-step sign is `sign(x[stride] - x[0])` at the *core*")
    a("stride (`1` when N<=1024, else `N/512`). A first-step change means that")
    a("sign differs between the unshifted and shifted windows.")
    a("")
    a("| N | pairs | core flips | core flip rate | ref flips | ref flip rate | core flips with first-step change | share |")
    a("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for n in PHASE_NS:
        p = ctx["phase"][n]
        a(
            f"| {n} | {p['pairs']} | {p['core_flips']} | {p['core_rate']:.6f} | "
            f"{p['ref_flips']} | {p['ref_rate']:.6f} | {p['core_flips_fs']} | {p['core_fs_share']:.6f} |"
        )
    a("")
    a("### sigma_delta == 0 vs first-step direction (core, unshifted DS1 windows)")
    a("")
    a("Claim under test: σ_Δ is exactly 0 whenever the first step is flat or falling,")
    a("and 96–99.6% of flips at N<=1024 coincide with the first step changing.")
    a("")
    a("| N | first-step | windows | sigma_delta == 0 | rate |")
    a("|---:|---|---:|---:|---:|")
    for n in PHASE_NS:
        s = ctx["sd_by_first"][n]
        for label, key in (("flat or falling (<=0)", "le0"), ("rising (>0)", "gt0")):
            tot = s[f"n_{key}"]
            z = s[f"z_{key}"]
            a(f"| {n} | {label} | {tot} | {z} | {(z / tot if tot else 0):.6f} |")
    a("")
    a("Claim check (core, N=1024):")
    c1024 = ctx["phase"][1024]
    s1024 = ctx["sd_by_first"][1024]
    always_zero = (s1024["z_le0"] == s1024["n_le0"]) and s1024["n_le0"] > 0
    a(f"- σ_Δ exactly 0 on every flat/falling first step at N=1024: **{'YES' if always_zero else 'NO'}**")
    a(f"  ({s1024['z_le0']}/{s1024['n_le0']}). Rising first step: {s1024['z_gt0']}/{s1024['n_gt0']} have σ_Δ == 0.")
    share = c1024["core_fs_share"]
    in_band = 0.96 <= share <= 0.996
    a(f"- Share of N=1024 core flips coinciding with a first-step change: **{share:.6f}** "
      f"({c1024['core_flips_fs']}/{c1024['core_flips']}); in the claimed 96–99.6% band: **{'YES' if in_band else 'NO'}**.")
    a("")
    a("## Runtime")
    a("")
    a(f"- Ref (or stub) DS1: wall {ctx['ds1_wall']:.3f}s, sum of per-window eval {ctx['ds1_eval']:.3f}s, "
      f"mean {ctx['ds1_eval'] / max(len(ctx['ds1']), 1):.6f}s/window")
    a(f"- Ref (or stub) edge: wall {ctx['edge_wall']:.3f}s, sum of per-window eval {ctx['edge_eval']:.3f}s, "
      f"mean {ctx['edge_eval'] / max(len(ctx['edge']), 1):.6f}s/window")
    a(f"- Ref (or stub) shift: wall {ctx['shift_wall']:.3f}s, sum of per-window eval {ctx['shift_eval']:.3f}s")
    a(f"- Workers: {ctx['jobs']}")
    a("")
    path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def pick_stub_subset(ds1_core, edge_core, limit):
    """~limit windows total: half DS1 (evenly by N), half edge (by class)."""
    n_ds1 = max(1, limit // 2)
    n_edge = max(1, limit - n_ds1)
    per_n = max(1, n_ds1 // len(NS))
    picked_ds1 = []
    for n in NS:
        sub = [r for r in ds1_core if int(r["N"]) == n]
        if not sub:
            continue
        step = max(1, len(sub) // per_n)
        picked_ds1.extend(sub[::step][:per_n])
    picked_ds1 = picked_ds1[:n_ds1]
    by_c = defaultdict(list)
    for r in edge_core:
        by_c[r["class"]].append(r)
    picked_edge = []
    classes = sorted(by_c)
    i = 0
    while len(picked_edge) < n_edge and any(by_c[c] for c in classes):
        c = classes[i % len(classes)]
        if by_c[c]:
            # even spacing
            step = max(1, len(by_c[c]) // max(1, n_edge // len(classes)))
            picked_edge.append(by_c[c].pop(0) if step == 1 else by_c[c].pop(0))
            # pop already from front; after first take, skip ahead by dropping
            drop = min(step - 1, len(by_c[c]))
            del by_c[c][:drop]
        i += 1
    return picked_ds1, picked_edge[:n_edge]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compare ba2ea57 core dumps with the frozen clean-room ref.")
    p.add_argument("--frozen-dir", type=Path, default=DEFAULT_FROZEN)
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--core-ds1", type=Path, default=DEFAULT_RESULTS / "core_ds1_dump.csv")
    p.add_argument("--core-edge", type=Path, default=DEFAULT_RESULTS / "core_edge_dump.csv")
    p.add_argument("--core-shift", type=Path, default=DEFAULT_RESULTS / "core_ds1_shift1.csv")
    p.add_argument("--edge-suite", type=Path, default=HERE / "edge" / "edge_suite.jsonl")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_RESULTS)
    p.add_argument("--jobs", type=int, default=max(1, os.cpu_count() or 1))
    p.add_argument("--chunk-size", type=int, default=500)
    p.add_argument("--stub", action="store_true", help="Use the STUB tier, not the frozen reference.")
    p.add_argument("--limit", type=int, default=0, help="Max windows for a stub/smoke run (e.g. 200).")
    args = p.parse_args(argv)

    hashes = verify_frozen(args.frozen_dir)
    sys.stderr.write("frozen hashes OK\n")
    for k, v in hashes.items():
        sys.stderr.write(f"  {k} {v}\n")

    meta = load_meta(args.cache)
    sigs = load_signals(args.cache, meta)

    ds1_core = read_csv(args.core_ds1)
    edge_core = read_csv(args.core_edge)
    shift_core = read_csv(args.core_shift)
    # Confirm DS1 keys exist and are unique.
    ds1_index = {}
    for r in ds1_core:
        key = (int(r["N"]), int(r["record"]), int(r["window_start"]))
        ds1_index[key] = r

    if args.stub:
        if args.limit <= 0:
            args.limit = 200
        ds1_core, edge_core = pick_stub_subset(ds1_core, edge_core, args.limit)
        ds1_index = {(int(r["N"]), int(r["record"]), int(r["window_start"])): r for r in ds1_core}
        # Restrict shift rows to those origins we kept.
        keep = {(int(r["N"]), int(r["record"]), int(r["window_start"])) for r in ds1_core}
        shift_core = [r for r in shift_core if (int(r["N"]), int(r["record"]), int(r["orig_start"])) in keep]
        sys.stderr.write(
            f"STUB mode: ds1={len(ds1_core)} edge={len(edge_core)} shift={len(shift_core)}\n"
        )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.stub:
        (out_dir / "STUB_ONLY.txt").write_text(
            "STUB SMOKE-TEST OUTPUTS. Produced with a self-written stub tier(), "
            "not the frozen clean-room reference. Do not treat as the real comparison.\n"
        )

    # Build jobs
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
    edge_jobs = [{"kind": "edge", "id": r["id"], "N": int(r["N"]), "key": r["id"]} for r in edge_core]
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

    # Only the edge pass needs the jsonl in workers (saves ~27MB * jobs on DS1/shift).
    ds1_res, ds1_wall, ds1_eval = run_jobs(
        ds1_jobs, args.frozen_dir, args.cache, "", args.stub, args.jobs, args.chunk_size, "ds1-ref"
    )
    edge_res, edge_wall, edge_eval = run_jobs(
        edge_jobs, args.frozen_dir, args.cache, args.edge_suite, args.stub, args.jobs, args.chunk_size, "edge-ref"
    )
    shift_res, shift_wall, shift_eval = run_jobs(
        shift_jobs, args.frozen_dir, args.cache, "", args.stub, args.jobs, args.chunk_size, "shift-ref"
    )

    ds1_ref = {r["key"]: r for r in ds1_res}
    edge_ref = {r["id"]: r for r in edge_res}
    shift_ref = {r["key"]: r for r in shift_res}

    # Join DS1
    diff_ds1 = []
    disagreements_ds1 = []
    ds1_gap_counts = Counter()
    ds1_unexplained = []
    # Cache values only when we disagree or need first-step (phase N). That's still a lot
    # of first-step windows; first-step only needs two samples at the stride, cheap.
    for cr in ds1_core:
        n = int(cr["N"])
        rec = int(cr["record"])
        start = int(cr["window_start"])
        key = (n, rec, start)
        rr = ds1_ref[key]
        row = {
            "N": n,
            "record": rec,
            "window_start": start,
            "core_tier": cr["core_tier"],
            "ref_tier": rr["tier"],
            "core_confirmed": cr["confirmed"],
            "core_classical": cr["classical"],
            "ref_classical": f"{rr['classical']:.17g}",
            "core_sigma_delta": cr["sigma_delta"],
            "ref_sigma_delta": f"{rr['sigma_delta']:.17g}",
            "path": cr.get("path", "base"),
            "status": cr.get("status", "ok"),
            "agree": int(cr["core_tier"] == rr["tier"]),
            "gaps": "",
        }
        if cr["core_tier"] != rr["tier"]:
            values = window_list(sigs, rec, start, n)
            gaps = attribute(
                n, values, cr["core_tier"], rr["tier"],
                ffloat(cr["classical"]), rr["classical"],
                ffloat(cr["sigma_delta"]), rr["sigma_delta"],
            )
            row["gaps"] = "|".join(gaps)
            disagreements_ds1.append(row)
            ds1_gap_counts.update(gaps)
            if "UNEXPLAINED" in gaps:
                ds1_unexplained.append(row)
        diff_ds1.append(row)

    # Join edge
    edge_values = {}
    if edge_jobs:
        with args.edge_suite.open() as f:
            want = {r["id"] for r in edge_core}
            for line in f:
                if not line.strip():
                    continue
                recj = json.loads(line)
                if recj["id"] in want:
                    edge_values[recj["id"]] = recj["values"]

    diff_edge = []
    disagreements_edge = []
    edge_gap_counts = Counter()
    edge_unexplained = []
    edge_core_by_id = {r["id"]: r for r in edge_core}
    for cr in edge_core:
        eid = cr["id"]
        rr = edge_ref[eid]
        n = int(cr["N"])
        row = {
            "id": eid,
            "class": cr["class"],
            "N": n,
            "core_tier": cr["core_tier"],
            "ref_tier": rr["tier"],
            "core_confirmed": cr["confirmed"],
            "core_classical": cr["classical"],
            "ref_classical": f"{rr['classical']:.17g}",
            "core_sigma_delta": cr["sigma_delta"],
            "ref_sigma_delta": f"{rr['sigma_delta']:.17g}",
            "path": cr.get("path", "base"),
            "status": cr.get("status", "ok"),
            "agree": int(cr["core_tier"] == rr["tier"]),
            "gaps": "",
        }
        if cr["core_tier"] != rr["tier"]:
            values = edge_values[eid]
            gaps = attribute(
                n, values, cr["core_tier"], rr["tier"],
                ffloat(cr["classical"]), rr["classical"],
                ffloat(cr["sigma_delta"]), rr["sigma_delta"],
            )
            row["gaps"] = "|".join(gaps)
            disagreements_edge.append(row)
            edge_gap_counts.update(gaps)
            if "UNEXPLAINED" in gaps:
                edge_unexplained.append(row)
        diff_edge.append(row)

    # Phase test
    phase_rows = []
    phase_stats = {n: {} for n in PHASE_NS}
    sd_by_first = {n: {"n_le0": 0, "z_le0": 0, "n_gt0": 0, "z_gt0": 0} for n in PHASE_NS}
    # Also count on ALL unshifted DS1 windows at those N (not just stub subset when full).
    for cr in ds1_core:
        n = int(cr["N"])
        if n not in PHASE_NS:
            continue
        rec = int(cr["record"])
        start = int(cr["window_start"])
        values = window_list(sigs, rec, start, n)
        stride = core_stride(n)
        fs = first_step_sign(values, stride)
        sd = ffloat(cr["sigma_delta"])
        bucket = "le0" if fs <= 0 else "gt0"
        sd_by_first[n][f"n_{bucket}"] += 1
        if sd == 0.0:
            sd_by_first[n][f"z_{bucket}"] += 1

    shift_core_by = {(int(r["N"]), int(r["record"]), int(r["orig_start"])): r for r in shift_core}
    for cr in ds1_core:
        n = int(cr["N"])
        if n not in PHASE_NS:
            continue
        rec = int(cr["record"])
        start = int(cr["window_start"])
        sc = shift_core_by.get((n, rec, start))
        if sc is None or sc.get("skipped", "0") == "1":
            continue
        rr = ds1_ref[(n, rec, start)]
        rs = shift_ref.get((n, rec, start))
        if rs is None:
            continue
        values0 = window_list(sigs, rec, start, n)
        values1 = window_list(sigs, rec, int(sc["window_start"]), n)
        stride = core_stride(n)
        fs0 = first_step_sign(values0, stride)
        fs1 = first_step_sign(values1, stride)
        fs_changed = int(fs0 != fs1)
        core_flip = int(cr["core_tier"] != sc["core_tier"])
        ref_flip = int(rr["tier"] != rs["tier"])
        phase_rows.append({
            "N": n,
            "record": rec,
            "orig_start": start,
            "shifted_start": sc["window_start"],
            "core_tier": cr["core_tier"],
            "core_tier_shift": sc["core_tier"],
            "core_flip": core_flip,
            "ref_tier": rr["tier"],
            "ref_tier_shift": rs["tier"],
            "ref_flip": ref_flip,
            "core_classical": cr["classical"],
            "core_sigma_delta": cr["sigma_delta"],
            "core_classical_shift": sc["classical"],
            "core_sigma_delta_shift": sc["sigma_delta"],
            "ref_classical": f"{rr['classical']:.17g}",
            "ref_sigma_delta": f"{rr['sigma_delta']:.17g}",
            "ref_classical_shift": f"{rs['classical']:.17g}",
            "ref_sigma_delta_shift": f"{rs['sigma_delta']:.17g}",
            "stride": stride,
            "first_step": fs0,
            "first_step_shift": fs1,
            "first_step_changed": fs_changed,
            "core_flip_with_first_step_change": int(core_flip and fs_changed),
        })

    for n in PHASE_NS:
        sub = [r for r in phase_rows if int(r["N"]) == n]
        pairs = len(sub)
        cf = sum(r["core_flip"] for r in sub)
        rf = sum(r["ref_flip"] for r in sub)
        cfs = sum(r["core_flip_with_first_step_change"] for r in sub)
        phase_stats[n] = {
            "pairs": pairs,
            "core_flips": cf,
            "core_rate": (cf / pairs) if pairs else 0.0,
            "ref_flips": rf,
            "ref_rate": (rf / pairs) if pairs else 0.0,
            "core_flips_fs": cfs,
            "core_fs_share": (cfs / cf) if cf else 0.0,
        }

    # Write CSVs
    ds1_fields = [
        "N", "record", "window_start", "core_tier", "ref_tier", "core_confirmed",
        "core_classical", "ref_classical", "core_sigma_delta", "ref_sigma_delta",
        "path", "status", "agree", "gaps",
    ]
    edge_fields = [
        "id", "class", "N", "core_tier", "ref_tier", "core_confirmed",
        "core_classical", "ref_classical", "core_sigma_delta", "ref_sigma_delta",
        "path", "status", "agree", "gaps",
    ]
    write_csv(out_dir / "diff_ds1.csv", diff_ds1, ds1_fields)
    write_csv(out_dir / "diff_edge.csv", diff_edge, edge_fields)
    write_csv(out_dir / "disagreements_ds1.csv", disagreements_ds1, ds1_fields)
    write_csv(out_dir / "disagreements_edge.csv", disagreements_edge, edge_fields)
    phase_fields = list(phase_rows[0].keys()) if phase_rows else [
        "N", "record", "orig_start", "core_flip", "ref_flip", "first_step_changed"
    ]
    write_csv(out_dir / "phase_shift_ds1.csv", phase_rows, phase_fields)

    ctx = {
        "stub": args.stub,
        "frozen_dir": str(args.frozen_dir),
        "hashes": hashes,
        "sha_ds1": sha256_file(args.core_ds1),
        "sha_edge": sha256_file(args.core_edge),
        "sha_edge_suite": sha256_file(args.edge_suite),
        "ds1": diff_ds1,
        "edge": diff_edge,
        "ds1_by_n": {n: [r for r in diff_ds1 if int(r["N"]) == n] for n in NS},
        "ds1_gap_counts": ds1_gap_counts,
        "edge_gap_counts": edge_gap_counts,
        "ds1_n_disagree": len(disagreements_ds1),
        "edge_n_disagree": len(disagreements_edge),
        "ds1_unexplained": ds1_unexplained,
        "edge_unexplained": edge_unexplained,
        "phase": phase_stats,
        "sd_by_first": sd_by_first,
        "ds1_wall": ds1_wall,
        "ds1_eval": ds1_eval,
        "edge_wall": edge_wall,
        "edge_eval": edge_eval,
        "shift_wall": shift_wall,
        "shift_eval": shift_eval,
        "jobs": args.jobs,
    }
    write_summary(out_dir / "DIFF_SUMMARY.md", ctx)
    sys.stderr.write(f"wrote {out_dir / 'DIFF_SUMMARY.md'}\n")
    sys.stderr.write(
        f"DS1 agree {agree_rate(diff_ds1)[0]}/{agree_rate(diff_ds1)[1]} "
        f"disagree {len(disagreements_ds1)}; "
        f"edge agree {agree_rate(diff_edge)[0]}/{agree_rate(diff_edge)[1]} "
        f"disagree {len(disagreements_edge)}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
