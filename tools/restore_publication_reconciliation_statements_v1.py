#!/usr/bin/env python3
"""Restore reconciliation-appendix statements from the live claim census.

This repair is deliberately narrow. It changes only the text between
``Current exact statement:`` and ``Formal closure status:`` inside an existing
claim-specific reconciliation entry, and replaces that text with the exact
current statement from ``census/claims.json``.
"""

from __future__ import annotations

import argparse
import json
import re

import reconcile_publication_current_claim_records_v1 as source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    claims_by_branch = source.current_claims()
    paper_reports = []
    total_restored = 0

    for target in source.TARGETS:
        path = source.ROOT / target.path
        text = path.read_text(encoding="utf-8")
        restored = []

        if source.HEADING in text:
            for claim in claims_by_branch[target.branch]:
                claim_id = claim["claim_id"]
                pattern = re.compile(
                    rf"(?ms)(^### `{re.escape(claim_id)}`\n.*?"
                    rf"^Current exact statement: ).*?"
                    rf"(?=\n\nFormal closure status:)"
                )
                matches = list(pattern.finditer(text))
                if not matches:
                    continue
                if len(matches) != 1:
                    raise SystemExit(
                        f"ambiguous reconciliation entry for {claim_id}: {len(matches)}"
                    )
                current = matches[0].group(0).split("Current exact statement: ", 1)[1]
                if current == claim["statement"]:
                    continue
                text, count = pattern.subn(
                    lambda match: match.group(1) + claim["statement"], text, count=1
                )
                if count != 1:
                    raise SystemExit(f"failed to restore {claim_id}")
                restored.append(claim_id)

        if args.apply and restored:
            path.write_text(text, encoding="utf-8")
        total_restored += len(restored)
        paper_reports.append(
            {
                "branch": target.branch,
                "path": target.path,
                "restored_statement_count": len(restored),
                "restored_claim_ids": restored,
            }
        )

    report = {
        "schema": "sft-v3-publication-reconciliation-statement-restoration/1",
        "authoritative_source": "census/claims.json",
        "applied": args.apply,
        "restored_statement_count": total_restored,
        "papers": paper_reports,
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = source.ROOT / args.json_out
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(f"reconciliation statement restoration v1: {total_restored} restored")


if __name__ == "__main__":
    main()
