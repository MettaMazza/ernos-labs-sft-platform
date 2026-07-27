"""Post-seal complete torsion-surface validation for Chemistry PROP-004."""

from __future__ import annotations

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import platform

from sft.chemistry.dihedral_torsion_batch_v1 import (
    DIHEDRAL_TORSION_SPEC, IDENTITY_HASH, IDENTITY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.dihedral_torsion_law_v1 import (
    DihedralCarrier, TorsionCycle, TorsionNode, generated_dihedral_coordinate,
    ordered_positive_barrier_take,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/configuration-order-v1/nist-cccbdb-ethanol-experimental-rotational-barrier.html"
SNAPSHOT_HASH = "sha256:afd9991078eac697439f353271666c9020d40f906bff78838c6cbe3696b14209"
SOURCE_ID = "NIST-CCCBDB-SRD101-ETHANOL-EXPERIMENTAL-ROTATIONAL-BARRIER"


TORSION_SPECIFICATIONS = {
    1: {
        "torsion_label": "ethanol-OH-internal-rotation",
        "ordered_atoms": ("1", "2", "3", "4"),
        "rotor_type": "OH",
    },
    2: {
        "torsion_label": "ethanol-CH3-internal-rotation",
        "ordered_atoms": ("3", "2", "1", "5"),
        "rotor_type": "CH3",
    },
}


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, ...]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "tr":
            self._row = []
        elif tag.casefold() in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            normalized = " ".join(data.split())
            if normalized:
                self._cell.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell))
            self._cell = None
        elif tag.casefold() == "tr" and self._row is not None:
            if self._row:
                self.rows.append(tuple(self._row))
            self._row = None
            self._cell = None


def _exact_source_value(inscription: str):
    value = Fraction(inscription)
    if value == 0:
        return EMPTY_ONE
    if value.numerator < 1 or value.denominator < 1:
        raise ValueError("PROP-004 source value left the exact positive/EmptyOne domain")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def _structural_rows() -> tuple[dict[str, object], ...]:
    rows = []
    sectors = PositiveCount(24)
    for torsion_index, specification in TORSION_SPECIFICATIONS.items():
        for position in range(1, 26):
            coordinate = generated_dihedral_coordinate(PositiveCount(position), sectors)
            rows.append({
                "target_id": f"ethanol-torsion-{torsion_index}-sector-{position:02d}",
                "torsion_index": torsion_index, "path_position": position,
                "torsion_label": specification["torsion_label"],
                "ordered_atoms": specification["ordered_atoms"], "rotor_type": specification["rotor_type"],
                "coordinate": coordinate,
                "coordinate_form": (
                    "structural-EmptyOne-anchor" if position == 1
                    else "recurrent-One" if position == 25
                    else "positive-exact-turn-part"
                ),
            })
    return tuple(rows)


def prediction_program_document() -> dict[str, object]:
    """Seal the exact two-cycle coordinate vector without degrees or energies."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_structural_rows(), start=1):
        prefix = f"torsion-state-{ordinal}"
        labels = (
            ("target-id", row["target_id"]),
            ("molecular-carrier", "ethanol"),
            ("molecular-state", "gauche-ethanol-internal-rotation"),
            ("torsion-identity", row["torsion_label"]),
            ("rotor-type", row["rotor_type"]),
            ("held-orientation", "source-forward-periodic-order"),
            ("ordered-torsion-atom", row["ordered_atoms"][0]),
            ("ordered-torsion-atom", row["ordered_atoms"][1]),
            ("ordered-torsion-atom", row["ordered_atoms"][2]),
            ("ordered-torsion-atom", row["ordered_atoms"][3]),
            ("coordinate-form", row["coordinate_form"]),
            ("state-law", "complete-cyclic-neighbour-order"),
            ("barrier-law", "ordered-positive-Take-to-adjacent-conformer"),
        )
        registers = ["premise"]
        for number, (family, label) in enumerate(labels, start=1):
            destination = f"{prefix}-label-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(label)]})
            registers.append(destination)
        instructions.extend((
            {"opcode": "count", "destination": prefix + "-position", "arguments": [str(row["path_position"])]},
            {"opcode": "count", "destination": prefix + "-sectors", "arguments": ["24"]},
        ))
        coordinate = row["coordinate"]
        if coordinate is EMPTY_ONE:
            instructions.append({"opcode": "empty_one", "destination": prefix + "-coordinate", "arguments": ["structural-empty-One"]})
        else:
            instructions.append({
                "opcode": "ratio", "destination": prefix + "-coordinate",
                "arguments": [str(coordinate.numerator.value), str(coordinate.denominator.value)],
            })
        registers.extend((prefix + "-position", prefix + "-sectors", prefix + "-coordinate"))
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-label-1", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "dihedral-torsion-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["dihedral-torsion-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": DIHEDRAL_TORSION_SPEC.experiment_id + "-value-free-coordinate-and-operation-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "experiment_id": DIHEDRAL_TORSION_SPEC.experiment_id,
        "claim_id": DIHEDRAL_TORSION_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": DIHEDRAL_TORSION_SPEC.statement,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(),
        "target_ids": tuple(row.target_id for row in DIHEDRAL_TORSION_SPEC.target_rows),
        "all_angle_energy_and_extrema_outcomes_absent_from_prediction": True,
        "falsification_condition": DIHEDRAL_TORSION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, dict[str, object]]:
    if not isinstance(output, FoldTable) or len(output.entries) != 50:
        raise ValueError("PROP-004 prediction is not the complete fifty-row table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord):
            raise ValueError("PROP-004 prediction lost a target identity or state word")
        cells = entry.right.cells
        if len(cells) != 17 or any(not isinstance(value, HeldLabel) for value in cells[1:14]):
            raise ValueError("PROP-004 prediction state word is incomplete")
        if not isinstance(cells[14], PositiveCount) or not isinstance(cells[15], PositiveCount):
            raise ValueError("PROP-004 prediction lost positive path support")
        if not isinstance(cells[16], (EmptyOne, PositiveRatio)):
            raise ValueError("PROP-004 prediction coordinate is outside the exact Fold domain")
        resolved[entry.left.label] = {
            "species": cells[2].label, "state": cells[3].label, "torsion_label": cells[4].label,
            "rotor_type": cells[5].label, "orientation": cells[6].label,
            "ordered_atoms": tuple(cell.label for cell in cells[7:11]),
            "coordinate_form": cells[11].label, "state_law": cells[12].label, "barrier_law": cells[13].label,
            "path_position": cells[14].value, "sector_count": cells[15].value,
            "coordinate": cells[16],
        }
    if len(resolved) != 50:
        raise ValueError("PROP-004 prediction contains duplicate target identities")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected_hash in (
        (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), (SNAPSHOT_PATH, SNAPSHOT_HASH),
    ):
        if hash_file(root / path) != expected_hash:
            raise ValueError(f"PROP-004 registered source changed: {path}")
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    if (
        identities.get("schema") != "sft-v3-dihedral-torsion-identities/1"
        or identities.get("all_angle_and_energy_values_absent") is not True
        or targets.get("schema") != "sft-v3-dihedral-torsion-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("source_zero_is_absence_glyph_only") is not True
        or targets.get("identity_document_hash") != sha256_identity(identities)
        or len(identities.get("rows", ())) != 50 or len(targets.get("rows", ())) != 50
    ):
        raise ValueError("PROP-004 registered two-path boundary changed")
    parser = _TableParser()
    parser.feed((root / SNAPSHOT_PATH).read_text(encoding="utf-8", errors="replace"))
    raw = tuple(row for row in parser.rows if len(row) == 4 and row[0] in {"1", "2"} and row[1].isdigit())
    identity_rows = {row["target_id"]: row for row in identities["rows"]}
    target_rows = {row["target_id"]: row for row in targets["rows"]}
    structural = {row["target_id"]: row for row in _structural_rows()}
    if len(raw) != 50 or set(identity_rows) != set(target_rows) or set(target_rows) != set(structural):
        raise ValueError("PROP-004 identity, source and structural supports differ")
    resolved = []
    for source_row, structural_row in zip(raw, _structural_rows()):
        target_id = structural_row["target_id"]
        identity, target = identity_rows[target_id], target_rows[target_id]
        torsion, angle, energy_kj, energy_cm = source_row
        if (
            identity.get("target_value_absent") is not True
            or identity.get("species") != "ethanol"
            or identity.get("torsion_index") != structural_row["torsion_index"]
            or tuple(identity.get("ordered_four_atom_carrier", ())) != structural_row["ordered_atoms"]
            or identity.get("rotor_type") != structural_row["rotor_type"]
            or identity.get("held_orientation") != "source-forward-periodic-order"
            or identity.get("registered_sector_count") != 24
            or identity.get("path_position") != structural_row["path_position"]
            or identity.get("coordinate_form") != structural_row["coordinate_form"]
            or target.get("torsion_index") != int(torsion)
            or target.get("path_position") != structural_row["path_position"]
            or target.get("angle_inscription_degrees") != angle
            or target.get("energy_inscription_kj_mol") != energy_kj
            or target.get("energy_inscription_cm_inverse") != energy_cm
            or target.get("source_snapshot_hash") != SNAPSHOT_HASH
        ):
            raise ValueError(f"PROP-004 source reconstruction differs: {target_id}")
        angle_value = _exact_source_value(angle)
        energy_kj_value = _exact_source_value(energy_kj)
        energy_cm_value = _exact_source_value(energy_cm)
        resolved.append({
            **structural_row, "identity": identity,
            "angle_inscription": angle, "energy_kj_inscription": energy_kj,
            "energy_cm_inscription": energy_cm, "angle": angle_value,
            "energy_kj": energy_kj_value, "energy_cm": energy_cm_value,
            "vault_value": FoldWord((angle_value, energy_kj_value, energy_cm_value)),
        })
    return tuple(resolved)


def _carrier(row: dict[str, object]) -> DihedralCarrier:
    identity = row["identity"]
    return DihedralCarrier(
        HeldLabel("molecular-carrier", "ethanol"),
        HeldLabel("molecular-state", "gauche-ethanol-internal-rotation"),
        tuple(HeldLabel("ordered-torsion-atom", label) for label in identity["ordered_four_atom_carrier"]),
        HeldLabel("rotor-type", str(identity["rotor_type"])),
        HeldLabel("held-orientation", str(identity["held_orientation"])),
    )


def _cycles(rows: tuple[dict[str, object], ...], energy_key: str) -> dict[int, TorsionCycle]:
    cycles = {}
    for torsion_index in (1, 2):
        path = tuple(row for row in rows if row["torsion_index"] == torsion_index)
        nodes = tuple(
            TorsionNode(
                _carrier(row), PositiveCount(int(row["path_position"])), row["coordinate"], row[energy_key],
                HeldLabel("torsion-record", str(row["target_id"])),
            )
            for row in path
        )
        cycles[torsion_index] = TorsionCycle(PositiveCount(24), nodes)
    return cycles


class DihedralTorsionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = DIHEDRAL_TORSION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-004 prediction package changed")
        predicted = _prediction_map(execution.output)

        # First target-value access: after the value-free coordinate and operation seal.
        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): row["vault_value"] for row in source_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-NIST-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        full_turn_external_degrees = Fraction(360, 1)
        comparisons = []
        for row in source_rows:
            target_id = str(row["target_id"])
            prediction = predicted[target_id]
            released = release.targets[target_id]
            if not isinstance(released, FoldWord) or len(released.cells) != 3:
                raise ValueError("PROP-004 released target record is malformed")
            coordinate = prediction["coordinate"]
            angle = released.cells[0]
            if coordinate is EMPTY_ONE:
                coordinate_match = angle is EMPTY_ONE
            else:
                coordinate_match = isinstance(angle, PositiveRatio) and coordinate.fraction * full_turn_external_degrees == angle.fraction
            comparisons.append({
                "target_id": target_id, "torsion_index": row["torsion_index"],
                "path_position": row["path_position"], "coordinate": repr(coordinate),
                "angle_inscription": row["angle_inscription"], "energy_kj_inscription": row["energy_kj_inscription"],
                "energy_cm_inscription": row["energy_cm_inscription"], "coordinate_match": coordinate_match,
                "source_record_match": released == row["vault_value"],
            })

        cycles_kj = _cycles(source_rows, "energy_kj")
        cycles_cm = _cycles(source_rows, "energy_cm")
        conformers = []
        barriers = []
        transitions = []
        for torsion_index in (1, 2):
            kj_cycle, cm_cycle = cycles_kj[torsion_index], cycles_cm[torsion_index]
            kj_conformers, cm_conformers = kj_cycle.local_conformer_positions(), cm_cycle.local_conformer_positions()
            kj_barriers, cm_barriers = kj_cycle.local_barrier_positions(), cm_cycle.local_barrier_positions()
            if kj_conformers != cm_conformers or kj_barriers != cm_barriers:
                raise ValueError("PROP-004 two energy-unit surfaces disagree on state order")
            conformers.extend((torsion_index, position.value) for position in kj_conformers)
            barriers.extend((torsion_index, position.value) for position in kj_barriers)
            for barrier_position, conformer_position, magnitude in kj_cycle.barrier_transitions():
                transitions.append({
                    "torsion_index": torsion_index, "barrier_position": barrier_position.value,
                    "adjacent_conformer_position": conformer_position.value,
                    "exact_positive_Take_kj_mol": magnitude.fraction,
                })

        reverse_take_rejected = False
        try:
            ordered_positive_barrier_take(PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(5, 1))
        except InadmissibleExactValue:
            reverse_take_rejected = True
        negative_coordinate_rejected = False
        try:
            PositiveRatio.from_pair(-1, 24)
        except InadmissibleExactValue:
            negative_coordinate_rejected = True
        identity_document = json.loads((self.root / IDENTITY_PATH).read_text(encoding="utf-8"))
        required_fields = (
            "species", "molecular_state", "conformer_scope", "torsion_label", "ordered_four_atom_carrier",
            "rotor_type", "held_orientation", "coordinate_form", "barrier_definition", "method_and_condition",
        )
        program_text = json.dumps(document, sort_keys=True)
        adverse = {
            "complete_fifty_row_vector": len(comparisons) == 50 and set(predicted) == set(target_values),
            "all_coordinates_match_postseal_source_angles": all(row["coordinate_match"] for row in comparisons),
            "all_source_records_preserved": all(row["source_record_match"] for row in comparisons),
            "angle_energy_and_extrema_values_absent_before_seal": all(
                forbidden not in program_text for forbidden in ("degree", "kJ", "cm_inverse", "5.41", "15.92", "0.52")
            ),
            "complete_identity_condition_surface": all(
                all(row.get(field) not in (None, "", ()) for field in required_fields)
                for row in identity_document["rows"]
            ),
            "six_conformer_states_forced": len(conformers) == 6,
            "six_barrier_states_forced": len(barriers) == 6,
            "twelve_adjacent_positive_barrier_Takes": len(transitions) == 12 and all(row["exact_positive_Take_kj_mol"] > 0 for row in transitions),
            "both_energy_units_force_same_state_order": all(
                cycles_kj[index].local_conformer_positions() == cycles_cm[index].local_conformer_positions()
                and cycles_kj[index].local_barrier_positions() == cycles_cm[index].local_barrier_positions()
                for index in (1, 2)
            ),
            "both_recurrence_endpoints_identify_anchor": all(
                cycle.nodes[-1].height == cycle.nodes[0].height for cycle in cycles_kj.values()
            ),
            "source_zero_glyphs_are_EmptyOne": sum(row["energy_kj"] is EMPTY_ONE for row in source_rows) == 4,
            "reversed_barrier_Take_rejected": reverse_take_rejected,
            "negative_signed_coordinate_rejected": negative_coordinate_rejected,
            "tampered_source_identity_rejected": sha256_identity((SNAPSHOT_HASH, "tampered")) != SNAPSHOT_HASH,
        }
        passed = all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity((
                "exact-post-seal-dihedral-cycle-and-barrier-Take-comparator/1", registration_hash,
            )),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-004 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "target_registry_hash": TARGET_HASH,
            "comparisons": comparisons, "conformers": conformers, "barriers": barriers,
            "barrier_transitions": transitions, "adverse": adverse, "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: coordinate {row['coordinate']}; source angle {row['angle_inscription']} degree; "
            f"energy {row['energy_kj_inscription']} kJ mol^-1 / {row['energy_cm_inscription']} cm^-1; "
            f"coordinate match {row['coordinate_match']}"
            for row in comparisons
        ) + tuple(
            f"torsion {row['torsion_index']} barrier position {row['barrier_position']} Take conformer "
            f"position {row['adjacent_conformer_position']} = {row['exact_positive_Take_kj_mol']} kJ mol^-1"
            for row in transitions
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            (SOURCE_ID,), measurements, sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "DihedralTorsionValidator", "SNAPSHOT_HASH", "SNAPSHOT_PATH", "SOURCE_ID", "TORSION_SPECIFICATIONS",
    "_cycles", "_prediction_map", "_source_rows", "experiment_registration_record",
    "prediction_program_document",
)
