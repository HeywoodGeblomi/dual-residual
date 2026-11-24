# Publish notes (Toni, 2026-11-24)
Slim public copy of the Dual Residual clean-room statement check at core ba2ea57.
Left out: compiled binaries (bin/, obj/), the 27 MB edge suite (regenerate with `scripts/generate_edge.py`, seed 20261123; its sha256 is in `edge/edge_suite.jsonl.sha256`), per-window dumps over 4 MB (diff_ds1, disagreements_ds1, core_ds1_dump and the edge equivalents), and the v2 candidate run, which stays sealed until the room's independent run is posted.
No DS2 data is included. Gate 3 still fails at ba2ea57; this repo documents why and finds no code bug.
