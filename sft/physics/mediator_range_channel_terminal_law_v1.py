"""Exact preserved/broken channel and mediator-range correspondence."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020"
ONE = Fraction(1, 1)
EMPTY_ONE = ("empty-One",)


def preserved_mass_record(channel_sum: Fraction):
    if not isinstance(channel_sum, Fraction) or channel_sum <= 0 or channel_sum > 1:
        raise ValueError("channel sum must be one exact positive part")
    return EMPTY_ONE if channel_sum == ONE else ONE - channel_sum


def broken_channel_mass(channel: Fraction) -> Fraction:
    record = preserved_mass_record(channel)
    if record == EMPTY_ONE:
        raise ValueError("the preserved One has no positive mass shortfall")
    return record


def positive_forward_trace(mass_share: Fraction) -> tuple[Fraction, ...]:
    """Retain every positive forward carrier before the next act closes it."""

    if not isinstance(mass_share, Fraction) or mass_share <= 0 or mass_share >= 1:
        raise ValueError("massive transport requires a proper positive mass share")
    current = ONE
    trace = (current,)
    while current > mass_share:
        current = current - mass_share
        trace += (current,)
    return trace


def finite_reach_count(mass_share: Fraction) -> int:
    return len(positive_forward_trace(mass_share)) - 1


def forward_rest_ledger(mass_share: Fraction) -> tuple[tuple[Fraction, object], ...]:
    trace = positive_forward_trace(mass_share)
    rows: list[tuple[Fraction, object]] = [(trace[0], EMPTY_ONE)]
    for forward in trace[1:]:
        rows.append((forward, ONE - forward))
    return tuple(rows)


def ledger_conserves_one(mass_share: Fraction) -> bool:
    rows = forward_rest_ledger(mass_share)
    return rows[0] == (ONE, EMPTY_ONE) and all(
        forward + rest == ONE for forward, rest in rows[1:]
    )


def reciprocal_range_scale(mass_share: Fraction) -> Fraction:
    if not isinstance(mass_share, Fraction) or mass_share <= 0:
        raise ValueError("reciprocal range requires one positive mass carrier")
    return ONE / mass_share


def larger_mass_shorter_range(smaller: Fraction, larger: Fraction) -> bool:
    if not (0 < smaller < larger):
        raise ValueError("ordered positive mass carriers are required")
    return reciprocal_range_scale(larger) < reciprocal_range_scale(smaller)


def massless_forward_trace(depth: int) -> tuple[Fraction, ...]:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("massless trace requires a positive finite depth")
    return tuple(ONE for _ in range(depth + 1))


def massless_inverse_square(source: Fraction, radius: Fraction) -> Fraction:
    if (
        not isinstance(source, Fraction)
        or not isinstance(radius, Fraction)
        or source <= 0
        or radius <= 0
    ):
        raise ValueError("inverse-square transport requires positive exact carriers")
    return source / (radius * radius)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Preserved/broken Fold channels and inverse mediator range",
    statement=(
        "A complete channel combination that reassembles the One has the structural "
        "empty mass record and retains its forward carrier at every generated finite "
        "step.  Every proper broken channel has a positive mass shortfall.  Repeated "
        "positive transfer of that share from forward to co-located rest support "
        "conserves the One and leaves a finite positive forward trace; the following "
        "act is the empty boundary rather than numerical zero.  Independently, the "
        "characteristic normalized range scale is One divided by mass, so every "
        "larger positive mediator mass has shorter range.  A massless inverse-square "
        "carrier remains positive at every finite radius.  This forces the exact "
        "preserved/massless versus broken/massive discriminator without importing a "
        "Yukawa exponential or asserting a hard physical zero beyond the range scale."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003",
        "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
        "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-SPACETIME-LIMIT-SPEED-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of carrier, channel completion, mass record, "
        "forward/rest transfer, conservation, range scale, mass ordering, massless "
        "transport, post-seal comparison and extension forms."
    ),
    grammar_boundary=(
        "Every exact positive proper Fold channel and every complete channel sum; "
        "every positive finite mass share, its complete positive subtraction trace "
        "and reciprocal range; every exact positive finite radius; and the already "
        "sealed W/Z, electroweak-share and mediator-range comparison records."
    ),
    axes=(
        binary_axis("carrier", "What carries mediation?", "untracked-field-value", "An untracked value cannot conserve transferred support.", "held-forward-and-rest-carriers", "Every forward and captured-rest part remains explicitly held."),
        binary_axis("channel", "Which channel is preserved?", "named-unbroken-channel", "A name does not prove completion.", "combination-reassembling-the-One", "Only complete channel support reaches the invariant One."),
        binary_axis("mass", "What distinguishes massive from massless?", "assigned-mass-label", "An assigned label imports the classification.", "positive-shortfall-or-empty-record", "Proper parts have positive One-shortfall; completed One has structural empty mass."),
        binary_axis("transfer", "How does massive forward support evolve?", "sink-or-imported-exponential", "A sink loses support and an exponential is not generated.", "exact-positive-forward-to-rest-transfer", "Each act moves one mass share into a retained rest carrier."),
        binary_axis("conservation", "What happens to total support?", "forward-loss-without-ledger", "That violates closed transfer.", "forward-plus-rest-reassembles-One", "Every retained row exactly reconstructs the One."),
        binary_axis("range", "What fixes massive range?", "selected-cutoff-distance", "A selected cutoff is a free parameter.", "positive-trace-and-reciprocal-mass-scale", "The finite native trace and One-over-mass scale are both exact."),
        binary_axis("ordering", "How do masses order ranges?", "independent-range-order", "Independent ordering can contradict the carrier.", "larger-mass-shorter-range", "Reciprocal order reverses every positive mass ordering."),
        binary_axis("massless", "How does an empty mass record propagate?", "finite-hard-stop", "No generated positive mass exists to supply a stop.", "held-forward-and-positive-finite-radius", "Forward support is retained and inverse-square response is positive at every finite radius."),
        binary_axis("comparison", "When are physical mediators named?", "W-Z-photon-selected-before-law", "Named targets cannot select the discriminator.", "inherit-sealed-electroweak-and-range-records", "The formal law composes already sealed W/Z and mediator-range comparisons."),
        binary_axis("extension", "May another profile enter?", "free-Yukawa-or-cutoff-rule", "A free profile or cutoff adds a parameter.", "no-extra-rule", "Completion, shortfall, exact transfer and reciprocal order exhaust the grammar."),
    ),
    exact_result=(
        "Complete-One channels have an empty mass record and no finite transport "
        "endpoint; proper channels have positive shortfall, exact conserved "
        "forward/rest transfer, a finite native trace and reciprocal mass range; "
        "larger mass means shorter range, while massless inverse-square response "
        "remains positive at every finite radius."
    ),
    induction_base=(
        "At the first act, one positive mass share transfers from the One-forward "
        "carrier into rest and the pair reassembles the One."
    ),
    induction_step=(
        "Whenever forward support exceeds the mass share, one further exact take "
        "leaves a positive forward carrier and adds the same share to rest.  A "
        "finite rational mass exhausts the finite native budget at a generated "
        "boundary; reciprocal order is depth-independent."
    ),
    exclusions=(
        "no V1/V2 executable, answer table, selected particle name or stored survivor",
        "no imported exponential, fitted range, hard physical numerical-zero cutoff or sink",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no claim that the finite native subtraction trace is a universal physical field profile",
        "no target access before the predecessor electroweak and mediator-range seals",
    ),
    witnesses=(
        Witness("preserved-combinations", "Both registered channel pairs reassemble the One and have empty mass records.", preserved_mass_record(Fraction(1, 2) + Fraction(1, 2)) == EMPTY_ONE and preserved_mass_record(Fraction(2, 3) + Fraction(1, 3)) == EMPTY_ONE),
        Witness("broken-shortfalls", "Each proper channel has its exact positive One-shortfall.", broken_channel_mass(Fraction(1, 2)) == Fraction(1, 2) and broken_channel_mass(Fraction(2, 3)) == Fraction(1, 3)),
        Witness("v2-reach", "Mass one-third reaches two acts, one-seventh reaches six, half-One reaches one and two-thirds reaches one.", tuple(finite_reach_count(mass) for mass in (Fraction(1, 3), Fraction(1, 7), Fraction(1, 2), Fraction(2, 3))) == (2, 6, 1, 1)),
        Witness("conservation", "Every exact massive control trace retains forward plus rest equal to the One.", all(ledger_conserves_one(mass) for mass in (Fraction(1, 7), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)))),
        Witness("range-order", "The lighter exact mediator has the longer reciprocal scale.", larger_mass_shorter_range(Fraction(1, 7), Fraction(1, 3))),
        Witness("massless-finite-radius", "Massless forward support remains One and inverse-square response stays positive at every tested finite radius.", massless_forward_trace(8) == (ONE,) * 9 and all(massless_inverse_square(ONE, Fraction(radius, 1)) > 0 for radius in range(1, 17))),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EMPTY_ONE",
    "SPEC",
    "broken_channel_mass",
    "finite_reach_count",
    "forward_rest_ledger",
    "larger_mass_shorter_range",
    "ledger_conserves_one",
    "massless_forward_trace",
    "massless_inverse_square",
    "positive_forward_trace",
    "preserved_mass_record",
    "reciprocal_range_scale",
)
