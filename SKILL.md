---
name: value-first-gate
description: >
  Force a pre-implementation value gate before coding starts. Use when the user asks
  for planning, review, prioritization, tradeoff analysis, "should we build this",
  roadmap ordering, or scope decisions before implementation. Also trigger on:
  值不值得做、做个价值评估、先评估一下、有没有必要做、这个需求值得投入吗、
  go/no-go 决策、优先级评估。Run this after planning and before any TDD/SDD or coding.
version: "2.0"
triggers:
  - "值不值得做"
  - "做个价值评估"
  - "先评估一下"
  - "有没有必要做"
  - "这个需求值得投入吗"
  - "go/no-go"
  - "优先级评估"
  - "value gate"
  - "should we build this"
  - "is this worth doing"
---

# Value-First Gate v2.0

Run a strict decision gate **after planning** and **before TDD/SDD**.

If the user asks to implement immediately but value is unclear, pause implementation and run this gate first.

## Placement in Workflow

Use this sequence:

1. Planning (requirements, constraints, options)
2. **Value-First Gate (this skill)**
3. TDD/SDD (if and only if decision is GO AND no rubber-stamp flag triggered)
4. Implementation

Do not enter TDD/SDD when gate result is `NO-GO`, `REVISE`, or any rubber-stamp flag is triggered.

## Required Outputs — Dual Artifact

Every gate run produces **two** files, side-by-side:

| File | Role | Readership |
|------|------|-----------|
| `value-review.md` | Human review with YAML frontmatter | Author, reviewer, future self |
| `value-review.json` | **Authoritative** machine-readable sidecar | triadev, check_review.py, evals |

**The sidecar is authoritative.** When read by triadev or tooling, the sidecar wins over markdown.

Load the template at [templates/value-review-template.md](templates/value-review-template.md) and the sidecar template at [templates/value-review.json](templates/value-review.json).

### Path Resolution

Default output path: `value-reviews/YYYY-MM-DD-<slug>.md` + `value-review.json` next to it.

When invoked via triadev with an active change directory, triadev overrides the path to `changes/active/<change-name>/value-review.md`. Value-first-gate does not force `changes/` on plain projects.

**Never write to project root.** Root-level `value-review.md` collides on re-run.

### REVISE Iteration

If verdict is REVISE and the gate is re-run:
- Do NOT overwrite prior review
- Write a new dated file (`value-reviews/YYYY-MM-DD-<slug>-r2.md`)
- In the new sidecar, append the prior to `previous_reviews[]`
- `value_gate.review_path` in handoff.json always points at the latest

See [references/verdict-extraction.md](references/verdict-extraction.md) for the full contract.

## Gate Workflow

Execute in order. Do not skip steps.

### 1) Problem Framing

Define the decision object in one sentence:

- Problem: what pain exists now
- User: who is affected
- Outcome: what changes if solved
- Time horizon: when value should appear

Then record:

- Current baseline (how it works today)
- Opportunity cost (what else could be done)
- Constraints (team, tech, budget, compliance, deadline)

### 2) First-Principles Check

Decompose assumptions until reaching fundamentals.

For each major claim, label:

- `Fact` (evidence-backed)
- `Inference` (reasoned but uncertain)
- `Assumption` (untested belief)

Challenge at least these:

1. Is this a real problem or a proxy problem?
2. What would happen if we did nothing for 30/60/90 days?
3. What is the simplest intervention that could capture 80% value?
4. Which dependency is truly required vs habitual?
5. What metric would falsify the idea quickly?

### 2+) First-Principles Critique Layer

Before scoring, force a structured deconstruction. If any question below cannot be answered clearly, apply a score cap (max 3/5) on the corresponding dimension.

1. **Root value**: What is the fundamental reason this exists? Strip away all assumptions — what remains?
2. **True beneficiary**: Who actually benefits? (User / System / Vanity metric?)
3. **Cost of inaction**: What is the worst outcome if we do nothing for 90 days? (Tests whether urgency is real)
4. **80% shortcut**: Is there a simpler intervention that achieves 80% of the value? (Tests necessity)
5. **Key uncertainty**: What is the primary unknown that could invalidate this decision? (Tests confidence)

**Scoring impact**: For each question with an unclear or weak answer, note it explicitly in `critique_caps_applied[]` in the sidecar. If ≥2 are unclear, force REVISE regardless of total score.

### 3) Value Scoring

Score each criterion from **0 to 5** using evidence.

## Measurable Rubric (0-5 each)

| Criterion | What to measure | 0 | 3 | 5 |
|---|---|---:|---:|---:|
| User Impact | Magnitude and reach of benefit | No visible benefit | Moderate benefit for target segment | High benefit for core users with clear pain relief |
| Strategic Fit | Alignment with roadmap and goals | Off-strategy | Useful but not core | Directly advances top strategic objective |
| Urgency | Cost of delay and timing sensitivity | Delay has little effect | Moderate penalty if delayed | Delay causes major loss/risk |
| Evidence Strength | Data quality supporting the decision | Opinion only | Partial data/signals | Strong quantitative + qualitative evidence |
| Effort Efficiency | Expected value per unit effort | Very high effort for low value | Balanced | High value with low/moderate effort |
| Risk Controllability | Ability to mitigate technical/product risks | Uncontrolled/high unknowns | Risks known with partial mitigation | Risks bounded with clear mitigations |

### Score Calculation

- `total_score = sum(all 6 criteria)` (max 30)
- `confidence = High / Medium / Low` based on evidence quality
- `score_spread = max(scores) - min(scores)` (for rubber-stamp detection)

### Decision Thresholds

- **GO**: `total_score >= 22` AND no criterion < 2 AND no rubber-stamp flag triggered
- **REVISE**: `16-21` OR any criterion = 1 with plausible mitigation OR any rubber-stamp flag triggered
- **NO-GO**: `<= 15` OR critical risk cannot be mitigated

If confidence is `Low`, cap final decision at `REVISE` even if score says GO.

### 4) Rubber-Stamp Guards

Before writing the final verdict, populate the sidecar's `rubber_stamp_flags` block.
If **any** flag triggers, verdict MUST be `REVISE` or `NO-GO` — never `GO`.

The 5 rules:

| Rule | Flag field | Trigger |
|------|-----------|---------|
| R1 | `score_spread_zero` | All 6 criterion scores identical |
| R2 | `evidence_cells_empty_count` | ≥2 Evidence cells in rubric blank |
| R3 | `devils_advocate_empty` | Section 9 left blank or at placeholder |
| R4 | `critique_unclear_count` | ≥2 of 5 critique questions unclear |
| R5 | `anti_patterns_all_silent` | 0 anti-patterns checked AND 0 justifications |

Derived: `any_triggered = OR of the five rule conditions`.

Details and rationale: [references/rubber-stamp-rules.md](references/rubber-stamp-rules.md).

**Script enforcement**: run `python scripts/check_review.py <path-to-value-review.json>` after writing the sidecar. Exit 0 = clean, exit 1 = rubber-stamp violation(s) present.

### 5) Devil's Advocate Pass

Section 9 of the template has one mandatory field:

> **The strongest argument against this decision is:** \_\_\_

One sentence. Must identify a genuine weakness. "None, it's a clear GO" fails this rule — no decision has zero counterargument. Blank or placeholder triggers R3.

### 6) Go/No-Go Decision

Return one verdict in both the markdown and the sidecar:

- `GO`
- `REVISE`
- `NO-GO`

**Before** writing `verdict=GO` to `triadev-handoff.json.value_gate.verdict`, invoke [`verification-before-completion`](../verification-before-completion/SKILL.md) skill to verify:
- (a) sidecar passes `contracts/value-review.schema.json`
- (b) `scripts/check_review.py` exits 0 (0 violations)
- (c) sidecar `rubber_stamp_flags.any_triggered == false`

If any check fails, degrade verdict to `REVISE` or `NO-GO`.

Then provide:

- Top 3 reasons for verdict
- Preconditions to change verdict
- Next action within 48 hours

## Anti-Patterns (Block or Flag)

Flag these explicitly in `value-review.md` Section 5.2 — check the box OR justify why not present. Silent skip counts toward R5:

1. **Solution-first bias**: jumping to implementation before proving problem value
2. **Metric theater**: vanity metrics with no user/business outcome
3. **Roadmap cargo-cult**: doing it because competitors or old plans say so
4. **Unpriced complexity**: underestimating integration, maintenance, or migration cost
5. **Single-stakeholder capture**: prioritizing one loud request over broad value
6. **Evidence laundering**: treating assumptions as facts

If 2+ anti-patterns are present and unresolved, default to `REVISE` or `NO-GO`.

## Hand-off JSON Fields

After the gate completes, triadev copies fields from `value-review.json` into `triadev-handoff.json.value_gate`:

| Source (sidecar) | Target (handoff) | Mapping |
|------------------|------------------|---------|
| `verdict` | `value_gate.verdict` | Direct copy |
| derived from verdict | `value_gate.status` | GO → `passed`, REVISE\|NO-GO → `blocked` |
| `review_path` | `value_gate.review_path` | Direct copy |

Triadev does **not** read the markdown. Always update the sidecar.

Triadev refuses to transition `current_phase` from `value-gate` to `implementation` unless:
- `value_gate.verdict == "GO"` AND
- Sidecar `rubber_stamp_flags.any_triggered == false`

This is documented in [triadev/references/phase-transitions.md](../triadev/references/phase-transitions.md).

## Output Quality Rules

- Make claims falsifiable; avoid vague language.
- Quantify uncertainty where possible.
- Separate facts from assumptions.
- Tie every recommendation to expected value and measurable signal.
- Keep it concise and decision-oriented.

## Hand-off Rules

- If verdict is `GO`: hand off to TDD/SDD with explicit scope, success metrics, and risk controls from `value-review.md`.
- If verdict is `REVISE`: propose the smallest validation experiment and re-run gate after results.
- If verdict is `NO-GO`: propose 1-2 higher-value alternatives.

## Working Examples

- [examples/legitimate-go/](examples/legitimate-go/) — clean GO with varied scores, filled evidence, substantive Devil's Advocate.
- [examples/rubber-stamp-caught/](examples/rubber-stamp-caught/) — plausible-looking review that the validator downgrades to REVISE. Shows all 5 rules firing.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_review.py` | Validate sidecar against 5 rubber-stamp rules. Run after emitting the sidecar. Exit 1 on violation. |
| `scripts/emit_verdict_json.py` | Regenerate sidecar from a hand-edited `value-review.md`. Use during REVISE iteration when editing MD by hand. |

Scripts are optional for the skill's reasoning — Claude can perform the checks directly. Use scripts when integrating with automation or when verifying post-hoc.
