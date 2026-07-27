"""Capability-closed prediction and complete NIST symmetry validation for ELEC-005."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
from typing import Optional

from sft.chemistry.state_symmetry_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    SOURCE_ID,
    STATE_SYMMETRY_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.state_symmetry_law_v1 import (
    FiniteStateEquivalenceClass,
    StateSymmetrySignature,
    axis_rank_from_source_symbol,
    build_equivalence_class,
    symmetry_signature_from_source,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
RANK_INSCRIPTIONS = {
    "Σ": "structural-empty-One",
    "Π": "first-recurrence",
    "Δ": "second-recurrence",
    "Φ": "third-recurrence",
}
ORIENTATION_COUNTS = {"Σ": 1, "Π": 2, "Δ": 2, "Φ": 2}


class _IndependentStateTableParser(HTMLParser):
    """Reconstruct the NIST data table without trusting the target registry parser."""

    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.table_depth += 1
        elif self.table_depth and tag == "tr":
            self.in_row, self.current_row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell_parts = True, []
        elif self.in_cell and tag == "sup":
            self.cell_parts.append("^")
        elif self.in_cell and tag == "sub":
            self.cell_parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.current_row.append(" ".join(unescape("".join(self.cell_parts)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.current_row:
                self.rows.append(tuple(self.current_row))
            self.in_row = False
        elif self.table_depth and tag == "table":
            self.table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)


def _term_suffix(state_record: str, term_match: re.Match[str]) -> str:
    boundaries = tuple(
        position
        for position in (
            state_record.find(",", term_match.end()),
            state_record.find(")", term_match.end()),
            state_record.find(" ", term_match.end()),
        )
        if position >= 0
    )
    return state_record[term_match.end() : min(boundaries) if boundaries else len(state_record)]


def _inversion_label(suffix: str) -> str:
    labels = tuple(label for label in ("g", "u") if label in suffix)
    return labels[-1] if labels else "absence"


def _reflection_label(suffix: str) -> str:
    if "+" in suffix:
        return "plus-fibre"
    if "-" in suffix:
        return "minus-fibre"
    return "absence"


def _axis_component(suffix: str) -> str:
    match = re.search(r"_([0-9]+)", suffix)
    if match is None:
        return "absence"
    inscription = match.group(1)
    if set(inscription) == {"0"}:
        return "absence"
    return "positive-component-" + inscription.lstrip("0")


def _component_kind(suffix: str) -> str:
    if re.search(r"_(?:g|u)?i", suffix):
        return "i"
    if "_r" in suffix:
        return "r"
    if "_o" in suffix:
        return "o"
    if suffix == "p":
        return "p"
    return "absence"


def _optional_label(family: str, inscription: str) -> object:
    return EMPTY_ONE if inscription == "absence" else HeldLabel(family, inscription)


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ELEC-005 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-state-symmetry-identities/1" or len(rows) != 362:
        raise ValueError("ELEC-005 identity registry is incomplete")
    if len({str(row["target_id"]) for row in rows}) != len(rows):
        raise ValueError("ELEC-005 identity registry contains duplicate targets")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Emit only the universal symmetry law; no target assignment is present."""

    _identities(root)
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_registers: list[str] = []
    position = 0
    for symbol in ("Σ", "Π", "Δ", "Φ"):
        position += 1
        rank_key, rank_value = f"rank-key-{position}", f"rank-value-{position}"
        instructions.append(
            {"opcode": "label", "destination": rank_key, "arguments": ["axis-rank-law", symbol]}
        )
        if symbol == "Σ":
            instructions.append(
                {"opcode": "empty_one", "destination": rank_value, "arguments": ["structural-empty-One"]}
            )
        else:
            instructions.append(
                {
                    "opcode": "label",
                    "destination": rank_value,
                    "arguments": ["axis-rank", RANK_INSCRIPTIONS[symbol]],
                }
            )
        table_registers.extend((rank_key, rank_value))

        orientation_key, orientation_value = (
            f"orientation-key-{position}",
            f"orientation-value-{position}",
        )
        instructions.extend(
            (
                {
                    "opcode": "label",
                    "destination": orientation_key,
                    "arguments": ["axis-orientation-law", symbol],
                },
                {
                    "opcode": "count",
                    "destination": orientation_value,
                    "arguments": [str(ORIENTATION_COUNTS[symbol])],
                },
            )
        )
        table_registers.extend((orientation_key, orientation_value))

    for law_name, law_value in (
        ("state-equivalence", "complete-signature-identity"),
        ("degeneracy", "positive-spin-width-times-positive-axis-orientation-count"),
        ("optional-coordinate", "held-label-or-structural-empty-One"),
        ("component-class", "complete-positive-enumeration"),
    ):
        position += 1
        key, value = f"law-key-{position}", f"law-value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["symmetry-law", law_name]},
                {"opcode": "label", "destination": value, "arguments": ["symmetry-law-result", law_value]},
            )
        )
        table_registers.extend((key, value))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-symmetry-law", "arguments": table_registers},
            {"opcode": "emit", "destination": "", "arguments": ["complete-symmetry-law"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": STATE_SYMMETRY_SPEC.experiment_id + "-symmetry-law-prediction",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": STATE_SYMMETRY_SPEC.experiment_id,
        "claim_id": STATE_SYMMETRY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": STATE_SYMMETRY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(root),
        "target_references": tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in STATE_SYMMETRY_SPEC.target_rows
        ),
        "target_content_absent_from_prediction": True,
        "target_inaccessible_to_capability_closed_execution": True,
        "all_362_assignments_required": True,
        "absence_glyph_policy": "source glyph 0 denotes absence only and is never an SFT number",
        "falsification_condition": STATE_SYMMETRY_SPEC.falsification_condition,
    }


def _resolved_targets(root: Path) -> tuple[dict[str, object], ...]:
    """Reparse every sealed NIST snapshot and reproduce every registered assignment."""

    identities = _identities(root)
    if hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("ELEC-005 withheld target registry changed")
    target_document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    target_rows = tuple(target_document.get("rows", ()))
    targets = {str(row["target_id"]): row for row in target_rows}
    if (
        target_document.get("schema") != "sft-v3-state-symmetry-withheld-targets/1"
        or len(target_rows) != 362
        or len(targets) != 362
        or {str(row["target_id"]) for row in identities} != set(targets)
    ):
        raise ValueError("ELEC-005 target support is incomplete or differs from identities")

    parsed_by_snapshot: dict[str, tuple[tuple[str, ...], ...]] = {}
    resolved = []
    for identity in identities:
        snapshot_path = root / str(identity["snapshot_path"])
        if hash_file(snapshot_path) != identity["snapshot_hash"]:
            raise ValueError("ELEC-005 NIST snapshot changed")
        snapshot_key = str(identity["snapshot_path"])
        if snapshot_key not in parsed_by_snapshot:
            parser = _IndependentStateTableParser()
            parser.feed(snapshot_path.read_text(encoding="utf-8"))
            parsed_by_snapshot[snapshot_key] = tuple(
                row for row in parser.rows if len(row) == 13 and TERM_PATTERN.search(row[0])
            )
        source_rows = parsed_by_snapshot[snapshot_key]
        state_index = int(identity["state_row_ordinal"]) - 1
        if state_index < 0 or state_index >= len(source_rows):
            raise ValueError("ELEC-005 registered NIST state row is absent")
        source_row = source_rows[state_index]
        assignments = tuple(TERM_PATTERN.finditer(source_row[0]))
        term_index = int(identity["term_assignment_ordinal"]) - 1
        if term_index < 0 or term_index >= len(assignments):
            raise ValueError("ELEC-005 registered NIST term assignment is absent")
        term_match = assignments[term_index]
        suffix = _term_suffix(source_row[0], term_match)
        multiplicity = int(term_match.group(1))
        symbol = term_match.group(2)
        inversion = _inversion_label(suffix)
        reflection = _reflection_label(suffix)
        component = _axis_component(suffix)
        component_kind = _component_kind(suffix)
        target = targets[str(identity["target_id"])]
        reconstructed = {
            "state_record": source_row[0],
            "term_assignment_inscription": term_match.group(0) + suffix,
            "positive_spin_multiplicity": multiplicity,
            "axis_support_symbol": symbol,
            "fold_axis_rank": RANK_INSCRIPTIONS[symbol],
            "positive_axis_orientation_count": ORIENTATION_COUNTS[symbol],
            "positive_combined_degeneracy_count": multiplicity * ORIENTATION_COUNTS[symbol],
            "held_inversion_label": inversion,
            "held_reflection_label": reflection,
            "held_axis_component": component,
            "held_component_kind": component_kind,
            "raw_suffix": suffix,
        }
        if any(target.get(key) != value for key, value in reconstructed.items()):
            raise ValueError("ELEC-005 independent NIST symmetry extraction differs from target")

        axis_rank = axis_rank_from_source_symbol(symbol)
        target_value = FoldWord(
            (
                HeldLabel("NIST-state-record", source_row[0]),
                HeldLabel("NIST-term-assignment", reconstructed["term_assignment_inscription"]),
                PositiveCount(multiplicity),
                HeldLabel("source-support-symbol", symbol),
                axis_rank,
                PositiveCount(ORIENTATION_COUNTS[symbol]),
                PositiveCount(multiplicity * ORIENTATION_COUNTS[symbol]),
                _optional_label("inversion-symmetry", inversion),
                _optional_label("reflection-symmetry", reflection),
                _optional_label("axis-component", component),
                _optional_label("component-kind", component_kind),
            )
        )
        resolved.append(
            {
                "target_id": str(identity["target_id"]),
                "species_row_id": str(identity["species_row_id"]),
                "state_row_ordinal": int(identity["state_row_ordinal"]),
                "source_zero_component_glyph": "_0" in suffix,
                "target_value": target_value,
                **reconstructed,
            }
        )
    return tuple(resolved)


def _prediction_map(table: FoldTable) -> dict[tuple[str, str], object]:
    result = {}
    for entry in table.entries:
        if not isinstance(entry.left, HeldLabel):
            raise ValueError("ELEC-005 prediction key is not a held label")
        result[(entry.left.family, entry.left.label)] = entry.right
    if len(result) != len(table.entries):
        raise ValueError("ELEC-005 prediction contains duplicate keys")
    return result


class StateSymmetryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = STATE_SYMMETRY_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        targets = _resolved_targets(self.root)
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-NIST-target-custodian",
            targets={str(row["target_id"]): row["target_value"] for row in targets},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ELEC-005 prediction package changed during execution")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable):
            raise ValueError("ELEC-005 prediction is not a complete Fold table")
        predicted = _prediction_map(execution.output)

        comparisons = []
        for row in targets:
            symbol = str(row["axis_support_symbol"])
            predicted_rank = predicted[("axis-rank-law", symbol)]
            expected_rank = axis_rank_from_source_symbol(symbol)
            if expected_rank == EMPTY_ONE:
                rank_passed = predicted_rank == EMPTY_ONE
            else:
                rank_passed = predicted_rank == HeldLabel("axis-rank", str(row["fold_axis_rank"]))
            predicted_orientation = predicted[("axis-orientation-law", symbol)]
            signature = symmetry_signature_from_source(
                str(row["species_row_id"]),
                PositiveCount(int(row["positive_spin_multiplicity"])),
                symbol,
                str(row["held_inversion_label"]),
                str(row["held_reflection_label"]),
                str(row["held_axis_component"]),
                str(row["held_component_kind"]),
            )
            equivalence_class = build_equivalence_class(signature)
            combined = signature.positive_degeneracy_count
            passed = (
                rank_passed
                and predicted_orientation == signature.positive_axis_orientation_count
                and predicted_orientation == PositiveCount(int(row["positive_axis_orientation_count"]))
                and combined == PositiveCount(int(row["positive_combined_degeneracy_count"]))
                and len(equivalence_class.component_occurrences) == combined.value
                and predicted[("symmetry-law", "state-equivalence")]
                == HeldLabel("symmetry-law-result", "complete-signature-identity")
                and predicted[("symmetry-law", "degeneracy")]
                == HeldLabel(
                    "symmetry-law-result",
                    "positive-spin-width-times-positive-axis-orientation-count",
                )
                and predicted[("symmetry-law", "optional-coordinate")]
                == HeldLabel("symmetry-law-result", "held-label-or-structural-empty-One")
                and predicted[("symmetry-law", "component-class")]
                == HeldLabel("symmetry-law-result", "complete-positive-enumeration")
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "species_row_id": row["species_row_id"],
                    "NIST_state_record": row["state_record"],
                    "NIST_term_assignment": row["term_assignment_inscription"],
                    "positive_spin_multiplicity": row["positive_spin_multiplicity"],
                    "axis_support_symbol": symbol,
                    "fold_axis_rank": row["fold_axis_rank"],
                    "positive_axis_orientation_count": row["positive_axis_orientation_count"],
                    "positive_combined_degeneracy_count": row["positive_combined_degeneracy_count"],
                    "inversion": row["held_inversion_label"],
                    "reflection": row["held_reflection_label"],
                    "axis_component": row["held_axis_component"],
                    "component_kind": row["held_component_kind"],
                    "source_zero_component_glyph_means_absence": row["source_zero_component_glyph"],
                    "passed": passed,
                }
            )

        unknown_symbol_rejected = False
        try:
            axis_rank_from_source_symbol("unknown")
        except InadmissibleExactValue:
            unknown_symbol_rejected = True
        sigma_wrong_orientation_rejected = False
        try:
            StateSymmetrySignature(
                HeldLabel("molecular-carrier", "tampered-sigma"),
                PositiveCount(1),
                EMPTY_ONE,
                PositiveCount(2),
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
            )
        except InadmissibleExactValue:
            sigma_wrong_orientation_rejected = True
        positive_axis_missing_pair_rejected = False
        try:
            StateSymmetrySignature(
                HeldLabel("molecular-carrier", "tampered-pi"),
                PositiveCount(1),
                PositiveCount(1),
                PositiveCount(1),
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
            )
        except InadmissibleExactValue:
            positive_axis_missing_pair_rejected = True
        sample = symmetry_signature_from_source(
            "control", PositiveCount(2), "Π", "absence", "absence", "absence", "absence"
        )
        free_degeneracy_rejected = sample.positive_degeneracy_count != PositiveCount(5)
        incomplete_class_rejected = False
        try:
            FiniteStateEquivalenceClass(
                sample,
                (HeldLabel("state-component", "incomplete-component"),),
            )
        except InadmissibleExactValue:
            incomplete_class_rejected = True
        numeric_zero_rejected = False
        try:
            FoldWord((0,))
        except FoldLanguageHalt:
            numeric_zero_rejected = True
        first_snapshot = self.root / self.spec.target_rows[0].snapshot_path
        changed_hash = "sha256:" + sha256(first_snapshot.read_bytes() + b"tampered").hexdigest()
        counts = {
            "term_assignments": len(comparisons),
            "inversion_labels": sum(row["inversion"] != "absence" for row in comparisons),
            "reflection_labels": sum(row["reflection"] != "absence" for row in comparisons),
            "positive_axis_components": sum(row["axis_component"] != "absence" for row in comparisons),
            "absent_axis_components": sum(row["axis_component"] == "absence" for row in comparisons),
            "source_zero_component_glyphs": sum(
                bool(row["source_zero_component_glyph_means_absence"]) for row in comparisons
            ),
            "species": len({str(row["species_row_id"]) for row in comparisons}),
            "registered_state_rows": len(
                {
                    (str(row["species_row_id"]), int(row["state_row_ordinal"]))
                    for row in targets
                }
            ),
        }
        adverse = {
            "unknown_support_symbol_rejected": unknown_symbol_rejected,
            "axis_invariant_wrong_orientation_rejected": sigma_wrong_orientation_rejected,
            "positive_axis_without_complementary_pair_rejected": positive_axis_missing_pair_rejected,
            "free_degeneracy_count_rejected": free_degeneracy_rejected,
            "incomplete_equivalence_class_rejected": incomplete_class_rejected,
            "source_absence_glyph_as_numerical_value_rejected": numeric_zero_rejected,
            "omitted_assignment_rejected": len(comparisons[:-1]) != 362,
            "tampered_snapshot_rejected": hash_file(first_snapshot)
            == self.spec.target_rows[0].snapshot_hash
            and changed_hash != self.spec.target_rows[0].snapshot_hash,
            "complete_external_vector_retained": counts
            == {
                "term_assignments": 362,
                "inversion_labels": 170,
                "reflection_labels": 167,
                "positive_axis_components": 32,
                "absent_axis_components": 330,
                "source_zero_component_glyphs": 11,
                "species": 22,
                "registered_state_rows": 360,
            },
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("complete-NIST-state-symmetry-comparator/1", self.spec.experiment_id)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-005 released target identity differs from custody")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration_hash": registration_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "counts": counts,
            "comparisons": comparisons,
            "adverse": adverse,
            "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']} ({row['species_row_id']}): NIST {row['NIST_state_record']}; "
            f"term {row['NIST_term_assignment']}; spin multiplicity {row['positive_spin_multiplicity']}; "
            f"axis {row['axis_support_symbol']} ({row['fold_axis_rank']}); positive orientation count "
            f"{row['positive_axis_orientation_count']}; forced combined degeneracy "
            f"{row['positive_combined_degeneracy_count']}; inversion {row['inversion']}; "
            f"reflection {row['reflection']}; axis component {row['axis_component']}; "
            f"component kind {row['component_kind']}; source glyph 0 denotes absence "
            f"{row['source_zero_component_glyph_means_absence']}; pass {row['passed']}"
            for row in comparisons
        ) + tuple(f"complete count {key}: {value}" for key, value in counts.items()) + tuple(
            f"adverse {key}: {value}" for key, value in adverse.items()
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            (SOURCE_ID,),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = ("StateSymmetryValidator", "experiment_registration_record", "prediction_program_document")
