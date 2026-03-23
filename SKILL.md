---
name: value-first-gate
description: Force a pre-implementation value gate before coding starts. Use when the user asks for planning, review, prioritization, tradeoff analysis, "should we build this", roadmap ordering, or scope decisions before implementation. Run this after planning and before any TDD/SDD or coding workflow to prevent low-value execution and convert vague ideas into a measurable Go/No-Go decision.
---

# Value-First Gate

Run a strict decision gate **after planning** and **before TDD/SDD**.

If the user asks to implement immediately but value is unclear, pause implementation and run this gate first.

## Placement in Workflow

Use this sequence:

1. Planning (requirements, constraints, options)
2. **Value-First Gate (this skill)**
3. TDD/SDD (if and only if decision is GO)
4. Implementation

Do not enter TDD/SDD when gate result is `NO-GO` or `REVISE`.

## Required Output

Always produce `value-review.md` using the template at:

- `references/value-review-template.md`

If the template is unavailable, reproduce its exact section structure.

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

**Scoring impact**: For each question with an unclear or weak answer, note it explicitly and cap that dimension's score at 3/5 (marked as "First-principles unclear").

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

### Decision Thresholds

- **GO**: `total_score >= 22` and no criterion < 2
- **REVISE**: `16-21` or any criterion = 1 with plausible mitigation
- **NO-GO**: `<= 15` or critical risk cannot be mitigated

If confidence is `Low`, cap final decision at `REVISE` even if score says GO.

If 2+ First-Principles Critique questions were unclear, cap final decision at `REVISE`.

### 4) Go/No-Go Decision

Return one verdict:

- `GO`
- `REVISE`
- `NO-GO`

Then provide:

- Top 3 reasons for verdict
- Preconditions to change verdict
- Next action within 48 hours

## Anti-Patterns (Block or Flag)

Flag these explicitly in `value-review.md`:

1. **Solution-first bias**: jumping to implementation before proving problem value
2. **Metric theater**: vanity metrics with no user/business outcome
3. **Roadmap cargo-cult**: doing it because competitors or old plans say so
4. **Unpriced complexity**: underestimating integration, maintenance, or migration cost
5. **Single-stakeholder capture**: prioritizing one loud request over broad value
6. **Evidence laundering**: treating assumptions as facts

If 2+ anti-patterns are present and unresolved, default to `REVISE` or `NO-GO`.

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
