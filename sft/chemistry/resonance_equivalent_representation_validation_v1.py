"""Capability-closed empirical validation for Chemistry ORG-002."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.resonance_equivalent_representation_law_v1 import (
    append_shared_successor,
    encoding,
    equivalent_pair,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id",
    "source_record_ordinal",
    "source_id",
    "authority",
    "registered_identity",
    "source_record_role",
    "custody_class",
)
EXPECTED_LAWS = (
    "one-complete-molecular-carrier",
    "multiple-formal-encodings",
    "complete-fold-fibre-complement",
    "representation-not-equilibrium-or-species",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-002 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "definition",
        "note",
        "example",
        "value",
        "outcome",
        "source_outcome",
        "presence",
        "target_payload_hash",
    }
    if (
        document.get("complete_registered_target_count") != 4
        or document.get(
            "target_definitions_notes_examples_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 4
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("ORG-002 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"resonance-equivalence-record-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        for identity_ordinal, key in enumerate(IDENTITY_KEYS[1:], 1):
            destination = f"{prefix}-identity-{identity_ordinal}"
            instructions.append(
                {
                    "opcode": "label",
                    "destination": destination,
                    "arguments": ["registered-source-identity", str(row[key])],
                }
            )
            registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": ["representation-law", label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-representation-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-representation-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": RESONANCE_EQUIVALENT_REPRESENTATION_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    spec = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "provenance": "forward_forcing_with-value-free-sealed-organic-representation-vector",
        "frozen_relation": spec.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in spec.target_rows),
        "all_four_rows_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "v1_search_scope_error_must_be_preserved": True,
        "falsification_condition": spec.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 4:
        raise ValueError("ORG-002 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("ORG-002 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 4:
        raise ValueError("ORG-002 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-002 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 4
        or len(rows) != 4
        or document.get("release_requires_prediction_seal") is not True
        or document.get("preserved_predecessor", (None, None))[1]
        != "sha256:18df21662ac89606b6d6e3cd2c7c80247b20cfe86156a97f85f1375f74185dbd"
    ):
        raise ValueError("ORG-002 corrected target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-002 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("ORG-002 target payload changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 4:
        raise ValueError("ORG-002 requires all four external surfaces")
    first = encoding(
        "first",
        "carrier",
        ("atom-a", "atom-b", "atom-c"),
        ((1, 2), (2, 3)),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    second = encoding(
        "second",
        "carrier",
        ("atom-a", "atom-b", "atom-c"),
        ((1, 2), (2, 3)),
        ("fold-fibre-two", "fold-fibre-one"),
    )
    pair = equivalent_pair("carrier", first, second)
    successor = append_shared_successor(pair, "atom-d")
    carrier_rejected = adjacency_rejected = partial_rejected = identical_rejected = False
    try:
        other = encoding(
            "other", "other-carrier", ("atom-a", "atom-b", "atom-c"), ((1, 2), (2, 3)),
            ("fold-fibre-two", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, other)
    except InadmissibleExactValue:
        carrier_rejected = True
    try:
        changed = encoding(
            "changed", "carrier", ("atom-a", "atom-b", "atom-c"), ((1, 3), (2, 3)),
            ("fold-fibre-two", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, changed)
    except InadmissibleExactValue:
        adjacency_rejected = True
    try:
        partial = encoding(
            "partial", "carrier", ("atom-a", "atom-b", "atom-c"), ((1, 2), (2, 3)),
            ("fold-fibre-one", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, partial)
    except InadmissibleExactValue:
        partial_rejected = True
    try:
        equivalent_pair("carrier", first, first)
    except InadmissibleExactValue:
        identical_rejected = True
    postseal = primary["exact_postseal_analysis"]
    return {
        "base_atom_count": len(pair.first.atoms),
        "base_adjacency_count": len(pair.first.adjacency),
        "base_representation_count": pair.representation_count.value,
        "successor_atom_count": len(successor.first.atoms),
        "successor_adjacency_count": len(successor.first.adjacency),
        "prior_atom_prefix_preserved": successor.first.atoms[:-1] == pair.first.atoms,
        "prior_adjacency_prefix_preserved": successor.first.adjacency[:-1] == pair.first.adjacency,
        "complete_complement_preserved": tuple(row.label for row in successor.first.fibres)
        == tuple(
            "fold-fibre-two" if row.label == "fold-fibre-one" else "fold-fibre-one"
            for row in successor.second.fibres
        ),
        "carrier_mismatch_rejected": carrier_rejected,
        "adjacency_mismatch_rejected": adjacency_rejected,
        "partial_complement_rejected": partial_rejected,
        "identical_encoding_rejected": identical_rejected,
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed" for row in rows
        ),
        "predecessor_opened_target_count": sum(
            row["custody_class"] == "family-identity-opened-by-admitted-ORG-001" for row in rows
        ),
        **postseal,
    }


class ResonanceEquivalentRepresentationValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC

    def validate(self, sealed):
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
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
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-002 capability-closed package changed")
        predictions = _prediction_map(execution.output)
        rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={
                row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
                for row in rows
            },
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        for row in rows:
            word = predictions[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, 1)
            )
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-complete-source-record-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "identity_match": identity_match,
                    "law_match": law_match,
                    "postseal_target_hash_match": target_match,
                    "passed": identity_match and law_match and target_match,
                }
            )
        analysis = exact_analysis(rows, json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")))
        try:
            exact_analysis(rows[:-1], {})
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        try:
            FoldWord((0,))
            numerical_zero_rejected = False
        except FoldLanguageHalt:
            numerical_zero_rejected = True
        document_text = json.dumps(document, sort_keys=True)
        controls = {
            "omitted_source_row_rejected": omission_rejected,
            "numerical_zero_rejected": numerical_zero_rejected,
            "all_four_target_hashes_bound_postseal": len(release.targets) == 4,
            "different_carrier_rejected": analysis["carrier_mismatch_rejected"],
            "changed_adjacency_rejected": analysis["adjacency_mismatch_rejected"],
            "partial_noncomplement_rejected": analysis["partial_complement_rejected"],
            "identical_encoding_rejected": analysis["identical_encoding_rejected"],
            "external_wavefunction_coefficient_and_charge_downstream_and_preserved": analysis[
                "external_wavefunction_and_coefficient_language_preserved"
            ]
            and analysis["external_signed_charge_inscription_preserved"],
            "v1_search_scope_error_preserved_and_corrected_separately": analysis[
                "preserved_v1_charge_search_scope_false_result_count"
            ]
            == 1
            and analysis["v2_corrected_complete_record_search_count"] == 4,
            "sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_definition_note_example_wavefunction_coefficient_charge_or_payload": not any(
                token in document_text.casefold()
                for token in (
                    "complete_term_record",
                    "definition",
                    "wavefunction",
                    "coefficient",
                    "o^{-}",
                    "target_payload_hash",
                )
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["base_atom_count"] == 3
            and analysis["base_adjacency_count"] == 2
            and analysis["base_representation_count"] == 2
            and analysis["successor_atom_count"] == 4
            and analysis["successor_adjacency_count"] == 3
            and analysis["prior_atom_prefix_preserved"]
            and analysis["prior_adjacency_prefix_preserved"]
            and analysis["complete_complement_preserved"]
            and analysis["complete_target_count"] == 4
            and analysis["complete_source_count"] == 4
            and analysis["development_observed_target_count"] == 3
            and analysis["predecessor_opened_target_count"] == 1
            and analysis["one_molecular_entity_representation_surface_present"]
            and analysis["at_least_two_formal_structures_surface_present"]
            and analysis["single_structure_insufficient_surface_present"]
            and analysis["formal_not_species_surface_present"]
            and analysis["not_equilibrium_surface_present"]
            and analysis["nonlocal_support_surface_present"]
            and analysis["all_rows_preserved"]
            and all(controls.values())
        )
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
                    ("exact-one-carrier-multiple-representation/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("ORG-002 target identity differs")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = (
            "Fold witness: one carrier, three atom occurrences, two incidences and two exact complementary encodings",
            "successor: four atom occurrences and three incidences with complete prior prefixes and complement retained",
            "IUPAC resonance surface: one molecular entity represented through contributing structures",
            "IUPAC resonance-form surface: at least two formal structures where one structure is insufficient",
            "IUPAC contributing-structure surface: formal encodings are not separate species",
            "IUPAC resonance-form control: representation arrow is not an equilibrium arrow",
            "IUPAC delocalization surface: support is not localized between two atoms",
            "external wavefunction, coefficient and signed-charge inscriptions preserved downstream only",
            "one V1 incomplete record-search result preserved; corrected across all four records in claim-specific V2 without recapture",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(row["source_id"] for row in rows),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = (
    "ResonanceEquivalentRepresentationValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
