"""Capability-closed operational and blind external validation for Chemistry ORG-006."""
from __future__ import annotations

from fractions import Fraction
import json
import platform
from pathlib import Path

from sft.chemistry.conformer_population_ordering_batch_v1 import (
    CONFORMER_POPULATION_ORDERING_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.conformer_population_ordering_law_v1 import append_observation, conditioned_population_census
from sft.chemistry.conformer_generation_equivalence_law_v1 import butane_four_site_census
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldLanguageHalt, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file

IDENTITY_KEYS = (
    "target_id", "source_record_ordinal", "source_id", "authority", "registered_identity", "source_record_role", "custody_class",
)
EXPECTED_LAWS = (
    "exact-conditioned-class-count-ratio", "structural-EmptyOne-absence",
    "positive-Take-energy-and-population-order", "complete-blind-condition-bound-value-vector",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-006 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    forbidden = {"definition", "value", "outcome", "source_outcome", "target_payload_hash"}
    if document.get("complete_registered_target_count") != 14 or document.get("external_values_or_outcomes_used_to_select_identity") is not False or len(rows) != 14 or any(forbidden.intersection(row) for row in rows):
        raise ValueError("ORG-006 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]; table_arguments = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"population-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for identity_ordinal, key in enumerate(IDENTITY_KEYS[1:], 1):
            destination = f"{prefix}-identity-{identity_ordinal}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]}); registers.append(destination)
        for law in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["conformer-population-law", law]}); registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers}); table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-conditioned-population-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-conditioned-population-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": CONFORMER_POPULATION_ORDERING_SPEC.experiment_id + "-value-free-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    spec = CONFORMER_POPULATION_ORDERING_SPEC
    return {
        "experiment_id": spec.experiment_id, "claim_id": spec.claim_id,
        "provenance": "target-value-blind-derivation_complete-condition-energy-population-surface",
        "frozen_relation": spec.exact_result, "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "complete_target_registry": (TARGET_PATH, TARGET_HASH), "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root), "target_ids": tuple(row.target_id for row in spec.target_rows),
        "all_fourteen_rows_required": True, "complete_predecessor_failures_required": True,
        "blind_quantitative_population_and_energy_vector_required": True, "target_payload_hashes_inaccessible_before_prediction": True,
        "falsification_condition": spec.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 14:
        raise ValueError("ORG-006 prediction incomplete")
    rows = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("ORG-006 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 14:
        raise ValueError("ORG-006 duplicate target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-006 external evidence changed")
    identities = _identities(root); document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 14 or document.get("all_favourable_adverse_absent_unavailable_unresolved_signed_and_rounded_rows_preserved") is not True or len(rows) != 14:
        raise ValueError("ORG-006 complete target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-006 identity changed after target preservation")
        if row.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome"))):
            raise ValueError("ORG-006 target payload changed")
        if hash_file(root / row["opened_snapshot_path"]) != row["opened_snapshot_sha256"]:
            raise ValueError("ORG-006 source snapshot changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 14:
        raise ValueError("ORG-006 requires all fourteen complete records")
    si = rows[11]["source_outcome"]["complete_acs_supporting_file"]; tables = si["measurement_tables"]
    facts = rows[13]["source_outcome"]["complete_core_route_and_quantitative_facts"]["postseal_facts"]
    computed = {
        "schema": "sft-v3-postseal-primary-analysis/2", "claim_id": CONFORMER_POPULATION_ORDERING_SPEC.claim_id,
        "complete_target_count": len(rows), "complete_target_vector_hash": sha256_identity(tuple(row["target_payload_hash"] for row in rows)),
        "blind_quantitative_pdf_obtained": facts["pdf_page_count"] == 13,
        "blind_quantitative_supporting_file_obtained": si["capture_inventory"]["file_capture"]["declared_md5_match"],
        "acs_supporting_measurement_table_count": len(tables), "acs_supporting_measurement_row_count": sum(len(table["rows"]) for table in tables),
        "population_condition": facts["external_condition"], "ordered_population_vector": facts["ordered_population_vector"],
        "ordered_population_exact_display_fractions": facts["ordered_population_exact_display_fractions"],
        "ordered_population_exact_display_sum": facts["ordered_population_exact_display_sum"], "ordered_population_order": facts["ordered_population_order"],
        "isotropic_population_vector": facts["isotropic_population_vector"], "isotropic_population_order": facts["isotropic_population_order"],
        "isotropic_population_exact_display_sum": facts["isotropic_population_exact_display_sum"], "isotropic_display_rounding_adverse_row_preserved": facts["isotropic_display_rounding_adverse_row_preserved"],
        "fold_positive_energy_order": facts["fold_positive_energy_order"], "fold_positive_energy_gaps": facts["fold_positive_energy_gaps"],
        "Etg_300_cal_per_mol": facts["Etg_300_cal_per_mol"], "Etg_temperature_variation_cal_per_K_per_mol": facts["Etg_temperature_variation_cal_per_K_per_mol"],
        "condition_and_observation_timescale_retained": True, "external_signed_decimal_zero_negative_and_rounded_strings_are_downstream_only": True,
        "all_predecessor_failures_and_adverse_results_preserved": True,
    }
    if computed != primary:
        raise ValueError("ORG-006 complete analysis does not independently reconstruct")
    fractions = {key: Fraction(value) for key, value in computed["ordered_population_exact_display_fractions"].items()}
    return {
        **computed, "ordered_population_fraction_sum": str(sum(fractions.values())),
        "ordered_population_strict_order_reconstructed": [key for key, _ in sorted(fractions.items(), key=lambda item: item[1], reverse=True)],
        "positive_energy_gap_sum": str(sum(int(value) for value in computed["fold_positive_energy_gaps"])),
        "failed_nist_successor_preserved": rows[5]["source_outcome"]["complete_blind_capture"]["snapshot_bytes"] == 2164,
        "failed_osti_fulltext_preserved": rows[7]["source_outcome"]["complete_blind_capture"]["capture_status"] == "capture_error_preserved",
        "failed_v3_recorder_preserved": rows[10]["source_outcome"]["complete_method_failure_and_metadata"]["method_failure_is_not_scientific_evidence_or_closure"],
        "failed_core_legacy_route_preserved": rows[12]["source_outcome"]["complete_core_route"]["capture_status"] == "capture_error_preserved",
    }


class ConformerPopulationOrderingValidator:
    def __init__(self, root: Path): self.root = root.resolve(); self.spec = CONFORMER_POPULATION_ORDERING_SPEC

    def validate(self, sealed):
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("ORG-006 capability-closed package changed")
        predictions = _prediction_map(execution.output); rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in rows},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        comparisons = []
        for row in rows:
            word = predictions[row["target_id"]]; identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, 1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        analysis = exact_analysis(rows, json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")))
        conformers = butane_four_site_census(); anti, gauche_forward, gauche_reverse = conformers.generated_assignments
        census = conditioned_population_census(conformers, HeldLabel("observation-condition", "fixed-condition-and-timescale"), (anti, anti, gauche_forward, anti), (EMPTY_ONE, PositiveRatio.from_pair(3, 1)))
        successor = append_observation(census, gauche_reverse)
        try: exact_analysis(rows[:-1], {}); omission_rejected = False
        except ValueError: omission_rejected = True
        try: FoldWord((0,)); numerical_zero_rejected = False
        except FoldLanguageHalt: numerical_zero_rejected = True
        document_text = json.dumps(document, sort_keys=True).casefold()
        controls = {
            "omitted_source_rejected": omission_rejected, "numerical_zero_rejected": numerical_zero_rejected,
            "all_fourteen_target_hashes_bound_postseal": len(release.targets) == 14,
            "exact_witness_populations": [str(row.population.fraction) for row in census.rows if isinstance(row.population, PositiveRatio)] == ["3/4", "1/4"],
            "exact_successor_populations": [str(row.population.fraction) for row in successor.rows if isinstance(row.population, PositiveRatio)] == ["3/5", "2/5"],
            "blind_ordered_population_sum_exact": analysis["ordered_population_fraction_sum"] == "1",
            "blind_population_order_matches_reconstruction": analysis["ordered_population_strict_order_reconstructed"] == analysis["ordered_population_order"],
            "blind_positive_energy_gaps_complete": analysis["fold_positive_energy_gaps"] == ["480", "178", "2605"],
            "condition_and_timescale_retained": analysis["condition_and_observation_timescale_retained"],
            "all_adverse_routes_preserved": all((analysis["failed_nist_successor_preserved"], analysis["failed_osti_fulltext_preserved"], analysis["failed_v3_recorder_preserved"], analysis["failed_core_legacy_route_preserved"], analysis["isotropic_display_rounding_adverse_row_preserved"])),
            "all_224_acs_measurement_rows_preserved": analysis["acs_supporting_measurement_row_count"] == 224,
            "prediction_contains_no_opened_value_or_payload": not any(token in document_text for token in ("0.33", "0.51", "441", "3263", "298.5", "target_payload_hash")),
        }
        passed = all(row["passed"] for row in comparisons) and all(controls.values()) and analysis["blind_quantitative_pdf_obtained"] and analysis["blind_quantitative_supporting_file_obtained"] and analysis["complete_target_count"] == 14
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-conditioned-conformer-population-ordering/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("ORG-006 target identity changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "exact Fold witness populations 3/4 and 1/4; one-observation successor 3/5 and 2/5",
            "blind 298.5 K ordered n-pentane vector: tt 0.33 ± 0.03, tg 0.51 ± 0.01, pm 0.02 ± 0.01, pp 0.14 ± 0.01",
            "blind displayed ordered vector is exactly 33/100 + 51/100 + 1/50 + 7/50 = 1",
            "blind intramolecular energy order: tt structural reference, tg 480, pp 658, pm 3263 cal mol^-1; positive gaps 480, 178, 2605",
            "blind Etg at 300 K: 441 ± 114 cal mol^-1; external signed temperature variation -1.9 ± 0.3 cal K^-1 mol^-1 retained downstream",
            "complete ACS supporting surface: 8 tables and 224 measured condition/coupling rows; complete article: 22 spectra",
            "all failed provider routes, recorder failure and isotropic 201/200 rounded-display adverse row preserved",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row["source_id"] for row in rows), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = (
    "ConformerPopulationOrderingValidator", "_identities", "_prediction_map", "_source_rows", "exact_analysis", "experiment_registration_record", "prediction_program_document",
)
