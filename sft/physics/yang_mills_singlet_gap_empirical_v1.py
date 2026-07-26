"""Post-seal external spectrum boundary for the Fold singlet-gap theorem."""

from __future__ import annotations

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.yang_mills_singlet_gap_terminal_law_v1 import (
    physical_singlet_support,
    singlet_gap_trace,
    strong_gap_partition,
)


CLAIM_ID = "SFT-PHYS-YANG-MILLS-SINGLET-GAP-EMPIRICAL-027"
EXPERIMENT_ID = "SFT-EXP-PHYS-YANG-MILLS-SINGLET-GAP-EMPIRICAL-027"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/yang-mills-singlet-gap-source-record.json"
SOURCE_HASH = "sha256:cf0ccdbcb6d2fe3c69a5b64f07da0b9e5aef93c7d32654b341ec2eb1397ae75c"
PDG_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-quark-model.pdf"
PDG_HASH = "sha256:6aa98fa53857122f27b638c59081af1a2857d787c4205370d8fa38fcb6b70ff0"
SOURCE_IDS = ("PDG-2026-QUARK-MODEL-GLUEBALL-BOUNDARY",)
OBSERVATION_LABEL = (
    "positive-physical-colour-singlet-gap__all-registered-pure-gauge-"
    "glueball-intervals-positive__ground-and-excitation-order-retained__"
    "quenched-mixing-full-QCD-and-nonidentification-boundaries-retained__"
    "no-dimensional-fit"
)


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    """Use the common generated grammar while preserving historical provenance."""

    @property
    def registration(self):
        return replace(
            super().registration,
            provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
        )


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal lattice-spectrum boundary for the colour-singlet gap",
    statement=(
        "The independently admitted Fold theorem predicts only that the least "
        "physical colour-singlet excitation is positively separated from the "
        "empty excitation record; it does not predict a dimensionful glueball "
        "mass.  After the prediction is sealed, the complete registered PDG 2026 "
        "pure-gauge lattice spectrum is opened.  Its scalar ground-state interval "
        "and every retained tensor/pseudoscalar excitation interval lie strictly "
        "above the empty boundary and remain strictly ordered.  The quenched-"
        "approximation, mixing, full-QCD and unresolved experimental-identification "
        "limitations are mandatory parts of the result."
    ),
    dependencies=(
        "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of physical carrier, positive-"
        "gap relation, provenance, prediction isolation, measurement separation, "
        "complete spectrum-row retention, finite successor closure and extension."
    ),
    grammar_boundary=(
        "The admitted finite Fold colour-singlet gap and every registered PDG 2026 "
        "pure-gauge glueball mass/uncertainty row, ground/excitation ordering row, "
        "quenched, mixing, full-QCD and experimental-identification limitation."
    ),
    dimensions=empirical_dimensions(
        "positive-colour-singlet-gap-with-complete-spectrum-scope",
        "The formal Fold law fixes positivity before the external lattice values and their limitations are opened.",
    ),
    exact_result=(
        "The sealed Fold prediction of a positive physical colour-singlet gap "
        "matches every retained PDG pure-gauge lattice interval: 0++ at 1653+/-26 "
        "MeV, 2++ at 2376+/-32 MeV and 0-+ at 2561+/-40 MeV are each strictly "
        "positive and their intervals are ordered and disjoint.  These are external "
        "lattice records, not fitted Fold values.  Quenching, state mixing, full-QCD "
        "requirements and the lack of an unambiguous experimental glueball remain "
        "explicit boundaries."
    ),
    induction_base=(
        "The least Fold colour singlet has exact positive normalized gap one-third "
        "before any dimensionful spectrum row is opened."
    ),
    induction_step=(
        "Every positive finite Fold successor retains the one-third gap and adds "
        "positive confinement work; opening another registered external spectrum "
        "row changes neither the formal law nor its source separation."
    ),
    exclusions=(
        "no PDG, lattice mass, uncertainty or quantum-number ordering in the formal predecessor derivation",
        "no claim that normalized one-third equals 1653 MeV or any dimensionful mass",
        "no omission of quenched, mixing, full-QCD or unresolved-identification limitations",
        "no claim of direct experimental glueball detection or conventional continuum Yang-Mills proof",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
        "no target access before the prediction seal and no fitted correction",
    ),
    operational_witnesses=(
        ("positive-gap", "The formal normalized gap is exact positive one-third.", str(strong_gap_partition()["gap"]) == "1/3"),
        ("physical-singlet", "The least observable colour support is a nonempty antipodal pair.", physical_singlet_support()["least_singlet_constituents"] == 2),
        ("all-finite-successors", "The formal gap remains positive while confinement work increases.", singlet_gap_trace(20)["all_gaps_positive"] and singlet_gap_trace(20)["work_positive_and_increasing"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-GLUEBALL-0PP-POSITIVE", SOURCE_IDS[0], "pages 11-12 scalar ground-state and precise 0++ row", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-GLUEBALL-2PP-POSITIVE", SOURCE_IDS[0], "page 12 precise 2++ row", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-GLUEBALL-0MP-POSITIVE", SOURCE_IDS[0], "page 12 precise 0-+ row", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-GLUEBALL-ORDER", SOURCE_IDS[0], "pages 11-12 ground/first-excitation ordering", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-GLUEBALL-THEORY-SCOPE", SOURCE_IDS[0], "pages 11 and 32 quenched, mixing and full-QCD limitations", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-GLUEBALL-IDENTIFICATION-BOUNDARY", SOURCE_IDS[0], "pages 12 and 32 unresolved predominantly-glueball assignment", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if either source snapshot changes; if any registered spectrum or "
        "limitation row is omitted; if the least retained pure-gauge mass interval "
        "reaches the empty boundary; if registered intervals lose their stated "
        "ordering; if an external mass is imported into the Fold proof; if a "
        "lattice prediction is relabelled as direct detection; or if the target is "
        "available to the capability-closed predictor before sealing."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "OBSERVATION_LABEL",
    "ObservationalEmpiricalPhysicsProgram",
    "PDG_HASH",
    "PDG_PATH",
    "SOURCE_HASH",
    "SOURCE_IDS",
    "SOURCE_PATH",
    "SPEC",
)
