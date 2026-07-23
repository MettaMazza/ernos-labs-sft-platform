"""Small, dependency-free repository status interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sft import BUILD_GENERATION, BUILD_PHASE


ROOT = Path(__file__).resolve().parent.parent


def repository_status() -> dict[str, object]:
    census_path = ROOT / "census" / "claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    claims = census["claims"]
    return {
        "generation": BUILD_GENERATION,
        "phase": BUILD_PHASE,
        "registered_claims": len(claims),
        "admitted_claims": sum(
            claim.get("status") in {"uniquely_closed", "independently_replicated"}
            for claim in claims
        ),
        "remote_publication": "not-configured",
        "future_generation": "v4-sft-derived-self-hosted",
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="sft")
    parser.add_argument("command", choices=("status",))
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(repository_status(), indent=2, sort_keys=True))
