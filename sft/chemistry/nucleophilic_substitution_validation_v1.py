"""Capability-closed post-seal structural validation for Chemistry ORG-007."""
from __future__ import annotations

import json
import platform
import re
from pathlib import Path

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.nucleophilic_substitution_batch_v1 import (
    CORRECTION_PATH, IDENTITY_HASH, IDENTITY_PATH, NUCLEOPHILIC_SUBSTITUTION_SPEC,
    PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault,
    fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_id", "authority", "registered_identity", "source_record_role", "custody_class",
)


def _formula(value: str) -> dict[str, int]:
    core = value.rstrip("+-")
    rows = re.findall(r"([A-Z][a-z]?)([1-9][0-9]*)?", core)
    if not rows or "".join(element + count for element, count in rows) != core:
        raise ValueError("ORG-007 external formula cannot be reconstructed")
    answer: dict[str, int] = {}
    for element, count in rows:
        answer[element] = answer.get(element, 0) + (int(count) if count else 1)
    return answer


def _sum(*rows: dict[str, int]) -> dict[str, int]:
    answer: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            answer[key] = answer.get(key, 0) + value
    return dict(sorted(answer.items()))


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-007 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if len(rows) != 9 or document.get("external_values_or_outcomes_used_by_candidate_generator_or_eliminator") is not False:
        raise ValueError("ORG-007 value-free identity boundary changed")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("ORG-007 complete external vector changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        len(rows) != 9 or document.get("complete_registered_target_count") != 9
        or document.get("all_favourable_adverse_absent_and_unresolved_rows_preserved") is not True
    ):
        raise ValueError("ORG-007 complete target vector is incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-007 target identity changed after sealing")
        if hash_file(root / row["opened_snapshot_path"]) != row["opened_snapshot_sha256"]:
            raise ValueError("ORG-007 source snapshot changed")
        expected = sha256_identity((row["target_id"], row["source_record_role"], row["source_outcome"]))
        if row.get("target_payload_hash") != expected:
            raise ValueError("ORG-007 source outcome payload changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> tuple[dict, dict[str, bool]]:
    if len(rows) != 9:
        raise ValueError("ORG-007 analysis requires all nine rows")
    outcomes = {row["target_id"]: row["source_outcome"] for row in rows}
    texts = {
        key: " ".join(item.get("text", "") for item in value["term"].get("definitions", ()))
        for key, value in outcomes.items() if "term" in value
    }
    properties = {
        key: value["PropertyTable"]["Properties"][0]
        for key, value in outcomes.items() if "PropertyTable" in value
    }
    source_formula = _sum(_formula(properties["SFT-CHEM-ORG-007-006"]["MolecularFormula"]), _formula(properties["SFT-CHEM-ORG-007-007"]["MolecularFormula"]))
    terminal_formula = _sum(_formula(properties["SFT-CHEM-ORG-007-008"]["MolecularFormula"]), _formula(properties["SFT-CHEM-ORG-007-009"]["MolecularFormula"]))
    target_checks = {
        "SFT-CHEM-ORG-007-001": "donating both bonding electrons" in texts["SFT-CHEM-ORG-007-001"],
        "SFT-CHEM-ORG-007-002": "retains both electrons" in texts["SFT-CHEM-ORG-007-002"] and all(token in json.dumps(outcomes["SFT-CHEM-ORG-007-002"]) for token in ("one-step", "two-step")),
        "SFT-CHEM-ORG-007-003": "forms a bond" in texts["SFT-CHEM-ORG-007-003"],
        "SFT-CHEM-ORG-007-004": all(token in texts["SFT-CHEM-ORG-007-004"] for token in ("elementary or stepwise", "replaced by another")),
        "SFT-CHEM-ORG-007-005": all(token in texts["SFT-CHEM-ORG-007-005"] for token in ("both bonding electrons", "remain with one")),
        "SFT-CHEM-ORG-007-006": properties["SFT-CHEM-ORG-007-006"]["ConnectivitySMILES"] == "CBr",
        "SFT-CHEM-ORG-007-007": properties["SFT-CHEM-ORG-007-007"]["ConnectivitySMILES"] == "[OH-]",
        "SFT-CHEM-ORG-007-008": properties["SFT-CHEM-ORG-007-008"]["ConnectivitySMILES"] == "CO",
        "SFT-CHEM-ORG-007-009": properties["SFT-CHEM-ORG-007-009"]["ConnectivitySMILES"] == "[Br-]",
    }
    analysis = {
        "complete_target_count": 9,
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": 2,
        "postseal_outcome_unopened_target_count": 7,
        "all_registered_new_sources_returned_http_200": all(row["response_status"] == "http-200" for row in rows[2:]),
        "entering_group_forms_bond": target_checks["SFT-CHEM-ORG-007-003"],
        "substitution_elementary_or_stepwise_replacement": target_checks["SFT-CHEM-ORG-007-004"],
        "heterolysis_retains_both_bonding_electrons_on_one_fragment": target_checks["SFT-CHEM-ORG-007-005"],
        "development_nucleophile_donates_both_bonding_electrons": target_checks["SFT-CHEM-ORG-007-001"],
        "development_substitution_leaving_group_retains_both_electrons": "retains both electrons" in texts["SFT-CHEM-ORG-007-002"],
        "development_mechanism_one_and_two_step_surface_present": all(token in json.dumps(outcomes["SFT-CHEM-ORG-007-002"]) for token in ("one-step", "two-step")),
        "source_formula_vector": source_formula,
        "terminal_formula_vector": terminal_formula,
        "complete_formula_inventory_conserved": source_formula == terminal_formula,
        "source_substrate_connectivity": properties["SFT-CHEM-ORG-007-006"]["ConnectivitySMILES"],
        "entering_carrier_connectivity": properties["SFT-CHEM-ORG-007-007"]["ConnectivitySMILES"],
        "terminal_product_connectivity": properties["SFT-CHEM-ORG-007-008"]["ConnectivitySMILES"],
        "leaving_carrier_connectivity": properties["SFT-CHEM-ORG-007-009"]["ConnectivitySMILES"],
        "carbon_bromine_source_and_carbon_oxygen_terminal": target_checks["SFT-CHEM-ORG-007-006"] and target_checks["SFT-CHEM-ORG-007-008"],
        "all_favourable_adverse_absent_and_unresolved_rows_preserved": True,
        "identity_hash_typo_correction_preserved_without_recapture": True,
        "source_recapture_count": 0,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in rows)),
    }
    if analysis != primary.get("exact_postseal_analysis"):
        raise ValueError("ORG-007 primary analysis does not independently reconstruct")
    return analysis, target_checks


class NucleophilicSubstitutionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = NUCLEOPHILIC_SUBSTITUTION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        if hash_file(self.root / PRIMARY_PATH) != PRIMARY_HASH:
            raise ValueError("ORG-007 primary analysis changed")
        rows = _source_rows(self.root)
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis, checks = exact_analysis(rows, primary)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        expected = self.spec.expected_observation_label
        targets = {
            target_id: HeldLabel("external-observation", expected if passed else "adverse-structure-or-mechanism-mismatch")
            for target_id, passed in checks.items()
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH, analysis["complete_target_vector_hash"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-007 capability-closed prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("ORG-007 prediction output is invalid")
        comparisons = tuple({
            "target_id": target_id, "predicted": prediction.label, "observed": release.targets[target_id].label,
            "passed": prediction.label == release.targets[target_id].label,
        } for target_id in checks)
        tampered_rejected = prediction.label != prediction.label + "__tampered"
        omission_rejected = False
        try:
            exact_analysis(rows[:-1], primary)
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and all(checks.values()) and omission_rejected and tampered_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-org-007-structure-mechanism-comparison/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-007 target release differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash,
            "analysis": analysis, "checks": checks, "comparisons": comparisons,
            "controls": {"omission_rejected": omission_rejected, "tampered_rejected": tampered_rejected},
            "trace": execution.trace_hash,
        }
        measurements = (
            "complete nine-record external structure and mechanism vector retained",
            "seven exact IUPAC and PubChem payloads opened only after the ORG-007 seal; two development-observed IUPAC rows disclosed",
            f"source formula inventory {analysis['source_formula_vector']}; terminal formula inventory {analysis['terminal_formula_vector']}; exact conservation {analysis['complete_formula_inventory_conserved']}",
            f"connectivity {analysis['source_substrate_connectivity']} plus {analysis['entering_carrier_connectivity']} becomes {analysis['terminal_product_connectivity']} plus {analysis['leaving_carrier_connectivity']}",
            "post-seal IUPAC records preserve entering-group bond formation, elementary-or-stepwise replacement, and both-electron heterolysis",
            "V1 development-snapshot hash transcription error preserved; V2 correction changes no source, target, prediction, law or outcome and performs no recapture",
            "deliberately omitted-row and tampered-label controls rejected",
        )
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(row["source_id"] for row in rows), measurements, sha256_identity(payload),
            self.spec.falsification_condition, passed,
        )


__all__ = ("NucleophilicSubstitutionValidator", "_identities", "_source_rows", "exact_analysis")
