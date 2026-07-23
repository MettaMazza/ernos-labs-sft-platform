"""Validate the constitutional repository scaffold using the Python standard library."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = (
    "README.md",
    "CONSTITUTION.md",
    "AGENTS.md",
    "LANGUAGE_POLICY.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "docs/CLEAN_ROOM_PROTOCOL.md",
    "docs/CLAIM_LIFECYCLE.md",
    "docs/EMPIRICAL_METHOD.md",
    "docs/V4_SELF_HOSTED_REBUILD.md",
    "census/claims.json",
    "governance/claim.schema.json",
    "governance/experiment.schema.json",
)

REQUIRED_DIRECTORIES = (
    "sft/foundation",
    "sft/mathematics",
    "sft/information_science",
    "sft/computation",
    "sft/quantum_computation",
    "sft/physics",
    "sft/chemistry_materials",
    "sft/biology",
    "sft/earth_environment",
    "sft/astronomy_cosmology",
    "sft/engineering_translation",
    "claims",
    "experiments",
    "correspondence",
    "generated/c",
    "tests",
    "census",
    "frontier",
    "prior-work-ledger",
    "applications/frontier",
)


def validate() -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for relative in REQUIRED_DIRECTORIES:
        if not (ROOT / relative).is_dir():
            errors.append(f"missing required directory: {relative}")

    for path in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

    for path in sorted(ROOT.rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            errors.append(f"invalid Python: {path.relative_to(ROOT)}: {exc}")

    census_path = ROOT / "census" / "claims.json"
    if census_path.is_file():
        census = json.loads(census_path.read_text(encoding="utf-8"))
        if not isinstance(census.get("claims"), list):
            errors.append("census claims must be a list")
        if census.get("generation") != "v3-python-accessible":
            errors.append("census must identify the accessible v3 generation")
        if census.get("future_generation") != "v4-sft-derived-self-hosted":
            errors.append("census must preserve the registered v4 generation")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("repository validation failed:\n" + "\n".join(errors))
    print("repository validation: PASS")
    print("scientific status: constitutional scaffold; no v3 claims admitted")
    print("future generation: v4 SFT-derived self-hosted reconstruction registered")


if __name__ == "__main__":
    main()
