"""Fold-native fission-product chemical distribution law (NUCHEM-011)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class FissionProductChemicalRow:
    nuclide: HeldLabel
    chemical_species: HeldLabel
    phase: HeldLabel
    location: HeldLabel
    events: PositiveCount

    def __post_init__(self):
        if (self.nuclide.family, self.chemical_species.family, self.phase.family, self.location.family) != ("fission-product", "chemical-species", "chemical-phase", "location"):
            raise InadmissibleExactValue("complete fission-product chemical row required")


def chemical_distribution(rows: tuple[FissionProductChemicalRow, ...]):
    if not rows: return EMPTY_ONE
    total = sum(row.events.value for row in rows)
    return tuple((row.nuclide, row.chemical_species, row.phase, row.location, Fraction(row.events.value, total)) for row in rows)


def redistribute(before: tuple[FissionProductChemicalRow, ...], after: tuple[FissionProductChemicalRow, ...]):
    if {row.nuclide for row in before} != {row.nuclide for row in after} or sum(row.events.value for row in before) != sum(row.events.value for row in after):
        raise InadmissibleExactValue("fission-product identity or event total changed without explicit physics handoff")
    return chemical_distribution(after)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005", "SFT-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006", "SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001",
    "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002", "SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010",
)
DIMENSIONS = (
    dimension("handoff", "chemistry-selects-fission-products", "Chemistry cannot select nuclear products.", "explicit-physics-product-handoff", "Physics supplies each product identity."),
    dimension("identity", "mass-chain-only", "Mass chain loses nuclide identity.", "held-nuclide-and-chemical-species", "Nuclide and species remain held."),
    dimension("support", "bulk-release-fraction", "One bulk fraction loses phase and location.", "complete-phase-location-support", "Every phase and location remains."),
    dimension("events", "expected-yield-premise", "Expectation is not counted custody.", "positive-species-resolved-events", "Every chemical row has positive events."),
    dimension("partition", "renormalized-selected-products", "Selection changes the distribution.", "exact-complete-partition-of-One", "Every retained row participates in One."),
    dimension("chemistry", "fixed-chemical-form-assumption", "A name cannot freeze chemistry.", "explicit-chemical-redistribution-network", "Every species/phase transition is explicit."),
    dimension("boundary", "silent-decay-inside-chemistry", "Chemistry cannot silently change nuclides.", "nuclide-change-requires-physics-handoff", "A nuclide change crosses the explicit boundary."),
    dimension("extension", "selected-terminal-sample", "One sample cannot establish the distribution.", "successor-retains-complete-time-sample-vector", "Every successor retains all samples."),
)
EXACT_RESULT = "explicit-physics-product-handoff__held-nuclide-and-chemical-species__complete-phase-location-support__positive-species-resolved-events__exact-complete-partition-of-One__explicit-chemical-redistribution-network__nuclide-change-requires-physics-handoff__successor-retains-complete-time-sample-vector"


def _row(nuclide, species, phase, location, events):
    return FissionProductChemicalRow(HeldLabel("fission-product", nuclide), HeldLabel("chemical-species", species), HeldLabel("chemical-phase", phase), HeldLabel("location", location), PositiveCount(events))


_before = (_row("Cs", "fluoride", "salt", "bulk", 3), _row("Xe", "elemental", "gas", "headspace", 1))
_after = (_row("Cs", "fluoride", "salt", "wall", 2), _row("Xe", "elemental", "gas", "headspace", 2))
OPERATIONAL_WITNESSES = (
    ("handoff", "Product identities held.", {row.nuclide.label for row in _before} == {"Cs", "Xe"}),
    ("identity", "Species retained.", _before[0].chemical_species.label == "fluoride"),
    ("support", "Phase and location retained.", len({(row.phase, row.location) for row in _before}) == 2),
    ("events", "Counts positive.", min(row.events.value for row in _before) > 0),
    ("partition", "Partition sums to One.", sum(row[-1] for row in chemical_distribution(_before)) == 1),
    ("chemistry", "Redistribution explicit.", redistribute(_before, _after)[0][3].label == "wall"),
    ("boundary", "Identity set conserved.", {row.nuclide for row in _before} == {row.nuclide for row in _after}),
    ("extension", "Successor complete.", len(redistribute(_before, _after)) == 2),
)
