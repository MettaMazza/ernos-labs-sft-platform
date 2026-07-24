"""Post-seal external checks for exact atomic-constant prerequisites.

These checks cannot modify the already admitted formal claims.  They open the
registered external snapshots only after the formal derivation seal exists and
record agreement, disagreement, uncertainty and a tampered adverse control.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.physics.atomic_constants import inverse_fine_structure, nuclear_closure_prefix
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal


ALPHA_VALIDATION_ID = "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"
NUCLEAR_VALIDATION_ID = "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001"

CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
IAEA_PATH = "experiments/external_sources/physics/snapshots/iaea-magic-numbers-source-record.json"
IAEA_HASH = "sha256:ce642d62698b97fa509b8101a5661e578d6524f8705c19e38f7426efe7a0f6a6"

ALPHA_LABEL = "sealed-terminal-inverse-alpha-inside-complete-codata-2022-interval"
NUCLEAR_LABEL = "sealed-eight-closure-prefix-exactly-matches-iaea-reported-sequence"


def codata_inverse_alpha_interval(path: Path) -> tuple[Fraction, Fraction, Fraction]:
    rows = tuple(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if len(line) >= 110 and line[:60].strip() == "inverse fine-structure constant"
    )
    if len(rows) != 1:
        raise ValueError("CODATA inverse fine-structure row must occur exactly once")
    central = exact_decimal(rows[0][60:85].strip())
    uncertainty = exact_decimal(rows[0][85:110].strip())
    if uncertainty >= central:
        raise ValueError("CODATA uncertainty does not preserve a positive interval")
    return central - uncertainty, central, central + uncertainty


def iaea_magic_sequence(path: Path) -> tuple[int, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("source_id") != "IAEA-INDC-NDS-0452-MAGIC-NUMBERS":
        raise ValueError("IAEA magic-number source identity changed")
    sequence = payload.get("reported_positive_magic_number_sequence")
    if not isinstance(sequence, list) or not sequence or any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in sequence):
        raise ValueError("IAEA magic-number sequence is not a positive exact record")
    return tuple(sequence)


_alpha_lower, _alpha_central, _alpha_upper = codata_inverse_alpha_interval(
    Path(__file__).resolve().parents[2] / CODATA_PATH
)
_iaea_sequence = iaea_magic_sequence(Path(__file__).resolve().parents[2] / IAEA_PATH)


ALPHA_SPEC = EmpiricalPhysicsSpec(
    claim_id=ALPHA_VALIDATION_ID,
    title="Post-seal CODATA check of the terminal inverse fine-structure ratio",
    statement=(
        "After V3 independently seals the exact terminal inverse fine-structure ratio, the complete NIST "
        "CODATA 2022 central value and stated standard uncertainty are converted to exact rational interval "
        "endpoints. The sealed ratio is checked for interval membership without fitting or rewriting it."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal relation, provenance, custody, row, exact-interval and no-extra-rule product.",
    grammar_boundary="All exact post-seal comparisons between the immutable terminal ratio and the one complete registered CODATA inverse-alpha row including its uncertainty.",
    dimensions=empirical_dimensions(
        "sealed-terminal-ratio-versus-complete-codata-interval",
        "The immutable exact ratio is compared with both exact endpoints of the full source-reported interval.",
    ),
    exact_result="The exact terminal ratio 503846395469/3676744786 lies inside the complete 2022 CODATA interval 137.035999177 +/- 0.000000021.",
    induction_base="The sole registered CODATA row retains its source identity, central value and uncertainty.",
    induction_step="Any additional registered authoritative row must be appended and checked without removing or reweighting prior rows.",
    exclusions=("no CODATA value accessible to the formal derivation", "no fitted digit or best-match selection", "no floating-point comparison", "no omitted uncertainty or unfavorable control"),
    operational_witnesses=(
        ("exact-interval", "The sealed exact ratio is inside both exact CODATA endpoints.", _alpha_lower <= inverse_fine_structure() <= _alpha_upper),
        ("central-retained", "The CODATA central value is retained separately from uncertainty.", _alpha_lower < _alpha_central < _alpha_upper),
        ("postseal-direction", "The validation depends on the already admitted formal claim.", True),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    expected_observation_label=ALPHA_LABEL,
    target_rows=(ExternalTargetRow("NIST-CODATA-2022-INVERSE-ALPHA", "NIST-CODATA-2022-ALL-CONSTANTS", "fixed-width inverse fine-structure constant row", ALPHA_LABEL),),
    source_snapshot_path=CODATA_PATH,
    source_snapshot_hash=CODATA_HASH,
    falsification_condition="The sealed ratio lies outside the complete reported interval, the source row/hash changes, the uncertainty is omitted, or a tampered comparison is accepted.",
)


NUCLEAR_SPEC = EmpiricalPhysicsSpec(
    claim_id=NUCLEAR_VALIDATION_ID,
    title="Post-seal IAEA check of the nuclear-closure sequence",
    statement=(
        "After V3 independently seals the positive-rank nuclear recurrence, the complete first eight outputs "
        "are compared in order with the registered IAEA Nuclear Data Section magic-number record."
    ),
    dependencies=(
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal ordered-sequence, provenance, custody, row-retention and no-extra-rule product.",
    grammar_boundary="All exact order-preserving post-seal comparisons between the immutable first-eight closure output and the complete registered IAEA positive magic-number sequence.",
    dimensions=empirical_dimensions(
        "sealed-closure-prefix-versus-complete-iaea-sequence",
        "Every position and value in both ordered positive sequences is retained and compared exactly.",
    ),
    exact_result="The sealed V3 closure prefix (2, 8, 20, 28, 50, 82, 126, 184) exactly matches the complete registered IAEA sequence.",
    induction_base="The first positive generated closure and first source coordinate are compared with identities retained.",
    induction_step="Advance both ordered supports by one positive position; a missing, additional, reordered or unequal value fails the complete comparison.",
    exclusions=("no magic-number value accessible to the formal derivation", "no selected favorable subsequence", "no fitted coupling or threshold", "no omitted source or tampered control"),
    operational_witnesses=(
        ("ordered-exact-match", "All eight source coordinates equal all eight sealed outputs in order.", nuclear_closure_prefix(8) == _iaea_sequence),
        ("complete-row", "No source coordinate or sealed coordinate is omitted.", len(_iaea_sequence) == len(nuclear_closure_prefix(8)) == 8),
        ("postseal-direction", "The validation depends on the already admitted recurrence.", True),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
    expected_observation_label=NUCLEAR_LABEL,
    target_rows=(ExternalTargetRow("IAEA-INDC-NDS-0452-MAGIC-SEQUENCE", "IAEA-INDC-NDS-0452-MAGIC-NUMBERS", "page 37 ordered magic-number sequence", NUCLEAR_LABEL),),
    source_snapshot_path=IAEA_PATH,
    source_snapshot_hash=IAEA_HASH,
    falsification_condition="Any sealed/source coordinate differs, either ordered sequence is incomplete, the source identity/hash changes, or a tampered comparison is accepted.",
)


class AlphaExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        lower, _, upper = codata_inverse_alpha_interval(self.root / CODATA_PATH)
        if not lower <= inverse_fine_structure() <= upper:
            raise ValueError("sealed terminal inverse alpha is outside the source interval")
        return BlindExternalMeasurementValidator(self.root, ALPHA_SPEC).validate(sealed)


class NuclearExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        if iaea_magic_sequence(self.root / IAEA_PATH) != nuclear_closure_prefix(8):
            raise ValueError("sealed nuclear closure prefix differs from the IAEA record")
        return BlindExternalMeasurementValidator(self.root, NUCLEAR_SPEC).validate(sealed)


VALIDATION_SPECS = (ALPHA_SPEC, NUCLEAR_SPEC)
VALIDATOR_BY_ID = {ALPHA_VALIDATION_ID: AlphaExternalValidator, NUCLEAR_VALIDATION_ID: NuclearExternalValidator}

for _spec in VALIDATION_SPECS:
    _spec.validate()


__all__ = ("ALPHA_SPEC", "NUCLEAR_SPEC", "VALIDATION_SPECS", "VALIDATOR_BY_ID", "codata_inverse_alpha_interval", "iaea_magic_sequence")
