"""Fold-native exact composition of two half-cell potential coordinates (ECHEM-003)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension
from sft.chemistry.electrode_potential_law_v1 import ElectrodePotentialRelation

def _ratio(value: Fraction) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)

def _coordinate(relation: ElectrodePotentialRelation) -> tuple[str, Fraction]:
    direction = relation.orientation.label
    if direction == "coincident-with-reference":
        if relation.separation != EMPTY_ONE:
            raise InadmissibleExactValue("coincident potential must carry structural EmptyOne")
        return "coincident", Fraction(1, 1)
    if not isinstance(relation.separation, PositiveRatio):
        raise InadmissibleExactValue("directed potential requires positive exact separation")
    return direction, relation.separation.fraction

@dataclass(frozen=True)
class CellPotentialComposition:
    source_half_cell: HeldLabel
    terminal_half_cell: HeldLabel
    reaction_path: HeldLabel
    orientation: HeldLabel
    separation: PositiveRatio | EmptyOne
    reference: HeldLabel
    condition: HeldLabel

def compose_cell_potential(source: ElectrodePotentialRelation, terminal: ElectrodePotentialRelation, reaction_path: HeldLabel) -> CellPotentialComposition:
    if source.reference != terminal.reference or source.condition != terminal.condition:
        raise InadmissibleExactValue("cell composition requires common reference and condition")
    if source.subject == terminal.subject:
        raise InadmissibleExactValue("cell requires two distinct half-cell carriers")
    if reaction_path.family != "cell-reaction-path":
        raise InadmissibleExactValue("cell reaction path is missing")
    sd, sm = _coordinate(source); td, tm = _coordinate(terminal)
    if sd == td and sm == tm:
        orientation, separation = "cell-coincident", EMPTY_ONE
    elif sd == "coincident":
        orientation, separation = "toward-terminal-half-cell", _ratio(tm)
    elif td == "coincident":
        orientation, separation = "toward-source-half-cell", _ratio(sm)
    elif sd != td:
        orientation, separation = "toward-terminal-half-cell" if td == "subject-above-reference" else "toward-source-half-cell", _ratio(sm + tm)
    elif tm > sm:
        orientation, separation = "toward-terminal-half-cell", _ratio(tm - sm)
    elif sm > tm:
        orientation, separation = "toward-source-half-cell", _ratio(sm - tm)
    else:
        orientation, separation = "cell-coincident", EMPTY_ONE
    return CellPotentialComposition(source.subject, terminal.subject, reaction_path, HeldLabel("cell-potential-orientation", orientation), separation, source.reference, source.condition)

def reverse_cell(cell: CellPotentialComposition) -> CellPotentialComposition:
    direction = {"toward-terminal-half-cell": "toward-source-half-cell", "toward-source-half-cell": "toward-terminal-half-cell", "cell-coincident": "cell-coincident"}[cell.orientation.label]
    return CellPotentialComposition(cell.terminal_half_cell, cell.source_half_cell, HeldLabel("cell-reaction-path", cell.reaction_path.label + "-reverse"), HeldLabel("cell-potential-orientation", direction), cell.separation, cell.reference, cell.condition)

DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-QUANTUM-REVERSIBLE-MODEL-001",
    "SFT-CHEM-REDOX-COUPLING-001", "SFT-CHEM-ELECTROCHEM-CELL-001",
    "SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001", "SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002",
)
DIMENSIONS = (
    dimension("carriers", "anonymous-voltage-pair", "Anonymous values lose the two chemical half-cells.", "two-distinct-held-half-cell-carriers", "Both half-reaction identities remain explicit."),
    dimension("reference", "mixed-reference-subtraction", "Different references cannot compose directly.", "one-common-held-reference", "Both coordinates share one reference."),
    dimension("condition", "mixed-condition-subtraction", "Different conditions destroy a cell comparison.", "one-common-held-condition", "Both coordinates share one condition."),
    dimension("path", "unordered-potential-difference", "An unordered difference loses reaction direction.", "held-source-terminal-reaction-path", "The complete cell path fixes source and terminal orientation."),
    dimension("composition", "signed-arithmetic-premise", "Signed arithmetic imports negative proof values.", "exact-positive-sum-or-Take-composition", "Opposed coordinates add; aligned coordinates use exact positive Take."),
    dimension("coincidence", "numerical-zero-cell-potential", "Numerical zero is not a native proof magnitude.", "structural-EmptyOne-cell-coincidence", "Equal coordinates close the cell distinction structurally."),
    dimension("record", "selected-cell-voltage", "A selected voltage can conceal half-cell and condition rows.", "complete-full-cell-potential-vector", "Every cell composition and measured row remains downstream."),
    dimension("reverse", "irreversible-sign-flip", "A sign flip does not reconstruct the chemical path.", "exact-cell-reversal-preserves-positive-separation", "Reversal swaps carriers and orientation while retaining magnitude."),
)
EXACT_RESULT = "two-distinct-held-half-cell-carriers__one-common-held-reference__one-common-held-condition__held-source-terminal-reaction-path__exact-positive-sum-or-Take-composition__structural-EmptyOne-cell-coincidence__complete-full-cell-potential-vector__exact-cell-reversal-preserves-positive-separation"

def _relation(name, direction, n):
    return ElectrodePotentialRelation(HeldLabel("electrode-potential-orientation", direction), EMPTY_ONE if direction == "coincident-with-reference" else PositiveRatio.from_pair(n, 1), HeldLabel("half-reaction-identity", name), HeldLabel("half-reaction-identity", "reference"), HeldLabel("electrochemical-condition", "standard"))

def _witnesses():
    path = HeldLabel("cell-reaction-path", "forward")
    opposed = compose_cell_potential(_relation("low", "subject-below-reference", 2), _relation("high", "subject-above-reference", 3), path)
    aligned = compose_cell_potential(_relation("first", "subject-above-reference", 2), _relation("second", "subject-above-reference", 5), path)
    coincident = compose_cell_potential(_relation("first", "subject-above-reference", 2), _relation("second", "subject-above-reference", 2), path)
    reversed_cell = reverse_cell(opposed)
    return (
        ("opposed-sum", "Opposed half-cell coordinates add exactly.", opposed.separation.fraction == 5),
        ("aligned-Take", "Aligned half-cell coordinates compose by positive Take.", aligned.separation.fraction == 3),
        ("path", "Cell path identities remain held.", aligned.reaction_path == path),
        ("coincidence", "Equal coordinates close to EmptyOne.", coincident.separation == EMPTY_ONE),
        ("reverse-carriers", "Reversal swaps source and terminal.", reversed_cell.source_half_cell == opposed.terminal_half_cell and reversed_cell.terminal_half_cell == opposed.source_half_cell),
        ("reverse-direction", "Reversal changes held direction without a negative magnitude.", reversed_cell.orientation.label == "toward-source-half-cell"),
        ("reverse-magnitude", "Reversal preserves exact positive separation.", reversed_cell.separation == opposed.separation),
    )
OPERATIONAL_WITNESSES = _witnesses()
__all__ = ("CellPotentialComposition", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "compose_cell_potential", "reverse_cell")
