"""Target-inaccessible exact comparison for the terminal proton-radius law."""

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
from sft.physics.proton_radius_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    leading_radius_multiplier,
    structural_formula_census,
    terminal_radius_coefficient,
)


SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/proton-radius-terminal-source-record.json"
SOURCE_RECORD_HASH = "sha256:6bdbbef14cd8fc40d408028ba06911692f7b7c871b7214c038d51e33ed2118a1"
SOURCE_BINDINGS = (
    (
        "NATURE-2026-ELECTRONIC-HYDROGEN-PROTON-RADIUS",
        "experiments/external_sources/physics/snapshots/nature-2026-proton-radius-electronic.pdf",
        "sha256:834ddf04fdb3064d07307cc743544990e086601948903fb73390144d2a3ae253",
    ),
    (
        "NATURE-2019-PRAD-PROTON-RADIUS",
        "experiments/external_sources/physics/snapshots/arxiv-1902.08185-prad-proton-radius.pdf",
        "sha256:66925b870f8391be1a940b741ff60322877df7551cfa1db58b59add002e15ad5",
    ),
    (
        "NIST-CODATA-2022",
        "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt",
        "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    ),
    (
        "NIST-CODATA-2014-HISTORICAL",
        "experiments/external_sources/physics/snapshots/nist-codata-2014-all.pdf",
        "sha256:48c31408c79d3a9aa7c16efdbf5ef729d8ad162f2b9dbb8029d4d8cdcbef3568",
    ),
)
SOURCE_IDS = tuple(row[0] for row in SOURCE_BINDINGS)
TARGET_IDS = ("WITHHELD-PROTON-RADIUS-COMPLETE-VECTOR",)
FALSIFICATION_CONDITION = (
    "Reject if any source identity or registered row changes; if the exact terminal prediction leaves any "
    "registered current electronic, muonic, CODATA or outward PRad interval; if the historical CODATA-2014 "
    "conflict or current extraction limitations are omitted; if a probe, radius or Compton value enters "
    "before sealing; if observation is claimed to select ten charge cells; or if target access precedes the seal."
)


def source_hashes() -> dict[str, str]:
    return {SOURCE_RECORD_PATH: SOURCE_RECORD_HASH, **{path: digest for _, path, digest in SOURCE_BINDINGS}}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"proton-radius source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-proton-radius-terminal-source-record/1":
        raise ValueError("proton-radius source record schema changed")
    bindings = tuple(
        (row.get("source_id"), row.get("snapshot_path"), row.get("snapshot_hash"))
        for row in record.get("sources", ())
    )
    if bindings != SOURCE_BINDINGS:
        raise ValueError("proton-radius source bindings changed")
    target = record.get("registered_target", {})
    if target.get("dimension_scale") != {
        "quantity": "reduced proton Compton wavelength",
        "value_fm": "0.210308910051",
        "standard_uncertainty_fm": "0.000000000066",
        "source_id": "NIST-CODATA-2022",
    }:
        raise ValueError("proton-radius scale row changed")
    current = target.get("current_radius_rows", ())
    historical = target.get("historical_adverse_rows", ())
    if len(current) != 4 or len(historical) != 1:
        raise ValueError("proton-radius target row count changed")
    if tuple(row.get("row_id") for row in current) != (
        "electronic-hydrogen-2S-6P-2026",
        "muonic-hydrogen-current-reference",
        "codata-2022-global-adjustment",
        "PRad-electron-proton-scattering-2019",
    ):
        raise ValueError("proton-radius current target identities changed")
    if historical[0].get("row_id") != "codata-2014-global-adjustment":
        raise ValueError("proton-radius historical target identity changed")
    scope = target.get("scope_rows", {})
    if len(scope) != 6 or not all(value is True for value in scope.values()):
        raise ValueError("proton-radius scope rows changed")
    custody = record.get("row_custody", {})
    required_true = (
        "complete_current_electronic_and_muonic_rows_retained",
        "complete_current_CODATA_row_retained",
        "PRad_statistical_and_systematic_uncertainties_retained_separately",
        "historical_unfavorable_CODATA_row_retained",
        "current_discrepancy_and_scattering_analysis_limits_retained",
        "reduced_Compton_scale_and_uncertainty_retained",
        "target_inaccessible_to_prediction_program",
    )
    if not all(custody.get(key) is True for key in required_true):
        raise ValueError("proton-radius custody rows changed")
    if custody.get("measurement_selects_formula") is not False or custody.get("precision_widening_permitted") is not False:
        raise ValueError("proton-radius adverse custody rows changed")
    return record


def exact_interval(value: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    centre, width = Fraction(value), Fraction(uncertainty)
    if centre <= width or width <= 0:
        raise ValueError("radius interval must remain strictly positive")
    return centre - width, centre + width


def interval_contains(container: tuple[Fraction, Fraction], contained: tuple[Fraction, Fraction]) -> bool:
    return container[0] <= contained[0] <= contained[1] <= container[1]


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    scale = target["dimension_scale"]
    scale_interval = exact_interval(scale["value_fm"], scale["standard_uncertainty_fm"])
    coefficient = terminal_radius_coefficient()
    leading = leading_radius_multiplier()
    predicted = tuple(edge * coefficient for edge in scale_interval)
    predicted_centre = Fraction(scale["value_fm"]) * coefficient
    leading_interval = tuple(edge * leading for edge in scale_interval)
    current_intervals: dict[str, tuple[Fraction, Fraction]] = {}
    for row in target["current_radius_rows"]:
        if row["row_id"] == "PRad-electron-proton-scattering-2019":
            width = Fraction(row["statistical_uncertainty_fm"]) + Fraction(row["systematic_uncertainty_fm"])
            current_intervals[row["row_id"]] = exact_interval(row["value_fm"], str(width))
        else:
            current_intervals[row["row_id"]] = exact_interval(row["value_fm"], row["standard_uncertainty_fm"])
    historical_row = target["historical_adverse_rows"][0]
    historical = exact_interval(historical_row["value_fm"], historical_row["standard_uncertainty_fm"])
    adverse_rows = []
    scale_centre = Fraction(scale["value_fm"])
    for row in structural_formula_census():
        radius = row["coefficient"] * scale_centre
        adverse_rows.append({
            **row,
            "radius_fm": radius,
            "inside_muonic_interval": current_intervals["muonic-hydrogen-current-reference"][0] <= radius <= current_intervals["muonic-hydrogen-current-reference"][1],
        })
    adverse_inside = tuple(
        (row["charge_support"], row["transport_order"])
        for row in adverse_rows
        if row["inside_muonic_interval"]
    )
    return {
        "scale_interval_fm": scale_interval,
        "terminal_prediction_interval_fm": predicted,
        "terminal_prediction_centre_fm": predicted_centre,
        "leading_prediction_interval_fm": leading_interval,
        "current_intervals_fm": current_intervals,
        "current_interval_results": {key: interval_contains(value, predicted) for key, value in current_intervals.items()},
        "all_current_intervals_contain_prediction": all(interval_contains(value, predicted) for value in current_intervals.values()),
        "historical_CODATA_2014_interval_fm": historical,
        "historical_conflict_retained": historical[0] > predicted[1],
        "adverse_formula_rows": tuple(adverse_rows),
        "adverse_inside_muonic_interval": adverse_inside,
        "observation_uniquely_selects_ten_linear": adverse_inside == ((10, "linear"),),
        "scope_rows_retained": len(target["scope_rows"]) == 6 and all(target["scope_rows"].values()),
    }


def formal_prediction_inputs() -> dict[str, object]:
    coefficient = terminal_radius_coefficient()
    return {
        "terminal_coefficient": PositiveRatio.from_pair(coefficient.numerator, coefficient.denominator),
        "leading_multiplier": PositiveRatio.from_pair(leading_radius_multiplier().numerator, leading_radius_multiplier().denominator),
        "tripling_edge": HeldLabel("proton-radius", "outer-two-thirds-complement"),
        "charge_support": HeldLabel("proton-charge", "nine-internal-pairs-plus-one-external-charge"),
        "probe_relation": HeldLabel("probe", "one-proton-radius-independent-of-probe"),
        "scale_boundary": HeldLabel("dimensionful-scale", "reduced-proton-Compton-postseal-only"),
        "provenance": HeldLabel("provenance", "observational-derivation-not-historical-blindness"),
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
        "schema": "sft-v3-proton-radius-terminal-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "frozen_relation": "The exact radius coefficient is 4(One-alpha_terminal/10); every external scale and radius row remains post-seal.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_ids": SOURCE_IDS,
        "source_hashes": source_hashes(),
        "row_retention_policy": "all current electronic, muonic, global-adjustment and scattering rows; historical conflict; source limitations; all structural formula controls",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "exact rational interval propagation, complete current-vector comparison and historical adverse retention",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("proton-radius prediction has wrong Fold shape")
    return dict(zip(keys, output.cells))


class ProtonRadiusTerminalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong proton-radius seal")
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
            raise ValueError("proton-radius hostile-package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("proton-radius prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        all_rows = all((
            len(analysis["current_intervals_fm"]) == 4,
            len(analysis["adverse_formula_rows"]) == 9,
            analysis["scope_rows_retained"],
        ))
        controls = all((
            analysis["all_current_intervals_contain_prediction"],
            analysis["historical_conflict_retained"],
            analysis["observation_uniquely_selects_ten_linear"] is False,
            (8, "linear") in analysis["adverse_inside_muonic_interval"],
            (9, "linear") in analysis["adverse_inside_muonic_interval"],
            (10, "linear") in analysis["adverse_inside_muonic_interval"],
        ))
        tampered = json.loads(json.dumps(context[TARGET_IDS[0]]))
        tampered["current_radius_rows"][0]["value_fm"] = "0.8200"
        tampered["current_radius_rows"][0]["standard_uncertainty_fm"] = "0.0010"
        tampered_rejected = not exact_measurement_analysis(tampered)["all_current_intervals_contain_prediction"]
        passed = all((all_rows, controls, tampered_rejected))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-proton-radius-terminal-comparator/1", registration_hash, FALSIFICATION_CONDITION))
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
            "The exact coefficient and all structural alternatives seal before the four primary/authoritative source identities and radius rows are released.",
            "The exact terminal coefficient is 10069574419808/2519231977345 = 4(One-alpha_terminal/10), with no probe or radius measurement in its derivation.",
            "Post-seal composition with the complete CODATA-2022 reduced-proton-Compton interval predicts approximately 0.840621761 fm with exact outward uncertainty propagation.",
            "The prediction interval lies inside the registered 2026 electronic-hydrogen 0.8406(15) fm interval and the current muonic-hydrogen 0.84060(39) fm interval.",
            "The prediction interval lies inside the CODATA-2022 0.84075(64) fm interval and the conservative PRad 0.831 +/-0.007(stat) +/-0.012(syst) outward interval.",
            "The historical CODATA-2014 0.8751(61) fm interval is disjoint and remains an explicit unfavorable historical row.",
            "The primary 2026 paper's partly discrepant earlier electronic results and scattering-analysis dependence remain explicit; probe independence is not relabelled as universal agreement among all extractions.",
            "All three linear-support alternatives land inside the present muonic interval, so measurement does not select ten; the complete proton charge-support derivation does.",
            "Changing the current electronic-hydrogen row to a disjoint interval rejects the correspondence.",
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
    "ProtonRadiusTerminalValidator",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "source_hashes",
)
