# Example: rubber-stamp-caught — a plausible-looking review that the validator downgrades

## What this is

A realistic but shallow `value-first-gate` review for the proposal:
**"Add dark mode toggle to internal dashboard"**.

The author wrote "GO" with total_score 18/30 — on the surface below the 22 threshold,
but they could have adjusted scores to reach 22. The interesting part is: even if the
total were 22+, the validator would still force REVISE due to rubber-stamp signals.

## What's wrong

The review has **all 5 rubber-stamp flags triggered**:

1. **R1 `score_spread_zero: true`** — all 6 criteria scored 3/5 ("it's fine, I think")
2. **R2 `evidence_cells_empty_count: 4`** — most evidence cells blank or `-`
3. **R3 `devils_advocate_empty: true`** — section 9 left as template placeholder
4. **R4 `critique_unclear_count: 3`** — root value / beneficiary / uncertainty all marked unclear
5. **R5 `anti_patterns_all_silent: true`** — zero boxes checked, zero justifications

Running the validator: **exit code 1**, verdict forcibly downgraded to REVISE.

## Why this matters

This is the exact failure mode solo PMs slip into: the template gets filled to completion, the numbers add up, the verdict is written, but **no honest thinking happened**. Without these guards, triadev would wave it through to implementation.

With the guards, triadev's phase-transition rule refuses to advance to `implementation` because `rubber_stamp_flags.any_triggered == true`.

## Files

| File | Purpose |
|------|---------|
| `value-review.md` | The shallow review (intentionally thin) |
| `value-review.json` | Sidecar showing all 5 rubber-stamp flags triggered |
| `validator-output.txt` | Expected output from `scripts/check_review.py` |

## What the validator says

```
sidecar: examples/rubber-stamp-caught/value-review.json
verdict: REVISE
any_rubber_stamp_triggered: True
violations (5):
  - R1: score_spread == 0 — all 6 criterion scores are identical (rubber-stamp signal)
  - R2: 4 evidence cells left empty (>= 2 triggers REVISE)
  - R3: Devil's Advocate field is blank — required non-empty
  - R4: 3 critique questions unclear (>= 2 triggers REVISE)
  - R5: All 6 anti-patterns left unchecked AND unjustified — honest reviews have something to say

Result: rubber-stamp signals present; verdict correctly degraded.
```
