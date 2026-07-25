"""Post-seal V1, admitted-prerequisite, PDG and lattice-QCD comparison for D10e."""
from __future__ import annotations

import json
import platform
from fractions import Fraction
from pathlib import Path

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
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
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.strong_field_nonlinear_fixed_point_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    field_iteration_certificate,
)

SOURCE_ID = "D10E-STRONG-FIELD-NONLINEAR-FIXED-POINT-COMPARISON"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/strong-field-nonlinear-fixed-point-source-record.json"
SOURCE_RECORD_HASH = "sha256:6f398afa78b808889b2f0e259e81500f72b5ac128aec4f4a9eefcccc12444818"
V1_PATH = "audits/v1_theorem_manifest_observation_census.json"
V1_HASH = "sha256:05c7c285e87720c0b22a69cc69b07cdd9749a1aa1728afd934e1ed9f7c30ce93"
RUNNING_PATH = "claims/SFT-PHYS-STRONG-RUNNING-DIRECTION-002/certificate.json"
RUNNING_HASH = "sha256:a561407fd117a6109e6fb84c83d466c9120213947301d2d224812bb4068801a0"
GRAVITY_PATH = "claims/SFT-PHYS-POST-NEWTONIAN-FIXED-POINT-TERMINAL-009/certificate.json"
GRAVITY_HASH = "sha256:29f075d3b8331d053f5abb96b76bc24fdc67dae44932fb7e69b22d660b3c9441"
SOURCE_PATH = "claims/SFT-PHYS-FIELD-SOURCE-RESPONSE-001/certificate.json"
SOURCE_HASH = "sha256:0e20924541239a1623e3d1cef19f39f9d51538072a9b8044adca86144ce156ed"
SECTOR_PATH = "claims/SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003/certificate.json"
SECTOR_HASH = "sha256:a3864e036aca4e2fd083fd4e99334eb450d0e41b490f04439f402a91740a67ea"
CARRIER_PATH = "claims/SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013/certificate.json"
CARRIER_HASH = "sha256:189d82acd076b6f4f729af53a9d9733f9a4f96abcd2bdf85eb09933b99608d36"
ARITHMETIC_PATH = "claims/SFT-MATH-EXACT-ARITHMETIC-001/certificate.json"
ARITHMETIC_HASH = "sha256:b82b7eaf90c6796ad85bcdf06dd999f3aabf071d9392d59b586869f4d7a87b50"
DYNAMICS_PATH = "claims/SFT-MATH-DYNAMICAL-SYSTEMS-001/certificate.json"
DYNAMICS_HASH = "sha256:055f93fc7650642070961c4e7b1feecbbd340893faa5049058f4b2cf8472b979"
MEASURED_PATH = "claims/SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001/certificate.json"
MEASURED_HASH = "sha256:f26507521a00aa23286f77949a0f3cae2baea030feff5990885357499885c476"
CUSTODY_PATH = "claims/SFT-PHYS-MEAS-TARGET-CUSTODY-001/certificate.json"
CUSTODY_HASH = "sha256:2df6f9d76ec76047ac2d244218cc132197d04b0008f6f7f6e6654d0c4ebdacde"
PDG_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-qcd.pdf"
PDG_HASH = "sha256:c04c628d76b18610c5fa2a919c6081918a25b55fb971b6af5829f4ca2baa386f"
LATTICE_PATH = "experiments/external_sources/physics/snapshots/arxiv-1902.04006-string-breaking.pdf"
LATTICE_HASH = "sha256:6c6de4ebdfc86d7976fb343a35f490ff108ab0d56dd1450a1ee27539e2641bb5"
FORMAL_COMMIT = "8638badbc9d7fce370e1ad21b0fd04fcad42da21"
TARGET_IDS = ("D10E-WITHHELD-HISTORICAL-PREREQUISITE-PDG-AND-LATTICE-RECORD",)

REQUIRED_TARGET_ROWS = (
    "v1_source_entry",
    "v1_chargeless_relation",
    "v1_gravity_relation",
    "v1_strong_relation",
    "v1_joint_discriminator",
    "existing_v3_strong_running",
    "existing_v3_gravity_fixed_point",
    "existing_v3_field_source_response",
    "existing_v3_sector_inventory",
    "existing_v3_massless_confined_carrier",
    "formal_prediction_commit_precedes_target_access",
    "formal_chargeless_correction_record",
    "formal_chargeless_fixed_point",
    "formal_gravity_fixed_point",
    "formal_gravity_corrections",
    "formal_strong_initial_source",
    "formal_strong_successor",
    "formal_strong_correction",
    "formal_strong_positive_finite_fixed_point_record",
    "formal_strong_arbitrary_positive_bound_witness",
    "formal_completed_infinity_used",
    "pdg_qcd_nonabelian_gauge_theory",
    "pdg_qcd_gluon_carries_colour_charge",
    "pdg_qcd_three_and_four_gluon_self_interactions",
    "pdg_qcd_free_quarks_observed",
    "lattice_source_identity",
    "lattice_theory",
    "lattice_gluons_only_static_energy_relation",
    "lattice_linear_growth_rate",
    "lattice_full_QCD_pair_creation",
    "lattice_full_QCD_ground_state_saturates",
    "lattice_ground_state_asymptote",
    "lattice_string_and_broken_string_mixing_required",
    "lattice_string_branch_in_breaking_region",
    "lattice_light_string_breaking_distance",
    "lattice_strange_string_breaking_distance",
    "lattice_spacing",
    "lattice_pion_mass",
    "lattice_kaon_mass",
    "lattice_single_ensemble",
    "lattice_quark_masses_are_not_physical",
    "lattice_distances_are_not_universal_physical_thresholds",
    "formal_branch_correspondence",
    "external_values_select_formal_survivor",
    "external_distances_used_as_formal_proof_scalars",
    "measured_parameter_fitted_into_v3",
    "free_strong_field_correction_added_to_v3",
)

FALSIFICATION_CONDITION = (
    "Reject if the complete V1 D10e row, an admitted prerequisite, the current PDG review or the complete primary "
    "lattice study changes or is omitted; if the exact chargeless hold, quarter-One gravitational contraction, "
    "persistent binary strong correction, empty positive finite strong fixed-point record or finite witness above "
    "every positive exact bound fails; if QCD ceases to carry non-abelian gluon self-interaction; if the unbroken "
    "string branch ceases its linear growth; if pair-created broken-string mixing and full-QCD ground-state "
    "saturation are omitted; if the single-ensemble, nonphysical-mass or non-universal-threshold limits are hidden; "
    "or if an external target selects the survivor, enters formal arithmetic, fits a parameter or adds a correction."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        V1_PATH: V1_HASH,
        RUNNING_PATH: RUNNING_HASH,
        GRAVITY_PATH: GRAVITY_HASH,
        SOURCE_PATH: SOURCE_HASH,
        SECTOR_PATH: SECTOR_HASH,
        CARRIER_PATH: CARRIER_HASH,
        ARITHMETIC_PATH: ARITHMETIC_HASH,
        DYNAMICS_PATH: DYNAMICS_HASH,
        MEASURED_PATH: MEASURED_HASH,
        CUSTODY_PATH: CUSTODY_HASH,
        PDG_PATH: PDG_HASH,
        LATTICE_PATH: LATTICE_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"D10e source changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    target = record.get("registered_target", {})
    if record.get("source_id") != SOURCE_ID or record.get("formal_prediction_commit") != FORMAL_COMMIT:
        raise ValueError("D10e source identity or pre-target formal commit changed")
    if len(record.get("snapshots", ())) != 12 or tuple(target) != REQUIRED_TARGET_ROWS or len(target) != 47:
        raise ValueError("D10e complete target row ledger changed")
    expected_claims = {
        RUNNING_PATH: "SFT-PHYS-STRONG-RUNNING-DIRECTION-002",
        GRAVITY_PATH: "SFT-PHYS-POST-NEWTONIAN-FIXED-POINT-TERMINAL-009",
        SOURCE_PATH: "SFT-PHYS-FIELD-SOURCE-RESPONSE-001",
        SECTOR_PATH: "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        CARRIER_PATH: "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
        ARITHMETIC_PATH: "SFT-MATH-EXACT-ARITHMETIC-001",
        DYNAMICS_PATH: "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        MEASURED_PATH: "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        CUSTODY_PATH: "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    }
    for relative, claim_id in expected_claims.items():
        if json.loads((root / relative).read_text(encoding="utf-8")).get("claim_id") != claim_id:
            raise ValueError("D10e prerequisite identity changed")
    v1 = json.loads((root / V1_PATH).read_text(encoding="utf-8"))
    row = next(item for item in v1["rows"] if item["v1_claim_id"] == "D10e")
    observation = row["prior_result_observation"]
    if not all(
        fragment in observation
        for fragment in (
            "strong field equation: nonlinear, self-sourced through colour",
            "convergent fixed point with shrinking corrections",
            "corrections do not shrink",
            "chargeless field is linear",
        )
    ):
        raise ValueError("D10e V1 row changed")
    if not all(
        (
            target["v1_source_entry"] == "D10e",
            target["formal_strong_successor"] == "F-plus-2",
            target["formal_strong_correction"] == "2-at-every-successor",
            target["formal_strong_positive_finite_fixed_point_record"] == "empty",
            target["formal_completed_infinity_used"] is False,
            target["pdg_qcd_nonabelian_gauge_theory"] is True,
            target["pdg_qcd_gluon_carries_colour_charge"] is True,
            target["pdg_qcd_three_and_four_gluon_self_interactions"] is True,
            target["lattice_gluons_only_static_energy_relation"] == "grows-linearly-at-asymptotically-large-separations",
            target["lattice_full_QCD_pair_creation"] is True,
            target["lattice_full_QCD_ground_state_saturates"] is True,
            target["lattice_string_and_broken_string_mixing_required"] is True,
        )
    ):
        raise ValueError("D10e formal or external structural row changed")
    custody = record.get("custody", {})
    if not all(
        (
            custody.get("formal_claim_contains_historical_or_external_target_values") is False,
            custody.get("formal_prediction_commit_precedes_external_target_access") is True,
            custody.get("target_inaccessible_during_prediction_execution") is True,
            custody.get("prediction_sealed_before_target_release_within_run") is True,
            custody.get("all_historical_prerequisite_theory_measurement_and_scope_rows_retained") is True,
            custody.get("string_branch_not_inflated_to_full_QCD_ground_state") is True,
            custody.get("lattice_thresholds_not_misreported_as_universal_physical_constants") is True,
            custody.get("targets_select_formal_survivor") is False,
        )
    ):
        raise ValueError("D10e custody or scope row changed")
    return record


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    certificate = field_iteration_certificate(12)
    return {
        "formal_neutral_hold": certificate["neutral_linear_hold"],
        "formal_neutral_correction": certificate["neutral"]["correction_record"],
        "formal_gravity_fixed_point": certificate["gravity"]["admissible_fixed_points"],
        "formal_gravity_contracts": certificate["gravity_self_source_contracts"],
        "formal_strong_initial_source": certificate["strong"]["sources"][0],
        "formal_strong_correction": certificate["strong"]["correction"],
        "formal_strong_persists": certificate["strong_self_source_persists"],
        "formal_strong_finite_fixed_point_record": certificate["strong_finite_fixed_point_record"],
        "formal_strong_no_positive_finite_fixed_point": certificate["strong_has_no_positive_finite_fixed_point"],
        "formal_strong_registered_bounds_exceeded": certificate["all_registered_bounds_exceeded"],
        "formal_completed_infinity_used": certificate["completed_infinity_used"],
        "historical_discriminator_retained": target["v1_joint_discriminator"] == "chargeless-hold-gravity-contraction-strong-persistence",
        "all_target_rows_retained": tuple(target) == REQUIRED_TARGET_ROWS and len(target) == 47,
        "pdg_self_interaction_correspondence": all(
            target[key]
            for key in (
                "pdg_qcd_nonabelian_gauge_theory",
                "pdg_qcd_gluon_carries_colour_charge",
                "pdg_qcd_three_and_four_gluon_self_interactions",
            )
        ),
        "pdg_free_quark_boundary_retained": target["pdg_qcd_free_quarks_observed"] is False,
        "lattice_unbroken_branch_correspondence": all(
            (
                target["lattice_gluons_only_static_energy_relation"] == "grows-linearly-at-asymptotically-large-separations",
                target["lattice_linear_growth_rate"] == "string-tension-sigma",
                target["lattice_string_branch_in_breaking_region"] == "V-hat-of-r-equals-V-hat-0-plus-sigma-r",
            )
        ),
        "lattice_full_ground_state_limit_retained": all(
            (
                target["lattice_full_QCD_pair_creation"],
                target["lattice_full_QCD_ground_state_saturates"],
                target["lattice_ground_state_asymptote"] == "two-noninteracting-static-light-mesons",
                target["lattice_string_and_broken_string_mixing_required"],
                target["formal_branch_correspondence"] == "persistent-Fold-self-source-corresponds-to-unbroken-string-branch-not-full-QCD-ground-state",
            )
        ),
        "lattice_values_retained": tuple(
            target[key]
            for key in (
                "lattice_light_string_breaking_distance",
                "lattice_strange_string_breaking_distance",
                "lattice_spacing",
                "lattice_pion_mass",
                "lattice_kaon_mass",
            )
        ),
        "lattice_limits_retained": all(
            (
                target["lattice_single_ensemble"],
                target["lattice_quark_masses_are_not_physical"],
                target["lattice_distances_are_not_universal_physical_thresholds"],
            )
        ),
        "external_values_select_formal_survivor": target["external_values_select_formal_survivor"],
        "external_distances_used_as_formal_proof": target["external_distances_used_as_formal_proof_scalars"],
        "fitted_value_used": target["measured_parameter_fitted_into_v3"],
        "free_correction_used": target["free_strong_field_correction_added_to_v3"],
    }


def formal_prediction_inputs() -> dict[str, object]:
    return {
        "chargeless_relation": HeldLabel("chargeless-source", "empty-correction-and-held-One"),
        "gravity_relation": HeldLabel("gravity-self-source", "unique-quarter-One-fixed-point-with-shrinking-corrections"),
        "strong_update_relation": HeldLabel("colour-self-source", "each-successor-retains-F-and-appends-complete-binary-carrier"),
        "strong_fixed_relation": HeldLabel("strong-finite-fixed-point", "empty-for-every-positive-exact-finite-F-by-F-plus-two-order"),
        "strong_bound_relation": HeldLabel("strong-confinement", "finite-witness-above-every-positive-exact-finite-bound"),
        "scope_relation": HeldLabel("strong-field-scope", "persistent-self-source-branch-without-completed-infinity"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend(
        (
            {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-exact-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-strong-field-nonlinear-fixed-point-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "formal_prediction_commit": FORMAL_COMMIT,
        "frozen_relation": "Chargeless hold, gravitational quarter-One contraction and colour self-source F-plus-two persistence uniquely separate the three field-update classes; the strong branch has no positive finite fixed point and exceeds every positive exact finite bound at a generated witness.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": "complete V1 D10e row, nine admitted prerequisites, complete current PDG QCD review, complete primary lattice-QCD study and all forty-seven favourable and scope-limiting rows",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "independent exact-rational Fold reconstruction followed by structural QCD and uncertainty-retaining lattice string-branch comparison",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("D10e prediction shape changed")
    return dict(zip(keys, output.cells))


class StrongFieldNonlinearFixedPointValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong D10e seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        keys = tuple(inputs)
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {key: sha256_identity(value) for key, value in inputs.items()},
            TARGET_IDS,
            sha256_identity((sealed.seal_hash, registration["frozen_relation"], FORMAL_COMMIT)),
            registration_hash,
        )
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("D10e hostile audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("D10e prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        formal = all(
            (
                analysis["formal_neutral_hold"],
                analysis["formal_neutral_correction"] == (),
                analysis["formal_gravity_fixed_point"] == (Fraction(1, 4),),
                analysis["formal_gravity_contracts"],
                analysis["formal_strong_initial_source"] == Fraction(1, 1),
                analysis["formal_strong_correction"] == Fraction(2, 1),
                analysis["formal_strong_persists"],
                analysis["formal_strong_finite_fixed_point_record"] == (),
                analysis["formal_strong_no_positive_finite_fixed_point"],
                analysis["formal_strong_registered_bounds_exceeded"],
                analysis["formal_completed_infinity_used"] is False,
            )
        )
        rows = analysis["all_target_rows_retained"] and len(analysis["lattice_values_retained"]) == 5
        controls = all(
            (
                analysis["historical_discriminator_retained"],
                analysis["pdg_self_interaction_correspondence"],
                analysis["pdg_free_quark_boundary_retained"],
                analysis["lattice_unbroken_branch_correspondence"],
                analysis["lattice_full_ground_state_limit_retained"],
                analysis["lattice_limits_retained"],
                analysis["external_values_select_formal_survivor"] is False,
                analysis["external_distances_used_as_formal_proof"] is False,
                analysis["fitted_value_used"] is False,
                analysis["free_correction_used"] is False,
            )
        )
        passed = all((formal, rows, controls))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparison_hash = sha256_identity(
            ("exact-strong-field-nonlinear-fixed-point-comparator/1", registration_hash, FALSIFICATION_CONDITION)
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=interpreter_hash,
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=comparison_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
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
            "seal": sealed.seal_hash,
            "formal_commit": FORMAL_COMMIT,
            "prediction_seal": prediction_seal.seal_hash,
            "sources": source_hashes(),
            "target": target_identity,
            "analysis": analysis,
            "formal": formal,
            "rows": rows,
            "controls": controls,
        }
        measurements = (
            "The complete V1 D10e row, nine admitted prerequisites, the complete current PDG QCD review and complete primary lattice-QCD paper are hash-locked and released only after the frozen V3 commit and in-run prediction seal.",
            "V3 independently forces an empty chargeless correction with held One source, the admitted gravity quarter-One fixed point with shrinking corrections, and a colour self-source successor F plus two with the exact binary correction retained at every successor.",
            "For every positive exact finite F, F plus two is strictly above F, so the strong positive finite fixed-point record is empty; for every positive exact finite bound, the same law constructs a finite source witness above it without a completed infinity.",
            "The PDG QCD review independently retains non-abelian colour, colour-bearing gluons, three- and four-gluon self-interactions and the absence of observed free quarks.",
            "The lattice study independently reports that the gluons-only static energy grows linearly at asymptotically large separation with string tension sigma and models the unbroken string state as V-hat(r)=V-hat-0+sigma*r in the breaking region.",
            "The same study observes the required adverse boundary: dynamical light-quark pair creation mixes the string with broken-string states, and the full-QCD ground state tends to two noninteracting static-light mesons rather than growing without bound.",
            "The reported light and strange breaking distances, 1.224(15) fm and 1.293(16) fm, are retained with lattice spacing 0.06426(76) fm and the 280 MeV pion and 460 MeV kaon masses.",
            "Those distances come from one ensemble with nonphysical quark masses and are not promoted to universal physical constants; they neither select the Fold survivor nor enter its formal arithmetic.",
            "The exact correspondence is therefore branchwise: persistent Fold colour self-source matches the unbroken string branch, while pair-created state mixing supplies a distinct full-QCD saturation channel that the validation retains explicitly.",
            "No external value fits a parameter, supplies a free correction or changes the frozen generated grammar.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            rows,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "StrongFieldNonlinearFixedPointValidator",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
)
