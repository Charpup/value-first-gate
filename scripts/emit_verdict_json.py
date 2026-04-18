#!/usr/bin/env python3
"""emit_verdict_json.py — regenerate sidecar from an edited value-review.md.

Bob's convenience path: if you edit value-review.md by hand (e.g. during REVISE iteration),
run this to recompute value-review.json from the markdown. The sidecar is authoritative for
triadev, so keeping it in sync is mandatory.

This is a BEST-EFFORT parser. It extracts:
  - YAML frontmatter (verdict, total_score, confidence, generated_at)
  - Section 4 rubric scores (per-criterion)
  - Section 5.2 anti-patterns (checked vs justified vs silent)
  - Section 9 Devil's Advocate field
  - Section 3.3 critique questions with notes marked "unclear"

It does NOT perform semantic verdict derivation — it mirrors what the author wrote.
If you want the validator to re-derive verdict, run check_review.py after.

Usage:
    python scripts/emit_verdict_json.py <path-to-value-review.md>

Outputs value-review.json next to the input markdown (same directory, same stem).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def extract_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"')
    return fm


def extract_rubric_scores(text: str) -> dict[str, int]:
    mapping = {
        "User Impact": "user_impact",
        "Strategic Fit": "strategic_fit",
        "Urgency": "urgency",
        "Evidence Strength": "evidence_strength",
        "Effort Efficiency": "effort_efficiency",
        "Risk Controllability": "risk_controllability",
    }
    scores: dict[str, int] = {v: 0 for v in mapping.values()}
    for label, key in mapping.items():
        # | User Impact | 4 | ... |
        pattern = rf"\|\s*{re.escape(label)}\s*\|\s*(\d+)\s*\|"
        m = re.search(pattern, text)
        if m:
            scores[key] = int(m.group(1))
    return scores


def extract_evidence_empty_count(text: str) -> int:
    """Count empty Evidence cells in the rubric table."""
    mapping = [
        "User Impact", "Strategic Fit", "Urgency",
        "Evidence Strength", "Effort Efficiency", "Risk Controllability",
    ]
    empty = 0
    for label in mapping:
        # |<label>| <score> | <evidence> | <notes> |
        pattern = rf"\|\s*{re.escape(label)}\s*\|\s*\d+\s*\|\s*([^|]*?)\s*\|"
        m = re.search(pattern, text)
        if not m:
            empty += 1
            continue
        ev = m.group(1).strip()
        if not ev or ev in {"-", "—", "N/A", "n/a"}:
            empty += 1
    return empty


def extract_devils_advocate(text: str) -> str:
    """Extract the Devil's Advocate field content."""
    m = re.search(
        r"\*\*The strongest argument against this decision is:\*\*\s*\n([^\n]*)",
        text,
    )
    if not m:
        return ""
    content = m.group(1).strip()
    # Strip template placeholder
    if content.startswith("_(") and content.endswith(")_"):
        return ""
    return content


def extract_anti_patterns(text: str) -> tuple[list[str], bool]:
    """Return (flagged_patterns, all_silent)."""
    patterns = [
        ("Solution-first bias", "solution_first_bias"),
        ("Metric theater", "metric_theater"),
        ("Roadmap cargo-cult", "roadmap_cargo_cult"),
        ("Unpriced complexity", "unpriced_complexity"),
        ("Single-stakeholder capture", "single_stakeholder_capture"),
        ("Evidence laundering", "evidence_laundering"),
    ]
    flagged: list[str] = []
    justified = 0
    for label, key in patterns:
        # - [x] Solution-first bias ...
        if re.search(rf"-\s*\[x\]\s*{re.escape(label)}", text, flags=re.IGNORECASE):
            flagged.append(key)
            continue
        # - [ ] ... — not present because: <text>
        unchecked = re.search(
            rf"-\s*\[\s*\]\s*{re.escape(label)}.*?—\s*_not present because:_\s*([^\n]+)",
            text,
        )
        if unchecked and unchecked.group(1).strip() and not unchecked.group(1).strip().startswith("_"):
            justified += 1
    all_silent = (len(flagged) == 0) and (justified == 0)
    return flagged, all_silent


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: emit_verdict_json.py <path-to-value-review.md>", file=sys.stderr)
        return 2

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"error: {md_path} does not exist", file=sys.stderr)
        return 2

    text = md_path.read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    scores = extract_rubric_scores(text)
    empty_evidence = extract_evidence_empty_count(text)
    da = extract_devils_advocate(text)
    flagged, all_silent = extract_anti_patterns(text)

    score_values = list(scores.values())
    score_spread = max(score_values) - min(score_values) if score_values else 0
    total_score = sum(score_values)

    rubber_stamp_flags = {
        "score_spread_zero": score_spread == 0,
        "evidence_cells_empty_count": empty_evidence,
        "devils_advocate_empty": not da.strip(),
        "critique_unclear_count": 0,  # Not auto-extracted; author-supplied or check_review can flag
        "anti_patterns_all_silent": all_silent,
        "any_triggered": False,
    }
    rubber_stamp_flags["any_triggered"] = (
        rubber_stamp_flags["score_spread_zero"]
        or rubber_stamp_flags["evidence_cells_empty_count"] >= 2
        or rubber_stamp_flags["devils_advocate_empty"]
        or rubber_stamp_flags["critique_unclear_count"] >= 2
        or rubber_stamp_flags["anti_patterns_all_silent"]
    )

    sidecar = {
        "$comment": "Regenerated by scripts/emit_verdict_json.py from value-review.md",
        "schema_version": "2.0",
        "proposal": "",
        "generated_at": fm.get("generated_at") or datetime.now().isoformat(timespec="seconds"),
        "owner": "",
        "verdict": fm.get("verdict", "REVISE"),
        "total_score": total_score,
        "confidence": fm.get("confidence", "Low"),
        "per_criterion_scores": scores,
        "critique_caps_applied": [],
        "anti_patterns_flagged": flagged,
        "devils_advocate": da,
        "rubber_stamp_flags": rubber_stamp_flags,
        "score_spread": score_spread,
        "review_path": md_path.name,
        "previous_reviews": [],
        "preconditions_to_change_verdict": "",
        "next_action_48h": {"action": "", "owner": "", "expected_signal": "", "re_evaluation_date": ""},
    }

    out_path = md_path.with_suffix(".json")
    out_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"emitted: {out_path}")
    print(f"verdict (from frontmatter): {sidecar['verdict']}")
    print(f"rubber_stamp_any_triggered: {rubber_stamp_flags['any_triggered']}")
    if rubber_stamp_flags["any_triggered"] and sidecar["verdict"] == "GO":
        print("warning: frontmatter says GO but rubber-stamp signals triggered — run check_review.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
