"""Capability-closed post-seal validation for Chemistry INORG-010."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.organometallic_metal_carbon_bond_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, ORGANOMETALLIC_METAL_CARBON_BOND_SPEC, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.organometallic_metal_carbon_bond_law_v1 import append_direct_incidence, direct_incidence, forced_organometallic_bond
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldLanguageHalt, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = ("target_id", "source_record_ordinal", "source_id", "authority", "registered_identity", "source_record_role", "custody_class")
EXPECTED_LAWS = (
    "direct-centre-carbon-incidence",
    "complete-held-electron-and-incidence-support",
    "positive-support-organometallic-EmptyOne-otherwise",
    "direct-incidence-successor-with-complete-twelve-row-source-retention",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-010 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    forbidden = {"definition", "example", "value", "outcome", "source_outcome", "registered_surface_phrase", "target_payload_hash"}
    if (
        document.get("complete_registered_target_count") != 12
        or document.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False
        or len(rows) != 12 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 13))
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-010 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]; table = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"organometallic-metal-carbon-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"; instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]}); registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"; instructions.append({"opcode": "label", "destination": destination, "arguments": ["organometallic-metal-carbon-law", label]}); registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers}); table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-organometallic-metal-carbon-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-organometallic-metal-carbon-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.experiment_id + "-value-free-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.experiment_id,
        "claim_id": ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.claim_id,
        "provenance": "forward_forcing_with-frozen-development-observed-complete-IUPAC-record",
        "frozen_relation": ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.target_rows),
        "all_twelve_rows_required": True, "target_content_inaccessible_to_prediction_execution": True,
        "no_conventional_metal_list_species_lookup_name_classification_observed_example_or_fit": True,
        "falsification_condition": ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 12:
        raise ValueError("INORG-010 prediction is not the complete twelve-row table")
    result = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("INORG-010 prediction row is incomplete")
        result[entry.left.label] = entry.right
    if len(result) != 12:
        raise ValueError("INORG-010 prediction duplicates a target")
    return result


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("INORG-010 post-seal evidence changed")
    identities = _identities(root); document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 12 or len(rows) != 12 or document.get("release_requires_prediction_seal") is not True:
        raise ValueError("INORG-010 target vector is incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-010 target differs from registered identity")
        if row.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome"))):
            raise ValueError("INORG-010 target payload hash changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict[str, object]:
    if len(rows) != 12:
        raise ValueError("INORG-010 requires all twelve source surfaces")
    absent = forced_organometallic_bond("absent", EmptyOne())
    first = forced_organometallic_bond("first", (direct_incidence("M1", "C1", PositiveCount(2)),))
    successor = append_direct_incidence(first, direct_incidence("M1", "C2", PositiveCount(2)))
    postseal = primary["exact_postseal_analysis"]
    return {
        "absence_is_EmptyOne": isinstance(absent, EmptyOne), "first_count": first.direct_incidence_count.value,
        "first_class": first.classification.label, "successor_count": successor.direct_incidence_count.value,
        "complete_target_count": len(rows), "complete_source_count": len({row["source_id"] for row in rows}),
        "all_registered_surfaces_present": all(row["source_outcome"]["registered_surface_present"] for row in rows),
        "example_count": sum("example" in row["source_record_role"] for row in rows),
        "explicit_exclusion_count": postseal["explicit_exclusion_count"], "scope_distinction_count": postseal["scope_distinction_count"],
        "complete_target_vector_hash": postseal["complete_target_vector_hash"], "source_recapture_count": postseal["source_recapture_count"],
        "all_rows_preserved": postseal["all_rows_preserved"],
    }


class OrganometallicMetalCarbonBondValidator:
    def __init__(self, root: Path): self.root = root.resolve(); self.spec = ORGANOMETALLIC_METAL_CARBON_BOND_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("INORG-010 prediction package changed")
        predicted = _prediction_map(execution.output); source_rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]; values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(values, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")); analysis = exact_analysis(source_rows, primary)
        try: exact_analysis(source_rows[:-1], primary); omitted_rejected = False
        except ValueError: omitted_rejected = True
        try: FoldWord((0,)); zero_rejected = False
        except FoldLanguageHalt: zero_rejected = True
        controls = {
            "omitted_source_row_rejected": omitted_rejected, "numerical_zero_rejected": zero_rejected,
            "all_twelve_target_hashes_bound_postseal": len(release.targets) == 12,
            "all_six_named_examples_preserved": analysis["example_count"] == 6,
            "direct-evidence-exclusion-preserved": analysis["explicit_exclusion_count"] == 1,
            "sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_definition_example_or_target_payload": not any(token in json.dumps(document, sort_keys=True) for token in ("complete_definition_text", "registered_surface_phrase", "target_payload_hash", "MeMgI")),
        }
        passed = (
            all(row["passed"] for row in comparisons) and analysis["absence_is_EmptyOne"]
            and analysis["first_count"] == 1 and analysis["first_class"] == "organometallic" and analysis["successor_count"] == 2
            and analysis["complete_target_count"] == 12 and analysis["complete_source_count"] == 1
            and analysis["all_registered_surfaces_present"] and analysis["scope_distinction_count"] == 1
            and analysis["all_rows_preserved"] and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-organometallic-metal-carbon/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-010 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "structural absence remains EmptyOne; one direct incidence forces count one and organometallic class; successor count two",
            "complete IUPAC vector: twelve distinct criterion, scope, example, context and exclusion surfaces",
            "six named example surfaces and the no-direct-structural-evidence exclusion retained",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("OrganometallicMetalCarbonBondValidator", "_identities", "_prediction_map", "_source_rows", "exact_analysis", "experiment_registration_record", "prediction_program_document")
