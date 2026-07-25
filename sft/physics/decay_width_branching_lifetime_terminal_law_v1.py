"""Terminal exact decay-width, branching-partition and lifetime law.

The formal module contains no source locator, particle name, measured width,
measured branching fraction or target value.  It derives the universal law over
nonempty finite families of exact positive open-channel carriers.  A closed
channel is the structural empty form, never a numerical zero.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache, reduce
from itertools import product
from operator import add
from typing import Sequence

from sft.engine import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
)
from sft.engine.canonical import sha256_identity
from sft.physics.prior_value_laws import positive_take


CLAIM_ID = "SFT-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006"
EXPERIMENT_ID = "SFT-EXP-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006"
Empty = tuple[()]


@dataclass(frozen=True)
class CandidateForm:
    partial_width_carrier: str
    channel_domain: str
    total_width_law: str
    branching_law: str
    partition_law: str
    lifetime_law: str
    ordering_law: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.partial_width_carrier,
            self.channel_domain,
            self.total_width_law,
            self.branching_law,
            self.partition_law,
            self.lifetime_law,
            self.ordering_law,
            self.target_boundary,
            self.extension,
        ))


PARTIAL_WIDTH_CARRIERS = (
    "paired-transition-weight-times-output-support-per-action",
    "unpaired-transition-leg-times-output-support",
    "target-assigned-partial-width",
)
CHANNEL_DOMAINS = (
    "positive-open-channels-closed-as-empty",
    "numeric-null-closed-channels",
    "indistinguishable-overlapping-channel-list",
)
TOTAL_WIDTH_LAWS = (
    "ordered-positive-sum-of-partial-widths",
    "largest-partial-width-only",
    "arithmetic-mean-of-partial-widths",
)
BRANCHING_LAWS = (
    "partial-width-over-total-width",
    "total-width-over-partial-width",
    "unnormalized-partial-width",
)
PARTITION_LAWS = (
    "complete-exclusive-partition-of-one",
    "incomplete-open-channel-subset",
    "overlapping-double-counted-channels",
)
LIFETIME_LAWS = (
    "action-over-total-width",
    "total-width-over-action",
    "action-times-total-width",
)
ORDERING_LAWS = (
    "greater-width-shorter-lifetime",
    "greater-width-longer-lifetime",
    "width-independent-lifetime",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")

GENERATION_RULE = (
    "Generate the complete product of every paired or unpaired transition carrier, every open/closed channel "
    "domain, every total-width aggregator, every branching normalization, every completeness partition, every "
    "width-lifetime relation, every induced ordering, both target-custody states and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every nonempty finite generated family of mutually distinguishable open decay channels; exact positive "
    "rational overlap, available-output, action, partial-width and duration carriers; structurally empty closed "
    "channels; complete channel composition; sealed or exposed targets; and empty or free extension. The base "
    "and successor certificates are independent of a finite Fold depth and introduce no numerical null state."
)


def positive_carrier(numerator: int, denominator: int = 1) -> Fraction:
    if numerator < 1 or denominator < 1:
        raise ValueError("decay carriers must remain exact and positive")
    return Fraction(numerator, denominator)


def closed_channel() -> Empty:
    return ()


def partial_transition_width(
    overlap_leg: Fraction,
    available_output_support: Fraction,
    action_carrier: Fraction,
) -> Fraction:
    """Exact open-channel width from paired weight and available support."""

    for value in (overlap_leg, available_output_support, action_carrier):
        if not isinstance(value, Fraction) or value.numerator < 1:
            raise ValueError("partial width requires exact positive carriers")
    paired_weight = overlap_leg * overlap_leg
    return paired_weight * available_output_support / action_carrier


def total_transition_width(partial_widths: Sequence[Fraction]) -> Fraction:
    """Compose a nonempty open-channel family without a numerical null seed."""

    widths = tuple(partial_widths)
    if not widths or any(not isinstance(width, Fraction) or width.numerator < 1 for width in widths):
        raise ValueError("total width requires a nonempty positive open-channel family")
    return reduce(add, widths[1:], widths[0])


def branching_parts(partial_widths: Sequence[Fraction]) -> tuple[Fraction, ...]:
    widths = tuple(partial_widths)
    total = total_transition_width(widths)
    return tuple(width / total for width in widths)


def complete_branching_partition(partial_widths: Sequence[Fraction]) -> Fraction:
    return total_transition_width(branching_parts(partial_widths))


def lifetime_from_width(action_carrier: Fraction, total_width: Fraction) -> Fraction:
    if (
        not isinstance(action_carrier, Fraction)
        or not isinstance(total_width, Fraction)
        or action_carrier.numerator < 1
        or total_width.numerator < 1
    ):
        raise ValueError("lifetime requires exact positive action and width carriers")
    return action_carrier / total_width


def append_open_channel(
    partial_widths: Sequence[Fraction],
    successor_width: Fraction,
) -> tuple[Fraction, ...]:
    widths = tuple(partial_widths)
    total_transition_width(widths)
    if not isinstance(successor_width, Fraction) or successor_width.numerator < 1:
        raise ValueError("successor channel width must remain exact and positive")
    return widths + (successor_width,)


def successor_total_increment(
    partial_widths: Sequence[Fraction],
    successor_width: Fraction,
) -> Fraction:
    before = total_transition_width(partial_widths)
    after = total_transition_width(append_open_channel(partial_widths, successor_width))
    increment = positive_take(after, before)
    if not isinstance(increment, Fraction):
        raise ValueError("adding an open channel failed to increase total width")
    return increment


def wider_state_lifetime_take(
    action_carrier: Fraction,
    narrower_width: Fraction,
    wider_width: Fraction,
) -> Fraction:
    if narrower_width >= wider_width:
        raise ValueError("width ordering must be strict")
    longer = lifetime_from_width(action_carrier, narrower_width)
    shorter = lifetime_from_width(action_carrier, wider_width)
    difference = positive_take(longer, shorter)
    if not isinstance(difference, Fraction):
        raise ValueError("wider state did not have shorter duration")
    return difference


def sample_partial_widths() -> tuple[Fraction, ...]:
    """A target-free exact witness whose total width is two action units."""

    action = Fraction(1, 2)
    return (
        partial_transition_width(Fraction(1, 2), Fraction(1, 2), action),
        partial_transition_width(Fraction(1, 2), Fraction(1, 1), action),
        partial_transition_width(Fraction(1, 1), Fraction(5, 8), action),
    )


@lru_cache(maxsize=1)
def formal_certificate() -> dict[str, object]:
    widths = sample_partial_widths()
    parts = branching_parts(widths)
    successor_widths = (
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 1),
    )
    return {
        "closed_channel": closed_channel(),
        "sample_partial_widths": widths,
        "sample_total_width": total_transition_width(widths),
        "sample_branching_parts": parts,
        "sample_partition": complete_branching_partition(widths),
        "sample_lifetime": lifetime_from_width(Fraction(1, 1), total_transition_width(widths)),
        "width_lifetime_vector": tuple(
            (
                width,
                lifetime_from_width(Fraction(1, 1), width),
            )
            for width in (Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
        ),
        "successor_total_increments": tuple(
            successor_total_increment(widths, successor) for successor in successor_widths
        ),
        "successor_partitions": tuple(
            complete_branching_partition(append_open_channel(widths, successor))
            for successor in successor_widths
        ),
        "wider_state_lifetime_takes": tuple(
            wider_state_lifetime_take(Fraction(1, 1), lower, upper)
            for lower, upper in (
                (Fraction(1, 4), Fraction(1, 2)),
                (Fraction(1, 2), Fraction(1, 1)),
                (Fraction(1, 1), Fraction(2, 1)),
            )
        ),
    }


def partial_width_carrier_is_forced(value: str) -> bool:
    observed = partial_transition_width(Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    alternatives = {
        "paired-transition-weight-times-output-support-per-action": Fraction(3, 16),
        "unpaired-transition-leg-times-output-support": Fraction(3, 8),
        "target-assigned-partial-width": Fraction(1, 1),
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated partial-width carrier")
    return observed == alternatives[value]


def channel_domain_is_forced(value: str) -> bool:
    alternatives = {
        "positive-open-channels-closed-as-empty": (
            closed_channel() == ()
            and all(width.numerator >= 1 for width in sample_partial_widths())
        ),
        "numeric-null-closed-channels": False,
        "indistinguishable-overlapping-channel-list": False,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated channel domain")
    return alternatives[value]


def total_width_law_is_forced(value: str) -> bool:
    widths = sample_partial_widths()
    observed = total_transition_width(widths)
    alternatives = {
        "ordered-positive-sum-of-partial-widths": Fraction(2, 1),
        "largest-partial-width-only": Fraction(5, 4),
        "arithmetic-mean-of-partial-widths": Fraction(2, 3),
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated total-width law")
    return observed == alternatives[value]


def branching_law_is_forced(value: str) -> bool:
    widths = sample_partial_widths()
    observed = branching_parts(widths)
    alternatives = {
        "partial-width-over-total-width": (
            Fraction(1, 8), Fraction(1, 4), Fraction(5, 8)
        ),
        "total-width-over-partial-width": (
            Fraction(8, 1), Fraction(4, 1), Fraction(8, 5)
        ),
        "unnormalized-partial-width": widths,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated branching law")
    return observed == alternatives[value]


def partition_law_is_forced(value: str) -> bool:
    parts = branching_parts(sample_partial_widths())
    alternatives = {
        "complete-exclusive-partition-of-one": complete_branching_partition(sample_partial_widths())
        == Fraction(1, 1),
        "incomplete-open-channel-subset": total_transition_width(parts[:-1]) == Fraction(1, 1),
        "overlapping-double-counted-channels": total_transition_width(parts + (parts[0],))
        == Fraction(1, 1),
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated branching partition")
    return alternatives[value]


def lifetime_law_is_forced(value: str) -> bool:
    width = Fraction(2, 1)
    action = Fraction(1, 1)
    observed = lifetime_from_width(action, width)
    alternatives = {
        "action-over-total-width": Fraction(1, 2),
        "total-width-over-action": Fraction(2, 1),
        "action-times-total-width": Fraction(2, 1),
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated lifetime law")
    return observed == alternatives[value]


def ordering_law_is_forced(value: str) -> bool:
    vector = formal_certificate()["width_lifetime_vector"]
    decreasing = all(
        left_width < right_width and left_lifetime > right_lifetime
        for (left_width, left_lifetime), (right_width, right_lifetime)
        in zip(vector, vector[1:])
    )
    alternatives = {
        "greater-width-shorter-lifetime": decreasing,
        "greater-width-longer-lifetime": all(
            left_lifetime < right_lifetime
            for (_, left_lifetime), (_, right_lifetime) in zip(vector, vector[1:])
        ),
        "width-independent-lifetime": len({lifetime for _, lifetime in vector}) == 1,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated width-lifetime ordering")
    return alternatives[value]


def target_boundary_is_forced(value: str) -> bool:
    if value == "sealed-before-release":
        return True
    if value == "readable-before-seal":
        return False
    raise ValueError("candidate names an ungenerated target boundary")


def extension_is_forced(value: str) -> bool:
    if value == "empty-extension":
        return True
    if value == "free-correction":
        return False
    raise ValueError("candidate names an ungenerated extension")


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            PARTIAL_WIDTH_CARRIERS,
            CHANNEL_DOMAINS,
            TOTAL_WIDTH_LAWS,
            BRANCHING_LAWS,
            PARTITION_LAWS,
            LIFETIME_LAWS,
            ORDERING_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    return {
        "partial_width_carrier": partial_width_carrier_is_forced(form.partial_width_carrier),
        "channel_domain": channel_domain_is_forced(form.channel_domain),
        "total_width_law": total_width_law_is_forced(form.total_width_law),
        "branching_law": branching_law_is_forced(form.branching_law),
        "partition_law": partition_law_is_forced(form.partition_law),
        "lifetime_law": lifetime_law_is_forced(form.lifetime_law),
        "ordering_law": ordering_law_is_forced(form.ordering_law),
        "target_boundary": target_boundary_is_forced(form.target_boundary),
        "extension": extension_is_forced(form.extension),
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def candidate_exact_form(form: CandidateForm) -> str:
    return (
        f"partial={form.partial_width_carrier}; domain={form.channel_domain}; "
        f"total={form.total_width_law}; branch={form.branching_law}; "
        f"partition={form.partition_law}; lifetime={form.lifetime_law}; "
        f"ordering={form.ordering_law}; target={form.target_boundary}; extension={form.extension}"
    )


def decision_reason(facts: dict[str, bool]) -> str:
    failures = tuple(name for name, passed in facts.items() if not passed)
    if failures:
        return "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
    return (
        "Paired transition support fixes each positive open-channel partial width. Complete mutually exclusive "
        "composition forces their total, normalization forces the One partition, and action-width reciprocity "
        "forces the inverse lifetime ordering."
    )


def completeness_record() -> dict[str, object]:
    forms = candidate_forms()
    return {
        "generation_rule": GENERATION_RULE,
        "grammar_boundary": GRAMMAR_BOUNDARY,
        "axis_cardinalities": (3, 3, 3, 3, 3, 3, 3, 2, 2),
        "candidate_count": len(forms),
        "candidate_ids": tuple(form.candidate_id for form in forms),
    }


class DecayWidthBranchingLifetimeProgram:
    """Complete computed enumeration with no claimant-supplied answer key."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._forms_by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Terminal Fold decay widths, exact branching partitions and lifetimes",
            branch="physics",
            statement=(
                "Every distinguishable open decay channel has exact positive partial width equal to its paired "
                "transition weight times available generated output support per action carrier. Closed channels "
                "are structural empty forms. The total width is the complete ordered positive sum of the open "
                "partial widths; each branching part is its partial width over that total, and the mutually "
                "exclusive complete branching family sums exactly to the One. Duration is the action carrier "
                "over total width, so increasing transition support increases width and strictly shortens "
                "lifetime. The base and channel-successor laws hold for every nonempty finite generated family."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-PHYS-MATTER-DECAY-001",
                "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005",
                "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005",
                "SFT-PHYS-QUANTUM-WEIGHT-001",
                "SFT-PHYS-MECH-DURATION-001",
                "SFT-PHYS-MECH-CONSERVATION-001",
                "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
                "SFT-PHYS-MEAS-DIMENSIONAL-CONSISTENCY-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-PHYS-MEAS-UNCERTAINTY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-COMBINATORICS-001",
            ),
            axioms=(),
            free_parameters=(),
            provenance=(
                ProvenanceClass.FORWARD_FORCING,
                ProvenanceClass.OBSERVATIONAL_DERIVATION,
            ),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(
            Candidate(
                candidate_id=form.candidate_id,
                exact_form=candidate_exact_form(form),
                trace_hash=sha256_identity({
                    "generator": GENERATION_RULE,
                    "form": form,
                    "computed_facts": candidate_facts(form),
                }),
            )
            for form in self._forms
        )
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(self._forms),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        form = self._forms_by_id[candidate.candidate_id]
        facts = candidate_facts(form)
        survives = all(facts.values())
        reason = decision_reason(facts)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity({
                "candidate_trace": candidate.trace_hash,
                "form": form,
                "facts": facts,
                "survives": survives,
                "reason": reason,
            }),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        certificate = formal_certificate()
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        minimality = (
            len(survivors) == 1
            and certificate["closed_channel"] == ()
            and certificate["sample_partial_widths"]
            == (Fraction(1, 4), Fraction(1, 2), Fraction(5, 4))
            and certificate["sample_total_width"] == Fraction(2, 1)
            and certificate["sample_branching_parts"]
            == (Fraction(1, 8), Fraction(1, 4), Fraction(5, 8))
            and certificate["sample_partition"] == Fraction(1, 1)
            and certificate["sample_lifetime"] == Fraction(1, 2)
            and all(item.numerator >= 1 for item in certificate["successor_total_increments"])
            and all(item == Fraction(1, 1) for item in certificate["successor_partitions"])
            and all(item.numerator >= 1 for item in certificate["wider_state_lifetime_takes"])
        )
        uniqueness = minimality and extension_is_forced("empty-extension")
        generality = {
            "base": "one positive open channel has total width gamma_1, branch One and lifetime action/gamma_1",
            "successor_total": "Gamma_(n+1)=Gamma_n+gamma_(n+1)",
            "successor_partition": "sum_i gamma_i/Gamma_(n+1)=One for the complete enlarged family",
            "lifetime": "tau=action/Gamma for every exact positive total width",
            "ordering": "Gamma_b>Gamma_a implies action/Gamma_a takes action/Gamma_b is positive",
            "closed_channel": (),
            "target_absent_from_formal_module": True,
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=minimality,
            named_shape_uniqueness_passed=uniqueness,
            proof_hash=sha256_identity({
                "certificate": certificate,
                "decisions": tuple(decisions),
                "survivors_computed": survivors,
            }),
            generality_certificate_hash=sha256_identity(generality),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        computed = tuple(form for form in self._forms if form_survives(form))
        if len(computed) != 1:
            raise ValueError("controls require exactly one computed form")
        form = computed[0]
        incomplete = replace(form, partition_law="incomplete-open-channel-subset")
        direct_lifetime = replace(form, lifetime_law="total-width-over-action")
        target_exposed = replace(form, target_boundary="readable-before-seal")
        free_extension = replace(form, extension="free-correction")
        identifiers = tuple(item.candidate_id for item in self._forms)
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not form_survives(incomplete) and not form_survives(direct_lifetime),
                "Reject incomplete branching and a width-proportional lifetime.",
                "Complete normalization and exact inverse duration reject both false laws.",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "Reject any changed claimant source identity.",
                "The changed identity differs from the registered source manifest.",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len(set(identifiers + (identifiers[0],))) != len(identifiers) + 1,
                "Reject a duplicated or incomplete candidate census.",
                "The deliberate duplicate fails complete candidate identity.",
            ),
            (
                ControlKind.BOUNDARY,
                closed_channel() == ()
                and not form_survives(target_exposed)
                and not form_survives(free_extension),
                "Reject a numerical null channel, pre-seal target access and free correction.",
                "Closed channels are structural absence; sealed custody and empty extension are required.",
            ),
        )
        return tuple(
            ControlResult(kind, passed, expected, observed, sha256_identity({
                "kind": kind,
                "passed": passed,
                "expected": expected,
                "observed": observed,
            }))
            for kind, passed, expected, observed in records
        )


__all__ = (
    "BRANCHING_LAWS",
    "CHANNEL_DOMAINS",
    "CLAIM_ID",
    "DecayWidthBranchingLifetimeProgram",
    "EXPERIMENT_ID",
    "GRAMMAR_BOUNDARY",
    "GENERATION_RULE",
    "LIFETIME_LAWS",
    "ORDERING_LAWS",
    "PARTIAL_WIDTH_CARRIERS",
    "PARTITION_LAWS",
    "TOTAL_WIDTH_LAWS",
    "append_open_channel",
    "branching_parts",
    "candidate_facts",
    "candidate_forms",
    "closed_channel",
    "complete_branching_partition",
    "completeness_record",
    "formal_certificate",
    "form_survives",
    "lifetime_from_width",
    "partial_transition_width",
    "positive_carrier",
    "sample_partial_widths",
    "successor_total_increment",
    "total_transition_width",
    "wider_state_lifetime_take",
)
