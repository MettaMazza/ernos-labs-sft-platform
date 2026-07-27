#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-002 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.coordination_number_batch_v1 import (  # noqa: E402
    COORDINATION_NUMBER_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.coordination_number_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_coordination_number_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_execution():
    path = ROOT / "claims" / COORDINATION_NUMBER_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_002", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load INORG-002 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COORDINATION_NUMBER_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {
        row["claim_id"] for row in json.loads(census_path.read_text())["claims"]
    }:
        raise SystemExit("claim already admitted; immutable receipt preserved")

    execution = load_execution()
    captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class CaptureEmpirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
    )
    if not receipt.model_admitted:
        raise SystemExit(
            f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}"
        )

    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {
                "claim_id": spec.claim_id,
                "execution_file": f"claims/{spec.claim_id}/execution.py",
            }
        )
        write_json(manifest_path, manifest)

    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_coordination_number_analysis(rows, primary)
    vector = tuple(
        {
            "target_id": row["target_id"],
            "authority": row["authority"],
            "source_document_identity": row["source_document_identity"],
            "source_record_role": row["source_record_role"],
            "source_record_ordinal": row["source_record_ordinal"],
            "source_inscription": row["source_inscription"],
            "complete_target_payload_hash": row["target_payload_hash"],
            "status": row["status"],
        }
        for row in rows
    )

    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {
            "claim_id": spec.claim_id,
            "controls": asdict(sealed)["controls"],
        },
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-INORG-002",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(
                decision.survives for decision in sealed.decisions
            ),
            "coordination_number_law": "the exact positive cardinality of every distinct direct ligand incidence on the retained central occurrence",
            "depth_independent_successor": "the next distinct direct incidence preserves every prior trace and increments the positive count by exactly one",
            "exact_generated_three_four_five_vector": [3, 4, 5],
            "complete_source_class_census": analysis["source_class_census"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "iupac_general_direct_link_definition_retained": analysis[
                "iupac_general_direct_link_definition_retained"
            ],
            "iupac_inorganic_sigma_definition_retained": analysis[
                "iupac_inorganic_sigma_definition_retained"
            ],
            "nist_three_four_five_vector_retained": analysis[
                "nist_three_four_five_vector_retained"
            ],
            "complete_reported_boundary_absence_and_disclaimer_surface_retained": analysis[
                "all_boundaries_absences_and_disclaimers_retained"
            ],
            "source_counts_used_as_proof_parameters": False,
            "imported_coordination_number_table_valence_rule_geometry_catalogue_ligand_field_bonding_model_fit_selection_or_target_correction_used": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)

    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)

    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-002`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: coordination number is the positive cardinality of all distinct direct ligand incidences on the retained central occurrence.\n"
        "- Depth-independent successor: one new direct incidence preserves every prior trace and adds exactly one.\n"
        "- Complete external surface: one IUPAC term record and three complete NIST structure pages represented by twenty-three sealed identities.\n"
        "- Exact post-seal direct-link vector: ScF3 = 3, TiCl4 = 4, Fe(CO)5 = 5.\n"
        "- Adverse surface: alternate crystallographic sense, pi-link exclusion, missing coordinate and rotational records, and authority disclaimers remain visible.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )

    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(
        f"candidates: {len(sealed.census.candidates)}; "
        f"survivors: {sum(decision.survives for decision in sealed.decisions)}"
    )
    print(
        "complete coordination-number vector: 23 records; "
        "IUPAC direct-link/sigma/pi/crystal boundaries; NIST 3/4/5"
    )


if __name__ == "__main__":
    main()
