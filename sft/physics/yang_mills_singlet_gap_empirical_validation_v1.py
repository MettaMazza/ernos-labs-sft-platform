"""Claim-specific post-seal validation of every glueball spectrum row."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
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
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.yang_mills_singlet_gap_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    PDG_HASH,
    PDG_PATH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("PDG-2026-WITHHELD-COMPLETE-GLUEBALL-BOUNDARY",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes() -> dict[str, str]:
    return {SOURCE_PATH: SOURCE_HASH, PDG_PATH: PDG_HASH}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"Yang-Mills spectrum source identity changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-yang-mills-singlet-gap-source-record/1" or record.get("source_id") != SOURCE_IDS[0]:
        raise ValueError("Yang-Mills spectrum source record identity changed")
    source = record.get("source", {})
    if source.get("snapshot_hash") != PDG_HASH or source.get("snapshot_path") != PDG_PATH:
        raise ValueError("PDG snapshot binding changed")
    target = record.get("registered_target", {})
    if target.get("theory_scope") != "pure SU(3) gauge lattice spectrum with separate full-QCD and experimental-identification caveats":
        raise ValueError("glueball theory scope changed")
    rows = target.get("precise_lattice_rows", ())
    expected_rows = (
        ("0++", "1653", "26", "lightest registered pure-gauge glueball"),
        ("2++", "2376", "32", "first registered excitation"),
        ("0-+", "2561", "40", "registered pseudoscalar excitation"),
    )
    received_rows = tuple((row.get("quantum_numbers"), row.get("mass_mev"), row.get("standard_uncertainty_mev"), row.get("role")) for row in rows)
    if received_rows != expected_rows:
        raise ValueError("complete glueball spectrum rows changed")
    required_true = (
        "all_central_masses_positive",
        "all_lower_uncertainty_edges_positive",
        "intervals_strictly_ordered_and_disjoint",
        "quenched_approximation_neglects_quark_loops",
        "glue_and_quark_antiquark_states_can_mix",
        "full_qcd_requires_dynamical_light_quarks_mixing_control_and_high_statistics",
        "pdg_reports_no_scalar_below_2_gev_as_predominantly_glueball",
    )
    if not all(target.get(key) is True for key in required_true):
        raise ValueError("glueball spectrum or limitation row changed")
    if target.get("unambiguous_experimental_glueball_identification") is not False or target.get("dimensionful_mass_selected_formal_fold_gap") is not False:
        raise ValueError("glueball identification or derivation boundary changed")
    custody = record.get("row_custody", {})
    if custody.get("pages_retained") != ["11", "12", "32"] or not all(
        custody.get(key) is True
        for key in (
            "all_three_precise_mass_rows_retained",
            "ground_and_first_excitation_order_retained",
            "quenched_scope_retained",
            "mixing_scope_retained",
            "full_qcd_limitation_retained",
            "experimental_nonidentification_retained",
            "target_inaccessible_to_prediction_program",
        )
    ) or custody.get("measurement_or_lattice_value_selects_survivor") is not False:
        raise ValueError("glueball row custody changed")
    return record


def exact_spectrum_analysis(target: dict[str, object]) -> dict[str, object]:
    rows = tuple(
        {
            "quantum_numbers": row["quantum_numbers"],
            "mass": Fraction(row["mass_mev"]),
            "uncertainty": Fraction(row["standard_uncertainty_mev"]),
            "lower": Fraction(row["mass_mev"]) - Fraction(row["standard_uncertainty_mev"]),
            "upper": Fraction(row["mass_mev"]) + Fraction(row["standard_uncertainty_mev"]),
            "role": row["role"],
        }
        for row in target["precise_lattice_rows"]
    )
    return {
        "rows": rows,
        "row_count": len(rows),
        "quantum_number_order": tuple(row["quantum_numbers"] for row in rows),
        "all_central_masses_positive": all(row["mass"] > 0 for row in rows),
        "all_lower_edges_positive": all(row["lower"] > 0 for row in rows),
        "intervals_strictly_ordered_and_disjoint": all(rows[index]["upper"] < rows[index + 1]["lower"] for index in range(len(rows) - 1)),
        "ground_state_scalar": target["ground_state_quantum_numbers"] == "0++" and rows[0]["quantum_numbers"] == "0++",
        "first_excitation_tensor": target["first_excited_state_quantum_numbers"] == "2++" and rows[1]["quantum_numbers"] == "2++",
        "scope_rows_retained": all((
            target["quenched_approximation_neglects_quark_loops"],
            target["glue_and_quark_antiquark_states_can_mix"],
            target["full_qcd_requires_dynamical_light_quarks_mixing_control_and_high_statistics"],
            target["pdg_reports_no_scalar_below_2_gev_as_predominantly_glueball"],
            target["unambiguous_experimental_glueball_identification"] is False,
            target["dimensionful_mass_selected_formal_fold_gap"] is False,
        )),
    }


class YangMillsSingletGapSpectrumValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Yang-Mills spectrum seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            TARGET_IDS,
            sealed.seal_hash,
            registration_hash,
        )
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("Yang-Mills prediction package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.family != "physical-observation" or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("Yang-Mills spectrum prediction changed")
        analysis = exact_spectrum_analysis(context[TARGET_IDS[0]])
        formal = all((
            SPEC.operational_witnesses[0][2],
            SPEC.operational_witnesses[1][2],
            SPEC.operational_witnesses[2][2],
        ))
        all_rows = analysis["row_count"] == 3 and analysis["quantum_number_order"] == ("0++", "2++", "0-+") and analysis["scope_rows_retained"]
        controls = all((
            analysis["all_central_masses_positive"],
            analysis["all_lower_edges_positive"],
            analysis["intervals_strictly_ordered_and_disjoint"],
            analysis["ground_state_scalar"],
            analysis["first_excitation_tensor"],
        ))
        tampered = dict(context[TARGET_IDS[0]])
        tampered["precise_lattice_rows"] = list(tampered["precise_lattice_rows"])
        tampered["precise_lattice_rows"][0] = dict(tampered["precise_lattice_rows"][0])
        tampered["precise_lattice_rows"][0]["mass_mev"] = "2400"
        tampered_rejected = not exact_spectrum_analysis(tampered)["intervals_strictly_ordered_and_disjoint"]
        passed = all((formal, all_rows, controls, tampered_rejected))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-yang-mills-singlet-gap-spectrum-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
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
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "seal": sealed.seal_hash,
            "prediction_seal": prediction_seal.seal_hash,
            "source_hashes": source_hashes(),
            "target_identity": target_identity,
            "analysis": analysis,
            "formal": formal,
            "all_rows": all_rows,
            "controls": controls,
            "tampered_rejected": tampered_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "The PDG 2026 source record and complete PDF are hash-locked and released only after the Fold prediction seal.",
            "All three registered pure-gauge lattice mass and uncertainty rows are retained and evaluated with exact rational inscriptions.",
            "The 0++ interval 1627-1679 MeV, 2++ interval 2344-2408 MeV and 0-+ interval 2521-2601 MeV are each strictly positive and mutually ordered without overlap.",
            "The source identifies 0++ as the lattice ground state and 2++ as the first excitation; these quantum-number labels are retained external records, not separately forced by this Fold claim.",
            "The quenched approximation, neglected quark loops, glue/quark-state mixing, full-QCD requirements and high-statistics limitation are retained.",
            "The PDG nonidentification boundary is retained: no scalar below 2 GeV is established as predominantly glueball, and no unambiguous experimental glueball is claimed.",
            "No dimensionful lattice value selects, fits or numerically identifies the exact normalized Fold gap one-third.",
            "A deliberately altered lowest-mass row breaks interval ordering and is rejected.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            all_rows,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION",
    "TARGET_IDS",
    "YangMillsSingletGapSpectrumValidator",
    "authoritative_record",
    "exact_spectrum_analysis",
    "source_hashes",
)
