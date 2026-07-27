"""Capability-closed post-seal validation for Chemistry INORG-005."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.coordination_isomerism_batch_v1 import (
    ADDENDUM_HASH,
    ADDENDUM_INVENTORY_HASH,
    COORDINATION_ISOMERISM_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRELIMINARY_IDENTITY_HASH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOURCE_FILES,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.coordination_isomerism_law_v1 import (
    FiniteCoordinationForm,
    extend_coordination_form,
    forced_coordination_isomer_relation,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmptyOne,
    FoldLanguageHalt,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id",
    "source_record_ordinal",
    "authority",
    "source_id",
    "registered_identity",
    "source_record_role",
    "source_locator",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-005 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "source_inscription",
        "target_payload_hash",
        "definition",
        "class",
        "example",
        "formula",
        "page",
        "section",
        "status",
        "value",
        "outcome",
    }
    if (
        document.get("complete_registered_target_count") != 17
        or document.get("target_values_or_payload_hashes_present") is not False
        or document.get("all_definition_class_example_formula_page_section_status_source_citation_license_disclaimer_and_target_payload_values_absent") is not True
        or document.get("preserved_incomplete_preliminary_identity_sha256") != PRELIMINARY_IDENTITY_HASH
        or len(rows) != 17
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 18))
        or len({row["target_id"] for row in rows}) != 17
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-005 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"coordination-isomerism-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("coordination-isomer-equivalence-law", "complete-occurrence-bijection-preserves-composition-attachment-adjacency-and-three-axis-two-fibre-words"),
            ("coordination-isomer-composition-boundary", "same-complete-composition-required"),
            ("coordination-isomer-attachment-law", "first-attachment-or-graph-failure-forces-attachment-class"),
            ("coordination-isomer-orientation-law", "global-fibre-complement-precedes-remaining-orientation-adjacency-class"),
            ("coordination-isomer-evidence-law", "all-seventeen-surfaces-two-identity-redirects-and-literal-term-absence-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-coordination-isomerism-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-coordination-isomerism-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COORDINATION_ISOMERISM_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COORDINATION_ISOMERISM_SPEC.experiment_id,
        "claim_id": COORDINATION_ISOMERISM_SPEC.claim_id,
        "provenance": "observational_derivation_with_family_identity_seal_and_versioned_value_free_linkage_addendum",
        "frozen_relation": COORDINATION_ISOMERISM_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": SOURCE_FILES,
        "linkage_identity_addendum_hash": ADDENDUM_HASH,
        "linkage_source_inventory_hash": ADDENDUM_INVENTORY_HASH,
        "preserved_incomplete_preliminary_identity_hash": PRELIMINARY_IDENTITY_HASH,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COORDINATION_ISOMERISM_SPEC.target_rows),
        "all_definition_class_example_formula_page_section_status_source_citation_license_disclaimer_and_target_payload_values_absent": True,
        "development_observation_disclosed": True,
        "not_claimed_as_unknown_target_forward_prediction": True,
        "target_content_inaccessible_to_capability_closed_prediction": True,
        "identity_addendum_changes_authority_coverage_not_fold_law_or_candidate_conditions": True,
        "both_presented_identity_redirects_and_explicit_literal_term_absence_must_be_preserved": True,
        "falsification_condition": COORDINATION_ISOMERISM_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 17:
        raise ValueError("INORG-005 prediction is not the complete 17-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 12
        ):
            raise ValueError("INORG-005 prediction lost a consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 17:
        raise ValueError("INORG-005 prediction duplicated a target")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"INORG-005 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 17 or document.get("release_requires_prediction_seal") is not True or len(targets) != 17:
        raise ValueError("INORG-005 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-005 identity/target binding changed")
        inscription = target.get("source_inscription")
        if inscription is None or target.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], inscription)):
            raise ValueError("INORG-005 target payload changed")
        resolved.append(target)
    return tuple(resolved)


def _word(first: str, second: str = "EmptyOne", third: str = "EmptyOne"):
    def cell(label: str):
        return EmptyOne() if label == "EmptyOne" else HeldLabel("fold-orientation-fibre", label)
    return (cell(first), cell(second), cell(third))


def _form(
    compositions=("L", "L"),
    attachments=("mode-one", "mode-one"),
    words=(("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-two", "EmptyOne", "EmptyOne")),
    pairs=((1, 2),),
) -> FiniteCoordinationForm:
    return FiniteCoordinationForm(
        tuple(HeldLabel("coordination-composition-label", label) for label in compositions),
        tuple(HeldLabel("coordination-attachment-mode", label) for label in attachments),
        tuple(_word(*word) for word in words),
        tuple((PositiveCount(first), PositiveCount(second)) for first, second in pairs),
    )


def exact_coordination_isomerism_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 17 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 18)):
        raise ValueError("INORG-005 requires all 17 source records")
    base = _form()
    reordered = _form(words=(("fibre-two", "EmptyOne", "EmptyOne"), ("fibre-one", "EmptyOne", "EmptyOne")))
    attachment = _form(attachments=("mode-one", "mode-two"))
    orientation = _form(words=(("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-one", "EmptyOne", "EmptyOne")))
    chiral = _form(
        compositions=("A", "B", "C"),
        attachments=("mode-one", "mode-one", "mode-one"),
        words=(("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-one", "fibre-two", "EmptyOne"), ("fibre-two", "fibre-one", "EmptyOne")),
        pairs=((1, 2), (2, 3), (3, 1)),
    )
    mirror = _form(
        compositions=("A", "B", "C"),
        attachments=("mode-one", "mode-one", "mode-one"),
        words=(("fibre-two", "EmptyOne", "EmptyOne"), ("fibre-two", "fibre-one", "EmptyOne"), ("fibre-one", "fibre-two", "EmptyOne")),
        pairs=((1, 2), (2, 3), (3, 1)),
    )
    successor = extend_coordination_form(
        base,
        HeldLabel("coordination-composition-label", "L"),
        HeldLabel("coordination-attachment-mode", "mode-one"),
        _word("fibre-two", "fibre-two", "EmptyOne"),
        (PositiveCount(1), PositiveCount(2)),
    )
    equivalent_record = forced_coordination_isomer_relation(base, reordered)
    attachment_record = forced_coordination_isomer_relation(base, attachment)
    orientation_record = forced_coordination_isomer_relation(base, orientation)
    mirror_record = forced_coordination_isomer_relation(chiral, mirror)
    try:
        forced_coordination_isomer_relation(base, _form(compositions=("L", "M")))
        different_composition_rejected = False
    except InadmissibleExactValue:
        different_composition_rejected = True
    source_analysis = primary["exact_postseal_analysis"]
    return {
        "complete_registered_target_count": len(rows),
        "occurrence_permutation_equivalence_reconstructed": equivalent_record.exact_equivalence,
        "different_composition_rejected": different_composition_rejected,
        "attachment_class_reconstructed": attachment_record.native_distinction_class.label == "attachment-class-distinction",
        "orientation_adjacency_class_reconstructed": orientation_record.native_distinction_class.label == "orientation-adjacency-class-distinction",
        "mirror_complement_class_reconstructed": mirror_record.native_distinction_class.label == "mirror-complement-class-distinction",
        "successor_preserves_complete_prior_subform": successor.composition_labels[:2] == base.composition_labels and successor.attachment_labels[:2] == base.attachment_labels and successor.orientation_words[:2] == base.orientation_words and successor.adjacency_pairs[:1] == base.adjacency_pairs,
        "only_two_forced_fibre_labels_used": all(
            isinstance(cell, EmptyOne) or cell.label in {"fibre-one", "fibre-two"}
            for form in (base, reordered, attachment, orientation, chiral, mirror, successor)
            for word in form.orientation_words
            for cell in word
        ),
        **source_analysis,
        "registered_to_presented_identity_redirect_count": primary["registered_to_presented_identity_redirect_count"],
        "registered_to_presented_identity_redirects_preserved": primary["registered_to_presented_identity_redirects_preserved"],
        "explicit_linkage_literal_absence_preserved": primary["explicit_linkage_literal_absence_preserved"],
        "imported_catalogue_or_observed_class_used_as_fold_parameter": primary["isomer_catalogue_name_point_group_plane_mirror_or_observed_class_used_as_fold_proof_parameter"],
    }


class CoordinationIsomerismValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COORDINATION_ISOMERISM_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("INORG-005 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        expected_laws = (
            "complete-occurrence-bijection-preserves-composition-attachment-adjacency-and-three-axis-two-fibre-words",
            "same-complete-composition-required",
            "first-attachment-or-graph-failure-forces-attachment-class",
            "global-fibre-complement-precedes-remaining-orientation-adjacency-class",
            "all-seventeen-surfaces-two-identity-redirects-and-literal-term-absence-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})

        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis = exact_coordination_isomerism_analysis(source_rows, primary)
        try:
            exact_coordination_isomerism_analysis(source_rows[:-1], primary)
            omitted = False
        except ValueError:
            omitted = True
        try:
            FoldWord((0,))
            numerical_zero = False
        except FoldLanguageHalt:
            numerical_zero = True
        try:
            _form(words=(("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-three", "EmptyOne", "EmptyOne")))
            third_fibre = False
        except InadmissibleExactValue:
            third_fibre = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted,
            "numerical_zero_rejected": numerical_zero,
            "third_fibre_label_rejected": third_fibre,
            "different_composition_rejected": analysis["different_composition_rejected"],
            "both_presented_identity_redirects_preserved": analysis["registered_to_presented_identity_redirect_count"] == 2 and analysis["registered_to_presented_identity_redirects_preserved"],
            "explicit_linkage_literal_absence_preserved": analysis["explicit_linkage_literal_absence_preserved"],
            "complete_17_record_vector_retained": len(release.targets) == 17,
            "prediction_contains_no_withheld_target_hash_or_inscription": TARGET_HASH not in json.dumps(document, sort_keys=True) and "source_inscription" not in json.dumps(document, sort_keys=True),
        }
        boolean_analysis = {
            key: value
            for key, value in analysis.items()
            if isinstance(value, bool) and key != "imported_catalogue_or_observed_class_used_as_fold_parameter"
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(boolean_analysis.values())
            and analysis["registered_to_presented_identity_redirect_count"] == 2
            and analysis["imported_catalogue_or_observed_class_used_as_fold_parameter"] is False
            and all(controls.values())
        )

        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-coordination-isomer-equivalence-classes/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-005 released target differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "IUPAC general isomer relation retained",
            "IUPAC relative-position same-side/opposite-side distinction retained",
            "IUPAC mirror-image non-superposable distinction retained",
            "IUPAC Red Book point-of-ligation and two isomeric donor-attachment modes retained",
            "two registered-to-presented Gold Book identity redirects retained",
            "explicit literal linkage-isomer term absence in the complete extracted Red Book retained",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            ("IUPAC-GOLD-BOOK-I03294", "IUPAC-GOLD-BOOK-C01093", "IUPAC-GOLD-BOOK-E02069", "IUPAC-RED-BOOK-2005"),
            measurements, sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "CoordinationIsomerismValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_coordination_isomerism_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
