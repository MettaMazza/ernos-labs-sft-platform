"""Fold-native coordination-form equivalence and isomer classes for INORG-005."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Union

from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


OrientationCell = Union[HeldLabel, EmptyOne]
AdjacencyExtension = Union[tuple[PositiveCount, ...], EmptyOne]


@dataclass(frozen=True)
class FiniteCoordinationForm:
    composition_labels: tuple[HeldLabel, ...]
    attachment_labels: tuple[HeldLabel, ...]
    orientation_words: tuple[tuple[OrientationCell, OrientationCell, OrientationCell], ...]
    adjacency_pairs: tuple[tuple[PositiveCount, PositiveCount], ...]

    def __post_init__(self) -> None:
        width = len(self.composition_labels)
        if width < 1 or len(self.attachment_labels) != width or len(self.orientation_words) != width:
            raise InadmissibleExactValue("coordination form requires complete positive equal-width support")
        if any(label.family != "coordination-composition-label" for label in self.composition_labels):
            raise InadmissibleExactValue("coordination composition labels are invalid")
        if any(label.family != "coordination-attachment-mode" for label in self.attachment_labels):
            raise InadmissibleExactValue("coordination attachment labels are invalid")
        if any(len(word) != 3 or all(isinstance(cell, EmptyOne) for cell in word) for word in self.orientation_words):
            raise InadmissibleExactValue("every occurrence requires one nonempty three-axis orientation word")
        if any(
            isinstance(cell, HeldLabel)
            and (cell.family != "fold-orientation-fibre" or cell.label not in {"fibre-one", "fibre-two"})
            for word in self.orientation_words
            for cell in word
        ):
            raise InadmissibleExactValue("three axis positions admit only the two forced Fold fibre labels")
        normalized = []
        for first, second in self.adjacency_pairs:
            if not isinstance(first, PositiveCount) or not isinstance(second, PositiveCount):
                raise InadmissibleExactValue("coordination adjacency endpoints require positive counted ordinals")
            if first.value > width or second.value > width or first == second:
                raise InadmissibleExactValue("coordination adjacency endpoint is outside the form")
            normalized.append(tuple(sorted((first.value, second.value))))
        if len(normalized) != len(set(normalized)):
            raise InadmissibleExactValue("coordination adjacency pairs cannot duplicate")


def _cell(cell: OrientationCell) -> str:
    return "EmptyOne" if isinstance(cell, EmptyOne) else f"{cell.family}:{cell.label}"


def _canonical(form: FiniteCoordinationForm, include_orientation: bool = True) -> tuple:
    width = len(form.composition_labels)
    variants = []
    for order in permutations(range(width)):
        old_to_new = {old: new for new, old in enumerate(order, start=1)}
        vertices = tuple(
            (
                form.composition_labels[old].label,
                form.attachment_labels[old].label,
                tuple(_cell(cell) for cell in form.orientation_words[old]) if include_orientation else (),
            )
            for old in order
        )
        edges = tuple(sorted(tuple(sorted((old_to_new[first.value - 1], old_to_new[second.value - 1]))) for first, second in form.adjacency_pairs))
        variants.append((vertices, edges))
    return min(variants)


def _mirror(form: FiniteCoordinationForm) -> FiniteCoordinationForm:
    def mirror_cell(cell: OrientationCell) -> OrientationCell:
        if isinstance(cell, EmptyOne):
            return EmptyOne()
        if cell.label == "fibre-one":
            return HeldLabel(cell.family, "fibre-two")
        if cell.label == "fibre-two":
            return HeldLabel(cell.family, "fibre-one")
        return cell
    return FiniteCoordinationForm(
        form.composition_labels,
        form.attachment_labels,
        tuple(tuple(mirror_cell(cell) for cell in word) for word in form.orientation_words),
        form.adjacency_pairs,
    )


def extend_coordination_form(
    form: FiniteCoordinationForm,
    composition_label: HeldLabel,
    attachment_label: HeldLabel,
    orientation_word: tuple[OrientationCell, OrientationCell, OrientationCell],
    adjacency_to_prior: AdjacencyExtension,
) -> FiniteCoordinationForm:
    """Adjoin one occurrence while retaining the complete prior subform."""

    if not isinstance(form, FiniteCoordinationForm):
        raise InadmissibleExactValue("coordination successor requires one complete prior form")
    if not isinstance(composition_label, HeldLabel) or composition_label.family != "coordination-composition-label":
        raise InadmissibleExactValue("coordination successor requires one composition label")
    if not isinstance(attachment_label, HeldLabel) or attachment_label.family != "coordination-attachment-mode":
        raise InadmissibleExactValue("coordination successor requires one attachment label")
    if len(orientation_word) != 3:
        raise InadmissibleExactValue("coordination successor requires one complete three-axis word")
    width = len(form.composition_labels)
    new_ordinal = PositiveCount(width + 1)
    if isinstance(adjacency_to_prior, EmptyOne):
        new_pairs: tuple[tuple[PositiveCount, PositiveCount], ...] = ()
    else:
        if not isinstance(adjacency_to_prior, tuple) or any(
            not isinstance(endpoint, PositiveCount) or endpoint.value > width
            for endpoint in adjacency_to_prior
        ):
            raise InadmissibleExactValue("successor adjacency must name only retained prior occurrences")
        if len(adjacency_to_prior) != len(set(adjacency_to_prior)):
            raise InadmissibleExactValue("successor adjacency endpoints cannot duplicate")
        new_pairs = tuple((endpoint, new_ordinal) for endpoint in adjacency_to_prior)
    return FiniteCoordinationForm(
        form.composition_labels + (composition_label,),
        form.attachment_labels + (attachment_label,),
        form.orientation_words + (orientation_word,),
        form.adjacency_pairs + new_pairs,
    )


@dataclass(frozen=True)
class ExactCoordinationIsomerRecord:
    positive_occurrence_count: PositiveCount
    same_complete_composition: bool
    exact_equivalence: bool
    native_distinction_class: HeldLabel
    left_signature: tuple
    right_signature: tuple


def forced_coordination_isomer_relation(left: FiniteCoordinationForm, right: FiniteCoordinationForm) -> ExactCoordinationIsomerRecord:
    if not isinstance(left, FiniteCoordinationForm) or not isinstance(right, FiniteCoordinationForm):
        raise InadmissibleExactValue("coordination isomer relation requires two complete forms")
    if len(left.composition_labels) != len(right.composition_labels):
        raise InadmissibleExactValue("coordination isomer comparison requires equal positive width")
    same_composition = sorted(label.label for label in left.composition_labels) == sorted(label.label for label in right.composition_labels)
    if not same_composition:
        raise InadmissibleExactValue("different composition is outside the isomer boundary")
    left_signature = _canonical(left)
    right_signature = _canonical(right)
    equivalent = left_signature == right_signature
    if equivalent:
        distinction = HeldLabel("coordination-form-relation", "same-equivalence-class")
    elif _canonical(left, False) != _canonical(right, False):
        distinction = HeldLabel("coordination-form-relation", "attachment-class-distinction")
    elif _canonical(_mirror(left)) == right_signature:
        distinction = HeldLabel("coordination-form-relation", "mirror-complement-class-distinction")
    else:
        distinction = HeldLabel("coordination-form-relation", "orientation-adjacency-class-distinction")
    return ExactCoordinationIsomerRecord(PositiveCount(len(left.composition_labels)), True, equivalent, distinction, left_signature, right_signature)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-GEOMETRY-TOPOLOGY-001", "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-MOL-ISOMER-001", "SFT-CHEM-STEREO-CHIRALITY-001",
    "SFT-CHEM-STEREO-ENANTIOMER-001", "SFT-CHEM-STEREO-DIASTEREOMER-001",
    "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "names-or-formulae-only", "Names do not retain complete forms.", "two-complete-retained-coordination-forms", "Both forms retain every occurrence and relation."),
    dimension("composition", "different-compositions-called-isomers", "Isomer comparison requires the same complete composition.", "same-complete-composition-multiset", "Every composition occurrence is preserved under comparison."),
    dimension("bijection", "selected-correspondence-between-occurrences", "A selected mapping can manufacture equivalence.", "enumerate-every-occurrence-bijection", "Every finite occurrence bijection is generated."),
    dimension("graph", "partial-or-named-connectivity", "Partial connectivity omits attachment distinctions.", "complete-attachment-and-adjacency-preservation", "Equivalence preserves every attachment and adjacency."),
    dimension("orientation", "shape-name-point-group-or-continuum-transform", "Imported transformations select the result.", "complete-three-axis-two-fibre-relation", "Equivalence compares complete held orientation words made only from the two forced fibre labels and the generated global fibre complement."),
    dimension("class", "imported-isomer-catalogue", "A catalogue does not force the first failed invariant.", "first-failed-invariant-forces-native-class", "Attachment, mirror-complement and remaining orientation distinctions are forced in order."),
    dimension("observation", "selected-favourable-term", "Selected definitions cannot test all classes.", "complete-17-surface-sealed-vector-with-linkage-addendum", "All general, geometric, mirror, point-of-ligation and isomeric attachment-mode surfaces, identity redirects and the absent literal linkage term remain present."),
    dimension("extension", "new-occurrence-reclassifies-prior-subform", "Rewriting loses the prior class trace.", "successor-preserves-prior-signatures-and-adds-relations", "The next occurrence preserves every prior relation and extends both forms."),
)

EXACT_RESULT = "two-complete-retained-coordination-forms__same-complete-composition-multiset__enumerate-every-occurrence-bijection__complete-attachment-and-adjacency-preservation__complete-three-axis-two-fibre-relation__first-failed-invariant-forces-native-class__complete-17-surface-sealed-vector-with-linkage-addendum__successor-preserves-prior-signatures-and-adds-relations"


def _form(attachment_two: str = "mode-one", second_word: str = "fibre-two") -> FiniteCoordinationForm:
    return FiniteCoordinationForm(
        (HeldLabel("coordination-composition-label", "L"), HeldLabel("coordination-composition-label", "L")),
        (HeldLabel("coordination-attachment-mode", "mode-one"), HeldLabel("coordination-attachment-mode", attachment_two)),
        (
            (HeldLabel("fold-orientation-fibre", "fibre-one"), EmptyOne(), EmptyOne()),
            (HeldLabel("fold-orientation-fibre", second_word), EmptyOne(), EmptyOne()),
        ),
        ((PositiveCount(1), PositiveCount(2)),),
    )


_BASE = _form()
_EQUIVALENT = forced_coordination_isomer_relation(_BASE, _form())
_LINKAGE = forced_coordination_isomer_relation(_BASE, _form("mode-two"))
_GEOMETRIC = forced_coordination_isomer_relation(_BASE, _form("mode-one", "fibre-one"))
_CHIRAL = FiniteCoordinationForm(
    tuple(HeldLabel("coordination-composition-label", label) for label in ("A", "B", "C")),
    tuple(HeldLabel("coordination-attachment-mode", "mode-one") for _ in range(3)),
    (
        (HeldLabel("fold-orientation-fibre", "fibre-one"), EmptyOne(), EmptyOne()),
        (HeldLabel("fold-orientation-fibre", "fibre-one"), HeldLabel("fold-orientation-fibre", "fibre-two"), EmptyOne()),
        (HeldLabel("fold-orientation-fibre", "fibre-two"), HeldLabel("fold-orientation-fibre", "fibre-one"), EmptyOne()),
    ),
    ((PositiveCount(1), PositiveCount(2)), (PositiveCount(2), PositiveCount(3)), (PositiveCount(3), PositiveCount(1))),
)
_MIRROR = forced_coordination_isomer_relation(_CHIRAL, _mirror(_CHIRAL))
_SUCCESSOR = extend_coordination_form(
    _BASE,
    HeldLabel("coordination-composition-label", "L"),
    HeldLabel("coordination-attachment-mode", "mode-one"),
    (HeldLabel("fold-orientation-fibre", "fibre-two"), HeldLabel("fold-orientation-fibre", "fibre-two"), EmptyOne()),
    (PositiveCount(1), PositiveCount(2)),
)

OPERATIONAL_WITNESSES = (
    ("equivalence", "Complete identical forms occupy one exact equivalence class.", _EQUIVALENT.exact_equivalence),
    ("attachment", "A first failed attachment invariant forces the attachment distinction.", _LINKAGE.native_distinction_class.label == "attachment-class-distinction"),
    ("mirror", "A global fibre complement forces the mirror-complement distinction when not directly equivalent.", not _MIRROR.exact_equivalence and _MIRROR.native_distinction_class.label == "mirror-complement-class-distinction"),
    ("orientation", "A remaining held orientation difference forces the orientation-adjacency distinction.", _GEOMETRIC.native_distinction_class.label == "orientation-adjacency-class-distinction"),
    ("successor", "The next occurrence preserves the complete prior subform and adds only its own labels, word and adjacencies.", _SUCCESSOR.composition_labels[:2] == _BASE.composition_labels and _SUCCESSOR.attachment_labels[:2] == _BASE.attachment_labels and _SUCCESSOR.orientation_words[:2] == _BASE.orientation_words and _SUCCESSOR.adjacency_pairs[:1] == _BASE.adjacency_pairs and len(_SUCCESSOR.composition_labels) == 3),
)

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "FiniteCoordinationForm", "OPERATIONAL_WITNESSES", "ExactCoordinationIsomerRecord", "extend_coordination_form", "forced_coordination_isomer_relation")
