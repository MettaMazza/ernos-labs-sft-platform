"""Fold-native defect chemistry and non-stoichiometry law (INORG-016)."""
from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from math import gcd

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ExactFormulaEntry:
    species: HeldLabel
    count: PositiveCount

    def __post_init__(self) -> None:
        if self.species.family != "chemical-species":
            raise InadmissibleExactValue("formula entry requires a retained chemical species")


@dataclass(frozen=True)
class ReferenceSite:
    site: HeldLabel
    expected_species: HeldLabel

    def __post_init__(self) -> None:
        if self.site.family != "reference-solid-site":
            raise InadmissibleExactValue("reference site identity is invalid")
        if self.expected_species.family != "chemical-species":
            raise InadmissibleExactValue("reference site requires one expected species")


@dataclass(frozen=True)
class SiteOccupancy:
    reference: ReferenceSite
    occupant: object

    def __post_init__(self) -> None:
        if not isinstance(self.occupant, EmptyOne) and (
            not isinstance(self.occupant, HeldLabel) or self.occupant.family != "species-occurrence"
        ):
            raise InadmissibleExactValue("site occupant must be a retained occurrence or structural EmptyOne")


@dataclass(frozen=True)
class InterstitialOccurrence:
    site: HeldLabel
    occurrence: HeldLabel

    def __post_init__(self) -> None:
        if self.site.family != "interstitial-solid-site":
            raise InadmissibleExactValue("interstitial site identity is invalid")
        if self.occurrence.family != "species-occurrence":
            raise InadmissibleExactValue("interstitial support requires a species occurrence")


@dataclass(frozen=True)
class SpeciesReconciliation:
    species: HeldLabel
    reference_count: object
    observed_count: object
    missing_support: object
    added_support: object

    def __post_init__(self) -> None:
        if self.species.family != "chemical-species":
            raise InadmissibleExactValue("reconciliation species is invalid")
        for value in (
            self.reference_count,
            self.observed_count,
            self.missing_support,
            self.added_support,
        ):
            if not isinstance(value, (PositiveCount, EmptyOne)):
                raise InadmissibleExactValue("counts must be positive or structural EmptyOne")
        if not isinstance(self.missing_support, EmptyOne) and not isinstance(self.added_support, EmptyOne):
            raise InadmissibleExactValue("one species cannot be both missing and added")


@dataclass(frozen=True)
class ExactDefectChemistry:
    motif: HeldLabel
    reference_sites: tuple[ReferenceSite, ...]
    site_occupancies: tuple[SiteOccupancy, ...]
    interstitials: tuple[InterstitialOccurrence, ...]
    reference_formula: tuple[ExactFormulaEntry, ...]
    observed_formula: tuple[ExactFormulaEntry, ...]
    reconciliation: tuple[SpeciesReconciliation, ...]
    defect_classes: object
    origin_class: object

    def __post_init__(self) -> None:
        if self.motif.family != "local-solid-motif":
            raise InadmissibleExactValue("defect chemistry requires one local solid motif")
        if not self.reference_sites or len(set(self.reference_sites)) != len(self.reference_sites):
            raise InadmissibleExactValue("reference support must be positive, finite and complete")
        if tuple(row.reference for row in self.site_occupancies) != self.reference_sites:
            raise InadmissibleExactValue("every reference site requires exactly one occupancy record")
        if len({row.site for row in self.interstitials}) != len(self.interstitials):
            raise InadmissibleExactValue("interstitial site support is duplicated")
        if self.reference_formula != primitive_formula(
            tuple(site.expected_species.label for site in self.reference_sites)
        ):
            raise InadmissibleExactValue("reference formula is not the exact primitive site ratio")
        observed_labels = tuple(
            occurrence_species(row.occupant)
            for row in self.site_occupancies
            if not isinstance(row.occupant, EmptyOne)
        ) + tuple(occurrence_species(row.occurrence) for row in self.interstitials)
        if not observed_labels:
            raise InadmissibleExactValue("an observed local motif must retain positive chemical support")
        if self.observed_formula != primitive_formula(observed_labels):
            raise InadmissibleExactValue("observed formula is not the exact primitive occurrence ratio")
        if self.reconciliation != reconcile_species(self.reference_sites, self.site_occupancies, self.interstitials):
            raise InadmissibleExactValue("reference and observed supports do not reconcile exactly")
        expected_classes = classify_defects(self.site_occupancies, self.interstitials)
        if self.defect_classes != expected_classes:
            raise InadmissibleExactValue("defect class support is incomplete")
        if self.origin_class != classify_origin(self.reference_sites, self.site_occupancies, self.interstitials):
            raise InadmissibleExactValue("intrinsic/extrinsic composition classification changed")


def species(label: str) -> HeldLabel:
    return HeldLabel("chemical-species", label)


def occurrence(species_label: str, occurrence_label: str) -> HeldLabel:
    return HeldLabel("species-occurrence", f"{species_label}#{occurrence_label}")


def occurrence_species(value: object) -> str:
    if not isinstance(value, HeldLabel) or value.family != "species-occurrence" or "#" not in value.label:
        raise InadmissibleExactValue("species occurrence is malformed")
    return value.label.split("#", 1)[0]


def positive_or_empty(value: int) -> object:
    return EMPTY_ONE if value == 0 else PositiveCount(value)


def primitive_formula(labels: tuple[str, ...]) -> tuple[ExactFormulaEntry, ...]:
    if not labels:
        raise InadmissibleExactValue("a formula requires positive occurrence support")
    ordered = tuple(dict.fromkeys(labels))
    counts = tuple(sum(label == candidate for label in labels) for candidate in ordered)
    divisor = reduce(gcd, counts)
    return tuple(
        ExactFormulaEntry(species(label), PositiveCount(count // divisor))
        for label, count in zip(ordered, counts)
    )


def reconcile_species(
    reference_sites: tuple[ReferenceSite, ...],
    occupancies: tuple[SiteOccupancy, ...],
    interstitials: tuple[InterstitialOccurrence, ...],
) -> tuple[SpeciesReconciliation, ...]:
    reference_labels = tuple(site.expected_species.label for site in reference_sites)
    observed_labels = tuple(
        occurrence_species(row.occupant)
        for row in occupancies
        if not isinstance(row.occupant, EmptyOne)
    ) + tuple(occurrence_species(row.occurrence) for row in interstitials)
    labels = tuple(dict.fromkeys(reference_labels + observed_labels))
    rows = []
    for label in labels:
        reference_count = sum(item == label for item in reference_labels)
        observed_count = sum(item == label for item in observed_labels)
        rows.append(
            SpeciesReconciliation(
                species(label),
                positive_or_empty(reference_count),
                positive_or_empty(observed_count),
                positive_or_empty(reference_count - observed_count) if reference_count > observed_count else EMPTY_ONE,
                positive_or_empty(observed_count - reference_count) if observed_count > reference_count else EMPTY_ONE,
            )
        )
    return tuple(rows)


def classify_defects(
    occupancies: tuple[SiteOccupancy, ...], interstitials: tuple[InterstitialOccurrence, ...]
) -> object:
    classes = []
    if any(isinstance(row.occupant, EmptyOne) for row in occupancies):
        classes.append(HeldLabel("defect-class", "vacancy"))
    if any(
        not isinstance(row.occupant, EmptyOne)
        and occurrence_species(row.occupant) != row.reference.expected_species.label
        for row in occupancies
    ):
        classes.append(HeldLabel("defect-class", "substitution"))
    if interstitials:
        classes.append(HeldLabel("defect-class", "interstitial"))
    return tuple(classes) if classes else EMPTY_ONE


def classify_origin(
    reference_sites: tuple[ReferenceSite, ...],
    occupancies: tuple[SiteOccupancy, ...],
    interstitials: tuple[InterstitialOccurrence, ...],
) -> object:
    if isinstance(classify_defects(occupancies, interstitials), EmptyOne):
        return EMPTY_ONE
    reference_species = {site.expected_species.label for site in reference_sites}
    observed_species = {
        occurrence_species(row.occupant)
        for row in occupancies
        if not isinstance(row.occupant, EmptyOne)
    } | {occurrence_species(row.occurrence) for row in interstitials}
    return HeldLabel(
        "defect-origin",
        "extrinsic" if observed_species.difference(reference_species) else "intrinsic",
    )


def defect_state(
    motif: str,
    expected_species: tuple[str, ...],
    occupied_species: tuple[object, ...],
    interstitial_species: tuple[str, ...] = (),
) -> ExactDefectChemistry:
    if len(expected_species) != len(occupied_species):
        raise InadmissibleExactValue("reference and occupancy boundaries differ")
    references = tuple(
        ReferenceSite(HeldLabel("reference-solid-site", f"site-{index}"), species(label))
        for index, label in enumerate(expected_species, 1)
    )
    occupancies = tuple(
        SiteOccupancy(
            reference,
            EMPTY_ONE
            if isinstance(observed, EmptyOne)
            else occurrence(str(observed), f"site-{index}"),
        )
        for index, (reference, observed) in enumerate(zip(references, occupied_species), 1)
    )
    interstitials = tuple(
        InterstitialOccurrence(
            HeldLabel("interstitial-solid-site", f"interstitial-{index}"),
            occurrence(label, f"interstitial-{index}"),
        )
        for index, label in enumerate(interstitial_species, 1)
    )
    observed_labels = tuple(
        occurrence_species(row.occupant)
        for row in occupancies
        if not isinstance(row.occupant, EmptyOne)
    ) + tuple(occurrence_species(row.occurrence) for row in interstitials)
    return ExactDefectChemistry(
        HeldLabel("local-solid-motif", motif),
        references,
        occupancies,
        interstitials,
        primitive_formula(expected_species),
        primitive_formula(observed_labels),
        reconcile_species(references, occupancies, interstitials),
        classify_defects(occupancies, interstitials),
        classify_origin(references, occupancies, interstitials),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-MEAS-FORMULA-001",
    "SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "continuum-defect-density",
        "A continuum density loses the exact local defect occurrences.",
        "finite-complete-reference-and-observed-motif",
        "The law retains one finite complete reference motif and one complete observed motif.",
    ),
    dimension(
        "reference",
        "nominal-formula-only",
        "A nominal formula does not identify the occupied sites.",
        "complete-reference-site-and-species-support",
        "Every reference site and its expected species are explicit.",
    ),
    dimension(
        "vacancy",
        "numerical-zero-occupancy",
        "Numerical zero is not a Fold form.",
        "reference-site-with-structural-EmptyOne",
        "A vacancy is an exact reference site whose occupant is structural EmptyOne.",
    ),
    dimension(
        "difference",
        "signed-stoichiometric-subtraction",
        "Signed subtraction imports negative values.",
        "separate-positive-missing-and-added-supports",
        "Missing and added occurrences are separate positive supports or EmptyOne.",
    ),
    dimension(
        "class",
        "selected-defect-name",
        "A selected name omits alternative interruptions.",
        "complete-vacancy-substitution-interstitial-classes",
        "Vacancy, substitution and interstitial classes are generated from exact support.",
    ),
    dimension(
        "composition",
        "fitted-nonstoichiometric-variable",
        "A fitted variable is neither exact nor unique.",
        "exact-reference-observed-primitive-formulas",
        "Reference and observed formulas are exact primitive positive count vectors.",
    ),
    dimension(
        "origin",
        "assumed-intrinsic-or-extrinsic-label",
        "An assumed label does not follow from composition.",
        "reference-membership-forces-origin-class",
        "Foreign observed species force extrinsic; reference-only defects force intrinsic.",
    ),
    dimension(
        "extension",
        "catalogue-specific-defect-exception",
        "A catalogue exception destroys closure.",
        "site-occurrence-successor-no-extra-rule",
        "Fresh sites and occurrences are reconciled by the same exact law.",
    ),
)


def _operational_witnesses() -> tuple[tuple[str, str, bool], ...]:
    pristine = defect_state("AB", ("A", "A", "B", "B"), ("A", "A", "B", "B"))
    vacancy = defect_state("A-vacancy", ("A", "A", "B", "B"), ("A", EMPTY_ONE, "B", "B"))
    interstitial = defect_state(
        "native-interstitial",
        ("A", "A", "B", "B"),
        ("A", "A", "B", "B"),
        ("A",),
    )
    substitution = defect_state("foreign-substitution", ("A", "A", "B", "B"), ("A", "C", "B", "B"))
    vacancy_a = next(row for row in vacancy.reconciliation if row.species.label == "A")
    return (
        (
            "pristine-absence",
            "A complete unchanged motif has structural EmptyOne defect support.",
            isinstance(pristine.defect_classes, EmptyOne),
        ),
        (
            "vacancy",
            "One absent A occupant is a vacancy with one positive missing A and no signed count.",
            vacancy_a.missing_support == PositiveCount(1)
            and isinstance(vacancy_a.added_support, EmptyOne)
            and vacancy.origin_class == HeldLabel("defect-origin", "intrinsic"),
        ),
        (
            "interstitial",
            "One native interstitial is exact added support and remains intrinsic.",
            interstitial.defect_classes == (HeldLabel("defect-class", "interstitial"),)
            and interstitial.origin_class == HeldLabel("defect-origin", "intrinsic"),
        ),
        (
            "substitution",
            "A foreign occupant forces substitution and extrinsic origin.",
            substitution.defect_classes == (HeldLabel("defect-class", "substitution"),)
            and substitution.origin_class == HeldLabel("defect-origin", "extrinsic"),
        ),
    )


OPERATIONAL_WITNESSES = _operational_witnesses()
EXACT_RESULT = (
    "finite-complete-reference-and-observed-motif__complete-reference-site-and-species-support__"
    "reference-site-with-structural-EmptyOne__separate-positive-missing-and-added-supports__"
    "complete-vacancy-substitution-interstitial-classes__exact-reference-observed-primitive-formulas__"
    "reference-membership-forces-origin-class__site-occurrence-successor-no-extra-rule"
)

__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EMPTY_ONE",
    "EXACT_RESULT",
    "ExactDefectChemistry",
    "ExactFormulaEntry",
    "InterstitialOccurrence",
    "OPERATIONAL_WITNESSES",
    "ReferenceSite",
    "SiteOccupancy",
    "SpeciesReconciliation",
    "classify_defects",
    "classify_origin",
    "defect_state",
    "occurrence",
    "occurrence_species",
    "primitive_formula",
    "reconcile_species",
    "species",
)
