# Rubber-Stamp Guards — the 5 Validator Rules

Load this reference when writing or reviewing a `value-review.json` sidecar. Each rule exists because a solo-PM workflow is particularly vulnerable to gate-as-paperwork failure.

## Why these rules (not others)

The gate protects against "we implemented something that shouldn't have been built." The failure mode for a solo PM is NOT fabricating evidence (no peer to catch you) — it's **filling the template to completion without honest thinking**. The five rules below target the cheapest, most common forms of that failure. They're not committee review; they're the minimum friction that forces 30 seconds of honest thought.

Rejected alternatives: approval quorums, mandatory reviewer sign-off, word-count minimums, cooldown timers. All of these are theater for a solo workflow.

## The 5 Rules

### R1 — Score Spread Zero

**Rule**: If all 6 criterion scores are identical, `rubber_stamp_flags.score_spread_zero = true` and force `verdict ∈ {REVISE, NO-GO}`.

**Why**: No honest 6-dimension assessment produces the same score on every dimension. "User Impact" and "Risk Controllability" measure different things. Identical scores mean the author filled "3 3 3 3 3 3" without per-dimension reasoning.

**Edge case**: A truly balanced proposal might score 4-4-4-4-4-4. That's still a rubber-stamp signal — real proposals have tension between dimensions (high impact but uncertain evidence, or strong strategic fit but high effort). If your scores are truly uniform, you haven't yet thought about the proposal.

### R2 — Evidence Cells Empty (≥2)

**Rule**: If ≥2 cells in the rubric's Evidence column are empty, force REVISE.

**Why**: The rubric explicitly requires evidence per criterion. Blank cells mean the score is vibes-based. One blank can be an oversight; two is a pattern.

**What counts as empty**: truly blank, or filler like `-`, `—`, `N/A`, `n/a`. Actual evidence is a sentence or data point — even a short one counts.

### R3 — Devil's Advocate Field Blank

**Rule**: Section 9's "The strongest argument against this decision is: ___" must be filled. Template placeholder text `_(One sentence...)_` counts as blank.

**Why**: This is the central anti-rubber-stamp mechanism. It forces 30 seconds of opposition — what would a skeptic say? If you can't articulate the strongest counterargument, you haven't stress-tested your own thinking. This is the cheapest, highest-leverage guard in the set.

**Minimum viable answer**: one sentence that identifies a genuine weakness. "None, it's a clear GO" fails this — no decision has zero counterargument.

### R4 — Critique Questions Unclear (≥2)

**Rule**: Section 3.3's 5 First-Principles Critique Layer questions each cap the corresponding dimension at 3/5 when answered unclearly. If ≥2 of the 5 are unclear, force REVISE regardless of total score.

**Why**: If you can't answer "what is the root value?" or "who actually benefits?", the proposal is not yet ready for a gate. One unclear answer is normal exploration; two means the framing isn't done.

**Note**: this is author-declared (the author marks questions as unclear in the MD). The sidecar mirrors their declaration. The validator does not try to judge clarity automatically.

### R5 — Anti-Patterns All Silent

**Rule**: If Section 5.2 has 0 boxes checked AND 0 justifications provided (the "not present because: ___" slot is blank for all 6), force REVISE.

**Why**: Honest reviews have something to say about anti-patterns. Either some are present (check the box, then mitigate), or you've considered each and have a reason why it's not (fill the justification). Silent skip means no thought.

**What counts as justified**: the "_not present because:_" slot has content. Template placeholders or single dashes don't count.

## How Triadev Enforces These

Beyond the validator inside value-first-gate, triadev has a phase-transition precondition:

> Cannot transition `value-gate → implementation` when `value_gate.verdict != "GO"` OR the sidecar's `rubber_stamp_flags.any_triggered == true`.

This is a backstop: even if the author manually overwrites `verdict: "GO"` despite the validator firing, triadev refuses to let the implementation phase begin.

## What This Explicitly Does NOT Check

- **Truthfulness**: no way to detect fabricated evidence. Solo workflow must trust the author.
- **Score calibration**: a 5 in "User Impact" here versus a 3 there is the author's judgment. Not the validator's concern.
- **Verdict-to-score consistency**: the SKILL.md's existing threshold rules (GO ≥22 and no criterion <2) already handle this.
- **Strategic alignment**: judging whether a proposal actually fits the roadmap is out of scope.

These are intentional exclusions. Adding any of them pushes the gate from "honest pause" toward "bureaucratic ritual."

## Ordering of Rule Evaluation

The validator evaluates all 5 independently and reports all violations. There is no short-circuit — a review can trigger all 5 at once. The sidecar's `rubber_stamp_flags.any_triggered` is the logical OR of the five booleans; individual flags preserve which rules fired for diagnostics.

## Field Shape in Sidecar

```json
"rubber_stamp_flags": {
  "score_spread_zero": false,
  "evidence_cells_empty_count": 0,
  "devils_advocate_empty": false,
  "critique_unclear_count": 0,
  "anti_patterns_all_silent": false,
  "any_triggered": false
}
```

`any_triggered` is derived: `true` if any of the 5 individual flags evaluate to a triggering condition (`score_spread_zero == true`, `evidence_cells_empty_count >= 2`, `devils_advocate_empty == true`, `critique_unclear_count >= 2`, `anti_patterns_all_silent == true`).

When `any_triggered == true`, the JSON schema (`contracts/value-review.schema.json`) requires `verdict ∈ {REVISE, NO-GO}`, enforcing the degradation at the type level.
