# Gate 3 fix attempt v1 (Lucas), written before any scoring. EXPLORATORY: DS1 was already used for Gate 3, so no result here can pass the gate. DS2 stays sealed.
Data: Purp dataset_v1 DS1 (N=1024, N=4096), MIT-BIH MLII raw ints. Core ba2ea57 untouched; clean-room ref = Link's frozen copy (ref.py effc85ac).
Bars are the same as the Job 3 prereg (e9eb06e4):
  P1 phase stability: flip rate (decision on window vs window shifted +1 sample) <= 10% at both N.
  P2 mechanism: |sigma_delta| on V windows (T2+T3) > None windows, one-sided Mann-Whitney p < 0.01 at both N,
      AND owned rate on V windows exceeds same windows shuffled (seed 7) by >= 10 points, at both N.
Candidate A, facade guard "PhaseLock" (core unchanged, constants unchanged, no new signal): run the core on offsets 0..4,
  emit the majority (confirmed, talent) if >= 3 of 5 agree, else HOLD. Shifted window = offsets 1..5. HOLD counts as a decision.
  Score P1 and coverage (non-HOLD rate). P2 cannot move under a guard (sigma_delta unchanged), so it is not scored for A.
Candidate B, directive-literal core = Purp's clean-room ref.py, unmodified. Decision = tier; owned = tier != None; sigma_delta = ref's sd.
  Score P1 and P2 with the bars above.
Prediction (mine, before running): A gets P1 under 10% at a coverage cost; B passes P1 (Cheddar saw 0/60 synthetic flips) but P2 is a coin flip.
Score once.
