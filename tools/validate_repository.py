"""Validate the constitutional repository scaffold using the Python standard library."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import ENGINE_ID, REQUIRED_DENIED_CAPABILITIES, ROOT_THEOREM  # noqa: E402
from sft.engine.receipt_io import verify_receipt_mapping  # noqa: E402

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
    "docs/ENGINE_AUTHORITY.md",
    "docs/ENGINE_STATUS.md",
    "docs/PORTABILITY.md",
    "docs/VERIFICATION.md",
    "docs/V4_SELF_HOSTED_REBUILD.md",
    "census/claims.json",
    "census/execution_manifest.json",
    "census/branches.json",
    "governance/claim.schema.json",
    "governance/engine_policy.json",
    "governance/engine_receipt.schema.json",
    "governance/execution_manifest.schema.json",
    "governance/experiment.schema.json",
    ".github/workflows/portable-validation.yml",
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
    "sft/engine",
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
        for claim in census.get("claims", []):
            relative_receipt = claim.get("receipt_path")
            if not isinstance(relative_receipt, str):
                errors.append(f"census claim lacks receipt path: {claim.get('claim_id')}")
                continue
            receipt_path = ROOT / relative_receipt
            if not receipt_path.is_file():
                errors.append(f"census receipt is missing: {relative_receipt}")
                continue
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if not verify_receipt_mapping(receipt):
                errors.append(f"census receipt hash is invalid: {relative_receipt}")
            if not receipt.get("model_admitted"):
                errors.append(f"census points to an unclosed receipt: {relative_receipt}")

    policy_path = ROOT / "governance" / "engine_policy.json"
    if policy_path.is_file():
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        if policy.get("engine_id") != ENGINE_ID:
            errors.append("engine policy identity differs from the executable engine")
        if policy.get("root_theorem") != ROOT_THEOREM:
            errors.append("engine policy root differs from the executable engine")
        if policy.get("axioms_permitted") is not False:
            errors.append("engine policy must forbid axioms")
        if policy.get("free_parameters_permitted") is not False:
            errors.append("engine policy must forbid free parameters")
        if policy.get("halt_on_any_violation") is not True:
            errors.append("engine policy must be fail-closed")
        if policy.get("portable_host_systems") != ["macos", "windows", "linux"]:
            errors.append("engine policy must support macOS, Windows and Linux through one contract")
        if policy.get("third_party_runtime_required") is not False:
            errors.append("portable baseline must not require a third-party runtime")
        if tuple(policy.get("prediction_denied_capabilities", ())) != REQUIRED_DENIED_CAPABILITIES:
            errors.append("engine policy and executable denied-capability sets differ")
        if policy.get("host_platform_may_select_scientific_behavior") is not False:
            errors.append("host platform must not select scientific behavior")

    branches_path = ROOT / "census" / "branches.json"
    if branches_path.is_file():
        branch_census = json.loads(branches_path.read_text(encoding="utf-8"))
        branch_ids = [branch.get("branch_id") for branch in branch_census.get("branches", [])]
        if not branch_ids or len(set(branch_ids)) != len(branch_ids):
            errors.append("branch census must contain unique registered branches")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("repository validation failed:\n" + "\n".join(errors))
    print("repository validation: PASS")
    census = json.loads((ROOT / "census" / "claims.json").read_text(encoding="utf-8"))
    print(f"scientific status: {len(census['claims'])} v3 claim(s) admitted through the engine")
    print("future generation: v4 SFT-derived self-hosted reconstruction registered")


if __name__ == "__main__":
    main()
