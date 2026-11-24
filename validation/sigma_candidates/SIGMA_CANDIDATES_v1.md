# σ_Δ candidate definitions v1 (Purp). Status: exploratory; to be frozen by Link before any run.

## Why
- Blam (Nov 23, 11:57 PM ET): the directive's "zero-crossing events" was a hint, not a definition.
- Tater (bridge_v1): the core's σ_Δ splits events by even and odd *event index*. Crossings alternate up and down, so it only ever reads one direction.
- So we are choosing a definition. A win is recorded as "a definition we picked," never as proof that the original hint was right.

## Scope: change ONE thing
- Each candidate replaces only how σ_Δ is computed from the core's sign stream s[0..m-1] (+1/-1/0).
- Everything else stays as in `ba2ea57`: sampling, stride, cap, classical, ownership, refusal, precedence, and the four constants (0.04 / 0.005 / 0.1 / 0.2).
- Every candidate splits by the *sample position* parity of each event, never by event index, which avoids Tater's degeneracy.
- In each case, e_j is an event indicator, and σ_Δ = mean(e_j over even j) − mean(e_j over odd j), taken over the positions j where e_j is defined.

## Candidates (exactly three; no fourth will be added after any result)
- **C1, direction flips (turns).** For j in 1..m-1, e_j = 1 if s[j-1] and s[j] are both nonzero and opposite; else 0.
- **C2, flat steps (ties).** For j in 0..m-1, e_j = 1 if s[j] = 0; else 0.
- **C3, any change in the sign stream.** For j in 1..m-1, e_j = 1 if s[j] ≠ s[j-1], which counts entering or leaving a tie as well as turns; else 0.

Textual note, a clue and not proof: the directive says "tie-free streams force σ_Δ ≡ 0". Of the three, only C2 makes that true by construction.

## Proposed bars (Link sets the final ones at freeze)
Each candidate must pass all four, with Bonferroni over 3 candidates (α = 0.05/3 ≈ 0.0167):
1. **Discrimination.** On DS1, |σ_Δ| on T3 and T2 windows is higher than on None windows (one-sided Mann-Whitney, p < 0.0167) at N=1024 and N=4096.
2. **Phase.** A one-sample shift flips ≤ 10% of decisions at N=1024 and N=4096 (the unchanged Gate 3 bar).
3. **Not degenerate.** No single tier exceeds 80% of DS1 windows, and the tier mix is reported next to the flip rate.
4. **Shuffle null.** The flag rate on sample-shuffled windows is lower than on real T2 and T3 windows.

## Selection
- If several candidates pass, the one with the lowest N=1024 flip rate goes to DS2, which is scored once.
- If none pass, that is the logged result, with no new candidates.
- DS2 stays sealed until a single candidate and its prereg are frozen.
- This needs Blam's explicit OK to change `detail::compute` in the locked header.
