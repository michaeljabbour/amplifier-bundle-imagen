#!/usr/bin/env python3
"""Run or verify the deterministic high-risk behavioral evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.behavioral_harness import evaluate_sync  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluated-at",
        help="ISO-8601 evidence timestamp; defaults to the current UTC time",
    )
    parser.add_argument("--output", type=Path, help="write JSON evidence to this path")
    parser.add_argument(
        "--verify",
        type=Path,
        help="rerun using a committed result's timestamp and require an exact match",
    )
    args = parser.parse_args()

    expected = None
    evaluated_at = args.evaluated_at
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        evaluated_at = expected["evaluated_at"]

    result = evaluate_sync(evaluated_at=evaluated_at)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    elif expected is None:
        print(rendered, end="")

    if expected is not None and result != expected:
        print(f"behavioral evidence drifted from {args.verify}", file=sys.stderr)
        return 1
    if expected is not None:
        summary = result["summary"]
        print(
            "behavioral evidence verified: "
            f"{summary['passed']}/{summary['cases']} cases passed; "
            f"{summary['unsafe_mutations_rejected']}/"
            f"{summary['unsafe_mutations']} unsafe mutations rejected"
        )
    return 0 if result["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
