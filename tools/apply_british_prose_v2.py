#!/usr/bin/env python3
"""Extend the frozen v1 British-prose pass with additional safe spellings.

The v1 protection boundaries remain authoritative: claim records, literal
identifiers, hashes, source material, quotations, code and post-reference
material are reported rather than rewritten. This version adds only ordinary
human-prose variants identified during the publication proofreading pass.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import apply_british_prose_v1 as v1


ADDITIONAL_SPELLINGS = {
    "authorization": "authorisation",
    "authorize": "authorise",
    "authorized": "authorised",
    "authorizes": "authorises",
    "authorizing": "authorising",
    "catalog": "catalogue",
    "cataloged": "catalogued",
    "cataloging": "cataloguing",
    "catalogs": "catalogues",
    "center": "centre",
    "centers": "centres",
    "optimization": "optimisation",
    "rigor": "rigour",
}

v1.SPELLINGS.update(ADDITIONAL_SPELLINGS)
v1.PROTECTED_RECORD_MARKERS = re.compile(
    v1.PROTECTED_RECORD_MARKERS.pattern
    + r"|Current exact statement:|Earlier display gap:|Formal closure status:"
    + r"|Current external status:|Model-admitted receipt:|Receipt path:",
    re.IGNORECASE,
)
v1.TOKEN = re.compile(
    "|".join(
        rf"\b{re.escape(word)}\b"
        for word in sorted(v1.SPELLINGS, key=len, reverse=True)
    ),
    re.IGNORECASE,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    reports = [v1.process(v1.ROOT / paper, args.apply) for paper in v1.PAPERS]
    result = {
        "schema": "sft-v3-british-prose-editorial-pass/2",
        "inherits": "sft-v3-british-prose-editorial-pass/1",
        "applied": args.apply,
        "additional_spellings": ADDITIONAL_SPELLINGS,
        "papers": reports,
        "summary": {
            "safe_changes": sum(item["safe_change_count"] for item in reports),
            "protected_occurrences": sum(
                item["protected_occurrence_count"] for item in reports
            ),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = v1.ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    action = "applied" if args.apply else "proposed"
    print(
        f"British prose v2 {action}: {result['summary']['safe_changes']} safe "
        f"changes; {result['summary']['protected_occurrences']} protected occurrences"
    )


if __name__ == "__main__":
    main()
