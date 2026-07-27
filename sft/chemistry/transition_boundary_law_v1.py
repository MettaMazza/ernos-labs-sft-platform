"""Fold-native finite transition-boundary carrier for Chemistry KIN-005."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class TransitionPathState:
    state_identity: HeldLabel
    relative_support: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.state_identity, HeldLabel) or self.state_identity.family != "generated-path-state":
            raise InadmissibleExactValue("transition boundary requires generated path-state identity")
        if not isinstance(self.relative_support, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("transition boundary requires positive support or structural EmptyOne")


@dataclass(frozen=True)
class TransitionPath:
    reaction_identity: HeldLabel
    path_identity: HeldLabel
    isotopologue_identity: HeldLabel
    ordered_states: tuple[TransitionPathState, ...]
    source_row: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("transition path requires registered reaction identity")
        if not isinstance(self.path_identity, HeldLabel) or self.path_identity.family != "generated-reaction-path":
            raise InadmissibleExactValue("transition path requires generated path identity")
        if not isinstance(self.isotopologue_identity, HeldLabel) or self.isotopologue_identity.family != "held-isotopologue":
            raise InadmissibleExactValue("transition path requires held isotopologue identity")
        if len(self.ordered_states) < 2 or any(not isinstance(row, TransitionPathState) for row in self.ordered_states):
            raise InadmissibleExactValue("transition path requires a complete finite state word")
        if len({row.state_identity for row in self.ordered_states}) != len(self.ordered_states):
            raise InadmissibleExactValue("transition path contains duplicate state identity")
        positive = tuple(row for row in self.ordered_states if isinstance(row.relative_support, PositiveRatio))
        if not positive:
            raise InadmissibleExactValue("transition path requires positive boundary support")
        greatest = max(row.relative_support.fraction for row in positive)
        if sum(row.relative_support.fraction == greatest for row in positive) != 1:
            raise InadmissibleExactValue("transition path requires one unique greatest finite boundary")
        if not isinstance(self.source_row, PositiveCount):
            raise InadmissibleExactValue("transition path requires positive source-row identity")


@dataclass(frozen=True)
class TransitionBoundaryCarrier:
    reaction_identity: HeldLabel
    path_identity: HeldLabel
    isotopologue_identity: HeldLabel
    entry_word: tuple[TransitionPathState, ...] | EmptyOne
    boundary_state: TransitionPathState
    exit_word: tuple[TransitionPathState, ...] | EmptyOne
    orientation: HeldLabel


@dataclass(frozen=True)
class ExternalBarrierSignature:
    orientation: HeldLabel
    positive_magnitude: PositiveRatio
    uncertainty: PositiveRatio


@dataclass(frozen=True)
class TransitionBoundaryCollection:
    carrier: HeldLabel
    ordered_rows: tuple[tuple[PositiveCount, HeldLabel, HeldLabel, HeldLabel], ...]


def forced_transition_boundary(path: TransitionPath) -> TransitionBoundaryCarrier:
    if not isinstance(path, TransitionPath):
        raise InadmissibleExactValue("transition boundary requires one complete generated path")
    positive = tuple(row for row in path.ordered_states if isinstance(row.relative_support, PositiveRatio))
    greatest = max(row.relative_support.fraction for row in positive)
    boundary_indices = tuple(
        index for index, row in enumerate(path.ordered_states)
        if isinstance(row.relative_support, PositiveRatio) and row.relative_support.fraction == greatest
    )
    if len(boundary_indices) != 1:
        raise InadmissibleExactValue("transition boundary is not unique")
    index = boundary_indices[0]
    before, after = path.ordered_states[:index], path.ordered_states[index + 1:]
    return TransitionBoundaryCarrier(
        path.reaction_identity,
        path.path_identity,
        path.isotopologue_identity,
        before if before else EmptyOne(),
        path.ordered_states[index],
        after if after else EmptyOne(),
        HeldLabel("path-boundary-orientation", "entry-through-unique-boundary-to-exit"),
    )


def forced_boundary_collection(paths: tuple[TransitionPath, ...]) -> TransitionBoundaryCollection:
    if not paths or any(not isinstance(path, TransitionPath) for path in paths):
        raise InadmissibleExactValue("transition boundary collection requires complete path census")
    if len({path.source_row.value for path in paths}) != len(paths):
        raise InadmissibleExactValue("transition boundary collection duplicates a source row")
    ordered = tuple(sorted(paths, key=lambda path: path.source_row.value))
    return TransitionBoundaryCollection(
        HeldLabel("transition-boundary-collection", "complete-source-ordered-finite-path-boundary-census"),
        tuple(
            (
                path.source_row,
                path.reaction_identity,
                path.isotopologue_identity,
                forced_transition_boundary(path).boundary_state.state_identity,
            )
            for path in ordered
        ),
    )


def external_barrier_signature(signed_inscription: str, orientation_label: str, uncertainty: str) -> ExternalBarrierSignature:
    if not isinstance(signed_inscription, str) or not signed_inscription.strip():
        raise InadmissibleExactValue("external barrier signature requires source inscription")
    inscription = signed_inscription.strip().replace("−", "-")
    reverse = inscription.startswith("-")
    magnitude_text = inscription[1:] if reverse else inscription.lstrip("+")
    try:
        magnitude = Fraction(magnitude_text)
        uncertainty_value = Fraction(uncertainty)
    except Exception as exc:
        raise InadmissibleExactValue("external barrier signature is not exact finite provenance") from exc
    if magnitude <= 0 or uncertainty_value <= 0:
        raise InadmissibleExactValue("external barrier signature requires positive magnitude and uncertainty")
    expected = "reverse-held-temperature-order" if reverse else "held-temperature-order"
    if orientation_label != expected:
        raise InadmissibleExactValue("external signed inscription and held orientation disagree")
    return ExternalBarrierSignature(
        HeldLabel("external-barrier-orientation", expected),
        PositiveRatio.from_pair(magnitude.numerator, magnitude.denominator),
        PositiveRatio.from_pair(uncertainty_value.numerator, uncertainty_value.denominator),
    )


def complete_path_append_preserves_boundaries(paths: tuple[TransitionPath, ...], successor: TransitionPath) -> bool:
    prior = forced_boundary_collection(paths)
    extended = forced_boundary_collection(paths + (successor,))
    return extended.carrier == prior.carrier and extended.ordered_rows[: len(prior.ordered_rows)] == prior.ordered_rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-KIN-ACTIVATION-001",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011", "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003", "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "saddle-point-or-continuum-transition-state-premise", "A named continuum saddle imports geometry not generated by the Fold path.", "finite-generated-path-boundary-carrier", "The complete finite path forces its boundary carrier without a continuum premise."),
    dimension("identity", "isotopologue-or-reaction-identity-collapsed", "Collapsed identities cannot preserve isotope-dependent observations.", "held-reaction-path-and-isotopologue-identities", "Reaction, path and isotopologue remain held through the boundary."),
    dimension("location", "arbitrary-named-state-or-fitted-coordinate", "A selected state or fitted coordinate could choose the boundary.", "unique-greatest-exact-positive-path-support", "Exact order and uniqueness force one boundary state."),
    dimension("partition", "endpoint-only-or-boundary-answer-only", "Endpoints alone erase the states adjacent to crossing.", "complete-entry-boundary-exit-partition", "Every state is retained exactly before, at or after the boundary."),
    dimension("orientation", "signed-or-negative-proof-scalar", "A signed scalar imports a prohibited negative number.", "positive-magnitude-plus-held-orientation", "Magnitude remains positive while direction is a held structural label."),
    dimension("observation", "single-favorable-isotope-or-barrier-only", "Selecting one isotope erases the measured contrast.", "complete-H2-D2-signature-uncertainty-and-adverse-record", "Both measured isotope directions, magnitudes, uncertainties and disclosures remain held."),
    dimension("provenance", "experimental-calculated-fitted-records-mixed", "Mixing provenance can promote a fitted calculation to measurement.", "experimental-targets-separated-from-calculated-and-fitted-records", "Experimental targets and calculated/fitted disclosures are retained but never conflated."),
    dimension("prediction", "conventional-KIE-equation-target-access-or-refit", "A conventional equation, target access or refit can select the outcome.", "value-free-complete-isotopologue-identity-seal-and-depth-independent-append", "All target identities seal before values open; appending a complete path preserves prior boundaries."),
)


EXACT_RESULT = (
    "finite-generated-path-boundary-carrier__held-reaction-path-and-isotopologue-identities__"
    "unique-greatest-exact-positive-path-support__complete-entry-boundary-exit-partition__"
    "positive-magnitude-plus-held-orientation__complete-H2-D2-signature-uncertainty-and-adverse-record__"
    "experimental-targets-separated-from-calculated-and-fitted-records__"
    "value-free-complete-isotopologue-identity-seal-and-depth-independent-append"
)


def _path(row: int, isotope: str, supports: tuple[int | None, ...]) -> TransitionPath:
    return TransitionPath(
        HeldLabel("registered-reaction", "dissociative-activation"),
        HeldLabel("generated-reaction-path", f"path-{row}"),
        HeldLabel("held-isotopologue", isotope),
        tuple(
            TransitionPathState(
                HeldLabel("generated-path-state", f"state-{number}"),
                EmptyOne() if support is None else PositiveRatio.from_pair(support, 1),
            )
            for number, support in enumerate(supports, start=1)
        ),
        PositiveCount(row),
    )


OPERATIONAL_WITNESSES = (
    ("finite-boundary", "One unique greatest state partitions one complete finite path.", forced_transition_boundary(_path(1, "H2", (None, 2, 5, 3))).boundary_state.relative_support.fraction == Fraction(5, 1)),
    ("complete-partition", "Entry, boundary and exit retain every generated state exactly once.", len(forced_transition_boundary(_path(1, "H2", (None, 2, 5, 3))).entry_word) + 1 + len(forced_transition_boundary(_path(1, "H2", (None, 2, 5, 3))).exit_word) == 4),
    ("orientation-without-negative", "External sign is retained only as orientation plus positive magnitude.", external_barrier_signature("−0.023", "reverse-held-temperature-order", "0.005").positive_magnitude.fraction == Fraction(23, 1000)),
    ("append-successor", "Appending a complete source path preserves every prior boundary.", complete_path_append_preserves_boundaries((_path(1, "H2", (None, 2, 5, 3)),), _path(2, "D2", (None, 3, 7, 4)))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "ExternalBarrierSignature",
    "TransitionBoundaryCarrier", "TransitionBoundaryCollection", "TransitionPath", "TransitionPathState",
    "complete_path_append_preserves_boundaries", "external_barrier_signature", "forced_boundary_collection",
    "forced_transition_boundary",
)
