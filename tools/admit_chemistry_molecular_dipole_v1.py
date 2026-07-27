#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-005."""

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

from sft.chemistry.molecular_dipole_batch_v1 import MOLECULAR_DIPOLE_SPEC  # noqa: E402
from sft.chemistry.molecular_dipole_validation_v1 import _load_targets, _square_interval  # noqa: E402
from sft.claim_evidence import EMPTY_ONE  # noqa: E402
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
    path = ROOT / "claims" / MOLECULAR_DIPOLE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_005", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-005 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = MOLECULAR_DIPOLE_SPEC
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({
            "claim_id": spec.claim_id,
            "execution_file": f"claims/{spec.claim_id}/execution.py",
        })
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    targets = _load_targets(ROOT)
    by_species = {
        species: tuple(row for row in targets if row["species"] == species)
        for species in ("H2", "D2", "H2O", "D2O", "HDO")
    }
    quantitative: dict[str, object] = {
        species: {
            "source_inscription": by_species[species][0]["inscription"],
            "native_magnitude": "EmptyOne",
            "source_absence_glyph_only": by_species[species][0]["value"] is EMPTY_ONE,
        }
        for species in ("H2", "D2")
    }
    for species, expected_components in (("H2O", 1), ("D2O", 1), ("HDO", 2)):
        components = tuple(row for row in by_species[species] if row["measurement_role"] == "component-magnitude")
        total = next(row for row in by_species[species] if row["measurement_role"] == "total-magnitude")
        if len(components) != expected_components:
            raise RuntimeError(f"PROP-005 {species} component support changed after admission")
        lower, upper = _square_interval(components)
        target_lower, target_upper = total["lower"] ** 2, total["upper"] ** 2
        quantitative[species] = {
            "component_target_ids": [row["target_id"] for row in components],
            "component_inscriptions_debye": [row["inscription"] for row in components],
            "total_target_id": total["target_id"],
            "total_inscription_debye": total["inscription"],
            "postseal_exact_squared_magnitude_lower_debye_squared": exact_pair(lower),
            "postseal_exact_squared_magnitude_upper_debye_squared": exact_pair(upper),
            "postseal_exact_squared_magnitude_lower_display_debye_squared": display(lower),
            "postseal_exact_squared_magnitude_upper_display_debye_squared": display(upper),
            "reported_total_squared_lower_debye_squared": exact_pair(target_lower),
            "reported_total_squared_upper_debye_squared": exact_pair(target_upper),
            "exact_interval_overlap": not (upper < target_lower or target_upper < lower),
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
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-005",
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
            "exact_magnitude_law": "molecular dipole magnitude squared = Junction of every retained positive component square",
            "quantitative_vector": quantitative,
            "complete_external_rows": len(targets),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "fitted_or_free_parameter_used": False,
            "measured_value_in_derivation_or_prediction": False,
            "all_measurement_values_released_after_relation_seal": True,
            "numerical_zero_used": False,
            "source_zero_glyph_interpreted_only_as_EmptyOne": True,
            "irrational_square_root_used": False,
            "conventional_signed_direction_is_correspondence_only": True,
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
    status_lines = [
        f"# {spec.claim_id}",
        "",
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`",
        "",
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-005`",
        f"- Closure: `{receipt.closure_status}`",
        "- Exact law: `molecular dipole magnitude squared = Junction of every retained positive component square`.",
        "- H2 and D2 source `0.000` glyphs map only to native `EmptyOne`.",
    ]
    for species in ("H2O", "D2O", "HDO"):
        row = quantitative[species]
        status_lines.append(
            f"- {species}: {len(row['component_target_ids'])} component record(s); exact squared interval "
            f"`{row['postseal_exact_squared_magnitude_lower_display_debye_squared']}` through "
            f"`{row['postseal_exact_squared_magnitude_upper_display_debye_squared']} D^2`; reported total-square overlap: "
            f"`{row['exact_interval_overlap']}`."
        )
    status_lines.extend((
        f"- Derivation seal: `{sealed.seal_hash}`",
        f"- Independent validation: `{receipt.external_validation_hash}`",
        f"- Empirical validation: `{receipt.empirical_validation_hash}`",
        f"- Engine receipt: `{receipt.receipt_hash}`",
    ))
    (package / "STATUS.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    for species in ("H2O", "D2O", "HDO"):
        print(f"{species} squared-magnitude overlap {quantitative[species]['exact_interval_overlap']}")


if __name__ == "__main__":
    main()
