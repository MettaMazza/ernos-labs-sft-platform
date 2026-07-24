"""Exact post-seal comparisons for the sealed cubic and hydrogen laws.

The formal atomic laws remain immutable.  This module records the disclosed
observational-derivation protocol, verifies the complete authoritative source
custody chain, evaluates the already sealed exact relations with rational
arithmetic, and only then releases the registered comparison labels.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.atomic_spectra_completion_laws_v1 import (
    cubic_coordination,
    hydrogen_transition,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal
from sft.physics.prior_value_laws import positive_take


CUBIC_VALIDATION_ID = "SFT-PHYS-VALIDATION-ATOMIC-CUBIC-SUPPORT-004"
HYDROGEN_VALIDATION_ID = "SFT-PHYS-VALIDATION-ATOMIC-HYDROGEN-SPECTRUM-004"

SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/atomic-spectra-postseal-source-record.json"
SOURCE_RECORD_HASH = "sha256:64fb03e6758e3274d33c6e15682b5739adfa7cf097453892d57248a98e6d12c3"

CUBIC_LABEL = "sealed-six-neighbour-cubic-support-exactly-matches-complete-nist-row"
HYDROGEN_LABEL = "sealed-hydrogen-gross-ratios-lie-inside-both-complete-nist-line-intervals"

EXPECTED_SOURCE_HASHES = {
    "NIST-NCNR-DCS-SUPERFLUID-HELIUM": "sha256:ab723f91d6658bd8b5d19889884fd87e07046d2b0060e23f7df8d7cb6c35fa5b",
    "NIST-ASD-HYDROGEN-ATOMIC-DATA": "sha256:cc54c774518d62cbb7e95f17b3b7fcd9d1faf0aa90043a607b91dff0a43e2087",
    "NIST-KRAMIDA-HYDROGEN-CRITICAL-COMPILATION-2010-2019": "sha256:86ccaeb875fcdb4445e727618509621ceee656e5dc02295140ecdb6e1d2dd443",
    "NIST-WEBBOOK-SRD69-H2-DIATOMIC-CONSTANTS": "sha256:18036a188088f880122249544ceb6b384fabfba93b300b4f9f0fa01aa0ed9b24",
}


def source_record(root: Path) -> dict[str, object]:
    """Load and verify the aggregate record and every underlying snapshot."""

    path = root.resolve() / SOURCE_RECORD_PATH
    if hash_file(path) != SOURCE_RECORD_HASH:
        raise ValueError("atomic-spectrum source record differs from registration")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "sft-v3-atomic-spectra-postseal-source-record/1":
        raise ValueError("atomic-spectrum source schema changed")
    custody = payload.get("custody")
    if not isinstance(custody, dict) or not all(
        custody.get(key) is True
        for key in (
            "development_targets_already_known",
            "target_inaccessible_during_prediction_execution",
            "formal_relations_contain_measurement",
            "measurements_select_formal_survivors",
            "engine_prediction_sealed_before_target_release_within_run",
            "complete_reported_uncertainties_retained",
            "unfavorable_molecular_ratio_retained",
        )
        if key not in {"formal_relations_contain_measurement", "measurements_select_formal_survivors"}
    ):
        raise ValueError("atomic-spectrum custody disclosure is incomplete")
    if custody.get("formal_relations_contain_measurement") is not False:
        raise ValueError("formal atomic relation improperly contains a measurement")
    if custody.get("measurements_select_formal_survivors") is not False:
        raise ValueError("measurement improperly selects a formal atomic survivor")
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != len(EXPECTED_SOURCE_HASHES):
        raise ValueError("atomic-spectrum source vector is incomplete")
    by_id = {row.get("source_id"): row for row in sources if isinstance(row, dict)}
    if set(by_id) != set(EXPECTED_SOURCE_HASHES):
        raise ValueError("atomic-spectrum source identities changed")
    for source_id, expected_hash in EXPECTED_SOURCE_HASHES.items():
        row = by_id[source_id]
        if row.get("snapshot_hash") != expected_hash:
            raise ValueError(f"registered source hash changed: {source_id}")
        snapshot = root.resolve() / str(row.get("snapshot_path"))
        if hash_file(snapshot) != expected_hash:
            raise ValueError(f"source snapshot differs from its registered hash: {source_id}")
    return payload


def _source_by_id(root: Path, source_id: str) -> dict[str, object]:
    record = source_record(root)
    return next(row for row in record["sources"] if row["source_id"] == source_id)


def cubic_observed_coordination(root: Path) -> int:
    row = _source_by_id(root, "NIST-NCNR-DCS-SUPERFLUID-HELIUM")
    value = row["reported_record"].get("simple_cubic_nearest_neighbours")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("NIST cubic coordination is not a positive exact count")
    return value


def hydrogen_comparison(root: Path) -> dict[str, Fraction | bool]:
    atomic = _source_by_id(root, "NIST-ASD-HYDROGEN-ATOMIC-DATA")["reported_record"]
    lines = _source_by_id(root, "NIST-KRAMIDA-HYDROGEN-CRITICAL-COMPILATION-2010-2019")["reported_record"]
    scale = exact_decimal(atomic["hydrogen_ionization_wavenumber_cm_inverse"])
    lyman_central = exact_decimal(lines["lyman_alpha_observed_wavenumber_cm_inverse"])
    lyman_uncertainty = exact_decimal(lines["lyman_alpha_uncertainty_cm_inverse"])
    balmer_central = exact_decimal(lines["balmer_alpha_observed_wavenumber_cm_inverse"])
    balmer_uncertainty = exact_decimal(lines["balmer_alpha_uncertainty_cm_inverse"])
    lyman_lower = positive_take(lyman_central, lyman_uncertainty)
    balmer_lower = positive_take(balmer_central, balmer_uncertainty)
    if not isinstance(lyman_lower, Fraction) or not isinstance(balmer_lower, Fraction):
        raise ValueError("hydrogen interval orientation failed")
    lyman_upper = lyman_central + lyman_uncertainty
    balmer_upper = balmer_central + balmer_uncertainty
    lyman_prediction = scale * hydrogen_transition(2, 1)
    balmer_prediction = scale * hydrogen_transition(3, 2)
    return {
        "scale": scale,
        "lyman_prediction": lyman_prediction,
        "lyman_lower": lyman_lower,
        "lyman_upper": lyman_upper,
        "lyman_passed": lyman_lower <= lyman_prediction <= lyman_upper,
        "balmer_prediction": balmer_prediction,
        "balmer_lower": balmer_lower,
        "balmer_upper": balmer_upper,
        "balmer_passed": balmer_lower <= balmer_prediction <= balmer_upper,
    }


_ROOT = Path(__file__).resolve().parents[2]
_CUBIC_OBSERVED = cubic_observed_coordination(_ROOT)
_HYDROGEN = hydrogen_comparison(_ROOT)


CUBIC_SPEC = EmpiricalPhysicsSpec(
    claim_id=CUBIC_VALIDATION_ID,
    title="Post-seal NIST comparison of the forced six-neighbour cubic support",
    statement=(
        "After the exact Fold law independently forces all two held directions on all three generated spatial "
        "axes, the sealed coordination count six is compared with the complete registered NIST simple-cubic row."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-CUBIC-SUPPORT-004",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal exact-count, provenance, custody, row-retention and no-extra-rule product.",
    grammar_boundary="All exact comparisons between the immutable six-neighbour Fold coordination and the sole complete registered NIST simple-cubic coordination row.",
    dimensions=empirical_dimensions(
        "sealed-six-neighbour-count-versus-complete-nist-row",
        "The immutable positive count is compared exactly with the full registered NIST coordination record.",
    ),
    exact_result="The sealed Fold count 2*3=6 exactly equals the complete NIST simple-cubic nearest-neighbour count six.",
    induction_base="One generated spatial axis retains both held Fold directions.",
    induction_step="Each remaining forced axis contributes its two held directions once; the completed three-axis support is sealed before the NIST row is released.",
    exclusions=("no NIST value accessible to the formal law", "no imported lattice premise", "no selected neighbour subset", "no fitted count or extra rule"),
    operational_witnesses=(
        ("formal-count", "The formal law remains exactly six.", cubic_coordination() == 6),
        ("complete-nist-row", "The registered NIST count is exactly six.", _CUBIC_OBSERVED == 6),
        ("postseal-equality", "The sealed and observed positive counts are identical.", cubic_coordination() == _CUBIC_OBSERVED),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-ATOMIC-CUBIC-SUPPORT-004",
    expected_observation_label=CUBIC_LABEL,
    target_rows=(ExternalTargetRow("NIST-SIMPLE-CUBIC-NEAREST-NEIGHBOURS", "NIST-NCNR-DCS-SUPERFLUID-HELIUM", "PDF page 10 nearest-neighbour packing row", CUBIC_LABEL),),
    source_snapshot_path=SOURCE_RECORD_PATH,
    source_snapshot_hash=SOURCE_RECORD_HASH,
    falsification_condition="The registered NIST row is not six, the formal count changes, any source hash changes, target access precedes sealing, or a tampered row is accepted.",
)


HYDROGEN_SPEC = EmpiricalPhysicsSpec(
    claim_id=HYDROGEN_VALIDATION_ID,
    title="Post-seal NIST comparison of the exact hydrogen spectral ladder",
    statement=(
        "The NIST hydrogen ionization wavenumber is retained solely as the dimensionful input carrier. The "
        "already sealed exact Fold gaps three-quarters and five-thirty-sixths are applied without adjustment, "
        "then compared with the complete NIST Lyman-alpha and Balmer-alpha measured intervals."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal carrier-times-gap, exact-interval, provenance, custody, complete-row and no-extra-rule product.",
    grammar_boundary="All exact post-seal applications of the immutable Fold Lyman-alpha and Balmer-alpha ratios to the one registered NIST hydrogen ionization carrier, compared with both complete reported line intervals.",
    dimensions=empirical_dimensions(
        "sealed-hydrogen-gaps-versus-complete-nist-line-vector",
        "Both immutable rational gaps act once on the registered scale carrier and both complete uncertainty intervals are retained.",
    ),
    exact_result=(
        "The sealed ratios predict Lyman-alpha 82259.078775 cm^-1 and Balmer-alpha "
        "1096787717/72000 cm^-1; these lie respectively inside the complete NIST intervals "
        "[82259.02, 82259.30] and [15233.14, 15233.28] cm^-1."
    ),
    induction_base="The positive ground-state ionization record supplies one dimensionful carrier while the sealed first emitted gap supplies three-quarters.",
    induction_step="Each additional ordered principal pair supplies only its already forced exact positive gap; every registered observed line and uncertainty must be appended without adjusting the relation.",
    exclusions=("no line target accessible to the formal law", "no adjusted spectral ratio", "no floating comparison", "no omitted line, uncertainty or adverse row"),
    operational_witnesses=(
        ("sealed-lyman-ratio", "The sealed first gap remains exactly three-quarters.", hydrogen_transition(2, 1) == Fraction(3, 4)),
        ("sealed-balmer-ratio", "The sealed second gap remains exactly five-thirty-sixths.", hydrogen_transition(3, 2) == Fraction(5, 36)),
        ("lyman-interval", "The target-inaccessible exact Lyman prediction lies inside the full NIST interval.", bool(_HYDROGEN["lyman_passed"])),
        ("balmer-interval", "The target-inaccessible exact Balmer prediction lies inside the full NIST interval.", bool(_HYDROGEN["balmer_passed"])),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-ATOMIC-HYDROGEN-SPECTRUM-004",
    expected_observation_label=HYDROGEN_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-H-I-LYMAN-ALPHA-INTERVAL", "NIST-KRAMIDA-HYDROGEN-CRITICAL-COMPILATION-2010-2019", "Table 11 observed Lyman n=2 row with uncertainty", HYDROGEN_LABEL),
        ExternalTargetRow("NIST-H-I-BALMER-ALPHA-INTERVAL", "NIST-KRAMIDA-HYDROGEN-CRITICAL-COMPILATION-2010-2019", "Table 10 observed Balmer 2-3 row with uncertainty", HYDROGEN_LABEL),
    ),
    source_snapshot_path=SOURCE_RECORD_PATH,
    source_snapshot_hash=SOURCE_RECORD_HASH,
    falsification_condition="Either exact prediction lies outside its complete NIST interval, a row or uncertainty is omitted, a source hash changes, target access precedes sealing, or a tampered row is accepted.",
)


class CubicExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        if cubic_observed_coordination(self.root) != cubic_coordination():
            raise ValueError("sealed cubic count differs from the complete NIST row")
        return BlindExternalMeasurementValidator(self.root, CUBIC_SPEC).validate(sealed)


class HydrogenExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        comparison = hydrogen_comparison(self.root)
        if comparison["lyman_passed"] is not True or comparison["balmer_passed"] is not True:
            raise ValueError("sealed hydrogen vector lies outside a complete NIST interval")
        return BlindExternalMeasurementValidator(self.root, HYDROGEN_SPEC).validate(sealed)


VALIDATION_SPECS = (CUBIC_SPEC, HYDROGEN_SPEC)
VALIDATOR_BY_ID = {
    CUBIC_VALIDATION_ID: CubicExternalValidator,
    HYDROGEN_VALIDATION_ID: HydrogenExternalValidator,
}

for _spec in VALIDATION_SPECS:
    _spec.validate()


__all__ = (
    "CUBIC_SPEC",
    "CUBIC_VALIDATION_ID",
    "HYDROGEN_SPEC",
    "HYDROGEN_VALIDATION_ID",
    "VALIDATION_SPECS",
    "VALIDATOR_BY_ID",
    "cubic_observed_coordination",
    "hydrogen_comparison",
    "source_record",
)
