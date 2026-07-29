"""Fold-native NMR scalar spin-coupling relation (ANAL-007)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class NMRScalarCouplingRecord:
    molecular_carrier: HeldLabel
    first_nucleus_site: HeldLabel
    second_nucleus_site: HeldLabel
    spin_relation: HeldLabel
    bonding_path: PositiveCount
    condition: HeldLabel
    position: PositiveCount
    coupling_magnitude: Fraction | EmptyOne
    uncertainty: Fraction | EmptyOne

    def __post_init__(self) -> None:
        if (
            self.molecular_carrier.family,
            self.first_nucleus_site.family,
            self.second_nucleus_site.family,
            self.spin_relation.family,
            self.condition.family,
        ) != ("molecular-carrier", "nucleus-site", "nucleus-site", "spin-relation", "nmr-condition"):
            raise InadmissibleExactValue("complete held scalar-coupling identity required")
        if self.first_nucleus_site == self.second_nucleus_site:
            raise InadmissibleExactValue("scalar coupling requires two retained sites")
        if self.spin_relation.label not in {"preserving-hand", "alternating-hand", "unresolved-hand"}:
            raise InadmissibleExactValue("spin-coupling relation is not generated")
        if self.coupling_magnitude != EMPTY_ONE and (
            not isinstance(self.coupling_magnitude, Fraction) or self.coupling_magnitude <= 0
        ):
            raise InadmissibleExactValue("resolved coupling magnitude must be exact and positive")
        if self.uncertainty != EMPTY_ONE and (
            not isinstance(self.uncertainty, Fraction) or self.uncertainty <= 0
        ):
            raise InadmissibleExactValue("coupling uncertainty must be positive or structurally absent")

    @property
    def unordered_site_pair(self) -> frozenset[HeldLabel]:
        return frozenset((self.first_nucleus_site, self.second_nucleus_site))


def complete_coupling_vector(rows: tuple[NMRScalarCouplingRecord, ...]) -> tuple[NMRScalarCouplingRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("scalar-coupling vector must be complete and ordered")
    if len({(row.unordered_site_pair, row.bonding_path, row.spin_relation) for row in rows}) != len(rows):
        raise InadmissibleExactValue("scalar-coupling vector duplicated a generated pair/path relation")
    if len({(row.molecular_carrier, row.condition) for row in rows}) != 1:
        raise InadmissibleExactValue("scalar-coupling vector crossed its molecular condition boundary")
    return rows


def site_swap_preserves_coupling(row: NMRScalarCouplingRecord) -> bool:
    swapped = NMRScalarCouplingRecord(
        row.molecular_carrier, row.second_nucleus_site, row.first_nucleus_site,
        row.spin_relation, row.bonding_path, row.condition, row.position,
        row.coupling_magnitude, row.uncertainty,
    )
    return swapped.unordered_site_pair == row.unordered_site_pair and swapped.coupling_magnitude == row.coupling_magnitude


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001",
    "SFT-CHEM-NMR-CHEMICAL-SHIFT-006",
)
DIMENSIONS = (
    dimension("pair", "single-peak-coupling-label", "Coupling is a relation between two retained sites.", "held-two-nucleus-site-pair", "Both nucleus-site identities remain."),
    dimension("spin", "unsigned-magnitude-only", "Magnitude alone loses the held spin hand.", "held-preserving-alternating-or-unresolved-spin-relation", "The spin relation remains a label rather than a signed proof value."),
    dimension("path", "coupling-without-bonding-path", "A detached value cannot establish molecular connectivity.", "positive-counted-bonding-path", "The declared bonding path remains held."),
    dimension("environment", "unconditioned-universal-coupling", "The reported value is condition-bound.", "held-molecule-and-condition", "Molecular carrier and measurement condition remain."),
    dimension("magnitude", "floating-or-fitted-coupling", "A float or fitted equation cannot force the relation.", "exact-positive-magnitude-or-EmptyOne", "Measured magnitude is exact positive support or unresolved absence."),
    dimension("symmetry", "ordered-pair-changes-value", "Relabelling the pair cannot alter a scalar coupling.", "site-swap-invariant-pair-relation", "Pair exchange preserves magnitude and path."),
    dimension("custody", "selected-couplings-only", "Selection hides limits and adverse rows.", "complete-value-error-bound-and-absence-custody", "Every value, error, bound, absent and unresolved row remains."),
    dimension("extension", "refitted-added-couplings", "Refitting can change earlier records.", "successor-retains-and-appends-complete-pairs", "New pairs append without altering prior relations."),
)
EXACT_RESULT = "held-two-nucleus-site-pair__held-preserving-alternating-or-unresolved-spin-relation__positive-counted-bonding-path__held-molecule-and-condition__exact-positive-magnitude-or-EmptyOne__site-swap-invariant-pair-relation__complete-value-error-bound-and-absence-custody__successor-retains-and-appends-complete-pairs"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_condition = HeldLabel("nmr-condition", "condition-a")
_site_a = HeldLabel("nucleus-site", "site-a")
_site_b = HeldLabel("nucleus-site", "site-b")
_site_c = HeldLabel("nucleus-site", "site-c")
_rows = (
    NMRScalarCouplingRecord(_carrier, _site_a, _site_b, HeldLabel("spin-relation", "preserving-hand"), PositiveCount(2), _condition, PositiveCount(1), Fraction(7, 2), Fraction(1, 10)),
    NMRScalarCouplingRecord(_carrier, _site_b, _site_c, HeldLabel("spin-relation", "unresolved-hand"), PositiveCount(3), _condition, PositiveCount(2), EMPTY_ONE, EMPTY_ONE),
)
_vector = complete_coupling_vector(_rows)
OPERATIONAL_WITNESSES = (
    ("pair", "Two distinct site pairs retained.", len({row.unordered_site_pair for row in _vector}) == 2),
    ("spin", "Spin hands retained.", tuple(row.spin_relation.label for row in _vector) == ("preserving-hand", "unresolved-hand")),
    ("path", "Positive paths retained.", tuple(row.bonding_path.value for row in _vector) == (2, 3)),
    ("environment", "Molecule and condition retained.", all(row.molecular_carrier == _carrier and row.condition == _condition for row in _vector)),
    ("magnitude", "Resolved and absent magnitudes distinct.", _vector[0].coupling_magnitude == Fraction(7, 2) and _vector[1].coupling_magnitude == EMPTY_ONE),
    ("symmetry", "Site swap preserves scalar relation.", site_swap_preserves_coupling(_vector[0])),
    ("custody", "Error and unresolved rows retained.", _vector[0].uncertainty == Fraction(1, 10) and _vector[1].uncertainty == EMPTY_ONE),
    ("extension", "Complete successor appends a pair.", len(complete_coupling_vector(_rows + (NMRScalarCouplingRecord(_carrier, _site_a, _site_c, HeldLabel("spin-relation", "alternating-hand"), PositiveCount(4), _condition, PositiveCount(3), Fraction(1, 2), EMPTY_ONE),))) == 3),
)
