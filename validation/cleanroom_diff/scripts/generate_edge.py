#!/usr/bin/env python3
"""Deterministic, seeded edge-case suite for the Dual Residual clean-room diff.

Writes cleanroom_diff/edge/edge_suite.jsonl (one window per line) and
edge_suite.jsonl.sha256. Does not import or invoke the frozen reference.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "edge"
OUT_PATH = OUT_DIR / "edge_suite.jsonl"
SHA_PATH = OUT_DIR / "edge_suite.jsonl.sha256"

SEED = 20261123
B_LENGTHS = (8, 16, 32, 64, 256, 512, 1024, 4096, 16384)
C_LENGTHS = (64, 256, 1024, 4096)
D_BOUNDARY_LENGTHS = (512, 513, 514, 1023, 1024, 1025)
E_LENGTHS = (1024, 2048, 4096)
E_KS = (511, 512, 513)
F_LENGTHS = (64, 96, 128, 192, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096, 8192, 12288, 16384)
F_COUNT = 2000


def emit(fh, rec_id: str, cls: str, values: list[int]) -> None:
    # Compact JSON, no spaces, guaranteed id/class have no quotes or commas.
    fh.write(json.dumps({"id": rec_id, "class": cls, "values": values}, separators=(",", ":")) + "\n")


def seq_inc(n: int) -> list[int]:
    return list(range(n))


def seq_dec(n: int) -> list[int]:
    return list(range(n - 1, -1, -1))


def seq_alt(n: int) -> list[int]:
    return [0, 1] * (n // 2) + ([0] if n % 2 else [])


def seq_constant(n: int, value: int = 0) -> list[int]:
    return [value] * n


def seq_tie_run(n: int, p: float) -> list[int]:
    """A constant run covering fraction p of the samples, then a strict climb."""
    run = max(1, int(round(p * n)))
    run = min(run, n)
    return [0] * run + list(range(1, n - run + 1))


def seq_half(n: int, first_tie: bool) -> list[int]:
    h = n // 2
    if first_tie:
        return [0] * h + list(range(1, n - h + 1))
    return list(range(h)) + [h] * (n - h)


def seq_zero_signs(n: int, k: int) -> list[int]:
    """Exactly k zeros among the N-1 stride-1 signs. Ties first, then +1 steps."""
    if k < 0 or k > n - 1:
        raise ValueError(f"k={k} out of range for n={n}")
    x = [0]
    ties = k
    for _ in range(n - 1):
        if ties > 0:
            x.append(x[-1])
            ties -= 1
        else:
            x.append(x[-1] + 1)
    return x


def seq_nonzero_signs(n: int, k: int) -> list[int]:
    """Exactly k nonzero stride-1 signs. Changes first, then ties.

    Distinct from seq_zero_signs (which places ties first) even when
    k_nonzero == (n-1) - k_zero for a paired construction.
    """
    if k < 0 or k > n - 1:
        raise ValueError(f"k={k} out of range for n={n}")
    x = [0]
    changes = k
    for _ in range(n - 1):
        if changes > 0:
            x.append(x[-1] + 1)
            changes -= 1
        else:
            x.append(x[-1])
    return x


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    n_rows = 0
    with OUT_PATH.open("w") as fh:
        # (a) exhaustive short inputs: all sequences of length 3..9 over {0,1,2}
        alphabet = (0, 1, 2)
        for n in range(3, 10):
            total = 3 ** n
            width = len(str(total - 1))
            # lexicographic mixed-radix from 0..3^n-1
            for i in range(total):
                vals = []
                t = i
                for _ in range(n):
                    vals.append(t % 3)
                    t //= 3
                # least-significant digit first would not be lex on the tuple;
                # reverse so index 0 is the most significant (lexicographic).
                vals.reverse()
                emit(fh, f"a_n{n}_{i:0{width}d}", "a_exhaustive", vals)
            counts["a_exhaustive"] = counts.get("a_exhaustive", 0) + total
            n_rows += total

        # (b) tie-free windows at several N
        for n in B_LENGTHS:
            emit(fh, f"b_strict_inc_N{n}", "b_strict_inc", seq_inc(n))
            emit(fh, f"b_strict_dec_N{n}", "b_strict_dec", seq_dec(n))
            emit(fh, f"b_strict_alt_N{n}", "b_strict_alt", seq_alt(n))
            counts["b_strict_inc"] = counts.get("b_strict_inc", 0) + 1
            counts["b_strict_dec"] = counts.get("b_strict_dec", 0) + 1
            counts["b_strict_alt"] = counts.get("b_strict_alt", 0) + 1
            n_rows += 3

        # (c) tie-heavy windows
        for n in C_LENGTHS:
            emit(fh, f"c_constant_N{n}", "c_constant", seq_constant(n))
            emit(fh, f"c_tie50_N{n}", "c_tie50", seq_tie_run(n, 0.50))
            emit(fh, f"c_tie80_N{n}", "c_tie80", seq_tie_run(n, 0.80))
            emit(fh, f"c_tie95_N{n}", "c_tie95", seq_tie_run(n, 0.95))
            for cls in ("c_constant", "c_tie50", "c_tie80", "c_tie95"):
                counts[cls] = counts.get(cls, 0) + 1
            n_rows += 4

        # (d) N=1024 half-splits, plus boundary lengths
        emit(fh, "d_half_tie_then_free_N1024", "d_half_tie_then_free", seq_half(1024, True))
        emit(fh, "d_half_free_then_tie_N1024", "d_half_free_then_tie", seq_half(1024, False))
        counts["d_half_tie_then_free"] = 1
        counts["d_half_free_then_tie"] = 1
        n_rows += 2
        for n in D_BOUNDARY_LENGTHS:
            # several patterns at each boundary length so the 512-cap and
            # half-window read can actually show up.
            emit(fh, f"d_boundary_n{n}_inc", "d_boundary_len", seq_inc(n))
            emit(fh, f"d_boundary_n{n}_constant", "d_boundary_len", seq_constant(n))
            emit(fh, f"d_boundary_n{n}_half_tie_then_free", "d_boundary_len", seq_half(n, True))
            emit(fh, f"d_boundary_n{n}_half_free_then_tie", "d_boundary_len", seq_half(n, False))
            emit(fh, f"d_boundary_n{n}_alt", "d_boundary_len", seq_alt(n))
            counts["d_boundary_len"] = counts.get("d_boundary_len", 0) + 5
            n_rows += 5

        # (e) exact zero-sign counts and exact nonzero-sign counts at stride 1
        for n in E_LENGTHS:
            for k in E_KS:
                emit(fh, f"e_zero_signs_k{k}_N{n}", "e_zero_signs", seq_zero_signs(n, k))
                emit(fh, f"e_nonzero_signs_k{k}_N{n}", "e_nonzero_signs", seq_nonzero_signs(n, k))
                counts["e_zero_signs"] = counts.get("e_zero_signs", 0) + 1
                counts["e_nonzero_signs"] = counts.get("e_nonzero_signs", 0) + 1
                n_rows += 2

        # (f) 2000 random windows, seeded
        rng = random.Random(SEED)
        for i in range(F_COUNT):
            n = rng.choice(F_LENGTHS)
            if i % 2 == 0:
                cls = "f_random_small"
                values = [rng.randint(0, 4) for _ in range(n)]
            else:
                cls = "f_random_wide"
                values = [rng.randint(-32768, 32767) for _ in range(n)]
            emit(fh, f"{cls}_{i:04d}_N{n}", cls, values)
            counts[cls] = counts.get(cls, 0) + 1
            n_rows += 1

    digest = hashlib.sha256(OUT_PATH.read_bytes()).hexdigest()
    SHA_PATH.write_text(digest + "  " + OUT_PATH.name + "\n")
    print(f"wrote {OUT_PATH} rows={n_rows}")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print(f"sha256={digest}")
    print(f"seed={SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
