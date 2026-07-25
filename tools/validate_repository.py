"""Validate the constitutional repository scaffold using the Python standard library."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.claim_evidence import (  # noqa: E402
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldOpcode,
    HostilePackageAuditor,
)
from sft.engine import (  # noqa: E402
    ENGINE_ID,
    REQUIRED_DENIED_CAPABILITIES,
    ROOT_THEOREM,
)
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
    "governance/AMENDMENT_2026-07-24_PRIOR_OBSERVATIONS.md",
    "census/claims.json",
    "census/execution_manifest.json",
    "census/branches.json",
    "census/prior_obligation_ownership.json",
    "audits/v1_theorem_manifest_observation_census.json",
    "audits/v2_407_step_observation_census.json",
    "audits/physics_prior_value_audit_2026-07-24.json",
    "governance/claim.schema.json",
    "governance/engine_policy.json",
    "sft/publication_compliance.py",
    "tools/verify_publication_compliance.py",
    "governance/engine_receipt.schema.json",
    "governance/execution_manifest.schema.json",
    "governance/experiment.schema.json",
    "governance/fold_program.schema.json",
    ".github/workflows/portable-validation.yml",
)

REQUIRED_DIRECTORIES = (
    "sft/foundation",
    "sft/mathematics",
    "sft/information_science",
    "sft/computation",
    "sft/quantum_computation",
    "sft/physics",
    "sft/chemistry",
    "sft/materials",
    "sft/biology",
    "sft/consciousness_cognitive_science",
    "sft/earth_environment",
    "sft/astronomy_cosmology",
    "sft/social_collective_systems",
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
        if policy.get("official_prediction_interpreter_id") != CapabilityClosedFoldInterpreter.interpreter_id:
            errors.append("engine policy and executable Fold interpreter identities differ")
        if policy.get("official_prediction_program_schema") != "sft-v3-fold-program/1":
            errors.append("engine policy must name the strict data-only Fold program schema")
        if tuple(policy.get("official_prediction_opcodes", ())) != tuple(opcode.value for opcode in FoldOpcode):
            errors.append("engine policy and executable Fold opcode surfaces differ")
        if policy.get("portable_target_exchange_id") != CrossPlatformCustodyExchange.exchange_id:
            errors.append("engine policy and executable target-exchange identities differ")
        if policy.get("target_commitment_precedes_prediction") is not True:
            errors.append("engine policy must require a target commitment before prediction")
        if policy.get("target_release_requires_matching_seal") is not True:
            errors.append("engine policy must bind target release to the matching prediction seal")
        if policy.get("hostile_package_auditor_id") != HostilePackageAuditor.auditor_id:
            errors.append("engine policy and executable hostile-package auditor identities differ")
        if policy.get("protected_authority_paths") != ["census", "receipts/engine/model_admitted"]:
            errors.append("engine policy must protect the census and model-admitted receipt tree")
        if policy.get("contributor_executable_prediction_source_permitted") is not False:
            errors.append("official empirical prediction must reject contributor executable source")
        if policy.get("branch_paper_requires_complete_prior_work_reconciliation") is not True:
            errors.append("branch publication must require complete prior-work reconciliation")
        if policy.get("branch_paper_requires_live_census_inventory_equality") is not True:
            errors.append("branch publication must require equality with the live branch census")
        if policy.get("zenodo_publication_requires_current_compliance_gate") is not True:
            errors.append("Zenodo publication must require the current compliance gate")

    branches_path = ROOT / "census" / "branches.json"
    if branches_path.is_file():
        branch_census = json.loads(branches_path.read_text(encoding="utf-8"))
        branch_ids = [branch.get("branch_id") for branch in branch_census.get("branches", [])]
        if not branch_ids or len(set(branch_ids)) != len(branch_ids):
            errors.append("branch census must contain unique registered branches")
        required_scientific_branches = {
            "foundation", "mathematics", "information_science", "computation",
            "quantum_computation", "physics", "chemistry", "materials",
            "biology", "consciousness_cognitive_science", "earth_environment",
            "astronomy_cosmology", "social_collective_systems",
            "engineering_translation",
        }
        missing_branches = sorted(required_scientific_branches - set(branch_ids))
        if missing_branches:
            errors.append("branch census is missing: " + ", ".join(missing_branches))

    prior_path = ROOT / "prior-work-ledger/manifest.json"
    if prior_path.is_file():
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        if prior.get("observational_authority") is not True:
            errors.append("prior SFT work must be registered as observational authority")
        if prior.get("prior_results_must_be_registered_before_reconstruction") is not True:
            errors.append("prior SFT results must define reconstruction obligations")
        if prior.get("answer_artifacts_permitted_in_v3_derivation_runtime") is not False:
            errors.append("prior answer artifacts must remain excluded from V3 derivation")

    v1_path = ROOT / "audits/v1_theorem_manifest_observation_census.json"
    if v1_path.is_file():
        v1 = json.loads(v1_path.read_text(encoding="utf-8"))
        rows = v1.get("rows", [])
        if v1.get("source_row_count") != 356 or len(rows) != 356:
            errors.append("V1 observational census must retain all 356 theorem-manifest rows")
        if len({row.get("v1_claim_id") for row in rows}) != len(rows):
            errors.append("V1 observational census claim identities must be unique")

    v2_path = ROOT / "audits/v2_407_step_observation_census.json"
    if v2_path.is_file():
        v2 = json.loads(v2_path.read_text(encoding="utf-8"))
        steps = v2.get("steps", [])
        if [row.get("step") for row in steps] != list(range(1, 408)):
            errors.append("V2 observational census must retain steps 1 through 407 once and in order")

    ownership_path = ROOT / "census/prior_obligation_ownership.json"
    if ownership_path.is_file():
        ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
        law = ownership.get("ownership_law", {})
        if law.get("composite_source_rows_must_be_decomposed") is not True:
            errors.append("composite prior source rows must be decomposed into atomic obligations")
        if law.get("exactly_one_primary_owner_per_atomic_obligation_required") is not True:
            errors.append("every atomic prior obligation must have exactly one primary owner")
        if law.get("physical_constants_and_dimensionless_physical_values_owner") != "physics":
            errors.append("physical constants and dimensionless physical values must be owned by Physics")
        if not isinstance(ownership.get("assignment_complete"), bool):
            errors.append("prior-obligation owner completion status must be boolean")
        if ownership.get("assignment_complete") and len(ownership.get("source_entry_assignments", [])) != 763:
            errors.append("complete prior-obligation ownership must cover all 763 source entries")
        registered_owners = set(ownership.get("registered_branches", []))
        if branches_path.is_file():
            branch_ids = {
                row.get("branch_id")
                for row in json.loads(branches_path.read_text(encoding="utf-8")).get("branches", [])
            }
            missing_owners = sorted((branch_ids - {"application_frontier"}) - registered_owners)
            if missing_owners:
                errors.append("ownership registry is missing branch owners: " + ", ".join(missing_owners))

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
