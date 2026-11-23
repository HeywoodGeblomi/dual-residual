#!/usr/bin/env python3
"""Wilson intervals, event-count table, and plots for the Job 2 null sweep.

Reads data/null_trials.csv and data/coverage.csv. Writes summary tables,
fit.json, and PNG plots. Does not refit the decision thresholds.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PLOTS = ROOT / "plots"
Z95 = 1.959963984540054
# Pre-set: a region "bounds" the |sigma| false-trigger rate when the
# Wilson 95% upper bound is at most this value. Not a new threshold
# in the core.
BOUND = 0.05
FOCUS = ("rw_q", "0.3")
NS = [64, 256, 1024, 4096, 16384]
BINS = [
    ("0", 0, 0),
    ("2-7", 2, 7),
    ("8-15", 8, 15),
    ("16-31", 16, 31),
    ("32-63", 32, 63),
    ("64-127", 64, 127),
    ("128-191", 128, 191),
    ("192-256", 192, 256),
]


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float, float]:
    if n <= 0:
        return (math.nan, math.nan, math.nan)
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / den
    return p, max(0.0, center - half), min(1.0, center + half)


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return math.nan
    ys = sorted(xs)
    k = (len(ys) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return ys[lo]
    return ys[lo] * (hi - k) + ys[hi] * (k - lo)


def in_bin(n_events: int, lo: int, hi: int) -> bool:
    return lo <= n_events <= hi


def bin_rank(name: str) -> int:
    for i, (label, _lo, _hi) in enumerate(BINS):
        if label == name:
            return i
    return len(BINS)


def logistic_irls(x: np.ndarray, y: np.ndarray, l2: float = 1e-6) -> dict:
    """Univariate logistic: logit(p) = a + b x. Returns a saturated flag."""
    n = int(y.size)
    rate = float(y.mean()) if n else math.nan
    if n < 20 or rate < 1e-8 or rate > 1.0 - 1e-8:
        return {"n": n, "rate": rate, "saturated": True, "a": None, "b": None}
    X = np.column_stack([np.ones(n), x])
    beta = np.zeros(2)
    converged = False
    for _ in range(40):
        eta = np.clip(X @ beta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1.0 - p), 1e-8, None)
        H = (X * w[:, None]).T @ X + l2 * np.eye(2)
        grad = X.T @ (y - p)
        step = np.linalg.solve(H, grad)
        beta = beta + step
        if float(np.max(np.abs(step))) < 1e-10:
            converged = True
            break
    return {
        "n": n,
        "rate": rate,
        "saturated": False,
        "converged": converged,
        "a": float(beta[0]),
        "b": float(beta[1]),
    }


def main() -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    cells: dict[tuple[str, str, int], dict] = {}
    bin_counts: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    # bin value: trials, sigma_gt, classical_gt, confirmed
    focus_sigma: dict[int, list[float]] = defaultdict(list)
    fit_x: list[float] = []
    fit_y: list[float] = []
    fit_z: list[float] = []
    stray = 0
    n_rows = 0
    gt_ge_mismatch = 0

    with (DATA / "null_trials.csv").open(newline="") as f:
        for rec in csv.DictReader(f):
            n_rows += 1
            family, step = rec["family"], rec["step"]
            n = int(rec["n"])
            key = (family, step, n)
            slot = cells.get(key)
            if slot is None:
                slot = {
                    "family": family,
                    "step": step,
                    "n": n,
                    "trials": 0,
                    "stride": int(rec["stride"]),
                    "tlen": int(rec["tlen"]),
                    "last_index": int(rec["last_index"]),
                    "fraction_window_read": float(rec["fraction_window_read"]),
                    "fraction_samples_touched": float(rec["fraction_samples_touched"]),
                    "zero_sum": 0.0,
                    "events_sum": 0.0,
                    "cross_sum": 0.0,
                    "events": [],
                    "abs_sigma": [],
                    "k_classical": 0,
                    "k_sigma_gt": 0,
                    "k_sigma_ge": 0,
                    "k_sigma_gt_0p1": 0,
                    "k_classical_gt_0p2": 0,
                    "k_confirmed": 0,
                    "k_none": 0,
                    "k_t1": 0,
                    "k_t2": 0,
                    "k_t3": 0,
                    "k_eq0": 0,
                    "k_eq0_events0": 0,
                    "k_eq0_events_pos": 0,
                    "k_eq0_refused": 0,
                }
                cells[key] = slot
            slot["trials"] += 1
            n_events = int(rec["n_events"])
            zero_rate = float(rec["zero_rate"])
            classical = float(rec["classical"])
            sigma = float(rec["sigma_delta"])
            abs_sigma = abs(sigma)
            sigma_gt = int(rec["abs_sigma_gt_0005"])
            sigma_ge = int(rec["abs_sigma_ge_0005"])
            classical_gt = int(rec["classical_gt_004"])
            confirmed = int(rec["confirmed"])
            if sigma_gt != sigma_ge:
                gt_ge_mismatch += 1
            slot["zero_sum"] += zero_rate
            slot["events_sum"] += n_events
            slot["cross_sum"] += int(rec["n_crossings"])
            slot["events"].append(n_events)
            slot["abs_sigma"].append(abs_sigma)
            slot["k_classical"] += classical_gt
            slot["k_sigma_gt"] += sigma_gt
            slot["k_sigma_ge"] += sigma_ge
            slot["k_sigma_gt_0p1"] += int(abs_sigma > 0.1)
            slot["k_classical_gt_0p2"] += int(classical > 0.2)
            slot["k_confirmed"] += confirmed
            talent = rec["talent"]
            slot[{"None": "k_none", "T1": "k_t1", "T2": "k_t2", "T3": "k_t3"}[talent]] += 1
            if int(rec["sigma_eq_0"]):
                slot["k_eq0"] += 1
                if n_events == 0:
                    slot["k_eq0_events0"] += 1
                else:
                    slot["k_eq0_events_pos"] += 1
                if confirmed == 0:
                    slot["k_eq0_refused"] += 1
            placed = False
            for name, lo, hi in BINS:
                if in_bin(n_events, lo, hi):
                    placed = True
                    for scope in ("all", family, f"{family}:{step}"):
                        acc = bin_counts[(scope, name, f"{lo}:{hi}")]
                        acc[0] += 1
                        acc[1] += sigma_gt
                        acc[2] += classical_gt
                        acc[3] += confirmed
                    break
            if not placed:
                stray += 1
            if (family, step) == FOCUS and n_events >= 2:
                fit_x.append(math.log(n_events))
                fit_y.append(float(sigma_gt))
                fit_z.append(zero_rate)
            if (family, step) == FOCUS:
                focus_sigma[n].append(abs_sigma)

    if stray:
        raise SystemExit(f"{stray} trials fell outside event-count bins")
    if n_rows == 0:
        raise SystemExit("empty trial csv")

    summary_path = DATA / "summary_by_cell.csv"
    fields = [
        "family", "step", "n", "trials", "stride", "tlen", "last_index",
        "fraction_window_read", "fraction_samples_touched",
        "mean_zero_rate", "mean_n_events", "median_n_events", "mean_n_crossings",
        "p50_abs_sigma", "p95_abs_sigma", "p99_abs_sigma",
        "k_classical_gt", "fpr_classical", "classical_lo", "classical_hi",
        "k_sigma_gt", "fpr_sigma_gt", "sigma_gt_lo", "sigma_gt_hi",
        "k_sigma_ge", "fpr_sigma_ge", "sigma_ge_lo", "sigma_ge_hi",
        "k_sigma_gt_0p1", "fpr_sigma_gt_0p1",
        "k_classical_gt_0p2", "fpr_classical_gt_0p2",
        "k_confirmed", "fpr_confirmed", "confirmed_lo", "confirmed_hi",
        "k_none", "k_t1", "k_t2", "k_t3",
        "rate_none", "rate_t1", "rate_t2", "rate_t3",
        "k_sigma_eq_0", "rate_sigma_eq_0",
        "k_sigma_eq_0_events0", "k_sigma_eq_0_events_pos",
        "refusal_given_sigma_eq_0",
    ]
    rows_out = []
    for key in sorted(cells, key=lambda k: (k[0], float(k[1]), k[2])):
        s = cells[key]
        m = s["trials"]
        if s["k_none"] + s["k_t1"] + s["k_t2"] + s["k_t3"] != m:
            raise SystemExit(f"state counts do not add up for {key}")
        fpr_c, c_lo, c_hi = wilson(s["k_classical"], m)
        fpr_g, g_lo, g_hi = wilson(s["k_sigma_gt"], m)
        fpr_ge, ge_lo, ge_hi = wilson(s["k_sigma_ge"], m)
        fpr_o, o_lo, o_hi = wilson(s["k_confirmed"], m)
        refusal = (s["k_eq0_refused"] / s["k_eq0"]) if s["k_eq0"] else math.nan
        row = {
            "family": s["family"],
            "step": s["step"],
            "n": s["n"],
            "trials": m,
            "stride": s["stride"],
            "tlen": s["tlen"],
            "last_index": s["last_index"],
            "fraction_window_read": f"{s['fraction_window_read']:.10f}",
            "fraction_samples_touched": f"{s['fraction_samples_touched']:.10f}",
            "mean_zero_rate": s["zero_sum"] / m,
            "mean_n_events": s["events_sum"] / m,
            "median_n_events": percentile(s["events"], 0.5),
            "mean_n_crossings": s["cross_sum"] / m,
            "p50_abs_sigma": percentile(s["abs_sigma"], 0.50),
            "p95_abs_sigma": percentile(s["abs_sigma"], 0.95),
            "p99_abs_sigma": percentile(s["abs_sigma"], 0.99),
            "k_classical_gt": s["k_classical"],
            "fpr_classical": fpr_c,
            "classical_lo": c_lo,
            "classical_hi": c_hi,
            "k_sigma_gt": s["k_sigma_gt"],
            "fpr_sigma_gt": fpr_g,
            "sigma_gt_lo": g_lo,
            "sigma_gt_hi": g_hi,
            "k_sigma_ge": s["k_sigma_ge"],
            "fpr_sigma_ge": fpr_ge,
            "sigma_ge_lo": ge_lo,
            "sigma_ge_hi": ge_hi,
            "k_sigma_gt_0p1": s["k_sigma_gt_0p1"],
            "fpr_sigma_gt_0p1": s["k_sigma_gt_0p1"] / m,
            "k_classical_gt_0p2": s["k_classical_gt_0p2"],
            "fpr_classical_gt_0p2": s["k_classical_gt_0p2"] / m,
            "k_confirmed": s["k_confirmed"],
            "fpr_confirmed": fpr_o,
            "confirmed_lo": o_lo,
            "confirmed_hi": o_hi,
            "k_none": s["k_none"],
            "k_t1": s["k_t1"],
            "k_t2": s["k_t2"],
            "k_t3": s["k_t3"],
            "rate_none": s["k_none"] / m,
            "rate_t1": s["k_t1"] / m,
            "rate_t2": s["k_t2"] / m,
            "rate_t3": s["k_t3"] / m,
            "k_sigma_eq_0": s["k_eq0"],
            "rate_sigma_eq_0": s["k_eq0"] / m,
            "k_sigma_eq_0_events0": s["k_eq0_events0"],
            "k_sigma_eq_0_events_pos": s["k_eq0_events_pos"],
            "refusal_given_sigma_eq_0": refusal,
        }
        rows_out.append(row)

    with summary_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows_out:
            writer.writerow(row)

    bin_rows = []
    meeting = []
    for (scope, name, span), (trials, k_gt, k_c, k_o) in sorted(bin_counts.items()):
        p, lo, hi = wilson(k_gt, trials)
        rec = {
            "scope": scope,
            "bin": name,
            "span": span,
            "trials": trials,
            "k_sigma_gt": k_gt,
            "fpr_sigma_gt": p,
            "sigma_gt_lo": lo,
            "sigma_gt_hi": hi,
            "fpr_classical": k_c / trials if trials else math.nan,
            "fpr_confirmed": k_o / trials if trials else math.nan,
            "meets_0p05_wilson_upper": int(trials >= 200 and hi <= BOUND),
        }
        bin_rows.append(rec)
        if rec["meets_0p05_wilson_upper"] and scope in ("all", "rw_q", "rw_q:0.3"):
            meeting.append(rec)
    with (DATA / "fpr_by_event_count.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(bin_rows[0].keys()))
        writer.writeheader()
        writer.writerows(bin_rows)

    fit = logistic_irls(np.asarray(fit_x), np.asarray(fit_y))
    # Descriptive cell-level contrast on the focus plateau, where the
    # cap holds event count nearly fixed while stride (and tie rate) change.
    plateau = []
    for row in rows_out:
        if (row["family"], row["step"]) == FOCUS and row["n"] in (1024, 4096, 16384):
            plateau.append({
                "n": row["n"],
                "stride": row["stride"],
                "fraction_window_read": float(row["fraction_window_read"]),
                "mean_zero_rate": row["mean_zero_rate"],
                "mean_n_events": row["mean_n_events"],
                "fpr_sigma_gt": row["fpr_sigma_gt"],
                "sigma_gt_lo": row["sigma_gt_lo"],
                "sigma_gt_hi": row["sigma_gt_hi"],
                "fpr_confirmed": row["fpr_confirmed"],
            })
    payload = {
        "trials_per_cell": rows_out[0]["trials"] if rows_out else 0,
        "n_rows": n_rows,
        "gt_ge_mismatch_rows": gt_ge_mismatch,
        "bound_wilson_upper": BOUND,
        "focus": {"family": FOCUS[0], "step": FOCUS[1]},
        "focus_logistic_log_n_events": fit,
        "focus_plateau_same_event_scale": plateau,
        "bins_meeting_bound": meeting,
    }
    (DATA / "fit.json").write_text(json.dumps(payload, indent=2) + "\n")

    plot_coverage()
    plot_ties(rows_out)
    plot_fpr(rows_out)
    plot_events(bin_rows, rows_out)
    plot_ecdf(focus_sigma)
    classical_rows = write_classical_table()
    plot_classical(classical_rows)
    write_markdown(rows_out, bin_rows, payload)
    print(f"rows={n_rows} cells={len(rows_out)} gt_ge_mismatch={gt_ge_mismatch}")
    print(f"focus logistic: {fit}")
    print(f"bins meeting bound: {len(meeting)}")


def plot_coverage() -> None:
    ns, span, touched, trunc = [], [], [], []
    with (DATA / "coverage.csv").open(newline="") as f:
        for rec in csv.DictReader(f):
            ns.append(int(rec["n"]))
            span.append(float(rec["fraction_window_read"]))
            touched.append(float(rec["fraction_samples_touched"]))
            trunc.append(int(rec["prefix_truncation"]))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(ns, span, "o-", color="#0072B2", label="fraction of window reached")
    ax.plot(ns, touched, "s--", color="#D55E00", label="fraction of samples touched")
    if any(trunc):
        left = min(n for n, t in zip(ns, trunc) if t)
        right = max(n for n, t in zip(ns, trunc) if t)
        ax.axvspan(left, right, color="#0072B2", alpha=0.08, label="prefix truncation")
    ax.set_xscale("log", base=2)
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns], rotation=45, ha="right")
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("N")
    ax.set_ylabel("fraction")
    ax.set_title("What the unmodified core actually reads")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "coverage_fraction_by_n.png", dpi=140)
    plt.close(fig)


def plot_ties(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    styles = {"gauss_q": ("#0072B2", "o"), "unif_k": ("#E69F00", "s"), "rw_q": ("#009E73", "D")}
    for family in ("gauss_q", "unif_k", "rw_q"):
        steps = sorted({r["step"] for r in rows if r["family"] == family}, key=float)
        color, marker = styles[family]
        for i, step in enumerate(steps):
            xs, ys = [], []
            for n in NS:
                rec = next(r for r in rows if r["family"] == family and r["step"] == step and r["n"] == n)
                xs.append(n)
                ys.append(rec["mean_zero_rate"])
            lw = 2.4 if (family, step) == FOCUS else 1.1
            ax.plot(xs, ys, marker=marker, color=color, alpha=0.45 + 0.18 * i, lw=lw,
                    label=f"{family} {step}")
    # Reported contract figures. Not measurements from this repository.
    ax.scatter([64, 256, 1024], [0.13, 0.13, 0.13], facecolors="none", edgecolors="#000000",
               s=48, zorder=4, label="reported stride-1 tie 13%")
    ax.scatter([4096], [0.04], facecolors="none", edgecolors="#000000", marker="^", s=48,
               zorder=4, label="reported N=4096 tie 4%")
    ax.scatter([16384], [0.02], facecolors="none", edgecolors="#000000", marker="v", s=48,
               zorder=4, label="reported N=16384 tie 2%")
    ax.set_xscale("log", base=2)
    ax.set_xticks(NS)
    ax.set_xticklabels([str(n) for n in NS])
    ax.set_xlabel("N")
    ax.set_ylabel("tie rate in the core sign stream")
    ax.set_title("Null tie rates (open markers are reported, not measured)")
    ax.set_ylim(0, 0.6)
    ax.legend(frameon=False, fontsize=7, ncol=2)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "tie_rate_vs_n.png", dpi=140)
    plt.close(fig)


def plot_fpr(rows: list[dict]) -> None:
    want = [("rw_q", "0.3"), ("rw_q", "0.2"), ("rw_q", "0.35"),
            ("gauss_q", "0.5"), ("unif_k", "8")]
    colors = {
        ("rw_q", "0.3"): "#009E73",
        ("rw_q", "0.2"): "#56B4E9",
        ("rw_q", "0.35"): "#CC79A7",
        ("gauss_q", "0.5"): "#0072B2",
        ("unif_k", "8"): "#E69F00",
    }
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.2), sharex=True)
    for ax, key, title in (
        (axes[0], "fpr_classical", "P(classical > 0.04)"),
        (axes[1], "fpr_sigma_gt", "P(|σ_Δ| > 0.005)"),
    ):
        for fam, step in want:
            xs, ys, lo, hi = [], [], [], []
            for n in NS:
                rec = next(r for r in rows if r["family"] == fam and r["step"] == step and r["n"] == n)
                xs.append(n)
                ys.append(rec[key])
                if key == "fpr_sigma_gt":
                    lo.append(rec["fpr_sigma_gt"] - rec["sigma_gt_lo"])
                    hi.append(rec["sigma_gt_hi"] - rec["fpr_sigma_gt"])
            yerr = np.vstack([lo, hi]) if key == "fpr_sigma_gt" else None
            ax.errorbar(xs, ys, yerr=yerr, marker="o", color=colors[(fam, step)],
                        lw=1.6 if (fam, step) == FOCUS else 1.0, capsize=2,
                        label=f"{fam} {step}")
        ax.set_xscale("log", base=2)
        ax.set_xticks(NS)
        ax.set_xticklabels([str(n) for n in NS])
        ax.set_ylim(-0.02, 1.05)
        ax.set_title(title)
        ax.set_xlabel("N")
        ax.grid(True, axis="y", alpha=0.3)
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Null false-trigger rates", y=1.02)
    fig.tight_layout()
    fig.savefig(PLOTS / "fpr_vs_n.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_events(bin_rows: list[dict], rows: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.2))
    ax = axes[0]
    focus_bins = sorted(
        (b for b in bin_rows if b["scope"] == "rw_q:0.3"),
        key=lambda b: bin_rank(b["bin"]),
    )
    xs = np.arange(len(focus_bins))
    ys = [b["fpr_sigma_gt"] for b in focus_bins]
    yerr = np.vstack([
        [b["fpr_sigma_gt"] - b["sigma_gt_lo"] for b in focus_bins],
        [b["sigma_gt_hi"] - b["fpr_sigma_gt"] for b in focus_bins],
    ])
    ax.bar(xs, ys, color="#009E73", alpha=0.85)
    ax.errorbar(xs, ys, yerr=yerr, fmt="none", ecolor="black", capsize=2)
    ax.axhline(BOUND, color="#D55E00", ls="--", lw=1, label="Wilson-upper criterion 0.05")
    ax.set_xticks(xs)
    ax.set_xticklabels([b["bin"] for b in focus_bins], rotation=45, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("P(|σ_Δ| > 0.005)")
    ax.set_xlabel("core n_events bin")
    ax.set_title("rw_q 0.3, pooled over N")
    ax.legend(frameon=False, fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1]
    for step, color in (("0.2", "#56B4E9"), ("0.3", "#009E73"), ("0.35", "#CC79A7")):
        xs, ys = [], []
        for rec in rows:
            if rec["family"] == "rw_q" and rec["step"] == step:
                xs.append(rec["mean_n_events"])
                ys.append(rec["fpr_sigma_gt"])
                ax.annotate(str(rec["n"]), (rec["mean_n_events"], rec["fpr_sigma_gt"]),
                            textcoords="offset points", xytext=(3, 3), fontsize=6, color=color)
        ax.plot(xs, ys, "o-", color=color, label=f"rw_q {step}")
    ax.set_xlabel("mean core n_events")
    ax.set_ylabel("P(|σ_Δ| > 0.005)")
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("Same event scale, different N")
    ax.legend(frameon=False, fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fpr_vs_event_count.png", dpi=140)
    plt.close(fig)


def plot_ecdf(focus_sigma: dict[int, list[float]]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = {64: "#000000", 256: "#0072B2", 1024: "#009E73", 4096: "#E69F00", 16384: "#D55E00"}
    for n in NS:
        xs = np.sort(np.asarray(focus_sigma[n], dtype=float))
        ys = np.arange(1, xs.size + 1) / xs.size
        ax.plot(xs, ys, color=colors[n], lw=1.5, label=f"N={n}")
    ax.axvline(0.005, color="#000000", ls="--", lw=1, label="|σ_Δ| = 0.005")
    ax.axvline(0.1, color="#000000", ls=":", lw=1, label="|σ_Δ| = 0.1")
    ax.set_xlim(0, 0.45)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("|σ_Δ|")
    ax.set_ylabel("ECDF")
    ax.set_title("rw_q step 0.3 null |σ_Δ|")
    ax.legend(frameon=False, fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "ecdf_abs_sigma_focus.png", dpi=140)
    plt.close(fig)


def write_classical_table() -> list[dict]:
    """Classical against the sign-stream tie rate, one row per family, step, and N."""
    buckets: dict[tuple[str, str, int], dict] = {}
    max_ratio_gap = 0.0
    max_knuth_gap = 0.0
    n_below_or_eq_02 = 0
    with (DATA / "null_trials.csv").open(newline="") as f:
        for rec in csv.DictReader(f):
            tlen = int(rec["tlen"])
            zeros = int(rec["n_zeros"])
            classical = float(np.float32(rec["classical"]))
            ratio = float(np.float32(tlen - zeros) / np.float32(tlen))
            knuth = float(np.float32(1.0) - (np.float32(zeros) / np.float32(tlen)))
            max_ratio_gap = max(max_ratio_gap, abs(classical - ratio))
            max_knuth_gap = max(max_knuth_gap, abs(classical - knuth))
            if classical <= 0.2:
                n_below_or_eq_02 += 1
            key = (rec["family"], rec["step"], int(rec["n"]))
            slot = buckets.get(key)
            if slot is None:
                slot = {
                    "family": rec["family"],
                    "step": rec["step"],
                    "n": int(rec["n"]),
                    "tlen": tlen,
                    "classical": [],
                    "tie": [],
                    "t1": 0,
                    "owned": 0,
                    "owned_t2": 0,
                    "owned_t3": 0,
                }
                buckets[key] = slot
            slot["classical"].append(classical)
            slot["tie"].append(zeros / tlen)
            if rec["talent"] == "T1":
                slot["t1"] += 1
            if int(rec["confirmed"]):
                slot["owned"] += 1
                if rec["talent"] == "T2":
                    slot["owned_t2"] += 1
                elif rec["talent"] == "T3":
                    slot["owned_t3"] += 1
    out = []
    for key in sorted(buckets, key=lambda k: (k[0], float(k[1]), k[2])):
        slot = buckets[key]
        c = slot["classical"]
        t = slot["tie"]
        m = len(c)
        out.append({
            "family": slot["family"],
            "step": slot["step"],
            "n": slot["n"],
            "tlen": slot["tlen"],
            "trials": m,
            "tie_min": min(t),
            "tie_p05": percentile(t, 0.05),
            "tie_p50": percentile(t, 0.50),
            "tie_mean": sum(t) / m,
            "tie_p95": percentile(t, 0.95),
            "tie_max": max(t),
            "classical_min": min(c),
            "classical_p05": percentile(c, 0.05),
            "classical_p50": percentile(c, 0.50),
            "classical_mean": sum(c) / m,
            "classical_p95": percentile(c, 0.95),
            "classical_max": max(c),
            "mean_one_minus_tie": 1.0 - (sum(t) / m),
            "frac_classical_gt_0p2": sum(v > 0.2 for v in c) / m,
            "frac_classical_le_0p2": sum(v <= 0.2 for v in c) / m,
            "k_t1": slot["t1"],
            "k_owned": slot["owned"],
            "owned_t2": slot["owned_t2"],
            "owned_t3": slot["owned_t3"],
        })
    path = DATA / "classical_vs_tie.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    note = {
        "rows": sum(r["trials"] for r in out),
        "max_abs_printed_classical_minus_float32_ratio": max_ratio_gap,
        "max_abs_printed_classical_minus_float32_one_minus_tie": max_knuth_gap,
        "trials_with_classical_le_0p2": n_below_or_eq_02,
        "t1_count": sum(r["k_t1"] for r in out),
    }
    (DATA / "classical_identity.json").write_text(json.dumps(note, indent=2) + "\n")
    print("classical identity", note)
    return out


def plot_classical(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    colors = {"gauss_q": "#0072B2", "unif_k": "#E69F00", "rw_q": "#009E73"}
    markers = {"gauss_q": "o", "unif_k": "s", "rw_q": "D"}
    xs = np.linspace(0, 1, 200)
    ax.plot(xs, 1.0 - xs, color="#000000", lw=1, label="classical = 1 − tie rate")
    ax.axvline(0.8, color="#D55E00", ls="--", lw=1, label="tie rate 0.8 (classical = 0.2)")
    ax.axhline(0.2, color="#D55E00", ls=":", lw=1)
    seen = set()
    for rec in rows:
        family = rec["family"]
        label = family if family not in seen else None
        seen.add(family)
        ax.errorbar(
            rec["tie_mean"],
            rec["classical_mean"],
            xerr=[[rec["tie_mean"] - rec["tie_min"]], [rec["tie_max"] - rec["tie_mean"]]],
            yerr=[[rec["classical_mean"] - rec["classical_min"]],
                  [rec["classical_max"] - rec["classical_mean"]]],
            fmt=markers[family],
            color=colors[family],
            ms=5,
            lw=0.6,
            capsize=0,
            alpha=0.85,
            label=label,
        )
    ax.set_xlim(-0.02, 0.85)
    ax.set_ylim(0.15, 1.05)
    ax.set_xlabel("tie rate z/T")
    ax.set_ylabel("classical")
    ax.set_title("Null classical tracks 1 − tie rate")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "classical_vs_tie_rate.png", dpi=140)
    plt.close(fig)


def write_markdown(rows: list[dict], bin_rows: list[dict], payload: dict) -> None:
    lines = ["# Generated tables", ""]
    lines.append("| family | step | N | stride | window read | samples touched | tie rate | mean events | FPR classical | FPR abs sigma > 0.005 | Wilson 95% | FPR confirmed | None | T1 | T2 | T3 | P(sigma=0) | refusal given sigma=0 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            "| {family} | {step} | {n} | {stride} | {fraction_window_read} | {fraction_samples_touched} | "
            "{tie:.4f} | {ev:.2f} | {fc:.4f} | {fs:.4f} | [{lo:.4f}, {hi:.4f}] | {fo:.4f} | "
            "{rn:.4f} | {r1:.4f} | {r2:.4f} | {r3:.4f} | {z:.4f} | {ref} |".format(
                tie=r["mean_zero_rate"], ev=r["mean_n_events"], fc=r["fpr_classical"],
                fs=r["fpr_sigma_gt"], lo=r["sigma_gt_lo"], hi=r["sigma_gt_hi"],
                fo=r["fpr_confirmed"], rn=r["rate_none"], r1=r["rate_t1"],
                r2=r["rate_t2"], r3=r["rate_t3"], z=r["rate_sigma_eq_0"],
                ref="n/a" if isinstance(r["refusal_given_sigma_eq_0"], float) and math.isnan(r["refusal_given_sigma_eq_0"]) else f"{r['refusal_given_sigma_eq_0']:.4f}",
                **r,
            )
        )
    lines += ["", "## Focus event-count bins", ""]
    lines.append("| bin | trials | FPR | Wilson 95% | meets 0.05 |")
    lines.append("|---|---:|---:|---|---:|")
    for b in sorted(
        (b for b in bin_rows if b["scope"] == "rw_q:0.3"),
        key=lambda b: bin_rank(b["bin"]),
    ):
        lines.append(
            f"| {b['bin']} | {b['trials']} | {b['fpr_sigma_gt']:.4f} | "
            f"[{b['sigma_gt_lo']:.4f}, {b['sigma_gt_hi']:.4f}] | {b['meets_0p05_wilson_upper']} |"
        )
    lines += ["", "## Fit", "", "```json", json.dumps(payload, indent=2), "```", ""]
    (DATA / "tables_generated.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
