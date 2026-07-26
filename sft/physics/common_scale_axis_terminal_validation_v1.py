"""Post-seal exact comparison for the common Fold scale axis."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
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
from sft.physics.common_scale_axis_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    common_axis_certificate,
    leading_electroweak_share,
    terminal_electroweak_chain,
)


SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/common-scale-axis-source-record.json"
SOURCE_RECORD_HASH = "sha256:157f5a0e4c74b26065747d354c1f942740831524618ab21b6b44bdc672d6325f"
SOURCE_BINDINGS = (
    (
        "PDG-2026-ELECTROWEAK-SCALE-VECTOR",
        "experiments/external_sources/physics/snapshots/pdg-2026-electroweak-model.pdf",
        "sha256:a102f6252b7190dc423200271dffa7c805cd15a50391b1c578853d2f777611cb",
    ),
    (
        "PDG-2025-2026-STRONG-EM-COMPLETE-RUNNING-VECTOR",
        "experiments/external_sources/physics/snapshots/coupling-running-convergence-source-record.json",
        "sha256:b83331089d96c073fbd5101753ba5c4716ae1a8b1b891e068684b6f7246d9953",
    ),
)
INHERITED_BINDINGS = (
    (
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "claims/SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006/certificate.json",
        "sha256:f598cd663a76f8137cf2e40c5e8154083b8196ec399751da8577ce9769f688d6",
    ),
    (
        "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
        "claims/SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003/certificate.json",
        "sha256:3d93670205eb78e5f45da65574c011beb64a142bdf07cd36a2f09f97f8c93980",
    ),
    (
        "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003",
        "claims/SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003/certificate.json",
        "sha256:41ac74e37c135774d5c8b384c5fcf5aae5415c21c2a63b3d77c5a5d2981ed651",
    ),
)
SOURCE_IDS = tuple(row[0] for row in SOURCE_BINDINGS)
TARGET_IDS = ("WITHHELD-COMMON-SCALE-AND-COUPLING-COMPLETE-VECTOR",)
FALSIFICATION_CONDITION = (
    "Reject if any source or inherited receipt identity changes; if the terminal on-shell prediction leaves "
    "the registered on-shell interval; if the registered sub-W low-transfer direction is reversed; if the "
    "NuTeV adverse row, scheme distinctions, W-threshold sign change, strong/EM complete vectors or "
    "proton-Planck scale receipt are omitted; if a measured value selects a rung or law; or if target access "
    "precedes the seal."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        **{path: digest for _, path, digest in SOURCE_BINDINGS},
        **{path: digest for _, path, digest in INHERITED_BINDINGS},
    }


def exact_interval(central: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    centre = Fraction(central)
    width = Fraction(uncertainty)
    if width <= 0 or centre <= width:
        raise ValueError("scale-vector intervals must remain positive")
    return centre - width, centre + width


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"common-scale source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-common-scale-axis-source-record/1":
        raise ValueError("common-scale source schema changed")
    sources = record.get("sources", ())
    if tuple((row.get("source_id"), row.get("snapshot_path"), row.get("snapshot_hash")) for row in sources) != SOURCE_BINDINGS:
        raise ValueError("common-scale external source binding changed")
    weak = sources[0]
    schemes = weak.get("complete_scheme_rows_printed_page_23", ())
    low = weak.get("complete_explicit_low_transfer_rows_printed_page_25", ())
    if tuple(row.get("scheme") for row in schemes) != (
        "on-shell", "effective lepton angle", "MS at Z", "MS non-decoupled"
    ):
        raise ValueError("weak scheme vector changed")
    if tuple(row.get("row_id") for row in low) != (
        "NuTeV-DIS-on-shell",
        "Jefferson-Lab-Hall-A-eDIS",
        "SLAC-E158",
        "Cesium-atomic-parity-violation",
    ):
        raise ValueError("weak low-transfer vector changed")
    figure = weak.get("figure_10_1_printed_page_26", {})
    if len(figure.get("displayed_measurement_classes", ())) != 8:
        raise ValueError("complete weak-running figure classes changed")
    if figure.get("complete_figure_retained_by_snapshot_hash") is not True or figure.get("numeric_reverse_digitization_permitted") is not False:
        raise ValueError("weak-running figure custody changed")
    if not all(value is True for value in weak.get("scope_rows", {}).values()):
        raise ValueError("weak-running scope rows changed")
    inherited = record.get("inherited_admitted_evidence", ())
    if tuple((row.get("claim_id"), row.get("certificate_path"), row.get("certificate_hash")) for row in inherited) != INHERITED_BINDINGS:
        raise ValueError("inherited scale evidence binding changed")
    custody = record.get("row_custody", {})
    required_true = (
        "all_printed_weak_scheme_rows_retained",
        "all_printed_low_transfer_numeric_rows_retained",
        "complete_weak_running_figure_retained",
        "complete_inherited_strong_and_electromagnetic_vectors_retained",
        "terminal_on_shell_and_proton_Planck_receipts_retained",
        "unfavorable_and_scheme_boundaries_retained",
        "target_inaccessible_to_prediction_program",
    )
    if not all(custody.get(key) is True for key in required_true):
        raise ValueError("common-scale row custody changed")
    if custody.get("measurement_selects_scale_law") is not False:
        raise ValueError("measurement-selection boundary changed")
    inherited_running = json.loads((root / SOURCE_BINDINGS[1][1]).read_text(encoding="utf-8"))
    if inherited_running.get("record_id") != "PDG-COUPLING-RUNNING-CONVERGENCE-2025-2026":
        raise ValueError("inherited running record identity changed")
    if len(inherited_running.get("sources", ())) != 3:
        raise ValueError("inherited running source vector changed")
    if len(inherited_running["sources"][0]["table_9_1"]["complete_rows"]) != 7:
        raise ValueError("complete QCD table changed")
    if len(inherited_running["sources"][1]["table_10_1"]["complete_rows"]) != 11:
        raise ValueError("complete electromagnetic table changed")
    inherited_certificates = {}
    for claim_id, relative, _ in INHERITED_BINDINGS:
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
        if payload.get("claim_id") != claim_id or payload.get("status") != "empirically_tested_and_independently_replicated":
            raise ValueError(f"inherited certificate changed: {claim_id}")
        inherited_certificates[claim_id] = payload
    return {
        "weak_source": weak,
        "inherited_running_source": inherited_running,
        "inherited_certificates": inherited_certificates,
        "row_custody": custody,
    }


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    weak = target["weak_source"]
    schemes = {row["scheme"]: exact_interval(row["central"], row["standard_uncertainty"]) for row in weak["complete_scheme_rows_printed_page_23"]}
    low = {row["row_id"]: exact_interval(row["central"], row["standard_uncertainty"]) for row in weak["complete_explicit_low_transfer_rows_printed_page_25"]}
    terminal = terminal_electroweak_chain()["terminal_share"]
    leading_r8 = leading_electroweak_share(4)
    ms_z = schemes["MS at Z"]
    e158 = low["SLAC-E158"]
    apv = low["Cesium-atomic-parity-violation"]
    nutev = low["NuTeV-DIS-on-shell"]
    edis = low["Jefferson-Lab-Hall-A-eDIS"]
    inherited = target["inherited_certificates"]
    running = inherited["SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"]
    electroweak = inherited["SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003"]
    hierarchy = inherited["SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"]
    return {
        "scheme_intervals": schemes,
        "low_transfer_intervals": low,
        "terminal_on_shell_prediction": terminal,
        "terminal_inside_on_shell_interval": schemes["on-shell"][0] <= terminal <= schemes["on-shell"][1],
        "leading_support_eight_prediction": leading_r8,
        "leading_support_eight_inside_APV_interval": apv[0] <= leading_r8 <= apv[1],
        "E158_interval_strictly_above_MS_Z": e158[0] > ms_z[1],
        "APV_interval_strictly_above_MS_Z": apv[0] > ms_z[1],
        "eDIS_interval_overlaps_MS_Z": not (edis[1] < ms_z[0] or edis[0] > ms_z[1]),
        "NuTeV_adverse_interval_above_terminal_on_shell": nutev[0] > schemes["on-shell"][1],
        "scheme_rows_complete": len(schemes) == 4,
        "low_transfer_rows_complete": len(low) == 4,
        "figure_classes_complete": len(weak["figure_10_1_printed_page_26"]["displayed_measurement_classes"]) == 8,
        "threshold_boundary_retained": weak["scope_rows"]["above_W_sign_change_prevents_universal_monotone_claim"] is True,
        "running_certificate_passed": running.get("controls_passed") is True and running.get("all_measurement_rows_preserved") is True,
        "terminal_electroweak_certificate_passed": electroweak.get("controls_passed") is True and electroweak.get("all_measurement_rows_preserved") is True,
        "proton_Planck_certificate_passed": hierarchy.get("controls_passed") is True and hierarchy.get("all_measurement_rows_preserved") is True,
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = common_axis_certificate()
    terminal = terminal_electroweak_chain()["terminal_share"]
    leading_r8 = leading_electroweak_share(4)
    return {
        "terminal_on_shell_share": PositiveRatio.from_pair(terminal.numerator, terminal.denominator),
        "leading_support_eight_share": PositiveRatio.from_pair(leading_r8.numerator, leading_r8.denominator),
        "unit_ratio_witness": PositiveRatio.from_pair(certificate["unit_ratio_witness"].numerator, certificate["unit_ratio_witness"].denominator),
        "axis": HeldLabel("scale-axis", "One-base-binary-support-successor"),
        "terminal_transport": HeldLabel("electroweak", "support-sixteen-hold-three-return-over-seventeen"),
        "scale_translation": HeldLabel("physical-scale", "exact-ratio-before-postseal-held-reference"),
        "provenance": HeldLabel("provenance", "observational-development-explicit"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend((
        {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-exact-prediction", "instructions": instructions}


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-common-scale-axis-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "frozen_relation": (
            "The common support axis, weak squared-support curve, terminal held level thirteen, exact on-shell "
            "share, unit invariance and exact scale-ratio transport seal before any coupling or scale target opens."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_ids": SOURCE_IDS,
        "source_hashes": source_hashes(),
        "row_retention_policy": "all printed weak scheme and low-transfer rows, complete weak figure, inherited complete strong/EM vector, terminal on-shell and proton-Planck certificates, every adverse and scheme boundary",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "exact rational interval comparison, direction checks, complete row custody and inherited-receipt identity validation",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("common-scale prediction has wrong Fold shape")
    return dict(zip(keys, output.cells))


class CommonScaleAxisTerminalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong common-scale seal")
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
            sha256_identity((sealed.seal_hash, registration["frozen_relation"])),
            registration_hash,
        )
        target = authoritative_record(self.root)
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets={TARGET_IDS[0]: target},
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
            raise ValueError("common-scale hostile-package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("common-scale prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        required_true = (
            "terminal_inside_on_shell_interval",
            "leading_support_eight_inside_APV_interval",
            "E158_interval_strictly_above_MS_Z",
            "APV_interval_strictly_above_MS_Z",
            "eDIS_interval_overlaps_MS_Z",
            "NuTeV_adverse_interval_above_terminal_on_shell",
            "scheme_rows_complete",
            "low_transfer_rows_complete",
            "figure_classes_complete",
            "threshold_boundary_retained",
            "running_certificate_passed",
            "terminal_electroweak_certificate_passed",
            "proton_Planck_certificate_passed",
        )
        controls = all(analysis[key] is True for key in required_true)
        tampered = json.loads(json.dumps(context[TARGET_IDS[0]]))
        tampered["weak_source"]["complete_scheme_rows_printed_page_23"][0]["central"] = "0.24000"
        tampered["weak_source"]["complete_scheme_rows_printed_page_23"][0]["standard_uncertainty"] = "0.00001"
        tampered_rejected = not exact_measurement_analysis(tampered)["terminal_inside_on_shell_interval"]
        all_rows = all((
            analysis["scheme_rows_complete"],
            analysis["low_transfer_rows_complete"],
            analysis["figure_classes_complete"],
            len(context[TARGET_IDS[0]]["inherited_certificates"]) == 3,
        ))
        passed = all((controls, tampered_rejected, all_rows))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-common-scale-axis-comparator/1", registration_hash, FALSIFICATION_CONDITION))
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
            "all_rows": all_rows,
            "controls": controls,
            "tampered_rejected": tampered_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "The exact common axis, terminal held-support chain and scale-ratio law sealed before release of any coupling or dimensional target.",
            "The terminal on-shell weak share lies inside the complete PDG 2026 on-shell interval without a fitted rung or correction.",
            "The exact leading support-eight weak share 25/106 lies inside the complete registered cesium APV interval; this is a post-seal correspondence, not the selector of support eight.",
            "The full SLAC E158 and cesium APV intervals lie above the MS Z interval, matching the sealed sub-W descending direction.",
            "The eDIS interval overlaps the Z interval and remains non-discriminating; the NuTeV on-shell interval lies above the terminal interval and remains an explicit adverse row with its interpretation concerns.",
            "The complete PDG weak-running figure is retained by immutable source hash; no unprinted coordinates are reverse-digitized.",
            "The PDG W-threshold minimum and sign change are retained, so the finite monotone Fold branch is not overclaimed as one universal all-energy curve.",
            "The already admitted complete strong and electromagnetic multi-scale vectors, terminal electroweak comparison and proton-Planck hierarchy comparison remain hash-bound dependencies of this one-axis result.",
            "Changing the on-shell target to a disjoint interval rejects the correspondence.",
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
    "CommonScaleAxisTerminalValidator",
    "FALSIFICATION_CONDITION",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "source_hashes",
)
