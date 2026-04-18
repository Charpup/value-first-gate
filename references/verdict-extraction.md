# Verdict Extraction Contract

How `value-first-gate` output flows into `triadev-handoff.json`.

## Output Artifacts

Every gate run produces **two** artifacts, written side-by-side:

| File | Role | Readership |
|------|------|-----------|
| `value-review.md` | Human-facing review. Full narrative + rubric + anti-pattern analysis + Devil's Advocate. | Author, reviewer, future self |
| `value-review.json` | Authoritative machine-readable sidecar. Mirrors verdict + scores + rubber-stamp flags. | `triadev`, `check_review.py`, future eval harness |

**The sidecar is authoritative.** The markdown may drift during hand-editing; the sidecar is the ground truth triadev consumes.

## Three-Way Consistency

Three places carry the verdict:

1. `value-review.md` Section 1 body: `**Verdict:** \`GO | REVISE | NO-GO\``
2. `value-review.md` YAML frontmatter (top of file): `verdict: "GO | REVISE | NO-GO"`
3. `value-review.json` root: `"verdict": "GO"`

Rules:
- If (3) disagrees with (1) or (2): **sidecar wins**. Fail loudly with a readable error.
- After hand-editing the markdown, regenerate the sidecar via `scripts/emit_verdict_json.py <path.md>`.
- Never parse the markdown body for verdict in automated flows. Read the sidecar.

## Triadev Handoff Mapping

When invoked as part of the Extended path, triadev reads `value-review.json` and copies three fields into `triadev-handoff.json`:

```
value-review.json              →  triadev-handoff.json.value_gate
─────────────────────────────     ──────────────────────────────
verdict: "GO"                  →  verdict: "GO"
verdict: "REVISE" or "NO-GO"   →  verdict: "REVISE" / "NO-GO"
(derived from verdict)         →  status: "passed" | "blocked"
review_path                    →  review_path
```

### Verdict-to-Status Mapping

| value-review.json `verdict` | triadev-handoff.json `value_gate.status` |
|---|---|
| `GO` | `passed` |
| `REVISE` | `blocked` |
| `NO-GO` | `blocked` |

Special case for Core path: value-first-gate is not invoked. triadev sets `value_gate.status = "skipped"` and `verdict = null` directly.

**Ownership**: value-first-gate writes its sidecar; triadev performs the copy+mapping. Value-first-gate does not touch `status` directly.

## Rubber-Stamp Gate

Triadev MUST refuse to transition `current_phase` from `value-gate` to `implementation` if either:

- `value_gate.verdict != "GO"`, **OR**
- The sidecar's `rubber_stamp_flags.any_triggered == true` (regardless of verdict — this is a safety net for authors who manually wrote GO despite validator warnings)

See `triadev/references/phase-transitions.md` for the transition rule.

## Fields Added to the Handoff Contract

The sidecar brings fields that the handoff does **not** store but the validator uses:

- `per_criterion_scores` — 6 integer scores (used by eval harness to detect rubber-stamp)
- `rubber_stamp_flags.*` — 6 booleans + derived `any_triggered`
- `score_spread` — deterministic integer for drift detection
- `previous_reviews` — history array, grows on REVISE

Triadev does not copy these, but they remain queryable via the sidecar path stored in `value_gate.review_path`.

## REVISE Iteration

When a gate result is REVISE:

1. Keep the current `value-review.md` and `value-review.json`; do not overwrite.
2. On re-run, write a **new** pair: `value-reviews/YYYY-MM-DD-<slug>-r2.md` (incrementing suffix).
3. In the new sidecar, append the prior review to `previous_reviews[]`:
   ```json
   "previous_reviews": [
     {"path": "value-reviews/2026-04-18-rate-limiter.md", "verdict": "REVISE", "generated_at": "..."}
   ]
   ```
4. Update `value_gate.review_path` in handoff.json to point at the latest.

This preserves audit trail: a second REVISE at 16/30 after a first REVISE at 14/30 is evidence of incremental progress, not a single stall.

## Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| triadev reads `verdict: null` from handoff after gate | value-first-gate did not write the sidecar | Run `scripts/emit_verdict_json.py` on the MD |
| Sidecar says GO, validator flags rubber-stamp | Author overrode validator's recommendation | Either (a) remove rubber-stamp signals from MD + regenerate, or (b) accept that the handoff's rubber-stamp gate will still block implementation |
| MD frontmatter disagrees with sidecar | Hand-edit drift | Regenerate sidecar; sidecar is authoritative |
| `review_path` in handoff points at deleted file | REVISE iteration cleaned up too aggressively | Never delete historical reviews; only add new ones |
