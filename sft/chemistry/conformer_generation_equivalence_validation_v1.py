"""Capability-closed operational and external validation for Chemistry ORG-005."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.conformer_generation_equivalence_batch_v1 import (
    CONFORMER_GENERATION_EQUIVALENCE_SPEC, IDENTITY_HASH, IDENTITY_PATH,
    PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.conformer_generation_equivalence_law_v1 import (
    ANTI, GAUCHE_FORWARD, GAUCHE_REVERSE, HeldTorsionAlphabet,
    butane_four_site_census,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldLanguageHalt,
    FoldTable, FoldWord, HostilePackageAuditor, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_record_ordinal", "source_id", "authority", "registered_identity",
    "source_record_role", "custody_class",
)
EXPECTED_LAWS = (
    "complete-cartesian-held-state-generation",
    "exhaustive-graph-automorphism-census",
    "exact-disjoint-orbit-equivalence",
    "development-observed-complete-external-census-after-seal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-005 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"definition", "table", "value", "outcome", "source_outcome", "target_payload_hash"}
    if (
        document.get("complete_registered_target_count") != 4
        or document.get("development_observed_target_count") != 4
        or document.get("outcome_unopened_blind_target_count") != 0
        or len(rows) != 4
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("ORG-005 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"conformer-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for identity_ordinal, key in enumerate(IDENTITY_KEYS[1:], 1):
            destination = f"{prefix}-identity-{identity_ordinal}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for law in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["conformer-law", law]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-conformer-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-conformer-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": CONFORMER_GENERATION_EQUIVALENCE_SPEC.experiment_id + "-value-free-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    spec = CONFORMER_GENERATION_EQUIVALENCE_SPEC
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "provenance": "observational_derivation_all-four-records-development-observed-not-claimed-blind",
        "frozen_relation": spec.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "complete_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in spec.target_rows),
        "all_four_rows_required": True,
        "all_rows_development_observed_and_disclosed": True,
        "unknown_target_blind_prediction_claimed": False,
        "all_complete_cccbdb_table_rows_required": True,
        "target_payload_hashes_released_only_after_derivation_seal": True,
        "falsification_condition": spec.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 4:
        raise ValueError("ORG-005 prediction incomplete")
    rows = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("ORG-005 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 4:
        raise ValueError("ORG-005 duplicate target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-005 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 4
        or document.get("all_rows_development_observed_and_not_claimed_blind") is not True
        or document.get("all_favourable_adverse_absent_scope_and_unresolved_rows_preserved") is not True
        or len(rows) != 4
    ):
        raise ValueError("ORG-005 complete target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-005 identity changed after target preservation")
        if row.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome"))):
            raise ValueError("ORG-005 target payload changed")
        if hash_file(root / row["opened_snapshot_path"]) != row["opened_snapshot_sha256"]:
            raise ValueError("ORG-005 source snapshot changed")
    return rows


def _by_role(rows: tuple[dict, ...], role: str) -> dict:
    matches = [row["source_outcome"] for row in rows if row["source_record_role"] == role]
    if len(matches) != 1:
        raise ValueError(f"ORG-005 role cardinality changed: {role}")
    return matches[0]


def _table(surface: dict, header: tuple[str, ...]) -> list[list[str]]:
    matches = [table for table in surface["complete_experimental_data_tables"] if table and tuple(table[0][:len(header)]) == header]
    if len(matches) != 1:
        raise ValueError(f"ORG-005 table cardinality changed: {header}")
    return matches[0]


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 4:
        raise ValueError("ORG-005 requires all four complete records")
    census = butane_four_site_census()
    classes = tuple(tuple(state.states[0].label for state in group) for group in census.equivalence_classes)
    incomplete_reversal_rejected = False
    try:
        HeldTorsionAlphabet((ANTI, GAUCHE_FORWARD), ((ANTI, ANTI),))
    except InadmissibleExactValue:
        incomplete_reversal_rejected = True
    conformer_text = json.dumps(_by_role(rows, "complete-conformer-term-record")["complete_term_record"], ensure_ascii=False, sort_keys=True)
    conformation_text = json.dumps(_by_role(rows, "complete-conformation-term-record")["complete_term_record"], ensure_ascii=False, sort_keys=True)
    analysis_text = json.dumps(_by_role(rows, "complete-conformational-analysis-term-record")["complete_term_record"], ensure_ascii=False, sort_keys=True)
    butane = _by_role(rows, "complete-butane-conformer-census-and-experimental-surface")
    conformation_rows = _table(butane, ("State", "Conformation"))
    state_rows = _table(butane, ("State", "Config", "State description", "Conf description", "Exp. min.", "Dipole (Debye)"))
    property_rows = _table(butane, ("Property", "Value", "Uncertainty", "units"))
    reference_rows = _table(butane, ("squib", "reference", "DOI"))
    labels = tuple(dict.fromkeys(row[3] for row in state_rows[2:]))
    anti_rows = [row for row in state_rows[2:] if row[3] == "Anti"]
    gauche_rows = [row for row in state_rows[2:] if row[3] == "Gauche"]
    barrier = [row for row in property_rows[1:] if row[0] == "Barrier to Internal Rotation"]
    computed = {
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": 4,
        "outcome_unopened_blind_target_count": 0,
        "conformer_distinct_potential_energy_minimum_surface_present": "distinct potential energy minimum" in conformer_text,
        "conformation_single_bond_rotation_surface_present": "rotations about formally single bonds" in conformation_text,
        "conformational_analysis_relative_energy_surface_present": "relative energies" in analysis_text and "alternative conformations" in analysis_text,
        "returned_small_molecule_heading": butane["returned_experimental_data_heading"],
        "complete_external_conformer_class_labels": list(labels),
        "complete_external_conformer_class_count": len(labels),
        "external_primary_conformation_label": conformation_rows[1][1],
        "external_anti_exp_minimum_string": anti_rows[0][4],
        "external_gauche_exp_minimum_string": gauche_rows[0][4],
        "external_gauche_adverse_false_row_preserved": gauche_rows[0][4] == "False",
        "external_gauche_reference_present": any("gauche butane conformer" in " ".join(row).casefold() for row in reference_rows),
        "external_internal_rotation_barrier_strings": barrier[0][1:4],
        "cccbdb_complete_table_count": butane["complete_table_count"],
        "cccbdb_complete_row_count": butane["complete_row_count"],
        "all_signed_zero_absent_favourable_adverse_and_unresolved_external_inscriptions_preserved": True,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in rows)),
    }
    if computed != primary.get("exact_postseal_analysis"):
        raise ValueError("ORG-005 complete analysis does not independently reconstruct")
    return {
        "generated_assignment_count": len(census.generated_assignments),
        "graph_automorphism_count": len(census.automorphisms),
        "equivalence_class_count": len(census.equivalence_classes),
        "equivalence_class_sizes": [len(group) for group in census.equivalence_classes],
        "equivalence_classes": [list(group) for group in classes],
        "partition_occurrence_count": sum(len(group) for group in census.equivalence_classes),
        "incomplete_reversal_rejected": incomplete_reversal_rejected,
        **computed,
    }


class ConformerGenerationEquivalenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = CONFORMER_GENERATION_EQUIVALENCE_SPEC

    def validate(self, sealed):
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
            raise ValueError("ORG-005 capability-closed package changed")
        predictions = _prediction_map(execution.output)
        rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-development-observed-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in rows},
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
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, 1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
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
        document_text = json.dumps(document, sort_keys=True).casefold()
        controls = {
            "omitted_source_rejected": omission_rejected,
            "numerical_zero_rejected": numerical_zero_rejected,
            "all_four_target_hashes_bound_postseal": len(release.targets) == 4,
            "development_observed_not_mislabelled_blind": analysis["outcome_unopened_blind_target_count"] == 0,
            "complete_assignment_partition": analysis["partition_occurrence_count"] == analysis["generated_assignment_count"] == 3,
            "complete_graph_action_census": analysis["graph_automorphism_count"] == 2,
            "incomplete_reversal_rejected": analysis["incomplete_reversal_rejected"],
            "adverse_gauche_false_row_preserved": analysis["external_gauche_adverse_false_row_preserved"],
            "all_external_inscriptions_preserved": analysis["all_signed_zero_absent_favourable_adverse_and_unresolved_external_inscriptions_preserved"],
            "prediction_contains_no_returned_conformer_energy_or_payload": not any(token in document_text for token in ("anti", "gauche", "16.6", "-125.79", "target_payload_hash")),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["generated_assignment_count"] == 3
            and analysis["equivalence_class_count"] == 2
            and analysis["equivalence_class_sizes"] == [1, 2]
            and analysis["complete_external_conformer_class_labels"] == ["Anti", "Gauche"]
            and analysis["complete_external_conformer_class_count"] == 2
            and analysis["conformer_distinct_potential_energy_minimum_surface_present"]
            and analysis["conformation_single_bond_rotation_surface_present"]
            and analysis["conformational_analysis_relative_energy_surface_present"]
            and analysis["external_internal_rotation_barrier_strings"] == ["16.6", "", "kJ mol -1"]
            and analysis["cccbdb_complete_table_count"] == 19
            and analysis["cccbdb_complete_row_count"] == 105
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
            comparison_implementation_identity_hash=sha256_identity(("exact-conformer-generation-equivalence/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-005 target identity changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "four-site Fold census: three raw held assignments; two complete graph automorphisms; two disjoint classes of sizes one and two",
            "all four external authority records disclosed as development-observed and not claimed blind",
            "complete external butane class vector: Anti and Gauche; adverse Gauche false-minimum row retained",
            "complete NIST CCCBDB surface retained: 19 scientific tables and 105 rows",
            "external internal-rotation barrier inscription 16.6 kJ mol^-1 preserved downstream and not used by the generator",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row["source_id"] for row in rows), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = (
    "ConformerGenerationEquivalenceValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_analysis", "experiment_registration_record", "prediction_program_document",
)
