#!/usr/bin/env python3
"""check_review.py — rubber-stamp validator for value-review.json sidecar.

Exits 0 if no rubber-stamp signals triggered, 1 otherwise.
Always prints structured summary to stdout.

Usage:
    python scripts/check_review.py <path-to-value-review.json>

The validator enforces 5 rules:
  R1: score_spread == 0        (all 6 criterion scores identical)
  R2: evidence_cells_empty >= 2
  R3: devils_advocate field is empty
  R4: critique_unclear_count >= 2
  R5: anti_patterns_all_silent (0 checked AND 0 justified)

Any rule triggered forces verdict to REVISE or NO-GO. If the sidecar's verdict is
"GO" while any rule is triggered, the validator reports a contract violation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check_sidecar(sidecar: dict) -> tuple[list[str], bool]:
    """Return (violations, any_triggered)."""
    violations: list[str] = []
    flags = sidecar.get("rubber_stamp_flags", {})

    if flags.get("score_spread_zero"):
        violations.append("R1: score_spread == 0 — all 6 criterion scores are identical (rubber-stamp signal)")

    ec = flags.get("evidence_cells_empty_count", 0)
    if ec >= 2:
        violations.append(f"R2: {ec} evidence cells left empty (>= 2 triggers REVISE)")

    if flags.get("devils_advocate_empty"):
        violations.append("R3: Devil's Advocate field is blank — required non-empty")

    cu = flags.get("critique_unclear_count", 0)
    if cu >= 2:
        violations.append(f"R4: {cu} critique questions unclear (>= 2 triggers REVISE)")

    if flags.get("anti_patterns_all_silent"):
        violations.append("R5: All 6 anti-patterns left unchecked AND unjustified — honest reviews have something to say")

    any_triggered = len(violations) > 0
    return violations, any_triggered


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_review.py <path-to-value-review.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    with open(path, encoding="utf-8") as f:
        sidecar = json.load(f)

    violations, any_triggered = check_sidecar(sidecar)
    verdict = sidecar.get("verdict")

    print(f"sidecar: {path}")
    print(f"verdict: {verdict}")
    print(f"any_rubber_stamp_triggered: {any_triggered}")
    print(f"violations ({len(violations)}):")
    for v in violations:
        print(f"  - {v}")

    # Contract violation check: GO + any triggered is a contract break
    if verdict == "GO" and any_triggered:
        print("\nCONTRACT VIOLATION: verdict=GO but rubber-stamp signals triggered.")
        print("The sidecar must set verdict to REVISE or NO-GO when any rule fires.")
        return 1

    if any_triggered:
        print("\nResult: rubber-stamp signals present; verdict correctly degraded.")
        return 1

    print("\nResult: clean review, no rubber-stamp signals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
