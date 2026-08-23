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
```

## 3. Interpret

- `test_evidence` covers controls (sorted / reverse / equal-heavy → not dual_owned), talent decision table, short arrays, and finite metrics on borderline-HE / random inputs.
- `test_parity_oracle` covers determinism, classical floor behaviour, and dual_confirm edge cases.

If both print `ALL GREEN`, the core matches the locked decision table and parity construction.

## 4. Optional: inspect the header

```bash
wc -l dual_residual.hpp   # ~140 lines
```

Public surface is only `dual_residual::Evidence` and `dual_residual::evidence()`.

No further setup. No network at compile time. No third-party libraries.
