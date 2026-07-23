"""Small, dependency-free repository status interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sft import BUILD_GENERATION, BUILD_PHASE
from sft.engine import ENGINE_ID, ROOT_THEOREM


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


def engine_status() -> dict[str, object]:
    policy = json.loads((ROOT / "governance" / "engine_policy.json").read_text(encoding="utf-8"))
    return {
        "engine_id": ENGINE_ID,
        "root_theorem": ROOT_THEOREM,
        "halt_on_any_violation": policy["halt_on_any_violation"],
        "axioms_permitted": policy["axioms_permitted"],
        "free_parameters_permitted": policy["free_parameters_permitted"],
        "required_controls": policy["required_control_kinds"],
        "portable_host_systems": policy["portable_host_systems"],
        "third_party_runtime_required": policy["third_party_runtime_required"],
        "official_prediction_isolation": policy["official_prediction_isolation"],
        "census_admission_requires_accepted_receipt": policy[
            "census_admission_requires_accepted_receipt"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="sft")
    parser.add_argument("command", choices=("status", "engine-status"))
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(repository_status(), indent=2, sort_keys=True))
    elif args.command == "engine-status":
        print(json.dumps(engine_status(), indent=2, sort_keys=True))
