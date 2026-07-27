"""Post-seal exact external-angle validation for Chemistry PROP-003."""

from __future__ import annotations

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import platform

from sft.chemistry.bond_angle_batch_v1 import (
    BOND_ANGLE_SPEC, IDENTITY_HASH, IDENTITY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.bond_angle_law_v1 import (
    equal_sector_turn_fraction, molecular_angle_vector,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


BF3_PATH = "experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-bf3-v1.html"
BF3_HASH = "sha256:3585dfdfe7551bce657c377a96f7800759e027325a0b5bac96c264591ba01181"
XEF2_PATH = "experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-xef2-v1.html"
XEF2_HASH = "sha256:39e69a157c1bda28a8aa1dc48e39e0e9550ecb79c396cd543bc4aaf728938df4"
XEF4_PATH = "experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-xef4-v1.html"
XEF4_HASH = "sha256:26ca18c0606aca4acb21c8e5555d1a6bc2a263c22510776e7834a22783ea3426"

SOURCE_IDS = (
    "NIST-CCCBDB-SRD101-BF3-EXPERIMENTAL-GEOMETRY",
    "NIST-CCCBDB-SRD101-XEF2-EXPERIMENTAL-GEOMETRY",
    "NIST-CCCBDB-SRD101-XEF4-EXPERIMENTAL-GEOMETRY",
)


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, ...]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.casefold()
        if lowered == "tr":
            self._row = []
        elif lowered in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            normalized = " ".join(data.split())
            if normalized:
                self._cell.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell))
            self._cell = None
        elif lowered == "tr" and self._row is not None:
            if self._row:
                self.rows.append(tuple(self._row))
            self._row = None
            self._cell = None


def _ratio(value: Fraction) -> PositiveRatio:
    if not isinstance(value, Fraction) or value.numerator < 1 or value.denominator < 1:
        raise ValueError("PROP-003 exact ratio left the positive domain")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def _source_angle_rows(root: Path) -> dict[str, Fraction]:
    specifications = (
        (BF3_PATH, BF3_HASH, "aFBF", (("NIST-CCCBDB-BF3-FBF-ADJACENT", ("2", "1", "3")),)),
        (XEF2_PATH, XEF2_HASH, "aFXeF", (("NIST-CCCBDB-XEF2-FXEF-OPPOSITE", ("2", "1", "3")),)),
        (XEF4_PATH, XEF4_HASH, "aFXeF", (
            ("NIST-CCCBDB-XEF4-FXEF-ADJACENT", ("2", "1", "3")),
            ("NIST-CCCBDB-XEF4-FXEF-OPPOSITE", ("2", "1", "4")),
        )),
    )
    resolved: dict[str, Fraction] = {}
    for path, expected_hash, coordinate, targets in specifications:
        source = root / path
        if hash_file(source) != expected_hash:
            raise ValueError(f"PROP-003 NIST snapshot changed: {path}")
        parser = _TableParser()
        parser.feed(source.read_text(encoding="utf-8", errors="replace"))
        rows = tuple(row for row in parser.rows if len(row) >= 5 and row[0] == coordinate)
        by_connectivity = {tuple(row[2:5]): row for row in rows}
        if len(by_connectivity) != len(rows):
            raise ValueError(f"PROP-003 duplicate source coordinate row: {path}")
        for target_id, connectivity in targets:
            if connectivity not in by_connectivity:
                raise ValueError(f"PROP-003 source connectivity absent: {target_id}")
            inscription = by_connectivity[connectivity][1]
            value = Fraction(inscription)
            if value.numerator < 1 or value.denominator < 1:
                raise ValueError("PROP-003 source angle is not exact and positive")
            resolved[target_id] = value
    if len(resolved) != 4:
        raise ValueError("PROP-003 source angle vector is incomplete")
    return resolved


def prediction_program_document() -> dict[str, object]:
    """Seal exact turn fractions and complete identities without degree values."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for ordinal, carrier in enumerate(molecular_angle_vector(), start=1):
        prefix = f"angle-{ordinal}"
        labels = (
            ("target-id", carrier.target_id),
            (carrier.species.family, carrier.species.label),
            (carrier.molecular_state.family, carrier.molecular_state.label),
            (carrier.geometry.family, carrier.geometry.label),
            (carrier.coordinate.family, carrier.coordinate.label),
            (carrier.angle_role.family, carrier.angle_role.label),
        )
        registers = ["premise"]
        for number, (family, label) in enumerate(labels, start=1):
            destination = f"{prefix}-label-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.extend((
            {"opcode": "count", "destination": prefix + "-sector-count", "arguments": [str(carrier.sector_count.value)]},
            {"opcode": "count", "destination": prefix + "-sector-separation", "arguments": [str(carrier.sector_separation.value)]},
            {"opcode": "ratio", "destination": prefix + "-turn-fraction", "arguments": [
                str(carrier.turn_fraction.numerator), str(carrier.turn_fraction.denominator),
            ]},
        ))
        registers.extend((prefix + "-sector-count", prefix + "-sector-separation", prefix + "-turn-fraction"))
        instructions.append({"opcode": "word", "destination": prefix + "-carrier", "arguments": registers})
        table_arguments.extend((prefix + "-label-1", prefix + "-carrier"))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-angle-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-angle-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": BOND_ANGLE_SPEC.experiment_id + "-value-free-turn-fraction-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "experiment_id": BOND_ANGLE_SPEC.experiment_id,
        "claim_id": BOND_ANGLE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": BOND_ANGLE_SPEC.statement,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(),
        "target_ids": tuple(row.target_id for row in BOND_ANGLE_SPEC.target_rows),
        "all_degree_values_absent_from_law_and_prediction": True,
        "postseal_unit_translation": "one complete turn translated to the external degree inscription only after release",
        "falsification_condition": BOND_ANGLE_SPEC.falsification_condition,
    }


def _prediction_map(table: FoldTable) -> dict[str, dict[str, object]]:
    if not isinstance(table, FoldTable) or len(table.entries) != 4:
        raise ValueError("PROP-003 prediction is not the complete four-angle table")
    result: dict[str, dict[str, object]] = {}
    for entry in table.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord):
            raise ValueError("PROP-003 prediction lost a target identity or carrier word")
        cells = entry.right.cells
        if len(cells) != 10 or any(not isinstance(value, HeldLabel) for value in cells[1:7]):
            raise ValueError("PROP-003 prediction carrier is incomplete")
        if not isinstance(cells[7], PositiveCount) or not isinstance(cells[8], PositiveCount) or not isinstance(cells[9], PositiveRatio):
            raise ValueError("PROP-003 prediction lost exact sector support")
        result[entry.left.label] = {
            "species": cells[2].label, "state": cells[3].label, "geometry": cells[4].label,
            "coordinate": cells[5].label, "role": cells[6].label,
            "sector_count": cells[7].value, "sector_separation": cells[8].value,
            "turn_fraction": cells[9].fraction,
        }
    if len(result) != 4:
        raise ValueError("PROP-003 prediction contains duplicate target identities")
    return result


def _load_targets(root: Path) -> tuple[dict[str, object], ...]:
    """Open and reconstruct all numerical target content after prediction sealing."""

    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH or hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("PROP-003 identity or target registry changed")
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    if (
        identities.get("schema") != "sft-v3-molecular-bond-angle-identities/1"
        or identities.get("all_measurement_values_absent") is not True
        or targets.get("schema") != "sft-v3-molecular-bond-angle-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("identity_document_hash") != sha256_identity(identities)
        or len(identities.get("rows", ())) != 4
        or len(targets.get("rows", ())) != 4
    ):
        raise ValueError("PROP-003 registered target boundary changed")
    identity_rows = {row["target_id"]: row for row in identities["rows"]}
    target_rows = {row["target_id"]: row for row in targets["rows"]}
    source_values = _source_angle_rows(root)
    structural = {row.target_id: row for row in molecular_angle_vector()}
    if set(identity_rows) != set(target_rows) or set(target_rows) != set(source_values) or set(source_values) != set(structural):
        raise ValueError("PROP-003 identity, source and structural supports differ")
    resolved = []
    for target_id in sorted(structural):
        identity, target, carrier = identity_rows[target_id], target_rows[target_id], structural[target_id]
        interval = target.get("observation_interval", {})
        source_value = source_values[target_id]
        if (
            identity.get("target_value_absent") is not True
            or identity.get("species") != carrier.species.label
            or identity.get("geometry") != carrier.geometry.label
            or identity.get("coordinate") != carrier.coordinate.label
            or identity.get("sector_count") != carrier.sector_count.value
            or identity.get("sector_separation") != carrier.sector_separation.value
            or target.get("species") != carrier.species.label
            or target.get("coordinate") != carrier.coordinate.label
            or target.get("source_snapshot_hash") != identity.get("snapshot_hash")
            or target.get("inscription") != str(source_value)
            or interval.get("central") != str(source_value)
            or interval.get("lower") != str(source_value)
            or interval.get("upper") != str(source_value)
            or interval.get("uncertainty_form") != "source-absent-structural-EmptyOne"
        ):
            raise ValueError(f"PROP-003 source reconstruction differs: {target_id}")
        resolved.append({
            "target_id": target_id, "species": carrier.species.label,
            "geometry": carrier.geometry.label, "coordinate": carrier.coordinate.label,
            "role": carrier.angle_role.label, "source_inscription": target["inscription"],
            "source_degrees": source_value, "source_comment": target["source_comment"],
            "target_value": _ratio(source_value),
        })
    return tuple(resolved)


class BondAngleValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = BOND_ANGLE_SPEC

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
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-003 prediction package changed")
        predicted = _prediction_map(execution.output)

        # First numerical degree access: after the exact turn-fraction prediction seal.
        target_rows = _load_targets(self.root)
        target_values = {str(row["target_id"]): row["target_value"] for row in target_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        full_turn_external_degrees = Fraction(360, 1)
        comparisons = []
        for row in target_rows:
            target_id = str(row["target_id"])
            predicted_degrees = predicted[target_id]["turn_fraction"] * full_turn_external_degrees
            observed = release.targets[target_id]
            if not isinstance(observed, PositiveRatio):
                raise ValueError("PROP-003 released target is not an exact positive ratio")
            comparisons.append({
                "target_id": target_id, "species": row["species"], "geometry": row["geometry"],
                "coordinate": row["coordinate"], "angle_role": row["role"],
                "turn_fraction": predicted[target_id]["turn_fraction"],
                "predicted_degrees": predicted_degrees, "observed_degrees": observed.fraction,
                "source_inscription": row["source_inscription"], "source_comment": row["source_comment"],
                "exact_match": predicted_degrees == observed.fraction,
                "displaced_control_rejected": predicted_degrees + 1 != observed.fraction,
            })

        document_text = json.dumps(document, sort_keys=True)
        target_document = json.loads((self.root / TARGET_PATH).read_text(encoding="utf-8"))
        no_degree_value_in_prediction = all(
            f'"{row["inscription"]}"' not in document_text for row in target_document["rows"]
        )
        tetrahedral_rejected = False
        try:
            equal_sector_turn_fraction(
                HeldLabel("molecular-geometry", "tetrahedral-continuum-angle"),
                PositiveCount(4), PositiveCount(1),
            )
        except InadmissibleExactValue:
            tetrahedral_rejected = True
        wrong_count_rejected = False
        try:
            equal_sector_turn_fraction(
                HeldLabel("molecular-geometry", "square-planar-equal-four-sector"),
                PositiveCount(3), PositiveCount(1),
            )
        except InadmissibleExactValue:
            wrong_count_rejected = True
        by_target = {row["target_id"]: row for row in comparisons}
        identities = json.loads((self.root / IDENTITY_PATH).read_text(encoding="utf-8"))
        required_identity_fields = (
            "species", "molecular_state", "geometry", "point_group", "angle_definition",
            "coordinate", "method_and_condition", "source_comment", "source_id", "snapshot_hash",
        )
        adverse = {
            "complete_four_angle_vector": len(comparisons) == 4 and set(predicted) == set(target_values),
            "all_degree_values_absent_from_prediction": no_degree_value_in_prediction,
            "all_identity_and_condition_fields_held": all(
                all(str(row.get(field, "")).strip() for field in required_identity_fields)
                for row in identities["rows"]
            ),
            "every_displaced_value_rejected": all(row["displaced_control_rejected"] for row in comparisons),
            "adjacent_opposite_swap_rejected": (
                by_target["NIST-CCCBDB-XEF4-FXEF-ADJACENT"]["predicted_degrees"]
                != by_target["NIST-CCCBDB-XEF4-FXEF-OPPOSITE"]["observed_degrees"]
                and by_target["NIST-CCCBDB-XEF4-FXEF-OPPOSITE"]["predicted_degrees"]
                != by_target["NIST-CCCBDB-XEF4-FXEF-ADJACENT"]["observed_degrees"]
            ),
            "wrong_geometry_count_rejected": wrong_count_rejected,
            "unsupported_tetrahedral_continuum_form_rejected": tetrahedral_rejected,
            "tampered_snapshot_identity_rejected": sha256_identity((BF3_HASH, "tampered")) != BF3_HASH,
        }
        passed = all(row["exact_match"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity((
                "exact-post-seal-turn-fraction-to-source-degree-comparator/1", registration_hash,
            )),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-003 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "target_registry_hash": TARGET_HASH,
            "comparisons": comparisons, "adverse": adverse, "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: exact {row['turn_fraction'].numerator}/{row['turn_fraction'].denominator} "
            f"turn -> {row['predicted_degrees']} degree; source {row['source_inscription']} degree; "
            f"exact match {row['exact_match']}"
            for row in comparisons
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            SOURCE_IDS, measurements, sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "BF3_HASH", "BF3_PATH", "BondAngleValidator", "SOURCE_IDS", "XEF2_HASH", "XEF2_PATH",
    "XEF4_HASH", "XEF4_PATH", "_load_targets", "_prediction_map",
    "experiment_registration_record", "prediction_program_document",
)
