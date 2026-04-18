# Example: legitimate-go — a clean GO decision

## What this is

A synthesized but realistic `value-first-gate` run for a real proposal:
**"Add `--voice bob` personal style injection to humanizer skill"**.

Harvested from `projects/humanizer-skill/` (March 2026, PR blader/humanizer#94 merged).

## Why this is a legitimate GO

All three signals line up:

- **Score spread is 3** (lowest 3 on Urgency, highest 5 on Effort Efficiency) — not uniform, reflects real tradeoffs
- **Devil's Advocate is filled** — the Challenger role in the original brainstorm questioned urgency; this is captured
- **Anti-patterns either checked or justified** — zero silent skips
- **Evidence cells filled** — references to GitHub PR, user profile, existing infrastructure

Total score 24/30, verdict GO. No rubber-stamp flags triggered.

## Files

| File | Purpose |
|------|---------|
| `value-review.md` | Human-facing review (with YAML frontmatter) |
| `value-review.json` | Machine sidecar (authoritative) |

## What validator says

Running `python scripts/check_review.py examples/legitimate-go/value-review.json` returns **exit 0** — clean review.
