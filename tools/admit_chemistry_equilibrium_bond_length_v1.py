#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-001."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, localcontext
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.equilibrium_bond_length_batch_v1 import (  # noqa: E402
    EQUILIBRIUM_BOND_LENGTH_SPEC,
)
from sft.chemistry.equilibrium_bond_length_law_v1 import (  # noqa: E402
    D2_MULTIPLIER,
    H2_MULTIPLIER,
)
from sft.chemistry.equilibrium_bond_length_validation_v1 import (  # noqa: E402
    _load_scale,
    _load_targets,
)
from sft.engine import EngineRepository  # noqa: E402
from sft.physics.molecular_spectroscopy_successor_laws_v1 import exact_alpha  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exact_pair(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def display(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 24
        return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def load_execution():
    path = ROOT / "claims" / EQUILIBRIUM_BOND_LENGTH_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_001", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-001 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = EQUILIBRIUM_BOND_LENGTH_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {
        row["claim_id"]
        for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]
    }
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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}
        )
        write_json(manifest_path, manifest)

    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    scale_central, scale_lower, scale_upper = _load_scale(ROOT)
    target_rows = {row["species"]: row for row in _load_targets(ROOT)}
    predictions = {
        "H2": (H2_MULTIPLIER * scale_lower, H2_MULTIPLIER * scale_central, H2_MULTIPLIER * scale_upper),
        "D2": (D2_MULTIPLIER * scale_lower, D2_MULTIPLIER * scale_central, D2_MULTIPLIER * scale_upper),
    }
    quantitative = {
        species: {
            "exact_multiplier": exact_pair(H2_MULTIPLIER if species == "H2" else D2_MULTIPLIER),
            "predicted_lower_angstrom": exact_pair(values[0]),
            "predicted_central_angstrom": exact_pair(values[1]),
            "predicted_upper_angstrom": exact_pair(values[2]),
            "predicted_central_display_angstrom": display(values[1]),
            "NIST_inscription_angstrom": target_rows[species]["inscription"],
            "NIST_lower_angstrom": exact_pair(target_rows[species]["lower"]),
            "NIST_upper_angstrom": exact_pair(target_rows[species]["upper"]),
            "contained": not (
                values[2] < target_rows[species]["lower"]
                or target_rows[species]["upper"] < values[0]
            ),
        }
        for species, values in predictions.items()
    }
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-001",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
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
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "exact_alpha": exact_pair(exact_alpha()),
            "atomic_length_central_angstrom": exact_pair(scale_central),
            "relations": {
                "H2": "r_e(H2)/a0 = 7/5 + 21 alpha^2",
                "D2": "r_e(D2)/a0 = 7/5 + 24 alpha^2",
            },
            "quantitative_vector": quantitative,
            "complete_external_rows": 2,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "fitted_or_free_parameter_used": False,
            "target_value_in_executable_law": False,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-001`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact relations: `r_e(H2)/a0 = 7/5 + 21 alpha^2`; `r_e(D2)/a0 = 7/5 + 24 alpha^2`.\n"
        f"- H2 predicted: `{quantitative['H2']['predicted_central_display_angstrom']} angstrom`; NIST: `{quantitative['H2']['NIST_inscription_angstrom']} angstrom`; contained: `{quantitative['H2']['contained']}`.\n"
        f"- D2 predicted: `{quantitative['D2']['predicted_central_display_angstrom']} angstrom`; NIST: `{quantitative['D2']['NIST_inscription_angstrom']} angstrom`; contained: `{quantitative['D2']['contained']}`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"H2 predicted {quantitative['H2']['predicted_central_display_angstrom']} A; NIST {quantitative['H2']['NIST_inscription_angstrom']}; contained {quantitative['H2']['contained']}")
    print(f"D2 predicted {quantitative['D2']['predicted_central_display_angstrom']} A; NIST {quantitative['D2']['NIST_inscription_angstrom']}; contained {quantitative['D2']['contained']}")


if __name__ == "__main__":
    main()
