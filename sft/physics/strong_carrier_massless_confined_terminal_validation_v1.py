"""Post-seal V1, prerequisite and current PDG comparison for D10f."""
from __future__ import annotations

from fractions import Fraction
import json
import platform
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
from sft.physics.strong_carrier_massless_confined_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    simultaneous_carrier_certificate,
)

SOURCE_ID = "D10F-STRONG-CARRIER-MASSLESS-CONFINED-COMPARISON"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/strong-carrier-massless-confined-source-record.json"
SOURCE_RECORD_HASH = "sha256:0e78e607dae7721adae01f99f79ea24ea6d38569abfd19c94413aaadca9550cc"
V1_PATH = "audits/v1_theorem_manifest_observation_census.json"
V1_HASH = "sha256:05c7c285e87720c0b22a69cc69b07cdd9749a1aa1728afd934e1ed9f7c30ce93"
SECTOR_PATH = "claims/SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003/certificate.json"
SECTOR_HASH = "sha256:a3864e036aca4e2fd083fd4e99334eb450d0e41b490f04439f402a91740a67ea"
RUNNING_PATH = "claims/SFT-PHYS-STRONG-RUNNING-DIRECTION-002/certificate.json"
RUNNING_HASH = "sha256:a561407fd117a6109e6fb84c83d466c9120213947301d2d224812bb4068801a0"
INTERVAL_PATH = "claims/SFT-PHYS-SPACETIME-EXACT-INTERVAL-003/certificate.json"
INTERVAL_HASH = "sha256:af3c471a117b27824fc66dcf53eb5fac205f4485389805c5613a260d3e3cad41"
WAVE_PATH = "claims/SFT-PHYS-WAVE-EXACT-OPERATIONS-003/certificate.json"
WAVE_HASH = "sha256:1919bf9175f3aebbf62fd630b7853b65b5da0f4949048d215ce2cdbb1f69440e"
RANGE_PATH = "claims/SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005/certificate.json"
RANGE_HASH = "sha256:6bf9067bb86ea1a522075a097e13ca867bef76e4a9e98e8c2d1f19b2330d039e"
HADRON_PATH = "claims/SFT-PHYS-MATTER-COMPOSITE-HADRONS-001/certificate.json"
HADRON_HASH = "sha256:e38e1be56e5ae4cdcf51d491f269ceb2c245b7ef7aee4e6fbb181328eb2bdb6b"
SOURCE_PATH = "claims/SFT-PHYS-FIELD-CONSERVED-SOURCE-001/certificate.json"
SOURCE_HASH = "sha256:9e78df61ebe776423956367e08d714261f56f0b55a58b579a768270bd0000937"
ARITHMETIC_PATH = "claims/SFT-MATH-EXACT-ARITHMETIC-001/certificate.json"
ARITHMETIC_HASH = "sha256:b82b7eaf90c6796ad85bcdf06dd999f3aabf071d9392d59b586869f4d7a87b50"
MEASURED_PATH = "claims/SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001/certificate.json"
MEASURED_HASH = "sha256:f26507521a00aa23286f77949a0f3cae2baea030feff5990885357499885c476"
CUSTODY_PATH = "claims/SFT-PHYS-MEAS-TARGET-CUSTODY-001/certificate.json"
CUSTODY_HASH = "sha256:2df6f9d76ec76047ac2d244218cc132197d04b0008f6f7f6e6654d0c4ebdacde"
PDG_GLUON_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-gluon-listing.pdf"
PDG_GLUON_HASH = "sha256:fcc152780d2efb6cb66d2f9351abd034d30cab0e914fd87a0daee46a0344353d"
PDG_QCD_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-qcd.pdf"
PDG_QCD_HASH = "sha256:c04c628d76b18610c5fa2a919c6081918a25b55fb971b6af5829f4ca2baa386f"
PDG_QUARK_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-quark-model.pdf"
PDG_QUARK_HASH = "sha256:6aa98fa53857122f27b638c59081af1a2857d787c4205370d8fa38fcb6b70ff0"
FORMAL_COMMIT = "5cc20feeaa53a7ecfba3208a2f60f70af36c3d4a"
TARGET_IDS = ("D10F-WITHHELD-HISTORICAL-PREREQUISITE-AND-PDG-RECORD",)

REQUIRED_TARGET_ROWS = (
    "v1_source_entry",
    "v1_mass_relation",
    "v1_causal_relation",
    "v1_confinement_relation",
    "v1_joint_relation",
    "existing_v3_sector_inventory",
    "existing_v3_self_source",
    "existing_v3_empty_mass_boundary",
    "existing_v3_One_speed_operation",
    "existing_v3_finite_range_control",
    "existing_v3_colour_neutral_composites",
    "existing_v3_conserved_source",
    "formal_prediction_commit_precedes_target_access",
    "formal_colour_labels",
    "formal_nonsinglet_carrier_count",
    "formal_mass_record",
    "formal_causal_speed",
    "formal_tube_width",
    "formal_separation_work_successor",
    "formal_isolated_colour_record",
    "pdg_gluon_listing_identity",
    "pdg_gluon_colour_representation",
    "pdg_gluon_mass_value",
    "pdg_gluon_mass_value_classification",
    "pdg_gluon_mass_caveat",
    "pdg_qcd_colour_count",
    "pdg_qcd_gluon_count",
    "pdg_qcd_gluon_representation",
    "pdg_qcd_nonlinear_field_term_present",
    "pdg_qcd_three_gluon_vertex_present",
    "pdg_qcd_four_gluon_vertex_present",
    "pdg_qcd_free_quarks_or_gluons_observed",
    "pdg_qcd_hadrons_are_colour_singlets",
    "pdg_measured_CA",
    "pdg_expected_CA",
    "pdg_measured_CF",
    "pdg_expected_CF",
    "pdg_CA_CF_correlation",
    "pdg_colour_factor_assessment",
    "pdg_gluon_jet_evidence",
    "pdg_quark_model_confinement_status",
    "pdg_physical_state_boundary",
    "pdg_permanent_colour_confinement_status",
    "direct_free_gluon_time_of_flight_measurement_available",
    "external_values_select_formal_survivor",
    "external_mass_value_used_as_formal_proof_scalar",
    "measured_parameter_fitted_into_v3",
    "free_carrier_correction_added_to_v3",
)

FALSIFICATION_CONDITION = (
    "Reject if the V1 D10f row, any admitted prerequisite or any complete PDG source changes or is omitted; if "
    "three colour labels, eight non-singlet carriers, empty mass/rest-capture, One-cell-per-tick propagation, "
    "self-source, fixed half-One tube, positive two-thirds work successor or empty isolated-colour record fails; "
    "if the PDG theoretical m=0 listing is misreported as a direct measurement or its few-MeV caveat is omitted; "
    "if measured colour-factor intervals cease to contain their published SU(3) expectations; if a free coloured "
    "state is observed; or if any external value selects the survivor, becomes a formal proof scalar, is fitted, "
    "or supplies a free correction."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        V1_PATH: V1_HASH,
        SECTOR_PATH: SECTOR_HASH,
        RUNNING_PATH: RUNNING_HASH,
        INTERVAL_PATH: INTERVAL_HASH,
        WAVE_PATH: WAVE_HASH,
        RANGE_PATH: RANGE_HASH,
        HADRON_PATH: HADRON_HASH,
        SOURCE_PATH: SOURCE_HASH,
        ARITHMETIC_PATH: ARITHMETIC_HASH,
        MEASURED_PATH: MEASURED_HASH,
        CUSTODY_PATH: CUSTODY_HASH,
        PDG_GLUON_PATH: PDG_GLUON_HASH,
        PDG_QCD_PATH: PDG_QCD_HASH,
        PDG_QUARK_PATH: PDG_QUARK_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"D10f source changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    target = record.get("registered_target", {})
    if record.get("source_id") != SOURCE_ID or record.get("formal_prediction_commit") != FORMAL_COMMIT:
        raise ValueError("D10f source identity or pre-target formal commit changed")
    if len(record.get("snapshots", ())) != 14 or tuple(target) != REQUIRED_TARGET_ROWS or len(target) != 48:
        raise ValueError("D10f complete target row ledger changed")
    if not all(
        (
            target["v1_source_entry"] == "D10f",
            target["v1_joint_relation"] == "masslessness-and-confinement-coexist",
            target["formal_prediction_commit_precedes_target_access"] is True,
            target["formal_colour_labels"] == "3",
            target["formal_nonsinglet_carrier_count"] == "8",
            target["formal_mass_record"] == "empty",
            target["formal_causal_speed"] == "One-support-cell-per-tick",
            target["formal_tube_width"] == "half-One",
            target["formal_separation_work_successor"] == "two-thirds",
            target["formal_isolated_colour_record"] == "empty",
        )
    ):
        raise ValueError("D10f historical or formal target row changed")
    if not all(
        (
            target["pdg_gluon_colour_representation"] == "SU(3)-color-octet",
            target["pdg_gluon_mass_value"] == "m=0",
            target["pdg_gluon_mass_value_classification"] == "theoretical-value",
            target["pdg_gluon_mass_caveat"] == "mass-as-large-as-a-few-MeV-may-not-be-precluded",
            target["pdg_qcd_colour_count"] == "Nc=3",
            target["pdg_qcd_gluon_count"] == "Nc-squared-minus-1=8",
            target["pdg_qcd_gluon_representation"] == "adjoint-SU(3)",
            target["pdg_qcd_nonlinear_field_term_present"] is True,
            target["pdg_qcd_three_gluon_vertex_present"] is True,
            target["pdg_qcd_four_gluon_vertex_present"] is True,
            target["pdg_qcd_free_quarks_or_gluons_observed"] is False,
            target["pdg_qcd_hadrons_are_colour_singlets"] is True,
        )
    ):
        raise ValueError("D10f PDG structure or mass row changed")
    expected_claims = {
        SECTOR_PATH: "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        RUNNING_PATH: "SFT-PHYS-STRONG-RUNNING-DIRECTION-002",
        INTERVAL_PATH: "SFT-PHYS-SPACETIME-EXACT-INTERVAL-003",
        WAVE_PATH: "SFT-PHYS-WAVE-EXACT-OPERATIONS-003",
        RANGE_PATH: "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
        HADRON_PATH: "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        SOURCE_PATH: "SFT-PHYS-FIELD-CONSERVED-SOURCE-001",
        ARITHMETIC_PATH: "SFT-MATH-EXACT-ARITHMETIC-001",
        MEASURED_PATH: "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        CUSTODY_PATH: "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    }
    for relative, claim_id in expected_claims.items():
        if json.loads((root / relative).read_text(encoding="utf-8")).get("claim_id") != claim_id:
            raise ValueError("D10f prerequisite changed")
    v1 = json.loads((root / V1_PATH).read_text(encoding="utf-8"))
    row = next(item for item in v1["rows"] if item["v1_claim_id"] == "D10f")
    observation = row["prior_result_observation"]
    if not all(
        fragment in observation
        for fragment in (
            "strong carrier is massless (luminal) yet confining",
            "strong carrier acquires no mass-part",
            "self-coupling forms a confining flux tube",
            "masslessness and confinement coexist",
        )
    ):
        raise ValueError("D10f V1 row changed")
    custody = record.get("custody", {})
    if not all(
        (
            custody.get("formal_claim_contains_historical_or_external_target_values") is False,
            custody.get("formal_prediction_commit_precedes_external_target_access") is True,
            custody.get("target_inaccessible_during_prediction_execution") is True,
            custody.get("prediction_sealed_before_target_release_within_run") is True,
            custody.get("all_historical_prerequisite_theory_measurement_and_scope_rows_retained") is True,
            custody.get("pdg_theoretical_mass_value_not_misreported_as_direct_measurement") is True,
            custody.get("targets_select_formal_survivor") is False,
        )
    ):
        raise ValueError("D10f custody changed")
    return record


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    certificate = simultaneous_carrier_certificate(32)
    measured_ca = Fraction(289, 100)
    ca_stat = Fraction(3, 100)
    ca_syst = Fraction(21, 100)
    expected_ca = Fraction(3, 1)
    measured_cf = Fraction(13, 10)
    cf_stat = Fraction(1, 100)
    cf_syst = Fraction(9, 100)
    expected_cf = Fraction(4, 3)
    ca_boundary = ca_stat + ca_syst
    cf_boundary = cf_stat + cf_syst
    prerequisite_keys = (
        "existing_v3_sector_inventory",
        "existing_v3_self_source",
        "existing_v3_empty_mass_boundary",
        "existing_v3_One_speed_operation",
        "existing_v3_finite_range_control",
        "existing_v3_colour_neutral_composites",
        "existing_v3_conserved_source",
    )
    scope_keys = (
        "pdg_gluon_mass_value_classification",
        "pdg_gluon_mass_caveat",
        "pdg_quark_model_confinement_status",
        "pdg_permanent_colour_confinement_status",
        "direct_free_gluon_time_of_flight_measurement_available",
    )
    return {
        "formal_colour_labels": certificate["structure"]["charge_labels"],
        "formal_carrier_count": certificate["structure"]["mediator_count"],
        "formal_coupling": certificate["structure"]["coupling"],
        "formal_mass_record": certificate["structure"]["mass_label"],
        "formal_One_speed": certificate["causal"]["causal_speed"],
        "formal_phase_retained": certificate["causal"]["phase_retained"],
        "formal_tube_width": certificate["tube"]["tube_width"],
        "formal_work_successor": certificate["tube"]["work_increment"],
        "formal_arbitrary_bounds_exceeded": certificate["all_registered_bounds_exceeded"],
        "formal_isolated_colour_record": certificate["tube"]["isolated_colour_carrier_record"],
        "formal_joint_law": certificate["simultaneously_massless_and_One_speed"] and certificate["simultaneously_confined"],
        "historical_joint_relation_retained": target["v1_joint_relation"] == "masslessness-and-confinement-coexist",
        "prerequisite_rows_retained": tuple(target[key] for key in prerequisite_keys),
        "scope_rows_retained": tuple(target[key] for key in scope_keys),
        "all_target_rows_retained": tuple(target) == REQUIRED_TARGET_ROWS and len(target) == 48,
        "pdg_three_eight_correspondence": target["pdg_qcd_colour_count"] == "Nc=3" and target["pdg_qcd_gluon_count"] == "Nc-squared-minus-1=8",
        "pdg_massless_classification_correspondence": target["pdg_gluon_mass_value"] == "m=0",
        "pdg_mass_value_is_theoretical_not_direct_measurement": target["pdg_gluon_mass_value_classification"] == "theoretical-value",
        "pdg_mass_caveat_retained": target["pdg_gluon_mass_caveat"] == "mass-as-large-as-a-few-MeV-may-not-be-precluded",
        "pdg_self_source_correspondence": target["pdg_qcd_nonlinear_field_term_present"] and target["pdg_qcd_three_gluon_vertex_present"] and target["pdg_qcd_four_gluon_vertex_present"],
        "pdg_confinement_correspondence": target["pdg_qcd_free_quarks_or_gluons_observed"] is False and target["pdg_qcd_hadrons_are_colour_singlets"] is True,
        "pdg_gluon_jet_evidence_retained": target["pdg_gluon_jet_evidence"] == "clear-experimental-evidence-for-softer-broader-gluon-jets",
        "measured_CA": measured_ca,
        "measured_CA_conservative_boundary": ca_boundary,
        "expected_CA": expected_ca,
        "measured_CA_contains_expected": abs(expected_ca - measured_ca) <= ca_boundary,
        "measured_CF": measured_cf,
        "measured_CF_conservative_boundary": cf_boundary,
        "expected_CF": expected_cf,
        "measured_CF_contains_expected": abs(expected_cf - measured_cf) <= cf_boundary,
        "colour_factor_values_used_as_formal_proof": False,
        "direct_free_gluon_time_of_flight_available": target["direct_free_gluon_time_of_flight_measurement_available"],
        "external_values_select_formal_survivor": target["external_values_select_formal_survivor"],
        "external_mass_value_used_as_formal_proof": target["external_mass_value_used_as_formal_proof_scalar"],
        "fitted_value_used": target["measured_parameter_fitted_into_v3"],
        "free_correction_used": target["free_carrier_correction_added_to_v3"],
    }


def formal_prediction_inputs() -> dict[str, object]:
    return {
        "sector_relation": HeldLabel("strong-sector", "three-colour-labels-and-eight-nonsinglet-carriers"),
        "mass_relation": HeldLabel("strong-carrier-mass", "empty-mass-and-rest-capture-record"),
        "causal_relation": HeldLabel("strong-carrier-causal", "One-support-cell-per-tick-with-retained-phase"),
        "self_source_relation": HeldLabel("strong-carrier-self-source", "colour-carrying-mediator-resources-own-channel"),
        "tube_relation": HeldLabel("strong-carrier-tube", "fixed-half-One-width-and-two-thirds-work-successor"),
        "composition_relation": HeldLabel("strong-carrier-composition", "local-massless-and-asymptotic-confined-records-coexist"),
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
        "schema": "sft-v3-strong-carrier-massless-confined-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "formal_prediction_commit": FORMAL_COMMIT,
        "frozen_relation": "Three colour labels and eight carriers, empty mass/rest-capture, One-cell phase propagation, colour self-source, fixed half-One tube and positive two-thirds work successor jointly force local masslessness and asymptotic confinement.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": "complete V1 row, ten admitted prerequisites, three complete current PDG sources and all forty-eight favourable, theoretical, empirical and limiting rows",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "independent exact Fold reconstruction followed by exact comparison with PDG structural classifications and conservative rational intervals for measured colour factors",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("D10f prediction shape changed")
    return dict(zip(keys, output.cells))


class StrongCarrierMasslessConfinedValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong D10f seal")
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
            raise ValueError("D10f hostile audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("D10f prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        formal = all(
            (
                analysis["formal_colour_labels"] == 3,
                analysis["formal_carrier_count"] == 8,
                analysis["formal_coupling"] == Fraction(2, 3),
                analysis["formal_mass_record"] == (),
                analysis["formal_One_speed"] == Fraction(1, 1),
                analysis["formal_phase_retained"],
                analysis["formal_tube_width"] == Fraction(1, 2),
                analysis["formal_work_successor"] == Fraction(2, 3),
                analysis["formal_arbitrary_bounds_exceeded"],
                analysis["formal_isolated_colour_record"] == (),
                analysis["formal_joint_law"],
            )
        )
        rows = all(
            (
                analysis["all_target_rows_retained"],
                len(analysis["prerequisite_rows_retained"]) == 7,
                len(analysis["scope_rows_retained"]) == 5,
            )
        )
        controls = all(
            (
                analysis["historical_joint_relation_retained"],
                analysis["pdg_three_eight_correspondence"],
                analysis["pdg_massless_classification_correspondence"],
                analysis["pdg_mass_value_is_theoretical_not_direct_measurement"],
                analysis["pdg_mass_caveat_retained"],
                analysis["pdg_self_source_correspondence"],
                analysis["pdg_confinement_correspondence"],
                analysis["pdg_gluon_jet_evidence_retained"],
                analysis["measured_CA_contains_expected"],
                analysis["measured_CF_contains_expected"],
                analysis["colour_factor_values_used_as_formal_proof"] is False,
                analysis["direct_free_gluon_time_of_flight_available"] is False,
                analysis["external_values_select_formal_survivor"] is False,
                analysis["external_mass_value_used_as_formal_proof"] is False,
                analysis["fitted_value_used"] is False,
                analysis["free_correction_used"] is False,
            )
        )
        passed = all((formal, rows, controls))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparison_hash = sha256_identity(
            ("exact-strong-carrier-massless-confined-comparator/1", registration_hash, FALSIFICATION_CONDITION)
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
            "The complete V1 D10f row, ten admitted prerequisite certificates and three complete current PDG sources are hash-locked and released only after the V3 formal commit and in-run prediction seal.",
            "V3 independently forces three colour labels, eight non-singlet carriers, empty mass and rest-capture records, retained phase advancing one support cell per tick, and no fitted propagation value.",
            "The same colour-bearing carrier self-sources a fixed half-One tube whose exact separation work increases by two-thirds at every successor and exceeds every positive exact bound at a finite witness.",
            "The PDG gluon listing records an SU(3) colour octet and m=0, matching the frozen structural classification after release.",
            "The PDG explicitly classifies m=0 as a theoretical value and says a mass as large as a few MeV may not be precluded; this qualification is retained and no direct free-gluon time-of-flight measurement is claimed.",
            "The PDG QCD review records Nc=3, Nc-squared-minus-One=8, the adjoint gluon representation, nonlinear field term, three-gluon vertex and four-gluon vertex.",
            "The same review states that neither quarks nor gluons are observed as free particles and that hadrons are colour-singlet combinations, matching the frozen asymptotic observation boundary.",
            "Collider colour-factor measurements CA=2.89+/-0.03(stat)+/-0.21(syst) and CF=1.30+/-0.01(stat)+/-0.09(syst) contain the published SU(3) expectations 3 and 4/3 within exact conservative summed uncertainty boundaries.",
            "The PDG also records clear experimental evidence that gluon jets are softer and broader than light-quark jets; the quark-model review describes physical states as colour singlets and colour as believed permanently confined.",
            "External measurements and classifications test only the already sealed result: they do not select its survivor, enter its proof arithmetic, fit a parameter or add a carrier correction.",
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
    "StrongCarrierMasslessConfinedValidator",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
)
