#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-002."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, localcontext
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.bond_dissociation_energy_batch_v1 import BOND_DISSOCIATION_ENERGY_SPEC  # noqa: E402
from sft.chemistry.bond_dissociation_energy_law_v1 import ground_dissociation_from_transition  # noqa: E402
from sft.chemistry.bond_dissociation_energy_validation_v1 import _load_targets  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exact_pair(value) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def display(value) -> str:
    with localcontext() as context:
        context.prec = 24
        return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def load_execution():
    path = ROOT / "claims" / BOND_DISSOCIATION_ENERGY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_002", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-002 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = BOND_DISSOCIATION_ENERGY_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            result = execution.independent_validator.validate(sealed)
            captured["external"] = result
            return result

    class CaptureEmpirical:
        def validate(self, sealed):
            result = execution.empirical_validator.validate(sealed)
            captured["empirical"] = result
            return result

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    targets = _load_targets(ROOT)
    grouped = {(row["species"], row["measurement_role"]): row for row in targets}
    quantitative = {}
    for species in ("H2", "D2"):
        threshold = grouped[(species, "path-threshold")]
        atomic = grouped[(species, "atomic-path-segment")]
        lower = ground_dissociation_from_transition(threshold["lower"], atomic["upper"])
        upper = ground_dissociation_from_transition(threshold["upper"], atomic["lower"])
        comparisons = []
        for role in ("historical-ground-dissociation", "later-ground-dissociation"):
            target = grouped[(species, role)]
            comparisons.append({
                "target_id": target["target_id"], "record_class": role,
                "source_inscription_inverse_centimetre": target["inscription"],
                "source_lower_inverse_centimetre": exact_pair(target["lower"]),
                "source_upper_inverse_centimetre": exact_pair(target["upper"]),
                "overlap": not (upper < target["lower"] or target["upper"] < lower),
            })
        quantitative[species] = {
            "postseal_exact_Take_lower_inverse_centimetre": exact_pair(lower),
            "postseal_exact_Take_upper_inverse_centimetre": exact_pair(upper),
            "postseal_exact_Take_lower_display_inverse_centimetre": display(lower),
            "postseal_exact_Take_upper_display_inverse_centimetre": display(upper),
            "comparisons": comparisons,
            "all_registered_ground_targets_overlap": all(row["overlap"] for row in comparisons),
        }

    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-PROP-002",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "exact_path_law": "D0(M2) = B-prime threshold[M(1s)+M(2s)] Take atomic[M(1s)->M(2s)]",
            "quantitative_vector": quantitative, "complete_external_rows": len(targets),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "fitted_or_free_parameter_used": False, "measured_value_in_derivation_or_prediction": False,
            "all_measurement_values_released_after_relation_seal": True,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-002`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact path law: `D0(M2) = B-prime threshold[M(1s)+M(2s)] Take atomic[M(1s)->M(2s)]`.\n"
        f"- H2 post-seal Take interval: `{quantitative['H2']['postseal_exact_Take_lower_display_inverse_centimetre']}` through `{quantitative['H2']['postseal_exact_Take_upper_display_inverse_centimetre']} cm^-1`; both ground targets overlap: `{quantitative['H2']['all_registered_ground_targets_overlap']}`.\n"
        f"- D2 post-seal Take interval: `{quantitative['D2']['postseal_exact_Take_lower_display_inverse_centimetre']}` through `{quantitative['D2']['postseal_exact_Take_upper_display_inverse_centimetre']} cm^-1`; both ground targets overlap: `{quantitative['D2']['all_registered_ground_targets_overlap']}`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    for species in ("H2", "D2"):
        print(f"{species} post-seal Take {quantitative[species]['postseal_exact_Take_lower_display_inverse_centimetre']} through {quantitative[species]['postseal_exact_Take_upper_display_inverse_centimetre']} cm^-1; all targets overlap {quantitative[species]['all_registered_ground_targets_overlap']}")


if __name__ == "__main__":
    main()
