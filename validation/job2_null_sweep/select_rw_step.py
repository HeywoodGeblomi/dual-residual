#!/usr/bin/env python3
"""Apply the pre-registered rw_q tie-rate rule. Does not read FPRs.

score(q) = (tie_1024 - 0.13)^2 + (tie_4096 - 0.04)^2 + (tie_16384 - 0.02)^2

The three targets are reported MIT-BIH contract tie rates, used only as a
band. This script does not read ECG and does not score false triggers.

A candidate is eligible when every official N has mean tie rate inside
[0.015, 0.20]. The winner is the eligible candidate with the smallest
score; ties break toward the smaller step. Official flanks are the
candidate neighbors of the winner.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "data" / "pilot_tie_rates.csv"
CPP = ROOT / "sweep_null.cpp"
TARGETS = {1024: 0.13, 4096: 0.04, 16384: 0.02}
OFFICIAL_N = (64, 256, 1024, 4096, 16384)
BAND = (0.015, 0.20)


def load_rw(path: Path) -> dict[float, dict[int, float]]:
    rows: dict[float, dict[int, float]] = {}
    with path.open(newline="") as f:
        for rec in csv.DictReader(f):
            if rec["family"] != "rw_q":
                continue
            step = float(rec["step"])
            rows.setdefault(step, {})[int(rec["n"])] = float(rec["mean_zero_rate"])
    return rows


def score_of(ties: dict[int, float]) -> float:
    return sum((ties[n] - target) ** 2 for n, target in TARGETS.items())


def eligible(ties: dict[int, float]) -> bool:
    lo, hi = BAND
    return all(n in ties and lo <= ties[n] <= hi for n in OFFICIAL_N)


def choose(rows: dict[float, dict[int, float]]) -> tuple[float, list[float]]:
    ranked = []
    for step, ties in rows.items():
        if any(n not in ties for n in TARGETS):
            continue
        ranked.append((score_of(ties), step, eligible(ties)))
    pool = [item for item in ranked if item[2]] or ranked
    pool.sort(key=lambda item: (item[0], item[1]))
    winner = pool[0][1]
    steps = sorted(rows)
    i = steps.index(winner)
    flanks = []
    if i > 0:
        flanks.append(steps[i - 1])
    if i + 1 < len(steps):
        flanks.append(steps[i + 1])
    official = sorted(set(flanks + [winner]))
    return winner, official


def cpp_rw_steps(text: str) -> tuple[list[float], float | None]:
    block = re.search(r"const Spec kOfficial\[\] = \{.*?\};", text, re.S)
    if not block:
        raise SystemExit("kOfficial array not found")
    found = []
    focus = None
    for line in block.group(0).splitlines():
        m = re.search(r'\{"rw_q", "([^"]+)", ([0-9.]+), kRw\}', line)
        if not m:
            continue
        step = float(m.group(2))
        found.append(step)
        if "focus:" in line:
            focus = step
    return found, focus


def fmt_step(step: float) -> str:
    return f"{step:.4g}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--pilot", type=Path, default=PILOT)
    args = parser.parse_args()
    rows = load_rw(args.pilot)
    if not rows:
        raise SystemExit(f"no rw_q rows in {args.pilot}")
    winner, official = choose(rows)
    print("step,eligible,score,tie64,tie256,tie1024,tie4096,tie16384")
    for step in sorted(rows):
        ties = rows[step]
        if any(n not in ties for n in OFFICIAL_N):
            continue
        print(
            f"{fmt_step(step)},{int(eligible(ties))},{score_of(ties):.8f},"
            + ",".join(f"{ties[n]:.6f}" for n in OFFICIAL_N)
        )
    print(f"winner={fmt_step(winner)}")
    print("official=" + ",".join(fmt_step(s) for s in official))
    if not args.check:
        return 0
    baked, focus = cpp_rw_steps(CPP.read_text())
    ok = baked == official and focus == winner
    print(f"cpp_official={','.join(fmt_step(s) for s in baked)} cpp_focus={focus}")
    if not ok:
        print("LOCKED GRID DOES NOT MATCH THE TIE-RATE RULE", file=sys.stderr)
        return 1
    print("locked grid matches the tie-rate rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
