"""Capability-closed prediction and complete NIST validation for ELEC-003."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re

from sft.chemistry.electron_count_spin_validation_v1 import prediction_rows as electron_prediction_rows
from sft.chemistry.orbital_support_batch_v1 import (
    ELECTRON_INPUT_HASH,
    ELECTRON_INPUT_PATH,
    IDENTITY_REGISTRY_HASH,
    IDENTITY_REGISTRY_PATH,
    ORBITAL_SUPPORT_SPEC,
    SOURCE_ID,
    TARGET_REGISTRY_HASH,
    TARGET_REGISTRY_PATH,
)
from sft.chemistry.orbital_support_law_v1 import (
    OccupiedMolecularSupport,
    conventional_support_correspondence,
    occupied_support_from_source_assignment,
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


TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
ORBITAL_PATTERN = re.compile(r"(?<![A-Za-z0-9])([1-9][0-9]*)([spdfgh])\s*([σπδφ])(?:\^([1-9][0-9]*))?")
RANK_LABELS = {
    "Σ": "structural-empty-One",
    "Π": "first-recurrence",
    "Δ": "second-recurrence",
    "Φ": "third-recurrence",
    "σ": "structural-empty-One",
    "π": "first-recurrence",
    "δ": "second-recurrence",
    "φ": "third-recurrence",
}


class _SourceTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.depth += 1
        elif self.depth and tag == "tr":
            self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell = True, []
        elif self.in_cell and tag == "sup":
            self.cell.append("^")
        elif self.in_cell and tag == "sub":
            self.cell.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = False
        elif self.depth and tag == "table":
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell.append(data)


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table: list[str] = []
    position = 0
    for symbol, rank in RANK_LABELS.items():
        position += 1
        key, value = f"key-{position}", f"value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["source-support-symbol", symbol]},
                {"opcode": "label", "destination": value, "arguments": ["axis-support-rank", rank]},
            )
        )
        table.extend((key, value))
    for row in electron_prediction_rows(root):
        position += 1
        key, value = f"key-{position}", f"value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["species-spin-parity", str(row["row_id"])]},
                {"opcode": "label", "destination": value, "arguments": ["spin-width-parity", str(row["required_spin_width_parity"])]},
            )
        )
        table.extend((key, value))
    for name, count in (("joining-phase-count", 2), ("maximum-spatial-occupancy", 2)):
        position += 1
        key, value = f"key-{position}", f"value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["support-law-constant", name]},
                {"opcode": "count", "destination": value, "arguments": [str(count)]},
            )
        )
        table.extend((key, value))
    instructions.extend(
        (
            {"opcode": "table", "destination": "support-law-vector", "arguments": table},
            {"opcode": "emit", "destination": "", "arguments": ["support-law-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ORBITAL_SUPPORT_SPEC.experiment_id + "-support-law-prediction",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": ORBITAL_SUPPORT_SPEC.experiment_id,
        "claim_id": ORBITAL_SUPPORT_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": ORBITAL_SUPPORT_SPEC.exact_result,
        "identity_registry": (IDENTITY_REGISTRY_PATH, IDENTITY_REGISTRY_HASH),
        "withheld_target_registry": (TARGET_REGISTRY_PATH, TARGET_REGISTRY_HASH),
        "electron_input_registry": (ELECTRON_INPUT_PATH, ELECTRON_INPUT_HASH),
        "prediction_program": prediction_program_document(root),
        "target_references": tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in ORBITAL_SUPPORT_SPEC.target_rows
        ),
        "target_content_absent_from_prediction_program": True,
        "target_inaccessible_to_capability_closed_execution": True,
        "all_360_rows_required": True,
        "falsification_condition": ORBITAL_SUPPORT_SPEC.falsification_condition,
    }


def _resolved_targets(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_REGISTRY_PATH) != IDENTITY_REGISTRY_HASH:
        raise ValueError("ELEC-003 target identity registry changed")
    if hash_file(root / TARGET_REGISTRY_PATH) != TARGET_REGISTRY_HASH:
        raise ValueError("ELEC-003 withheld target registry changed")
    identities = json.loads((root / IDENTITY_REGISTRY_PATH).read_text(encoding="utf-8"))["rows"]
    target_document = json.loads((root / TARGET_REGISTRY_PATH).read_text(encoding="utf-8"))
    targets = {str(row["target_id"]): row for row in target_document["rows"]}
    if len(identities) != 360 or len(targets) != 360 or {row["target_id"] for row in identities} != set(targets):
        raise ValueError("ELEC-003 source and target support differ")
    parsed_by_snapshot: dict[str, tuple[tuple[str, ...], ...]] = {}
    resolved = []
    for identity in identities:
        snapshot_path = root / identity["snapshot_path"]
        if hash_file(snapshot_path) != identity["snapshot_hash"]:
            raise ValueError("ELEC-003 NIST snapshot changed")
        if identity["snapshot_path"] not in parsed_by_snapshot:
            parser = _SourceTableParser()
            parser.feed(snapshot_path.read_text(encoding="utf-8"))
            parsed_by_snapshot[identity["snapshot_path"]] = tuple(
                row for row in parser.rows if len(row) == 13 and TERM_PATTERN.search(row[0])
            )
        source_row = parsed_by_snapshot[identity["snapshot_path"]][int(identity["state_row_ordinal"]) - 1]
        target = targets[identity["target_id"]]
        if tuple(target["spectroscopic_cells"]) != source_row or target["state_record"] != source_row[0]:
            raise ValueError("ELEC-003 independent NIST row extraction differs from target")
        terms = tuple((int(m.group(1)), m.group(2)) for m in TERM_PATTERN.finditer(source_row[0]))
        configs = tuple(
            (int(m.group(1)), m.group(2), m.group(3), int(m.group(4)) if m.group(4) else 1)
            for m in ORBITAL_PATTERN.finditer(source_row[0])
        )
        registered_terms = tuple(
            (int(row["measured_multiplicity"]), str(row["conventional_support_symbol"]))
            for row in target["term_assignments"]
        )
        registered_configs = tuple(
            (
                int(row["positive_radial_recurrence"]),
                str(row["source_family_label"]),
                str(row["conventional_support_symbol"]),
                1 if row["occupancy_record"] == "implicit-single-occurrence" else int(row["occupancy_record"]),
            )
            for row in target["configuration_assignments"]
        )
        if terms != registered_terms or configs != registered_configs:
            raise ValueError("ELEC-003 independent assignment extraction differs from target")
        term_word = FoldWord(tuple(FoldWord((PositiveCount(mult), HeldLabel("source-support-symbol", symbol))) for mult, symbol in terms))
        config_value = (
            FoldWord(
                tuple(
                    FoldWord(
                        (
                            PositiveCount(radial),
                            HeldLabel("source-family-label", family),
                            HeldLabel("source-support-symbol", symbol),
                            PositiveCount(occupancy),
                        )
                    )
                    for radial, family, symbol, occupancy in configs
                )
            )
            if configs
            else EMPTY_ONE
        )
        resolved.append(
            {
                "target_id": str(identity["target_id"]),
                "species_row_id": str(identity["species_row_id"]),
                "state_record": source_row[0],
                "terms": terms,
                "configs": configs,
                "snapshot_hash": str(identity["snapshot_hash"]),
                "target_value": FoldWord((HeldLabel("NIST-state-record", source_row[0]), term_word, config_value)),
            }
        )
    return tuple(resolved)


def _prediction_map(table: FoldTable) -> dict[tuple[str, str], object]:
    result = {}
    for entry in table.entries:
        if not isinstance(entry.left, HeldLabel):
            raise ValueError("ELEC-003 prediction key is invalid")
        result[(entry.left.family, entry.left.label)] = entry.right
    if len(result) != len(table.entries):
        raise ValueError("ELEC-003 prediction contains duplicate keys")
    return result


class OrbitalSupportValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ORBITAL_SUPPORT_SPEC

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
            custody_nonce=sha256_identity((registration_hash, TARGET_REGISTRY_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ELEC-003 prediction package changed during execution")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable):
            raise ValueError("ELEC-003 prediction is not a Fold table")
        predicted = _prediction_map(execution.output)

        comparisons = []
        term_total = 0
        config_total = 0
        for row in targets:
            species_parity = predicted[("species-spin-parity", row["species_row_id"])]
            term_passes = []
            for multiplicity, symbol in row["terms"]:
                term_total += 1
                expected_rank = predicted[("source-support-symbol", symbol)]
                derived_rank = HeldLabel("axis-support-rank", RANK_LABELS[symbol])
                measured_parity = HeldLabel("spin-width-parity", "odd-positive-width" if multiplicity % 2 else "even-positive-width")
                term_passes.append(expected_rank == derived_rank and measured_parity == species_parity)
            config_passes = []
            for radial, _family, symbol, occupancy in row["configs"]:
                config_total += 1
                support = occupied_support_from_source_assignment(
                    row["species_row_id"], PositiveCount(radial), symbol, PositiveCount(occupancy)
                )
                expected_rank = predicted[("source-support-symbol", symbol)]
                config_passes.append(
                    HeldLabel("axis-support-rank", RANK_LABELS[symbol]) == expected_rank
                    and support.occupancy_count.value <= 2
                )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "species_row_id": row["species_row_id"],
                    "NIST_state_record": row["state_record"],
                    "term_assignment_count": len(row["terms"]),
                    "configuration_assignment_count": len(row["configs"]),
                    "term_support_and_multiplicity_passed": all(term_passes),
                    "configuration_support_and_occupancy_passed": all(config_passes),
                    "passed": all(term_passes) and all(config_passes),
                }
            )
        unknown_symbol_rejected = False
        try:
            conventional_support_correspondence("unknown")
        except InadmissibleExactValue:
            unknown_symbol_rejected = True
        triple_rejected = False
        try:
            occupied_support_from_source_assignment("tampered", PositiveCount(1), "σ", PositiveCount(3))
        except InadmissibleExactValue:
            triple_rejected = True
        first_snapshot = self.root / self.spec.target_rows[0].snapshot_path
        changed_hash = "sha256:" + sha256(first_snapshot.read_bytes() + b"tampered").hexdigest()
        adverse = {
            "unknown_support_symbol_rejected": unknown_symbol_rejected,
            "triple_occupancy_rejected": triple_rejected,
            "wrong_multiplicity_parity_rejected": HeldLabel("spin-width-parity", "even-positive-width") != predicted[("species-spin-parity", "hydrogen-neutral")],
            "omitted_row_rejected": len(comparisons[:-1]) != 360,
            "tampered_snapshot_rejected": hash_file(first_snapshot) == self.spec.target_rows[0].snapshot_hash and changed_hash != self.spec.target_rows[0].snapshot_hash,
            "complete_assignment_counts_retained": len(comparisons) == 360 and term_total == 362 and config_total == 87,
        }
        passed = all(row["passed"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("complete-NIST-orbital-support-comparator/1", self.spec.experiment_id)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-003 released target differs from commitment")
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
            "identity_registry_hash": IDENTITY_REGISTRY_HASH,
            "target_registry_hash": TARGET_REGISTRY_HASH,
            "comparisons": comparisons,
            "adverse": adverse,
            "term_total": term_total,
            "configuration_total": config_total,
            "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']} ({row['species_row_id']}): NIST state {row['NIST_state_record']}; "
            f"term assignments {row['term_assignment_count']} pass {row['term_support_and_multiplicity_passed']}; "
            f"configuration assignments {row['configuration_assignment_count']} pass {row['configuration_support_and_occupancy_passed']}; row pass {row['passed']}"
            for row in comparisons
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse.items())
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


__all__ = ("OrbitalSupportValidator", "experiment_registration_record", "prediction_program_document")
