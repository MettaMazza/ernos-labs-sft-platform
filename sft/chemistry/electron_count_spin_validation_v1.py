"""Capability-closed prediction and post-seal NIST validation for ELEC-002."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from hashlib import sha256
import json
from pathlib import Path
import platform
import re

from sft.chemistry.electron_count_spin_batch_v1 import (
    ELECTRON_COUNT_SPIN_SPEC,
    INPUT_REGISTRY_HASH,
    INPUT_REGISTRY_PATH,
    SOURCE_ID,
    TARGET_REGISTRY_HASH,
    TARGET_REGISTRY_PATH,
)
from sft.chemistry.electron_count_spin_law_v1 import (
    HeldChargeTransfer,
    NuclearPopulation,
    build_complete_spin_organization,
    exact_electron_count,
    required_spin_width_parity,
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
from sft.claim_evidence.fold_language import EMPTY_ONE
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


class _IndependentNistStateParser(HTMLParser):
    """Second implementation: retain text cells only inside NIST data tables."""

    def __init__(self) -> None:
        super().__init__()
        self.in_data_table = False
        self.in_row = False
        self.in_cell = False
        self.cell_text: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.in_data_table = True
        elif self.in_data_table and tag == "tr":
            self.in_row = True
            self.current_row = []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell = True
            self.cell_text = []
        elif self.in_cell and tag == "sup":
            self.cell_text.append("^")
        elif self.in_cell and tag == "sub":
            self.cell_text.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.current_row.append(" ".join(unescape("".join(self.cell_text)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.current_row:
                self.rows.append(tuple(self.current_row))
            self.in_row = False
        elif self.in_data_table and tag == "table":
            self.in_data_table = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_text.append(data)


def _load_inputs(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / INPUT_REGISTRY_PATH) != INPUT_REGISTRY_HASH:
        raise ValueError("ELEC-002 prediction input registry changed")
    document = json.loads((root / INPUT_REGISTRY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-electron-spin-inputs/1" or len(rows) != 22:
        raise ValueError("ELEC-002 prediction input registry is incomplete")
    if len({str(row["row_id"]) for row in rows}) != len(rows):
        raise ValueError("ELEC-002 prediction rows are duplicated")
    return rows


def _transfer_from_row(row: dict[str, object]) -> HeldChargeTransfer:
    action = str(row["charge_action"])
    count = row.get("charge_count")
    if action == "empty-One":
        return HeldChargeTransfer(HeldLabel("electron-transfer", action), EMPTY_ONE)
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("directed electron transfer requires a positive registered count")
    return HeldChargeTransfer(HeldLabel("electron-transfer", action), PositiveCount(count))


def _count_from_row(row: dict[str, object]) -> PositiveCount:
    populations = tuple(
        NuclearPopulation(
            HeldLabel("element-symbol", str(item["element_symbol"])),
            PositiveCount(int(item["atomic_number"])),
            PositiveCount(int(item["occurrence_count"])),
        )
        for item in row["nuclear_composition"]
    )
    return exact_electron_count(populations, _transfer_from_row(row))


def prediction_rows(root: Path) -> tuple[dict[str, object], ...]:
    """Generate all quantitative predictions without opening target content."""

    return tuple(
        {
            "row_id": str(row["row_id"]),
            "electron_count": _count_from_row(row).value,
            "required_spin_width_parity": required_spin_width_parity(_count_from_row(row)).label,
        }
        for row in _load_inputs(root)
    )


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for position, row in enumerate(prediction_rows(root), start=1):
        key = f"key-{position}"
        count = f"count-{position}"
        parity = f"parity-{position}"
        value = f"value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["molecular-row", str(row["row_id"])]},
                {"opcode": "count", "destination": count, "arguments": [str(row["electron_count"])]},
                {"opcode": "label", "destination": parity, "arguments": ["spin-width-parity", str(row["required_spin_width_parity"])]},
                {"opcode": "word", "destination": value, "arguments": [count, parity]},
            )
        )
        table_arguments.extend((key, value))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-prediction-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-prediction-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ELECTRON_COUNT_SPIN_SPEC.experiment_id + "-complete-vector-prediction",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": ELECTRON_COUNT_SPIN_SPEC.experiment_id,
        "claim_id": ELECTRON_COUNT_SPIN_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": ELECTRON_COUNT_SPIN_SPEC.exact_result,
        "input_registry_path": INPUT_REGISTRY_PATH,
        "input_registry_hash": INPUT_REGISTRY_HASH,
        "withheld_target_registry_path": TARGET_REGISTRY_PATH,
        "withheld_target_registry_hash": TARGET_REGISTRY_HASH,
        "prediction_program": prediction_program_document(root),
        "target_references": tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in ELECTRON_COUNT_SPIN_SPEC.target_rows
        ),
        "target_content_absent_from_prediction_program": True,
        "target_inaccessible_to_capability_closed_execution": True,
        "all_neutral_cation_anion_rows_required": True,
        "falsification_condition": ELECTRON_COUNT_SPIN_SPEC.falsification_condition,
    }


def _formula_composition(formula: str) -> tuple[dict[str, int], str]:
    if formula.endswith("+"):
        body, charge = formula[:-1], "remove-electron"
    elif formula.endswith("-"):
        body, charge = formula[:-1], "adjoin-electron"
    else:
        body, charge = formula, "empty-One"
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", body)
    if not parts or "".join(symbol + digits for symbol, digits in parts) != body:
        raise ValueError("NIST molecular formula is outside the declared finite grammar")
    composition = {symbol: int(digits) if digits else 1 for symbol, digits in parts}
    return composition, charge


def _source_targets(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / TARGET_REGISTRY_PATH) != TARGET_REGISTRY_HASH:
        raise ValueError("withheld NIST state target registry changed")
    target_document = json.loads((root / TARGET_REGISTRY_PATH).read_text(encoding="utf-8"))
    targets = {str(row["row_id"]): row for row in target_document.get("rows", ())}
    inputs = {str(row["row_id"]): row for row in _load_inputs(root)}
    if target_document.get("schema") != "sft-v3-electron-spin-withheld-targets/1" or set(targets) != set(inputs):
        raise ValueError("withheld NIST state target support differs from prediction support")
    resolved = []
    for reference in ELECTRON_COUNT_SPIN_SPEC.target_rows:
        target = targets[reference.target_id]
        source_path = root / reference.snapshot_path
        if hash_file(source_path) != reference.snapshot_hash or target["snapshot_hash"] != reference.snapshot_hash:
            raise ValueError("NIST source byte identity differs from registered target")
        parser = _IndependentNistStateParser()
        parser.feed(source_path.read_text(encoding="utf-8"))
        x_rows = tuple(row for row in parser.rows if row and re.match(r"^X(?:\s|\^)", row[0]))
        if not x_rows:
            raise ValueError("registered NIST source lacks an X-state row")
        state_term = x_rows[0][0]
        match = re.search(r"\^(\d+)", state_term)
        if match is None:
            raise ValueError("NIST X-state multiplicity is absent")
        multiplicity = int(match.group(1))
        if state_term != target["ground_state_term"] or multiplicity != target["measured_multiplicity"]:
            raise ValueError("independent NIST state extraction differs from target registry")
        formula_composition, formula_charge = _formula_composition(str(inputs[reference.target_id]["molecular_formula"]))
        registered_composition = {
            str(row["element_symbol"]): int(row["occurrence_count"])
            for row in inputs[reference.target_id]["nuclear_composition"]
        }
        if formula_composition != registered_composition or formula_charge != inputs[reference.target_id]["charge_action"]:
            raise ValueError("registered Fold input does not reproduce the NIST formula and held charge")
        resolved.append(
            {
                "row_id": reference.target_id,
                "state_term": state_term,
                "multiplicity": multiplicity,
                "snapshot_hash": reference.snapshot_hash,
                "target_value": FoldWord(
                    (
                        HeldLabel("measured-ground-state-term", state_term),
                        PositiveCount(multiplicity),
                    )
                ),
            }
        )
    return tuple(resolved)


class ElectronCountSpinValidator:
    """Validate the complete sealed 22-row vector after NIST target release."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ELECTRON_COUNT_SPIN_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.root)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        source_targets = _source_targets(self.root)
        target_values = {str(row["row_id"]): row["target_value"] for row in source_targets}
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
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_REGISTRY_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("ELEC-002 prediction package changed during sealed execution")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        if not isinstance(execution.output, FoldTable) or len(execution.output.entries) != 22:
            raise ValueError("ELEC-002 did not emit the complete prediction table")
        predicted = {}
        for entry in execution.output.entries:
            if not isinstance(entry.left, HeldLabel) or entry.left.family != "molecular-row":
                raise ValueError("ELEC-002 prediction key is invalid")
            if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 2:
                raise ValueError("ELEC-002 prediction value is invalid")
            count, parity = entry.right.cells
            if not isinstance(count, PositiveCount) or not isinstance(parity, HeldLabel) or parity.family != "spin-width-parity":
                raise ValueError("ELEC-002 prediction value left the exact Fold domain")
            predicted[entry.left.label] = (count, parity)
        if len(predicted) != 22:
            raise ValueError("ELEC-002 prediction table contains duplicate rows")

        input_by_id = {str(row["row_id"]): row for row in _load_inputs(self.root)}
        target_by_id = {str(row["row_id"]): row for row in source_targets}
        comparisons = []
        for reference in self.spec.target_rows:
            row_id = reference.target_id
            count, predicted_parity = predicted[row_id]
            exact_count = _count_from_row(input_by_id[row_id])
            released = release.targets[row_id]
            if not isinstance(released, FoldWord) or len(released.cells) != 2:
                raise ValueError("released NIST target is invalid")
            state_term, measured_width = released.cells
            if not isinstance(state_term, HeldLabel) or not isinstance(measured_width, PositiveCount):
                raise ValueError("released NIST state term or width is invalid")
            measured_parity = HeldLabel(
                "spin-width-parity",
                "odd-positive-width" if measured_width.value % 2 else "even-positive-width",
            )
            organization = build_complete_spin_organization(row_id, count, measured_width)
            passed = (
                count == exact_count
                and predicted_parity == measured_parity
                and organization.electron_count == count
                and target_by_id[row_id]["state_term"] == state_term.label
            )
            comparisons.append(
                {
                    "row_id": row_id,
                    "formula": input_by_id[row_id]["molecular_formula"],
                    "charge_action": input_by_id[row_id]["charge_action"],
                    "predicted_electron_count": count.value,
                    "predicted_width_parity": predicted_parity.label,
                    "measured_NIST_X_state": state_term.label,
                    "measured_multiplicity": measured_width.value,
                    "complementary_pair_count": organization.complementary_pair_count.value if isinstance(organization.complementary_pair_count, PositiveCount) else "empty-One",
                    "unmatched_fibre_count": organization.unmatched_fibre_count.value if isinstance(organization.unmatched_fibre_count, PositiveCount) else "empty-One",
                    "passed": passed,
                }
            )

        first = input_by_id[self.spec.target_rows[0].target_id]
        original_count = _count_from_row(first)
        tampered_transfer = HeldChargeTransfer(HeldLabel("electron-transfer", "remove-electron"), PositiveCount(1))
        tampered_count = exact_electron_count(
            tuple(
                NuclearPopulation(
                    HeldLabel("element-symbol", str(item["element_symbol"])),
                    PositiveCount(int(item["atomic_number"])),
                    PositiveCount(int(item["occurrence_count"])),
                )
                for item in first["nuclear_composition"]
            ),
            tampered_transfer,
        )
        incompatible_width_rejected = False
        try:
            build_complete_spin_organization("tampered-width", PositiveCount(14), PositiveCount(2))
        except InadmissibleExactValue:
            incompatible_width_rejected = True
        first_snapshot = self.root / self.spec.target_rows[0].snapshot_path
        tampered_snapshot_identity = "sha256:" + sha256(first_snapshot.read_bytes() + b"deliberate-tamper").hexdigest()
        adverse_controls = {
            "tampered_charge_rejected": tampered_count != original_count,
            "tampered_multiplicity_parity_rejected": incompatible_width_rejected,
            "omitted_row_rejected": len(comparisons[:-1]) != len(self.spec.target_rows),
            "tampered_snapshot_hash_rejected": (
                hash_file(first_snapshot) == self.spec.target_rows[0].snapshot_hash
                and tampered_snapshot_identity != self.spec.target_rows[0].snapshot_hash
            ),
            "all_registered_rows_retained": len(comparisons) == len(self.spec.target_rows) == 22,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(adverse_controls.values())

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-electron-count-spin-parity-NIST-state-comparison/1", self.spec.experiment_id))
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=interpreter_hash,
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=comparator_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released NIST target vector differs from its commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "input_registry_hash": INPUT_REGISTRY_HASH,
            "withheld_target_registry_hash": TARGET_REGISTRY_HASH,
            "comparisons": comparisons,
            "adverse_controls": adverse_controls,
            "complete_trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['row_id']} ({row['formula']}, {row['charge_action']}): forced electron count "
            f"{row['predicted_electron_count']}; forced {row['predicted_width_parity']}; NIST X-state "
            f"{row['measured_NIST_X_state']} gives multiplicity {row['measured_multiplicity']}; "
            f"pairs {row['complementary_pair_count']}; unmatched fibres {row['unmatched_fibre_count']}; pass {row['passed']}"
            for row in comparisons
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse_controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(SOURCE_ID,),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "ElectronCountSpinValidator",
    "experiment_registration_record",
    "prediction_program_document",
    "prediction_rows",
)
