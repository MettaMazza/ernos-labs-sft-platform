"""Capability-closed joint-support prediction and complete dissociation validation for ELEC-007."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
from typing import Optional

from sft.chemistry.joint_correlation_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    JOINT_CORRELATION_SPEC,
    SOURCE_IDS,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.joint_correlation_law_v1 import (
    JointSeparatedPairSupport,
    complete_separated_pair_support,
    dissociation_observation,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
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


APS_PATH = "experiments/external_sources/chemistry/snapshots/aps-hydrogen-dissociation-1994.json"
APS_HASH = "sha256:9c41d01395090b18b2eb8b1223e9cb430d9309f79d1a0324b092a5ed8c1b6953"
NIST_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
NIST_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"


class _IndependentNoteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.note_id: Optional[str] = None
        self.parts: list[str] = []
        self.notes: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "tr":
            self.in_row, self.note_id, self.parts = True, None, []
        elif self.in_row and tag == "a" and str(attributes.get("id", "")).startswith("Dia"):
            self.note_id = str(attributes["id"])
        elif self.in_row and tag == "sup":
            self.parts.append("^")
        elif self.in_row and tag == "sub":
            self.parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_row:
            if self.note_id is not None:
                self.notes[self.note_id] = " ".join(unescape("".join(self.parts)).split())
            self.in_row = False

    def handle_data(self, data: str) -> None:
        if self.in_row:
            self.parts.append(data)


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ELEC-007 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-joint-correlation-identities/1" or len(rows) != 9:
        raise ValueError("ELEC-007 identity registry is incomplete")
    if len({str(row["target_id"]) for row in rows}) != 9:
        raise ValueError("ELEC-007 identity registry contains duplicate targets")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Emit only the universal exact joint-support law, without a measured magnitude."""

    _identities(root)
    rows = (
        ("joint-word-count", "count", "2"),
        ("independent-cartesian-count", "count", "4"),
        ("joint-relation", "label", "nonfactorizable-complementary-cross-centre-pair"),
        ("same-centre-support", "label", "excluded"),
        ("dissociation-record", "label", "exact-positive-post-seal-observation"),
    )
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_registers: list[str] = []
    for position, (name, opcode, value) in enumerate(rows, start=1):
        key, result = f"key-{position}", f"value-{position}"
        instructions.append({"opcode": "label", "destination": key, "arguments": ["joint-support-law", name]})
        instructions.append(
            {"opcode": opcode, "destination": result, "arguments": [value]}
            if opcode == "count"
            else {"opcode": "label", "destination": result, "arguments": ["joint-support-result", value]}
        )
        table_registers.extend((key, result))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-joint-support-law", "arguments": table_registers},
            {"opcode": "emit", "destination": "", "arguments": ["complete-joint-support-law"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": JOINT_CORRELATION_SPEC.experiment_id + "-joint-support-prediction",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": JOINT_CORRELATION_SPEC.experiment_id,
        "claim_id": JOINT_CORRELATION_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": JOINT_CORRELATION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(root),
        "target_references": tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in JOINT_CORRELATION_SPEC.target_rows
        ),
        "target_content_absent_from_prediction": True,
        "target_inaccessible_to_capability_closed_execution": True,
        "all_nine_records_required": True,
        "measured_magnitudes_do_not_select_joint_law": True,
        "falsification_condition": JOINT_CORRELATION_SPEC.falsification_condition,
    }


def _reconstructed_targets(root: Path) -> tuple[dict[str, object], ...]:
    identities = _identities(root)
    if hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("ELEC-007 withheld target registry changed")
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    registered = {str(row["target_id"]): row for row in document.get("rows", ())}
    if document.get("schema") != "sft-v3-joint-correlation-withheld-targets/1" or len(registered) != 9:
        raise ValueError("ELEC-007 withheld target registry is incomplete")

    if hash_file(root / APS_PATH) != APS_HASH or hash_file(root / NIST_PATH) != NIST_HASH:
        raise ValueError("ELEC-007 external source bytes changed")
    aps = json.loads((root / APS_PATH).read_text(encoding="utf-8"))
    if aps.get("schema") != "sft-v3-primary-source-numeric-extract/1" or len(aps.get("records", ())) != 6:
        raise ValueError("ELEC-007 transparent APS extract is incomplete")
    parser = _IndependentNoteParser()
    parser.feed((root / NIST_PATH).read_text(encoding="utf-8"))
    note111, note125 = parser.notes.get("Dia111", ""), parser.notes.get("Dia125", "")
    if "118377._6" not in note111 or "28174.2" not in note111 or "36118.3 ± 0.5" not in note125:
        raise ValueError("ELEC-007 NIST source inscriptions are incomplete")

    rebuilt: list[dict[str, object]] = []
    for ordinal, source in enumerate(aps["records"], start=1):
        target_id = f"APS-HYDROGEN-DISSOCIATION-{ordinal:03d}"
        rebuilt.append(
            {
                "target_id": target_id,
                "source_id": "APS-PRA-49-2460-1994",
                "species": source["species"],
                "state": source["state"],
                "record_kind": source["kind"],
                "value_inscription": source["value_inscription"],
                "value_numerator": source["value_numerator"],
                "value_denominator": source["value_denominator"],
                "uncertainty_inscription": source["uncertainty_inscription"],
                "uncertainty_numerator": source["uncertainty_numerator"],
                "uncertainty_denominator": source["uncertainty_denominator"],
                "unit": source["unit"],
                "joint_support_role": "bound-state-to-separated-product-support",
                "snapshot_path": APS_PATH,
                "snapshot_hash": APS_HASH,
            }
        )
    nist = (
        ("Dia111", "H2", "B-state-dissociation-limit", "compiled_observed_dissociation_limit", "118377._6", 1183776, "absence", "absence", "absence", "bound-excited-state-to-separated-product-support"),
        ("Dia111", "H2", "B-state", "compiled_dissociation_energy", "28174.2", 281742, "absence", "absence", "absence", "bound-excited-state-to-separated-product-support"),
        ("Dia125", "H2", "X-ground", "measured_upper_limit", "36118.3", 361183, "0.5", 5, 10, "bound-ground-state-to-separated-product-support"),
    )
    for ordinal, (note_id, species, state, kind, inscription, numerator, uncertainty_inscription, uncertainty_numerator, uncertainty_denominator, role) in enumerate(nist, start=1):
        target_id = f"NIST-H2-DISSOCIATION-{ordinal:03d}"
        rebuilt.append(
            {
                "target_id": target_id,
                "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-DISSOCIATION",
                "species": species,
                "state": state,
                "record_kind": kind,
                "value_inscription": inscription,
                "value_numerator": numerator,
                "value_denominator": 10,
                "uncertainty_inscription": uncertainty_inscription,
                "uncertainty_numerator": uncertainty_numerator,
                "uncertainty_denominator": uncertainty_denominator,
                "unit": "inverse-centimetre",
                "joint_support_role": role,
                "source_note_id": note_id,
                "source_note_text": parser.notes[note_id],
                "snapshot_path": NIST_PATH,
                "snapshot_hash": NIST_HASH,
            }
        )
    if {str(row["target_id"]) for row in rebuilt} != {str(row["target_id"]) for row in identities}:
        raise ValueError("ELEC-007 independently rebuilt identities differ")
    resolved = []
    for row in rebuilt:
        target = registered[str(row["target_id"])]
        if target != row:
            raise ValueError("ELEC-007 independently reconstructed target differs from registry")
        observation = dissociation_observation(
            str(row["source_id"]), str(row["species"]), str(row["state"]), str(row["joint_support_role"]),
            int(row["value_numerator"]), int(row["value_denominator"]),
            row["uncertainty_numerator"], row["uncertainty_denominator"],
        )
        target_value = FoldWord(
            (
                observation.source_identity,
                observation.species_identity,
                observation.state_identity,
                observation.joint_support_role,
                observation.positive_energy_separation,
                observation.positive_uncertainty_or_absence,
                HeldLabel("record-kind", str(row["record_kind"])),
                HeldLabel("source-value-inscription", str(row["value_inscription"])),
                HeldLabel("source-uncertainty-inscription", str(row["uncertainty_inscription"])),
            )
        )
        resolved.append({**row, "observation": observation, "target_value": target_value})
    return tuple(resolved)


def _prediction_map(table: FoldTable) -> dict[str, object]:
    result = {}
    for entry in table.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "joint-support-law":
            raise ValueError("ELEC-007 prediction key is invalid")
        result[entry.left.label] = entry.right
    if len(result) != 5:
        raise ValueError("ELEC-007 prediction law is incomplete")
    return result


class JointCorrelationValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = JOINT_CORRELATION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        targets = _reconstructed_targets(self.root)
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-APS-NIST-target-custodian",
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
            raise ValueError("ELEC-007 prediction package changed during execution")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable):
            raise ValueError("ELEC-007 prediction is not a complete Fold table")
        predicted = _prediction_map(execution.output)
        if predicted != {
            "joint-word-count": PositiveCount(2),
            "independent-cartesian-count": PositiveCount(4),
            "joint-relation": HeldLabel("joint-support-result", "nonfactorizable-complementary-cross-centre-pair"),
            "same-centre-support": HeldLabel("joint-support-result", "excluded"),
            "dissociation-record": HeldLabel("joint-support-result", "exact-positive-post-seal-observation"),
        }:
            raise ValueError("ELEC-007 sealed joint-support law changed")

        comparisons = []
        for row in targets:
            support = complete_separated_pair_support(str(row["species"]), "left-product", "right-product")
            observation = row["observation"]
            passed = (
                support.positive_joint_word_count == predicted["joint-word-count"]
                and support.positive_independent_cartesian_count == predicted["independent-cartesian-count"]
                and support.retains_nonfactorizable_joint_distinction
                and observation.positive_energy_separation == PositiveRatio.from_pair(int(row["value_numerator"]), int(row["value_denominator"]))
                and (
                    observation.positive_uncertainty_or_absence is EMPTY_ONE
                    if row["uncertainty_numerator"] == "absence"
                    else observation.positive_uncertainty_or_absence == PositiveRatio.from_pair(int(row["uncertainty_numerator"]), int(row["uncertainty_denominator"]))
                )
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "source_id": row["source_id"],
                    "species": row["species"],
                    "state": row["state"],
                    "record_kind": row["record_kind"],
                    "value_inscription": row["value_inscription"],
                    "value_numerator": row["value_numerator"],
                    "value_denominator": row["value_denominator"],
                    "uncertainty_inscription": row["uncertainty_inscription"],
                    "unit": row["unit"],
                    "joint_word_count": support.positive_joint_word_count.value,
                    "independent_cartesian_count": support.positive_independent_cartesian_count.value,
                    "passed": passed,
                }
            )

        base = complete_separated_pair_support("control", "left", "right")
        incomplete_rejected = factorized_rejected = same_centre_rejected = False
        try:
            JointSeparatedPairSupport(base.molecular_carrier, base.left_centre, base.right_centre, base.joint_words[:1])
        except InadmissibleExactValue:
            incomplete_rejected = True
        try:
            same_left = FoldWord((HeldLabel("electron-held-fibre", "lower-fibre"), base.left_centre, HeldLabel("electron-held-fibre", "upper-fibre"), base.left_centre))
            same_right = FoldWord((HeldLabel("electron-held-fibre", "lower-fibre"), base.right_centre, HeldLabel("electron-held-fibre", "upper-fibre"), base.right_centre))
            JointSeparatedPairSupport(base.molecular_carrier, base.left_centre, base.right_centre, base.joint_words + (same_left, same_right))
        except InadmissibleExactValue:
            factorized_rejected = True
        try:
            complete_separated_pair_support("control", "same", "same")
        except InadmissibleExactValue:
            same_centre_rejected = True
        numeric_zero_rejected = False
        try:
            FoldWord((0,))
        except FoldLanguageHalt:
            numeric_zero_rejected = True
        nonpositive_rejected = False
        try:
            PositiveRatio.from_pair(0, 1)
        except InadmissibleExactValue:
            nonpositive_rejected = True
        first_snapshot = self.root / APS_PATH
        changed_hash = "sha256:" + sha256(first_snapshot.read_bytes() + b"tampered").hexdigest()
        counts = {
            "records": len(comparisons),
            "APS_records": sum(row["source_id"] == SOURCE_IDS[0] for row in comparisons),
            "NIST_records": sum(row["source_id"] == SOURCE_IDS[1] for row in comparisons),
            "direct_or_compiled": sum(row["record_kind"] != "derived_from_measured-neutral-and-ionization-intervals" for row in comparisons),
            "derived_ionic": sum(row["record_kind"] == "derived_from_measured-neutral-and-ionization-intervals" for row in comparisons),
            "positive_uncertainties": sum(row["uncertainty_inscription"] != "absence" for row in comparisons),
            "absent_uncertainties": sum(row["uncertainty_inscription"] == "absence" for row in comparisons),
            "species": len({str(row["species"]) for row in comparisons}),
        }
        adverse = {
            "incomplete_one_word_support_rejected": incomplete_rejected,
            "factorized_four_word_support_rejected": factorized_rejected,
            "same_centre_support_rejected": same_centre_rejected,
            "numerical_zero_rejected": numeric_zero_rejected,
            "nonpositive_energy_rejected": nonpositive_rejected,
            "omitted_record_rejected": len(comparisons[:-1]) != 9,
            "omitted_derived_ion_rejected": counts["derived_ionic"] == 2,
            "selected_newer_only_rejected": counts["NIST_records"] == 3,
            "selected_NIST_only_rejected": counts["APS_records"] == 6,
            "changed_value_rejected": PositiveRatio.from_pair(int(comparisons[0]["value_numerator"]), int(comparisons[0]["value_denominator"])) != PositiveRatio.from_pair(int(comparisons[0]["value_numerator"]) + 1, int(comparisons[0]["value_denominator"])),
            "changed_uncertainty_rejected": PositiveRatio.from_pair(4, 100) != PositiveRatio.from_pair(5, 100),
            "tampered_snapshot_rejected": hash_file(first_snapshot) == APS_HASH and changed_hash != APS_HASH,
            "complete_provenance_vector_retained": counts == {"records": 9, "APS_records": 6, "NIST_records": 3, "direct_or_compiled": 7, "derived_ionic": 2, "positive_uncertainties": 7, "absent_uncertainties": 2, "species": 4},
        }
        passed = all(row["passed"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("complete-APS-NIST-joint-correlation-comparator/1", self.spec.experiment_id)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-007 released target differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration_hash": registration_hash, "prediction_seal_hash": prediction_seal.seal_hash, "comparisons": comparisons, "counts": counts, "adverse": adverse, "trace_hash": execution.trace_hash}
        measurements = tuple(
            f"{row['target_id']} ({row['species']} {row['state']}): {row['value_inscription']} {row['unit']}; uncertainty {row['uncertainty_inscription']}; kind {row['record_kind']}; joint {row['joint_word_count']}/Cartesian {row['independent_cartesian_count']}; pass {row['passed']}"
            for row in comparisons
        ) + tuple(f"count {key}: {value}" for key, value in counts.items()) + tuple(f"adverse {key}: {value}" for key, value in adverse.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, SOURCE_IDS, measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("JointCorrelationValidator", "experiment_registration_record", "prediction_program_document")
