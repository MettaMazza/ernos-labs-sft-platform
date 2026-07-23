"""Measurement and metrology laws derived after the empirical prerequisites."""

from __future__ import annotations

from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)


SOURCE_PATH = "experiments/external_sources/physics/snapshots/bipm-si-brochure-9-en.pdf"
SOURCE_HASH = "sha256:5442eea2c680caf77a9d96879205a97f57c7c270b98a0bd0126c18fefe47e02c"
SOURCE_ID = "BIPM-SI-BROCHURE-9-2026"

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
    "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
)


def targets(prefix: str, label: str, *locators: str) -> tuple[ExternalTargetRow, ...]:
    return tuple(
        ExternalTargetRow(f"{prefix}-{position}", SOURCE_ID, locator, label)
        for position, locator in enumerate(locators, 1)
    )


def spec(
    claim_id: str,
    title: str,
    statement: str,
    relation_name: str,
    relation_reason: str,
    result: str,
    label: str,
    dependencies: tuple[str, ...],
    *locators: str,
) -> EmpiricalPhysicsSpec:
    slug = claim_id.removeprefix("SFT-PHYS-MEAS-").removesuffix("-001")
    return EmpiricalPhysicsSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        generation_rule=(
            "Generate the complete product of carrier, relation, provenance, prediction access, "
            "measurement record, row retention, finite generality and extra-rule forms."
        ),
        grammar_boundary=(
            "All measurement relations assembled from admitted Fold distinctions, exact reference pairing, "
            "held observation records, target-inaccessible execution and finite generated support."
        ),
        dimensions=empirical_dimensions(relation_name, relation_reason),
        exact_result=result,
        induction_base="One observed distinction is paired with one held reference and produces one source-bound comparison record.",
        induction_step="Adding one generated observation or reference appends one named exact pairing and one retained record without changing prior pairings or importing a scale.",
        exclusions=(
            "semantic numerical zero, negative proof magnitude, irrational, imaginary or floating proof value",
            "measurement target access before prediction seal",
            "a conventional unit, equation or measured constant selecting the Fold relation",
            "selected favorable rows, free scales and fitted parameters",
        ),
        operational_witnesses=(
            ("one-reference-pair", "One observation and one reference retain two named source coordinates and one pairing.", len((("observation", "reference"),)) == 1),
            ("successor-retention", "Appending a second named pairing leaves the first pairing unchanged.", (("a", "r-a"), ("b", "r-b"))[0] == ("a", "r-a")),
        ),
        experiment_id=f"SFT-EXP-PHYS-MEAS-{slug}-001",
        expected_observation_label=label,
        target_rows=targets(slug.lower(), label, *locators),
        source_snapshot_path=SOURCE_PATH,
        source_snapshot_hash=SOURCE_HASH,
        falsification_condition=(
            "The claim is falsified within this registered standards boundary if any committed BIPM target row "
            "does not exhibit the predicted structural label, if any row is omitted, or if the tampered control is accepted."
        ),
    )


OBSERVATION_CARRIER = spec(
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "Physical observation and retained distinction",
    "A physical observation is forced to retain a distinguishable phenomenon, a held reference condition and the exact comparison record; an answer without those three coordinates is not an admitted physical observation.",
    "distinction-reference-record",
    "A distinction alone has no physical reference, while reference alone has no observed distinction; their retained pairing produces the minimal complete observation.",
    "The unique observation carrier is a source-bound phenomenon/reference pairing plus its held comparison record, executed without target access and with every row retained.",
    "distinction-reference-comparison-record",
    BASE_DEPENDENCIES,
    "SI Brochure section 2.1: defining the unit of a quantity",
    "SI Brochure section 5.4: expressing values of quantities",
)

QUANTITY_CARRIER = spec(
    "SFT-PHYS-MEAS-QUANTITY-CARRIER-001",
    "Physical quantity as reference-equivalence carrier",
    "A physical quantity is forced as the equivalence class of observations comparable through one generated kind-preserving reference relation; its measured value is a separate record, not the quantity itself.",
    "kind-preserving-reference-equivalence",
    "Only kind-preserving reference equivalence permits different observations to denote one physical quantity without erasing their distinct records.",
    "The physical quantity carrier is the complete class of observations connected by a kind-preserving reference equivalence, with measured values retained separately.",
    "property-kind-reference-equivalence",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",),
    "SI Brochure section 1.1: quantities and units",
    "SI Brochure section 2.1: value of a quantity",
)

DIMENSION_COMPOSITION = spec(
    "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    "Dimension composition and independence",
    "A physical dimension is forced as the canonical generated composition path of independent quantity kinds; two descriptions share a dimension exactly when their paths reduce to the same held form.",
    "canonical-dimension-path",
    "A canonical generated composition path preserves independent kinds and makes equality decidable without importing a scalar field.",
    "Dimensions are canonical finite products and exact quotients of independent quantity-kind carriers, compared by form identity rather than numerical value.",
    "canonical-generated-dimension-composition",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-QUANTITY-CARRIER-001",),
    "SI Brochure section 2.3.1: base quantities and dimensions",
    "SI Brochure section 2.3.2: derived quantities and dimensions",
)

UNIT_COMPARISON = spec(
    "SFT-PHYS-MEAS-UNIT-COMPARISON-001",
    "Unit comparison and exact scale transport",
    "A unit is forced as one held reference quantity used to compare quantities of the same dimension; lawful scale transport is witnessed by an exact positive part ratio and cannot change dimension.",
    "same-dimension-reference-ratio",
    "Only a same-dimension reference with an exact pairing ratio permits reproducible comparison without changing the quantity kind.",
    "A unit comparison pairs a quantity with a held same-dimension reference and records an exact positive ratio; conversions compose those ratios and preserve dimension.",
    "same-dimension-reference-comparison",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",),
    "SI Brochure section 2.1: definition of a unit",
    "SI Brochure section 2.2: SI units",
)

REFERENCE_REALIZATION = spec(
    "SFT-PHYS-MEAS-REFERENCE-REALIZATION-001",
    "Reference realization and traceability",
    "A physical reference is forced to be operationally realized by a finite reproducible comparison process whose complete trace connects the definition to the observation; a name or assigned scalar alone is not a realization.",
    "definition-to-operation-trace",
    "The definition-to-operation trace is the only form that lets independent observers reproduce and audit the same reference.",
    "Reference realization is a complete finite operational trace from the held definition through each comparison to the observed record.",
    "definition-realized-by-reproducible-operation",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-UNIT-COMPARISON-001",),
    "SI Brochure section 1.3: implementation of the SI",
    "SI Brochure Appendix 2: practical realization of unit definitions",
)

VALUE_RECORD = spec(
    "SFT-PHYS-MEAS-VALUE-RECORD-001",
    "Measured-value record separated from proof value",
    "A measured value is forced as a held external record containing the exact reference identity, reported numerical inscription and observation provenance; the inscription never enters the proof as an SFT scalar.",
    "held-reference-number-provenance-record",
    "Retaining reference, inscription and provenance is minimal for interpreting and independently checking a reported value without importing it into the proof domain.",
    "The measured-value record holds the external number inscription, unit/reference identity and observation provenance while the derivation remains exact and separate.",
    "number-unit-provenance-measurement-record",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-REFERENCE-REALIZATION-001",),
    "SI Brochure section 5.4.1: quantity values and numerical values",
    "SI Brochure section 5.4.5: expressing measurement uncertainty",
)

UNCERTAINTY = spec(
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "Measurement uncertainty as retained admissible alternatives",
    "Measurement uncertainty is forced as the explicitly retained support of observation/reference distinctions not closed by the measurement process; it is not an irrational proof value or permission to choose a favorable result.",
    "retained-unresolved-observation-support",
    "The unresolved support exactly records what the measurement failed to distinguish and therefore preserves rather than invents uncertainty.",
    "Uncertainty is the source-bound set of still-admissible observation/reference relations, reported with the measured record and retained in full.",
    "retained-range-and-uncertainty-components",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-VALUE-RECORD-001",),
    "SI Brochure section 5.4.5: expressing measurement uncertainty",
    "SI Brochure Appendix 2: uncertainties of practical realizations",
)

CALIBRATION = spec(
    "SFT-PHYS-MEAS-CALIBRATION-001",
    "Calibration chain and comparison closure",
    "Calibration is forced as the finite compositional chain of exact reference comparisons connecting an instrument record to the realized unit, with every intermediate identity and uncertainty support retained.",
    "complete-composed-reference-chain",
    "Only the complete composed chain preserves traceability and exposes any changed or missing comparison.",
    "A calibration is the complete ordered composition of source-bound reference comparisons, closing at the realized unit and retaining every intermediate record.",
    "traceable-comparison-chain",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-UNCERTAINTY-001",),
    "SI Brochure section 1.3: dissemination and realization",
    "SI Brochure Appendix 2: practical realization chains",
)

DIMENSIONAL_CONSISTENCY = spec(
    "SFT-PHYS-MEAS-DIMENSIONAL-CONSISTENCY-001",
    "Dimensional consistency and lawful conversion",
    "A physical relation is dimensionally lawful exactly when every compared or joined path has the same canonical dimension form and every conversion is a reversible exact same-dimension reference map.",
    "canonical-path-identity-and-reversible-conversion",
    "Canonical path identity prevents unlike quantity kinds from being equated, while reversible reference maps preserve both information and dimension.",
    "Dimensional consistency is exact canonical path identity at every comparison, with conversions restricted to reversible same-dimension reference ratios.",
    "same-dimension-relation-and-conversion",
    BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-CALIBRATION-001",),
    "SI Brochure section 2.3.2: coherent derived units",
    "SI Brochure section 5.4.6: multiplying and dividing quantity symbols and values",
)


MEASUREMENT_SPECS = (
    OBSERVATION_CARRIER,
    QUANTITY_CARRIER,
    DIMENSION_COMPOSITION,
    UNIT_COMPARISON,
    REFERENCE_REALIZATION,
    VALUE_RECORD,
    UNCERTAINTY,
    CALIBRATION,
    DIMENSIONAL_CONSISTENCY,
)

for _spec in MEASUREMENT_SPECS:
    _spec.validate()

__all__ = ("MEASUREMENT_SPECS",)
