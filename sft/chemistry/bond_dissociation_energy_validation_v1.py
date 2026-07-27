"""Post-seal eight-row empirical validation for Chemistry PROP-002."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.bond_dissociation_energy_batch_v1 import (
    BOND_DISSOCIATION_ENERGY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.bond_dissociation_energy_law_v1 import ground_dissociation_from_transition
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldPair,
    FoldTable,
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


ATOMIC_HASH = "sha256:a6da423edfe31be4666d56eb6b83864512e5583760b016fce00d2b825a173267"
ATOMIC_PATH = "experiments/external_sources/chemistry/snapshots/prop-002-atomic-1s-2s-primary-records-v1.json"
APS_HASH = "sha256:9c41d01395090b18b2eb8b1223e9cb430d9309f79d1a0324b092a5ed8c1b6953"
APS_PATH = "experiments/external_sources/chemistry/snapshots/aps-hydrogen-dissociation-1994.json"
CURRENT_HASH = "sha256:304c92c783621b12706ce1ba92a3c2dc9b6426f884fb8ab3001523c65cbbfc80"
CURRENT_PATH = "experiments/external_sources/chemistry/snapshots/prop-002-current-dissociation-primary-records-v1.json"

SOURCE_IDS = (
    "APS-PRA-49-2460-1994",
    "PRL-UDEM-H-1S2S-1997",
    "PRL-PARTHEY-HD-1S2S-SHIFT-2010",
    "SI-DEFINING-LIGHT-SPEED",
    "JCP-LIU-H2-DISSOCIATION-2009",
    "PRA-HUSSELS-D2-DISSOCIATION-2022",
)


def _fraction(row: object) -> Fraction:
    if not isinstance(row, dict) or set(row) != {"numerator", "denominator"}:
        raise ValueError("PROP-002 exact fraction record is malformed")
    numerator, denominator = row["numerator"], row["denominator"]
    if (
        isinstance(numerator, bool)
        or isinstance(denominator, bool)
        or not isinstance(numerator, int)
        or not isinstance(denominator, int)
        or numerator < 1
        or denominator < 1
    ):
        raise ValueError("PROP-002 exact fraction left the positive domain")
    return Fraction(numerator, denominator)


def _ratio(value: Fraction) -> PositiveRatio:
    if not isinstance(value, Fraction) or value.numerator < 1 or value.denominator < 1:
        raise ValueError("PROP-002 measurement ratio must be exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def _interval(row: dict[str, object]) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    central = _fraction(row["central"])
    uncertainty = _fraction(row["uncertainty"])
    lower = _fraction(row["lower"])
    upper = _fraction(row["upper"])
    if lower + uncertainty != central or central + uncertainty != upper or not upper > lower:
        raise ValueError("PROP-002 interval does not reconstruct exactly")
    return central, uncertainty, lower, upper


def prediction_program_document() -> dict[str, object]:
    """Seal the forced relation and all retained identities without any number."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for species, atom in (("H2", "H"), ("D2", "D")):
        key = species.lower()
        labels = (
            ("isotopologue", species),
            ("molecular-origin", "X-1Sigma-g-plus-ground"),
            ("threshold-state", "B-prime-1Sigma-u-plus"),
            ("threshold-channel", f"{atom}-1s-plus-{atom}-2s"),
            ("ground-channel", f"{atom}-1s-plus-{atom}-1s"),
            ("path-operation", "ordered-positive-held-Take"),
            ("measurement-custody", "all-values-open-after-relation-seal"),
        )
        registers = ["premise"]
        for ordinal, (family, label) in enumerate(labels, start=1):
            destination = f"{key}-label-{ordinal}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": key + "-relation", "arguments": registers})
        table_arguments.extend((key + "-label-1", key + "-relation"))
    instructions.extend((
        {"opcode": "table", "destination": "structural-relation-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["structural-relation-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": BOND_DISSOCIATION_ENERGY_SPEC.experiment_id + "-value-free-relation-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "experiment_id": BOND_DISSOCIATION_ENERGY_SPEC.experiment_id,
        "claim_id": BOND_DISSOCIATION_ENERGY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": BOND_DISSOCIATION_ENERGY_SPEC.statement,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(),
        "target_ids": tuple(row.target_id for row in BOND_DISSOCIATION_ENERGY_SPEC.target_rows),
        "all_measured_values_absent_from_law_and_prediction": True,
        "all_eight_rows_required": True,
        "falsification_condition": BOND_DISSOCIATION_ENERGY_SPEC.falsification_condition,
    }


def _expected_measurements(root: Path) -> dict[str, tuple[str, str, Fraction, Fraction, str]]:
    if hash_file(root / APS_PATH) != APS_HASH or hash_file(root / ATOMIC_PATH) != ATOMIC_HASH or hash_file(root / CURRENT_PATH) != CURRENT_HASH:
        raise ValueError("PROP-002 primary-source bytes changed")
    aps = json.loads((root / APS_PATH).read_text(encoding="utf-8"))
    atomic = json.loads((root / ATOMIC_PATH).read_text(encoding="utf-8"))
    current = json.loads((root / CURRENT_PATH).read_text(encoding="utf-8"))
    aps_rows = {(row["species"], row["kind"]): row for row in aps["records"]}
    atomic_rows = {row["source_id"]: row for row in atomic["sources"]}
    current_rows = {row["species"]: row for row in current["sources"]}
    h = atomic_rows["PRL-UDEM-H-1S2S-1997"]
    shift = atomic_rows["PRL-PARTHEY-HD-1S2S-SHIFT-2010"]
    light = atomic_rows["SI-DEFINING-LIGHT-SPEED"]
    if light.get("value_inscription_m_per_s") != "299792458" or light.get("exact_definition") is not True:
        raise ValueError("PROP-002 SI translation identity changed")
    c_cm = Fraction(29979245800, 1)
    h_value, h_uncertainty = _fraction(h["value_hz"]), _fraction(h["standard_uncertainty_hz"])
    shift_value, shift_uncertainty = _fraction(shift["value_hz"]), _fraction(shift["standard_uncertainty_hz"])
    atomic_exact = {
        "H2": (h_value / c_cm, h_uncertainty / c_cm),
        "D2": ((h_value + shift_value) / c_cm, (h_uncertainty + shift_uncertainty) / c_cm),
    }
    expected: dict[str, tuple[str, str, Fraction, Fraction, str]] = {}
    for species, atom in (("H2", "H"), ("D2", "D")):
        threshold = aps_rows[(species, "measured_dissociation_threshold")]
        historical = aps_rows[(species, "measured_ground_state_dissociation_energy")]
        current_row = current_rows[species]
        expected[f"PATH-{species}-BPRIME-THRESHOLD"] = (
            species, "path-threshold",
            Fraction(threshold["value_numerator"], threshold["value_denominator"]),
            Fraction(threshold["uncertainty_numerator"], threshold["uncertainty_denominator"]), APS_HASH,
        )
        expected[f"PATH-{atom}-ATOMIC-1S2S"] = (species, "atomic-path-segment", *atomic_exact[species], ATOMIC_HASH)
        expected[f"APS-1994-{species}-X-GROUND-D0"] = (
            species, "historical-ground-dissociation",
            Fraction(historical["value_numerator"], historical["value_denominator"]),
            Fraction(historical["uncertainty_numerator"], historical["uncertainty_denominator"]), APS_HASH,
        )
        expected[f"CURRENT-{species}-X-GROUND-D0"] = (
            species, "later-ground-dissociation",
            Fraction(current_row["value_inscription_cm_inverse"]),
            Fraction(current_row["standard_uncertainty_inscription_cm_inverse"]), CURRENT_HASH,
        )
    return expected


def _load_targets(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH or hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("PROP-002 identity or measurement registry changed")
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    measurements = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    if (
        identities.get("schema") != "sft-v3-bond-dissociation-energy-identities/1"
        or identities.get("all_measurement_values_absent") is not True
        or measurements.get("schema") != "sft-v3-bond-dissociation-energy-withheld-measurements/1"
        or measurements.get("release_requires_prediction_seal") is not True
        or measurements.get("identity_document_hash") != sha256_identity(identities)
        or len(identities.get("rows", ())) != 8
        or len(measurements.get("rows", ())) != 8
    ):
        raise ValueError("PROP-002 complete eight-row boundary changed")
    identity_rows = {row["target_id"]: row for row in identities["rows"]}
    measurement_rows = {row["target_id"]: row for row in measurements["rows"]}
    expected = _expected_measurements(root)
    if set(identity_rows) != set(measurement_rows) or set(expected) != set(measurement_rows):
        raise ValueError("PROP-002 measurement support changed")
    resolved = []
    for target_id in sorted(expected):
        species, role, central, uncertainty, snapshot_hash = expected[target_id]
        identity, row = identity_rows[target_id], measurement_rows[target_id]
        exact_interval = (central, uncertainty, central - uncertainty, central + uncertainty)
        if (
            identity.get("target_value_absent") is not True
            or identity.get("species") != species
            or identity.get("measurement_role") != role
            or identity.get("snapshot_hash") != snapshot_hash
            or row.get("species") != species
            or row.get("measurement_role") != role
            or row.get("source_snapshot_hash") != snapshot_hash
            or _interval(row) != exact_interval
        ):
            raise ValueError(f"PROP-002 source reconstruction differs: {target_id}")
        resolved.append({
            "target_id": target_id,
            "species": species,
            "measurement_role": role,
            "inscription": row["inscription"],
            "lower": exact_interval[2],
            "upper": exact_interval[3],
            "interval": FoldPair(_ratio(exact_interval[2]), _ratio(exact_interval[3])),
        })
    return tuple(resolved)


def _validate_structural_prediction(output: object) -> None:
    if not isinstance(output, FoldTable) or len(output.entries) != 2:
        raise ValueError("PROP-002 value-free structural prediction is incomplete")
    observed = set()
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "isotopologue" or not isinstance(entry.right, FoldWord):
            raise ValueError("PROP-002 structural relation lost its identity")
        observed.add(entry.left.label)
        labels = entry.right.cells[1:]
        if len(entry.right.cells) != 8 or any(not isinstance(value, HeldLabel) for value in labels):
            raise ValueError("PROP-002 structural relation is incomplete")
        if labels[-2] != HeldLabel("path-operation", "ordered-positive-held-Take") or labels[-1] != HeldLabel("measurement-custody", "all-values-open-after-relation-seal"):
            raise ValueError("PROP-002 operation or custody law changed")
    if observed != {"H2", "D2"}:
        raise ValueError("PROP-002 structural isotopologue support changed")


class BondDissociationEnergyValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = BOND_DISSOCIATION_ENERGY_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
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
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-002 prediction package changed")
        _validate_structural_prediction(execution.output)

        # First numerical measurement access: after the value-free relation seal.
        target_rows = _load_targets(self.root)
        target_values = {str(row["target_id"]): row["interval"] for row in target_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        by_species_role = {(str(row["species"]), str(row["measurement_role"])): row for row in target_rows}
        comparisons = []
        for species in ("H2", "D2"):
            threshold = by_species_role[(species, "path-threshold")]
            atomic = by_species_role[(species, "atomic-path-segment")]
            lower = ground_dissociation_from_transition(threshold["lower"], atomic["upper"])
            upper = ground_dissociation_from_transition(threshold["upper"], atomic["lower"])
            for role in ("historical-ground-dissociation", "later-ground-dissociation"):
                target = by_species_role[(species, role)]
                overlap = not (upper < target["lower"] or target["upper"] < lower)
                displaced_lower, displaced_upper = upper + 1, upper + 2
                comparisons.append({
                    "target_id": target["target_id"], "species": species, "record_class": role,
                    "derived_lower": lower, "derived_upper": upper,
                    "observed_lower": target["lower"], "observed_upper": target["upper"],
                    "source_inscription": target["inscription"], "overlap": overlap,
                    "displaced_control_rejected": displaced_lower > target["upper"] and displaced_upper > displaced_lower,
                })

        program_text = json.dumps(document, sort_keys=True)
        target_document = json.loads((self.root / TARGET_PATH).read_text(encoding="utf-8"))
        no_measurement_in_prediction = all(str(row["inscription"]) not in program_text for row in target_document["rows"])
        reversed_take_rejected = False
        try:
            ground_dissociation_from_transition(Fraction(3, 4), Fraction(9, 8))
        except InadmissibleExactValue:
            reversed_take_rejected = True
        identity_document = json.loads((self.root / IDENTITY_PATH).read_text(encoding="utf-8"))
        adverse = {
            "complete_eight_row_vector": len(target_rows) == 8 and set(target_values) == set(envelope.withheld_target_ids),
            "all_measurements_absent_from_prediction": no_measurement_in_prediction,
            "states_and_channels_held": all(str(row.get("state", "")).strip() and str(row.get("channel", "")).strip() for row in identity_document["rows"]),
            "reversed_or_nonpositive_Take_halts": reversed_take_rejected,
            "every_displaced_interval_rejected": all(row["displaced_control_rejected"] for row in comparisons),
            "historical_and_later_rows_both_tested": len(comparisons) == 4 and {row["record_class"] for row in comparisons} == {"historical-ground-dissociation", "later-ground-dissociation"},
            "tampered_registry_identity_rejected": sha256_identity((TARGET_HASH, "tampered")) != TARGET_HASH,
        }
        passed = all(row["overlap"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-H2-D2-post-seal-Take-comparator/1", registration_hash)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-002 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "target_registry_hash": TARGET_HASH,
            "comparisons": comparisons, "adverse": adverse, "trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: post-seal exact Take interval "
            f"[{row['derived_lower'].numerator}/{row['derived_lower'].denominator}, "
            f"{row['derived_upper'].numerator}/{row['derived_upper'].denominator}] inverse-centimetre; "
            f"source {row['source_inscription']} within [{row['observed_lower'].numerator}/{row['observed_lower'].denominator}, "
            f"{row['observed_upper'].numerator}/{row['observed_upper'].denominator}]; overlap {row['overlap']}"
            for row in comparisons
        ) + tuple(f"adverse {name}: {value}" for name, value in adverse.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            SOURCE_IDS, measurements, sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "ATOMIC_HASH", "ATOMIC_PATH", "APS_HASH", "APS_PATH", "BondDissociationEnergyValidator",
    "CURRENT_HASH", "CURRENT_PATH", "SOURCE_IDS", "_load_targets", "_validate_structural_prediction",
    "experiment_registration_record", "prediction_program_document",
)
