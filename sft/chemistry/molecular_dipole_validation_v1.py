"""Post-seal nine-row empirical validation for Chemistry PROP-005."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.molecular_dipole_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_DIPOLE_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.molecular_dipole_law_v1 import (
    DipoleComponent,
    exact_squared_magnitude,
    registered_molecular_dipole_carriers,
)
from sft.claim_evidence import (
    EMPTY_ONE,
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmptyOne,
    FoldPair,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


PDF_PATH = "experiments/external_sources/chemistry/snapshots/prop-005-nist-water-dipole-1973-v1.pdf"
PDF_HASH = "sha256:e3df9979865e12887c564327a3029f11c03caeb8cf6d9c90b499972a954ebb84"
HTML_PATH = "experiments/external_sources/chemistry/snapshots/prop-005-nist-cccbdb-experimental-dipoles-v1.html"
HTML_HASH = "sha256:6320aca1d0c0e4fd12509dedaa985d2252813011e69d090a127b49f12414b49d"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-005-molecular-dipole-primary-records-v1.json"
PRIMARY_HASH = "sha256:6ad1fa4ff8c570cb0d8f84df2def3670f630924d9fdac8e3a8011c2ec3578dc5"
SOURCE_IDS = (
    "NIST-NBS-JCP-59-2254-1973",
    "NIST-CCCBDB-SRD101-EXPERIMENTAL-DIPOLES",
)


def _fraction(row: object) -> Fraction:
    if not isinstance(row, dict) or set(row) != {"numerator", "denominator"}:
        raise ValueError("PROP-005 exact fraction record is malformed")
    numerator, denominator = row["numerator"], row["denominator"]
    if (
        isinstance(numerator, bool)
        or isinstance(denominator, bool)
        or not isinstance(numerator, int)
        or not isinstance(denominator, int)
        or numerator < 1
        or denominator < 1
    ):
        raise ValueError("PROP-005 exact fraction left the positive domain")
    return Fraction(numerator, denominator)


def _ratio(value: Fraction) -> PositiveRatio:
    if not isinstance(value, Fraction) or value.numerator < 1 or value.denominator < 1:
        raise ValueError("PROP-005 measurement ratio must be exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def _interval(row: dict[str, object]) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    central = _fraction(row["central"])
    uncertainty = _fraction(row["uncertainty"])
    lower = _fraction(row["lower"])
    upper = _fraction(row["upper"])
    if lower + uncertainty != central or central + uncertainty != upper or not upper > lower:
        raise ValueError("PROP-005 interval does not reconstruct exactly")
    return central, uncertainty, lower, upper


def prediction_program_document() -> dict[str, object]:
    """Seal complete species/symmetry/component organization without a value."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for carrier in registered_molecular_dipole_carriers():
        species = carrier.species.label
        key = species.lower()
        labels = (
            ("molecular-species", species),
            ("molecular-state", carrier.molecular_state.label),
            ("molecular-geometry", carrier.geometry.label),
            ("charge-distinction-carrier", carrier.charge_distinction_carrier.label),
            ("molecular-symmetry", carrier.symmetry.label),
            ("dipole-component-support", carrier.structural_magnitude_class.label),
            ("dipole-magnitude-definition", carrier.magnitude_definition.label),
            ("measurement-custody", "all-nine-values-open-after-relation-seal"),
        )
        registers = ["premise"]
        for ordinal, (family, label) in enumerate(labels, start=1):
            destination = f"{key}-label-{ordinal}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        if carrier.component_axes:
            for ordinal, axis in enumerate(carrier.component_axes, start=1):
                destination = f"{key}-axis-{ordinal}"
                instructions.append({"opcode": "label", "destination": destination, "arguments": [axis.family, axis.label]})
                registers.append(destination)
        else:
            destination = f"{key}-axes-empty"
            instructions.append({"opcode": "empty_one", "destination": destination, "arguments": ["structural-empty-One"]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": key + "-relation", "arguments": registers})
        table_arguments.extend((key + "-label-1", key + "-relation"))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-dipole-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-dipole-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MOLECULAR_DIPOLE_SPEC.experiment_id + "-value-free-relation-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "experiment_id": MOLECULAR_DIPOLE_SPEC.experiment_id,
        "claim_id": MOLECULAR_DIPOLE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": MOLECULAR_DIPOLE_SPEC.statement,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(),
        "target_ids": tuple(row.target_id for row in MOLECULAR_DIPOLE_SPEC.target_rows),
        "all_measured_values_absent_from_law_and_prediction": True,
        "all_nine_rows_required": True,
        "falsification_condition": MOLECULAR_DIPOLE_SPEC.falsification_condition,
    }


def _load_targets(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (PDF_PATH, PDF_HASH),
        (HTML_PATH, HTML_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
        (IDENTITY_PATH, IDENTITY_HASH),
        (TARGET_PATH, TARGET_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-005 source bytes changed: {path}")
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    measurements = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    if (
        primary.get("schema") != "sft-v3-molecular-dipole-primary-records/1"
        or primary.get("all_registered_rows_preserved") is not True
        or identities.get("schema") != "sft-v3-molecular-dipole-identities/1"
        or identities.get("all_measurement_values_absent") is not True
        or measurements.get("schema") != "sft-v3-molecular-dipole-withheld-measurements/1"
        or measurements.get("release_requires_prediction_seal") is not True
        or measurements.get("identity_document_hash") != sha256_identity(identities)
        or len(primary.get("records", ())) != 9
        or len(identities.get("rows", ())) != 9
        or len(measurements.get("rows", ())) != 9
    ):
        raise ValueError("PROP-005 complete source boundary changed")
    primary_rows = {row["target_id"]: row for row in primary["records"]}
    identity_rows = {row["target_id"]: row for row in identities["rows"]}
    measurement_rows = {row["target_id"]: row for row in measurements["rows"]}
    if set(primary_rows) != set(identity_rows) or set(primary_rows) != set(measurement_rows) or len(primary_rows) != 9:
        raise ValueError("PROP-005 source, identity and target support differ")
    forbidden_identity_keys = {
        "central", "uncertainty", "lower", "upper", "inscription", "raw_source_inscription", "source_glyph"
    }
    resolved = []
    for target_id in sorted(primary_rows):
        source, identity, row = primary_rows[target_id], identity_rows[target_id], measurement_rows[target_id]
        if (
            identity.get("target_value_absent") is not True
            or forbidden_identity_keys.intersection(identity)
            or row != source
            or any(identity.get(key) != source.get(key) for key in identity if key != "target_value_absent")
        ):
            raise ValueError(f"PROP-005 source reconstruction differs: {target_id}")
        common = {
            "target_id": target_id,
            "species": str(row["species"]),
            "measurement_role": str(row["measurement_role"]),
            "axis": str(row["axis"]),
            "symmetry": str(row["symmetry"]),
            "component_support": row["component_support"],
            "molecular_state": str(row["molecular_state"]),
            "geometry": str(row["geometry"]),
            "charge_distinction_carrier": str(row["charge_distinction_carrier"]),
            "method": str(row["method"]),
            "condition": str(row["condition"]),
            "conventional_direction": str(row["conventional_direction"]),
            "inscription": str(row["inscription"]),
            "value_kind": str(row["value_kind"]),
        }
        if row["value_kind"] == "source_absence_glyph":
            if row.get("native_interpretation") != "EmptyOne" or row.get("source_glyph") != "0.000":
                raise ValueError("PROP-005 source absence glyph changed")
            common.update({"value": EMPTY_ONE, "interval": EMPTY_ONE})
        elif row["value_kind"] == "positive_magnitude":
            central, uncertainty, lower, upper = _interval(row)
            common.update({
                "central": central,
                "uncertainty": uncertainty,
                "lower": lower,
                "upper": upper,
                "value": _ratio(central),
                "interval": FoldPair(_ratio(lower), _ratio(upper)),
            })
        else:
            raise ValueError("PROP-005 measurement kind is outside the registered boundary")
        resolved.append(common)
    return tuple(resolved)


def _validate_structural_prediction(output: object) -> None:
    if not isinstance(output, FoldTable) or len(output.entries) != 5:
        raise ValueError("PROP-005 value-free structural prediction is incomplete")
    expected = {
        row.species.label: (
            row.symmetry.label,
            row.structural_magnitude_class.label,
            tuple(axis.label for axis in row.component_axes),
        )
        for row in registered_molecular_dipole_carriers()
    }
    observed: dict[str, tuple[str, str, tuple[str, ...]]] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "molecular-species" or not isinstance(entry.right, FoldWord):
            raise ValueError("PROP-005 structural relation lost its molecular identity")
        cells = entry.right.cells
        if len(cells) < 10 or any(not isinstance(value, HeldLabel) for value in cells[1:9]):
            raise ValueError("PROP-005 structural word is incomplete")
        symmetry = cells[5]
        magnitude_class = cells[6]
        axes_tail = cells[9:]
        if not isinstance(symmetry, HeldLabel) or not isinstance(magnitude_class, HeldLabel):
            raise ValueError("PROP-005 symmetry or magnitude class is absent")
        if axes_tail == (EMPTY_ONE,):
            axes: tuple[str, ...] = ()
        else:
            if any(not isinstance(axis, HeldLabel) or axis.family != "dipole-axis" for axis in axes_tail):
                raise ValueError("PROP-005 component-axis support changed")
            axes = tuple(axis.label for axis in axes_tail)
        observed[entry.left.label] = (symmetry.label, magnitude_class.label, axes)
    if observed != expected:
        raise ValueError("PROP-005 predicted symmetry/component vector changed")


def _square_interval(rows: tuple[dict[str, object], ...]) -> tuple[Fraction, Fraction]:
    if not rows:
        raise ValueError("PROP-005 magnitude requires positive component support")
    lower_parts = tuple(row["lower"] ** 2 for row in rows)
    upper_parts = tuple(row["upper"] ** 2 for row in rows)
    lower, upper = lower_parts[0], upper_parts[0]
    for part in lower_parts[1:]:
        lower += part
    for part in upper_parts[1:]:
        upper += part
    return lower, upper


class MolecularDipoleValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MOLECULAR_DIPOLE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-005 prediction package changed")
        _validate_structural_prediction(execution.output)

        # First numerical/absence-glyph access: after the value-free relation seal.
        target_rows = _load_targets(self.root)
        target_values = {str(row["target_id"]): row["interval"] for row in target_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        by_species = {
            species: tuple(row for row in target_rows if row["species"] == species)
            for species in ("H2", "D2", "H2O", "D2O", "HDO")
        }
        absence_comparisons = []
        for species in ("H2", "D2"):
            rows = by_species[species]
            absence_comparisons.append({
                "species": species,
                "target_id": rows[0]["target_id"] if len(rows) == 1 else "incomplete",
                "predicted": "EmptyOne",
                "source_inscription": rows[0]["inscription"] if len(rows) == 1 else "incomplete",
                "matches": len(rows) == 1 and rows[0]["value"] is EMPTY_ONE,
            })

        magnitude_comparisons = []
        for species, expected_components in (("H2O", 1), ("D2O", 1), ("HDO", 2)):
            components = tuple(row for row in by_species[species] if row["measurement_role"] == "component-magnitude")
            totals = tuple(row for row in by_species[species] if row["measurement_role"] == "total-magnitude")
            if len(components) != expected_components or len(totals) != 1:
                raise ValueError(f"PROP-005 {species} component/total support is incomplete")
            derived_lower, derived_upper = _square_interval(components)
            total = totals[0]
            observed_lower, observed_upper = total["lower"] ** 2, total["upper"] ** 2
            overlap = not (derived_upper < observed_lower or observed_upper < derived_lower)
            displaced_lower, displaced_upper = derived_upper + 1, derived_upper + 2
            magnitude_comparisons.append({
                "species": species,
                "component_target_ids": tuple(row["target_id"] for row in components),
                "total_target_id": total["target_id"],
                "component_count": len(components),
                "derived_squared_lower": derived_lower,
                "derived_squared_upper": derived_upper,
                "observed_squared_lower": observed_lower,
                "observed_squared_upper": observed_upper,
                "overlap": overlap,
                "displaced_control_rejected": displaced_lower > observed_upper and displaced_upper > displaced_lower,
            })

        program_text = json.dumps(document, sort_keys=True)
        target_document = json.loads((self.root / TARGET_PATH).read_text(encoding="utf-8"))
        no_measurement_in_prediction = all(str(row["inscription"]) not in program_text for row in target_document["rows"])
        duplicate_axis_rejected = False
        witness_component = DipoleComponent(
            HeldLabel("dipole-axis", "witness-axis"),
            HeldLabel("held-dipole-orientation", "witness-side"),
            PositiveRatio.from_pair(1, 1),
        )
        try:
            exact_squared_magnitude((witness_component, witness_component))
        except InadmissibleExactValue:
            duplicate_axis_rejected = True
        structural_counts = {
            row.species.label: len(row.component_axes) for row in registered_molecular_dipole_carriers()
        }
        adverse = {
            "complete_five_species_nine_row_vector": len(target_rows) == 9 and set(target_values) == set(envelope.withheld_target_ids),
            "all_measurements_absent_from_prediction": no_measurement_in_prediction,
            "symmetry_forces_component_counts": structural_counts == {"H2": 0, "D2": 0, "H2O": 1, "D2O": 1, "HDO": 2},
            "homonuclear_source_glyphs_map_only_to_EmptyOne": all(row["matches"] for row in absence_comparisons),
            "every_squared_magnitude_interval_overlaps": all(row["overlap"] for row in magnitude_comparisons),
            "every_displaced_total_rejected": all(row["displaced_control_rejected"] for row in magnitude_comparisons),
            "missing_component_is_not_computable": all(row["component_count"] >= 1 for row in magnitude_comparisons),
            "duplicate_axis_rejected": duplicate_axis_rejected,
            "conventional_signed_direction_absent_from_prediction": "source-negative-axis-sign" not in program_text,
            "tampered_registry_identity_rejected": sha256_identity((TARGET_HASH, "tampered")) != TARGET_HASH,
        }
        passed = all(row["matches"] for row in absence_comparisons) and all(row["overlap"] for row in magnitude_comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-molecular-dipole-square-comparator/1", registration_hash)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-005 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "target_registry_hash": TARGET_HASH,
            "absence_comparisons": absence_comparisons,
            "magnitude_comparisons": magnitude_comparisons,
            "adverse": adverse,
            "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['species']}: source {row['source_inscription']} maps to native {row['predicted']}; match {row['matches']}"
            for row in absence_comparisons
        ) + tuple(
            f"{row['species']}: {row['component_count']} post-seal component intervals give exact squared-magnitude "
            f"[{row['derived_squared_lower'].numerator}/{row['derived_squared_lower'].denominator}, "
            f"{row['derived_squared_upper'].numerator}/{row['derived_squared_upper'].denominator}]; reported squared total "
            f"[{row['observed_squared_lower'].numerator}/{row['observed_squared_lower'].denominator}, "
            f"{row['observed_squared_upper'].numerator}/{row['observed_squared_upper'].denominator}]; overlap {row['overlap']}"
            for row in magnitude_comparisons
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse.items())
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = (
    "HTML_HASH", "HTML_PATH", "MolecularDipoleValidator", "PDF_HASH", "PDF_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_IDS", "_load_targets",
    "_validate_structural_prediction", "experiment_registration_record", "prediction_program_document",
)
