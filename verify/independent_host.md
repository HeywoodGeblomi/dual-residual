# Independent Host — Dual Residual Core

Stranger path. No prior knowledge of any other repository required.

## 1. Obtain

```bash
git clone https://github.com/HeywoodGeblomi/dual-residual.git
cd dual-residual
```

## 2. Compile + run the verification suite

```bash
g++ -std=c++17 -O2 -I. tests/test_evidence.cpp -o test_evidence
./test_evidence
# expected: ALL GREEN (test_evidence)

g++ -std=c++17 -O2 -I. tests/test_parity_oracle.cpp -o test_parity_oracle
./test_parity_oracle
# expected: ALL GREEN (test_parity_oracle)

g++ -std=c++17 -O2 -I. tests/test_borderline_cases.cpp -o test_borderline_cases
./test_borderline_cases
# expected: ALL GREEN (test_borderline_cases)

g++ -std=c++17 -O2 -I. tests/test_table_lock.cpp -o test_table_lock
./test_table_lock
# expected: ALL GREEN (test_table_lock)
```

## 3. Interpret

- `test_evidence` covers controls (sorted / reverse / equal-heavy → not dual_owned), talent decision table, short arrays, and finite metrics on borderline-HE / random inputs.
- `test_parity_oracle` covers determinism, classical floor behaviour, and dual_confirm edge cases.
- `test_borderline_cases` is the honest single-soft failure suite: pairwise/alt/zigzag cases where classical alone would own residual but dual correctly refuses; plus a dual-owned confirmation case. See `BORDERLINE.md`.
- `test_table_lock` pins the existing floors and operators (`0.04 / 0.005 / 0.1 / 0.2`), early returns, stride cliff, and golden T2/T3 outcomes. Assertion only — the table is not rewritten.

If all print `ALL GREEN`, the core matches the locked decision table and parity construction.

## 4. Optional: inspect the header

```bash
wc -l dual_residual.hpp   # ~140 lines
```

Public surface is only `dual_residual::Evidence` and `dual_residual::evidence()`.

No further setup. No network at compile time. No third-party libraries.
