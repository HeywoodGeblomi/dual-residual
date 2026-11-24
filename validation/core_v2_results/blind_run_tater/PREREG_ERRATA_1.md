# Errata 1 to PREREG.md (sha 26953107...). Written 2026-11-24 ~00:17 ET, BEFORE any DS1 run, after a synthetic-only probe.
PREREG.md says "at N<=1024 both are identical to ba2ea57" and "At N=1024 each one reproduces T1v05/T1v06 exactly". That is WRONG for 513 < n <= 1024.
ba2ea57 caps the stream at 512 entries, so at N=1024 it reads only the first 513 samples. As defined in PREREG.md, (a) has "no 512 cap" and (b) states no cap, so both read all 1024 samples (1023-entry stream) at N=1024.
The written definitions of (a) and (b) govern and are what the harness implements. Nothing else changes.
Consequences, disclosed:
- At N=1024, (a) and (b) both equal Purp's "stride 1, no cap" sampling (L=1). So T2v02 and T2v04 at N=1024 give the same decisions as V2-T6 at N=1024, and T2v01/T2v03 give the same decisions as each other. They differ only at N=4096.
- Identity with ba2ea57 holds only for n <= 513 (N=64, 256), which are not scored.
The try count is unchanged (4).
