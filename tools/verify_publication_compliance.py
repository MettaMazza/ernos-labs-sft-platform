#!/usr/bin/env python3
"""Audit or enforce the current-knowledge branch publication gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.publication_compliance import (  # noqa: E402
    BRANCH_PREFIXES,
    CurrentPublicationHalt,
    audit_branch,
    require_current_publication_ready,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=tuple(BRANCH_PREFIXES))
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return failure unless the selected branch is currently publishable",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.require_ready and not args.branch:
        parser.error("--require-ready also requires --branch")

    branches = (args.branch,) if args.branch else tuple(BRANCH_PREFIXES)
    results = [audit_branch(ROOT, branch) for branch in branches]
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            status = "READY" if result.current_publication_ready else "BLOCKED"
            print(
                f"{result.branch_id}: {status}; live={result.live_claim_count}; "
                f"frozen={result.frozen_inventory_claim_count}; "
                f"paper={result.archival_paper_claim_count}"
            )
            for blocker in result.blockers:
                print(f"  - {blocker}")

    if args.require_ready:
        try:
            require_current_publication_ready(ROOT, args.branch)
        except CurrentPublicationHalt as exc:
            raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
