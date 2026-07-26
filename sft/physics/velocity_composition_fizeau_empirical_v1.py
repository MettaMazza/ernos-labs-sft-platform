"""Post-seal Fizeau discriminator for exact Fold velocity composition."""

from __future__ import annotations

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.velocity_composition_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-VELOCITY-COMPOSITION-034"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-VELOCITY-COMPOSITION-034"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/velocity-composition-fizeau-source-record.json"
SOURCE_HASH = "sha256:2d8f4c921c10e4d3917cce4c5cdeb83269c6f135d3d98c99d824ff3cc1fca1b7"
PDF_PATH = "experiments/external_sources/physics/snapshots/arxiv-1201.0501-fizeau.pdf"
PDF_HASH = "sha256:8c19ceeccda50a3c297aa13c6006a6cf032d41a3c714f128b2be663bd3c5b5b3"
SOURCE_IDS = ("ARXIV-1201.0501-FIZEAU-WATER-AIR",)
OBSERVATION_LABEL = (
    "sealed-exact-velocity-composition__water-slope-between-raw-and-corrected-relativistic-rows__"
    "ordinary-addition-control-strongly-disfavoured__air-control-compatible__systematics-retained__no-fit"
)


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal Fizeau discriminator for Fold velocity composition",
    statement=(
        "After the exact Fold operation (u+v)/(One+uv) is sealed, the complete registered Lahaye-Labastie-"
        "Mathevet Fizeau record is opened. The measured water phase-slope 274/1000 with stated 3/1000 statistical "
        "uncertainty lies between the reported raw and profile/dispersion-corrected relativistic predictions "
        "248/1000 and 299/1000, while ordinary addition predicts 563/1000. The best relativistic-row distance is "
        "25/1000, against 289/1000 for ordinary addition. The air row also rejects ordinary addition and remains "
        "compatible with relativistic composition. Every calibration, profile and path-length limitation is retained."
    ),
    dependencies=(
        "SFT-PHYS-SPACETIME-VELOCITY-COMPOSITION-TERMINAL-033",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed operation, Fizeau discriminator, provenance, target "
        "isolation, measurement separation, complete row/limitation retention, successor closure and extension."
    ),
    grammar_boundary=(
        "The admitted exact positive velocity operation; the complete registered water measured/uncertainty, raw "
        "relativistic, corrected relativistic and ordinary-addition rows; the air result; and every stated systematic limitation."
    ),
    dimensions=empirical_dimensions(
        "sealed-velocity-composition-with-complete-Fizeau-discriminator",
        "The formal operation is fixed before the external water, air and systematic rows are opened.",
    ),
    exact_result=(
        "The measured water slope is 274/1000 +/- 3/1000 rad s/m. It lies inside the complete reported "
        "relativistic-systematics bracket 248/1000 to 299/1000 and is more than ten times closer to its nearest "
        "relativistic row than to ordinary addition at 563/1000. The air result independently rejects ordinary "
        "addition and is compatible with relativistic composition. This is a post-seal discriminator, not a fit "
        "or precision confirmation; all source-stated systematics remain open."
    ),
    induction_base=(
        "The sealed operation has one exact structural survivor before any Fizeau target is released."
    ),
    induction_step=(
        "Opening another registered measurement or limitation row changes neither the operation nor its formal "
        "receipt; the row is retained once in the complete comparison ledger."
    ),
    exclusions=(
        "no Fizeau slope, refractive record or external velocity formula in the formal predecessor derivation",
        "no fit of a Fold coefficient to the water or air record",
        "no omission of the ordinary-addition control or source-stated systematic limitations",
        "no precision interval claim where the source reports an eight-percent systematic-level agreement",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
        "no target access before the formal prediction seal",
    ),
    operational_witnesses=(
        ("formal-unique", "The structural bilinear census has one survivor.", theorem_certificate()["candidate_count"] == 4),
        ("formal-closure", "The exact operation is closed and associative.", theorem_certificate()["closure"] and theorem_certificate()["associativity"]),
        ("formal-limit", "The limiting One is absorbing without a numerical-zero rest premise.", theorem_certificate()["limiting_speed_absorbing"] and theorem_certificate()["typed_rest_identity"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("FIZEAU-WATER-MEASURED", SOURCE_IDS[0], "Figure 6 and Section V.C measured water slope and uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("FIZEAU-WATER-RELATIVISTIC", SOURCE_IDS[0], "Figure 6 raw and corrected relativistic predictions", OBSERVATION_LABEL),
        ExternalTargetRow("FIZEAU-WATER-ORDINARY-CONTROL", SOURCE_IDS[0], "Figure 6 nonrelativistic ordinary-addition prediction", OBSERVATION_LABEL),
        ExternalTargetRow("FIZEAU-AIR-CONTROL", SOURCE_IDS[0], "Figure 8 and Section V.E air result", OBSERVATION_LABEL),
        ExternalTargetRow("FIZEAU-SYSTEMATICS", SOURCE_IDS[0], "Section V.C-D calibration, profile and path-length boundaries", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if either source identity changes; if a registered measurement, control or limitation is omitted; "
        "if the water measured interval leaves the complete reported relativistic-systematics bracket; if ordinary "
        "addition is at least as close as both relativistic rows; if the air control no longer disfavors ordinary "
        "addition; if any target changes the sealed operation; or if a precision confirmation is claimed beyond the source."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "PDF_HASH",
    "PDF_PATH", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
