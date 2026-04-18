# value-first-gate

Pre-implementation value gate: **GO / REVISE / NO-GO** decision before any coding starts.

Part of the TriaDev Golden Triangle. Runs after planning, before TDD/SDD.

## What it does

1. **Problem Framing** — one-line decision object, baseline, opportunity cost
2. **First-Principles Critique** — 5 structured questions; unclear answers cap scores
3. **6-Dimension Rubric** — user impact, strategic fit, urgency, evidence, effort, risk (each 0-5)
4. **Rubber-Stamp Guards** — 5 rules that force REVISE when the review looks shallow
5. **Devil's Advocate Pass** — one mandatory sentence capturing the strongest counterargument
6. **Verdict** — GO (≥22, no flags), REVISE (16-21 OR any flag), NO-GO (≤15)

## Outputs

Every run produces TWO files:

- `value-review.md` — human-facing, with YAML frontmatter
- `value-review.json` — machine-readable sidecar (**authoritative**)

Triadev reads the sidecar, never the markdown.

## Quick reference

| Task | See |
|------|-----|
| Run the gate | [SKILL.md](SKILL.md) |
| Template for MD + sidecar | [templates/](templates/) |
| How verdict flows to triadev | [references/verdict-extraction.md](references/verdict-extraction.md) |
| The 5 rubber-stamp rules | [references/rubber-stamp-rules.md](references/rubber-stamp-rules.md) |
| JSON Schema for sidecar | [contracts/value-review.schema.json](contracts/value-review.schema.json) |
| Run rubber-stamp validator | `python scripts/check_review.py <sidecar.json>` |
| Regenerate sidecar from MD | `python scripts/emit_verdict_json.py <review.md>` |
| Worked GO example | [examples/legitimate-go/](examples/legitimate-go/) |
| Worked rubber-stamp case | [examples/rubber-stamp-caught/](examples/rubber-stamp-caught/) |

## Files

```
value-first-gate/
├── SKILL.md                                      # Main workflow (v2.0)
├── README.md                                     # This file
├── contracts/
│   ├── stack-handshake.json                      # v2.0.0 — reads/writes handoff fields
│   └── value-review.schema.json                  # JSON Schema for sidecar
├── templates/
│   ├── value-review-template.md                  # Human-facing template + frontmatter
│   └── value-review.json                         # Sidecar template
├── references/
│   ├── verdict-extraction.md                     # Contract: MD → JSON → handoff
│   └── rubber-stamp-rules.md                     # The 5 validator rules
├── scripts/
│   ├── check_review.py                           # Validate sidecar, exit 1 on violation
│   └── emit_verdict_json.py                      # Regenerate sidecar from MD
├── evals/
│   └── evals.json                                # 8 test cases (GO/NO-GO/rubber-stamp × 5)
└── examples/
    ├── legitimate-go/                            # Clean GO — harvested from humanizer-skill
    └── rubber-stamp-caught/                      # All 5 rules fire — validator forces REVISE
```

## Triggers

- English: "should we build this", "is this worth doing", "go/no-go", "value gate"
- 中文：值不值得做、做个价值评估、先评估一下、有没有必要做、这个需求值得投入吗、优先级评估

## Integration

| Upstream | value-first-gate reads |
|----------|------------------------|
| planning-with-files | reads `task_plan.md` / `findings.md` for scope context |
| triadev | reads `triadev-handoff.json` → `planning.tasks_extracted`, `scheduling.batches` |

| Downstream | value-first-gate writes |
|------------|-------------------------|
| triadev | writes `triadev-handoff.json` → `value_gate.{status, verdict, review_path}` |
| tdd-sdd-development | gated by `verdict == "GO"` AND `rubber_stamp_flags.any_triggered == false` |

## Dependencies

- triadev ≥ 3.0.0
- planning-with-files ≥ 2.10.0
- Python 3.8+ (for optional validator scripts)
