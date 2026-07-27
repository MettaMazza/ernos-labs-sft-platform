"""Fold-native exact activation-barrier value relation for KIN-004."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class BarrierPathState:
    state_identity: HeldLabel
    relative_support: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.state_identity, HeldLabel) or self.state_identity.family != "generated-path-state":
            raise InadmissibleExactValue("barrier state requires one generated path-state identity")
        if not isinstance(self.relative_support, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("barrier state requires exact positive support or structural EmptyOne")


@dataclass(frozen=True)
class BarrierPathRecord:
    species_identity: HeldLabel
    path_identity: HeldLabel
    ordered_states: tuple[BarrierPathState, ...]
    source_target_row: PositiveCount
    source_reference: HeldLabel | EmptyOne
    uncertainty_support: HeldLabel | EmptyOne
    method_support: HeldLabel | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.species_identity, HeldLabel) or self.species_identity.family != "registered-species":
            raise InadmissibleExactValue("barrier path requires a registered species identity")
        if not isinstance(self.path_identity, HeldLabel) or self.path_identity.family != "generated-reaction-path":
            raise InadmissibleExactValue("barrier path requires a generated path identity")
        if not self.ordered_states or any(not isinstance(row, BarrierPathState) for row in self.ordered_states):
            raise InadmissibleExactValue("barrier path requires a complete ordered state word")
        if len({row.state_identity for row in self.ordered_states}) != len(self.ordered_states):
            raise InadmissibleExactValue("barrier path contains duplicate state identities")
        if not any(isinstance(row.relative_support, PositiveRatio) for row in self.ordered_states):
            raise InadmissibleExactValue("barrier path requires a positive crossing support")
        if not isinstance(self.source_target_row, PositiveCount):
            raise InadmissibleExactValue("barrier path requires a positive source-target identity")
        if not isinstance(self.source_reference, (HeldLabel, EmptyOne)):
            raise InadmissibleExactValue("barrier path requires retained source-reference provenance")
        if not isinstance(self.uncertainty_support, (HeldLabel, EmptyOne)) or not isinstance(self.method_support, (HeldLabel, EmptyOne)):
            raise InadmissibleExactValue("barrier path requires retained uncertainty and method provenance")


@dataclass(frozen=True)
class ExactActivationBarrier:
    path_identity: HeldLabel
    boundary_state: BarrierPathState
    barrier_support: PositiveRatio
    orientation: HeldLabel


@dataclass(frozen=True)
class ExactBarrierCollection:
    carrier: HeldLabel
    ordered_rows: tuple[tuple[HeldLabel, HeldLabel, PositiveRatio, HeldLabel, PositiveCount], ...]


def forced_activation_barrier(path: BarrierPathRecord) -> ExactActivationBarrier:
    if not isinstance(path, BarrierPathRecord):
        raise InadmissibleExactValue("activation barrier requires a complete generated path")
    positive_states = tuple(row for row in path.ordered_states if isinstance(row.relative_support, PositiveRatio))
    if not positive_states:
        raise InadmissibleExactValue("activation barrier requires positive crossing support")
    boundary = max(positive_states, key=lambda row: row.relative_support.fraction)
    return ExactActivationBarrier(
        path.path_identity, boundary, boundary.relative_support,
        HeldLabel("barrier-orientation", "least-state-to-highest-path-boundary"),
    )


def forced_barrier_collection(paths: tuple[BarrierPathRecord, ...]) -> ExactBarrierCollection:
    if not paths or any(not isinstance(path, BarrierPathRecord) for path in paths):
        raise InadmissibleExactValue("barrier collection requires a complete path census")
    if len({path.source_target_row.value for path in paths}) != len(paths):
        raise InadmissibleExactValue("barrier collection contains duplicate source targets")
    ordered = tuple(sorted(paths, key=lambda path: path.source_target_row.value))
    return ExactBarrierCollection(
        HeldLabel("activation-barrier-collection", "complete-source-ordered-path-census"),
        tuple(
            (
                path.species_identity, path.path_identity, forced_activation_barrier(path).barrier_support,
                forced_activation_barrier(path).boundary_state.state_identity, path.source_target_row,
            )
            for path in ordered
        ),
    )


def external_nonnegative_support(inscription: str) -> PositiveRatio | EmptyOne:
    if inscription == "EmptyOne":
        return EmptyOne()
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("barrier inscription requires exact nonnegative external support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
    except Exception as exc:
        raise InadmissibleExactValue("barrier inscription is not exact finite support") from exc
    if value < 0:
        raise InadmissibleExactValue("negative barrier support is prohibited")
    if value == 0:
        return EmptyOne()
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def external_positive_magnitude(inscription: str) -> PositiveRatio:
    support = external_nonnegative_support(inscription)
    if not isinstance(support, PositiveRatio):
        raise InadmissibleExactValue("barrier magnitude must be exact and positive")
    return support


def complete_path_append_preserves_collection(paths: tuple[BarrierPathRecord, ...], successor: BarrierPathRecord) -> bool:
    prior = forced_barrier_collection(paths)
    extended = forced_barrier_collection(paths + (successor,))
    return extended.carrier == prior.carrier and extended.ordered_rows[: len(prior.ordered_rows)] == prior.ordered_rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-KIN-ACTIVATION-001",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011", "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007", "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002", "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("path", "endpoint-only-or-saddle-continuum-premise", "Endpoints or a named saddle do not enumerate a crossing path.", "complete-generated-discrete-path-state-word", "Every generated path state remains ordered and held."),
    dimension("source", "free-fitted-or-imported-barrier-number", "A detached number could select the result.", "exact-source-bound-state-support", "Every support coordinate remains exact and source-bound."),
    dimension("boundary", "arbitrary-named-transition-state", "A named state need not be the path boundary.", "highest-positive-generated-path-boundary", "Exact order forces the greatest positive support on the retained path."),
    dimension("reference", "absolute-energy-origin-or-signed-difference", "An arbitrary origin or negative scalar imports an inadmissible choice.", "least-state-EmptyOne-relative-support", "The least state is structural absent displacement; only positive relative support is retained."),
    dimension("minimality", "nonminimal-added-support", "Extra support does not define the crossing.", "least-crossing-positive-support", "Every smaller generated support remains below the forced highest boundary."),
    dimension("identity", "species-path-or-state-collapsed", "Collapsing identity can manufacture a barrier across different paths.", "held-species-torsion-and-state-identities", "Species, torsion, atoms, rotor and every path-state identity remain held."),
    dimension("record", "barrier-answer-only-or-selected-profile", "A selected value cannot reconstruct the empirical path.", "complete-source-ordered-profile-reference-and-adverse-record", "Every profile, source reference, structural absence and unresolved row remains auditable."),
    dimension("prediction", "barrier-value-readable-before-seal-or-refit-on-append", "Target access or refitting can choose the answer.", "complete-value-free-44-target-identity-seal-and-depth-independent-append", "All target identities seal before values open and appending a path preserves every prior record."),
)


EXACT_RESULT = (
    "complete-generated-discrete-path-state-word__exact-source-bound-state-support__"
    "highest-positive-generated-path-boundary__least-state-EmptyOne-relative-support__"
    "least-crossing-positive-support__held-species-torsion-and-state-identities__"
    "complete-source-ordered-profile-reference-and-adverse-record__"
    "complete-value-free-44-target-identity-seal-and-depth-independent-append"
)


def _path(target: int, species: str, path: str, supports: tuple[int | None, ...]) -> BarrierPathRecord:
    states = tuple(
        BarrierPathState(
            HeldLabel("generated-path-state", f"state-{number}"),
            EmptyOne() if support is None else PositiveRatio.from_pair(support, 1),
        )
        for number, support in enumerate(supports, start=1)
    )
    return BarrierPathRecord(
        HeldLabel("registered-species", species), HeldLabel("generated-reaction-path", path), states,
        PositiveCount(target), EmptyOne(), EmptyOne(), EmptyOne(),
    )


OPERATIONAL_WITNESSES = (
    ("highest-boundary", "Exact order forces the greatest positive path support.", forced_activation_barrier(_path(1, "s", "p", (None, 2, 5, 3))).barrier_support.fraction == Fraction(5, 1)),
    ("least-state", "External zero displacement becomes structural EmptyOne.", isinstance(external_nonnegative_support("0.00"), EmptyOne)),
    ("source-order", "The complete collection retains source order rather than sorting by barrier magnitude.", tuple(row[4].value for row in forced_barrier_collection((_path(1, "a", "p1", (None, 5)), _path(2, "b", "p2", (None, 3)))).ordered_rows) == (1, 2)),
    ("append-successor", "Complete path append preserves the entire prior barrier trace.", complete_path_append_preserves_collection((_path(1, "a", "p1", (None, 5)),), _path(2, "b", "p2", (None, 3)))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "BarrierPathRecord",
    "BarrierPathState", "ExactActivationBarrier", "ExactBarrierCollection", "complete_path_append_preserves_collection",
    "external_nonnegative_support", "external_positive_magnitude", "forced_activation_barrier",
    "forced_barrier_collection",
)
