"""Terminal atomic-precision successor laws.

The earlier atomic hierarchy, hydrogen ladder, terminal proton/electron graph
and finite-turn receipts remain immutable.  These successors use the registered
observational-derivation protocol: observation informed the explicit frozen
relations, but this executable module contains no measured frequency, Rydberg
carrier, wavelength, uncertainty or source record and cannot read one.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import (
    atomic_endpoint,
    binary_count,
    fine_structure_blocks,
    inverse_fine_structure,
    positive_power,
    promotion_rungs,
)
from sft.physics.matter_flavour_completion_laws_v1 import mass_ratio_family
from sft.physics.matter_flavour_laws_v1 import bisect_bracket, isolate_cubic_roots
from sft.physics.matter_flavour_terminal_anomaly_laws_v1 import (
    terminal_turn_projection,
)
from sft.physics.matter_flavour_terminal_proton_laws_v1 import (
    terminal_proton_retention,
)
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
    positive_predecessor,
)


TERMINAL_LAMB_ID = "SFT-PHYS-ATOMIC-LAMB-SHIFT-TERMINAL-005"
TERMINAL_FINE_ID = "SFT-PHYS-ATOMIC-FINE-STRUCTURE-TERMINAL-005"
TERMINAL_HYPERFINE_ID = "SFT-PHYS-ATOMIC-HYPERFINE-TERMINAL-005"


def exact_alpha() -> Fraction:
    return Fraction(1, 1) / inverse_fine_structure()


def depth_three_heavy_complement() -> int:
    carrier = mass_ratio_family(generator_period_three())["heavy_over_light"]
    if not isinstance(carrier, Fraction) or carrier.denominator != 1:
        raise ValueError("depth-three heavy complement is not a positive count")
    return carrier.numerator


def terminal_binary_support() -> int:
    return positive_power(binary_count(), len(promotion_rungs()))


def predecessor_up_support() -> int:
    up_predecessor = positive_predecessor(fine_structure_blocks()["up"])
    return positive_power(binary_count(), up_predecessor)


def terminal_lamb_carrier() -> Fraction:
    """Exact Lamb frequency divided by the post-seal Rydberg-frequency carrier."""

    alpha = exact_alpha()
    colour = generator_period_three()
    down = fine_structure_blocks()["down"]
    heavy = depth_three_heavy_complement()
    support = predecessor_up_support()
    bridge = binary_count() * heavy + colour
    leading = Fraction(heavy, support)
    first_return = Fraction(binary_count() * down, bridge) * alpha
    second_return = alpha ** binary_count() / (colour * heavy * support)
    terminal_return = alpha ** colour / (heavy * support)
    retained = positive_take(leading, first_return)
    retained = positive_take(retained, second_return)
    retained = positive_take(retained, terminal_return)
    result = alpha ** colour * retained
    expected = alpha ** 3 * (
        Fraction(53, 64)
        - Fraction(10, 109) * alpha
        - alpha ** 2 / (3 * 53 * 64)
        - alpha ** 3 / (53 * 64)
    )
    if result != expected:
        raise ValueError("terminal Lamb carrier routes disagree")
    return result


def terminal_fine_carrier() -> Fraction:
    """Exact hydrogen n=2 fine splitting divided by the Rydberg carrier."""

    alpha = exact_alpha()
    binary = binary_count()
    colour = generator_period_three()
    down = fine_structure_blocks()["down"]
    turn_denominator = terminal_turn_projection().denominator
    down_support = positive_power(binary, down)
    boundary = positive_power(colour, binary)
    endpoint = atomic_endpoint()
    initial = Fraction(1, 1) + alpha / positive_power(binary, binary)
    second = Fraction(turn_denominator, down_support * boundary) * alpha ** binary
    third = alpha ** colour / down_support
    terminal = Fraction(binary * down, endpoint) * alpha ** (binary * binary)
    retained = positive_take(initial, second)
    retained = positive_take(retained, third)
    retained = positive_take(retained, terminal)
    result = alpha ** binary / terminal_binary_support() * retained
    expected = alpha ** 2 / 16 * (
        Fraction(1, 1)
        + alpha / 4
        - Fraction(113, 288) * alpha ** 2
        - alpha ** 3 / 32
        - Fraction(10, 137) * alpha ** 4
    )
    if result != expected:
        raise ValueError("terminal fine carrier routes disagree")
    return result


def terminal_proton_ratio_interval() -> tuple[Fraction, Fraction]:
    """Reconstruct the admitted terminal proton graph without target access."""

    pair_sum = Fraction(1, binary_count() * generator_period_three())
    product_value = Fraction(1, 485)
    roots = isolate_cubic_roots(pair_sum, product_value)
    resolution = Fraction(1, 10 ** 18)
    while any(upper - lower > resolution for lower, upper in roots[:2]):
        roots = tuple(bisect_bracket(root, pair_sum, product_value) for root in roots)
    electron_root, muon_root = roots[:2]
    electron_mass = (electron_root[0] ** 2, electron_root[1] ** 2)
    muon_mass = (muon_root[0] ** 2, muon_root[1] ** 2)
    low_difference = positive_take(
        Fraction(1, 1) / electron_mass[1],
        Fraction(1, 1) / muon_mass[0],
    )
    high_difference = positive_take(
        Fraction(1, 1) / electron_mass[0],
        Fraction(1, 1) / muon_mass[1],
    )
    colour = generator_period_three()
    retention = terminal_proton_retention()
    lower = Fraction(1, colour) * low_difference * retention
    upper = Fraction(1, colour) * high_difference * retention
    if not lower < upper:
        raise ValueError("terminal proton interval orientation failed")
    return lower, upper


def reduced_mass_retention(proton_electron_ratio: Fraction) -> Fraction:
    if not isinstance(proton_electron_ratio, Fraction) or proton_electron_ratio <= 1:
        raise ValueError("reduced-mass transport requires an exact ratio above the One")
    return proton_electron_ratio / (proton_electron_ratio + Fraction(1, 1))


def terminal_proton_magnetic_projection() -> Fraction:
    """Exact finite proton magnetic carrier, represented by positive held parts."""

    alpha = exact_alpha()
    binary = binary_count()
    colour = generator_period_three()
    down, up = fine_structure_blocks()["down"], fine_structure_blocks()["up"]
    terminal = terminal_binary_support()
    heavy = depth_three_heavy_complement()
    volume = positive_power(colour, colour)

    projection = positive_take(terminal_turn_projection(), Fraction(1, colour))
    projection = positive_take(projection, binary * alpha)
    projection += Fraction(down, terminal) * alpha
    projection = positive_take(projection, Fraction(terminal, heavy) * alpha ** binary)
    projection = positive_take(projection, Fraction(up, down * terminal) * alpha ** colour)
    projection += alpha ** (binary * binary) / (down * volume)

    expected = (
        terminal_turn_projection()
        - Fraction(1, 3)
        - 2 * alpha
        + Fraction(5, 16) * alpha
        - Fraction(16, 53) * alpha ** 2
        - Fraction(7, 80) * alpha ** 3
        + alpha ** 4 / 135
    )
    if projection != expected:
        raise ValueError("terminal proton magnetic projection routes disagree")
    return projection


def hyperfine_carrier_at(proton_electron_ratio: Fraction) -> Fraction:
    alpha = exact_alpha()
    binary = binary_count()
    colour = generator_period_three()
    reduced = reduced_mass_retention(proton_electron_ratio)
    return (
        Fraction(positive_power(binary, binary * binary), colour)
        * alpha ** binary
        * Fraction(1, 1)
        / proton_electron_ratio
        * reduced ** colour
        * terminal_proton_magnetic_projection()
    )


def terminal_hyperfine_carrier_interval() -> tuple[Fraction, Fraction]:
    lower_ratio, upper_ratio = terminal_proton_ratio_interval()
    # rho^2/(rho+1)^3 is decreasing throughout the admitted rho>2 interval.
    lower = hyperfine_carrier_at(upper_ratio)
    upper = hyperfine_carrier_at(lower_ratio)
    if not lower < upper:
        raise ValueError("hyperfine carrier interval orientation failed")
    return lower, upper


def precision_axes(topic: str) -> tuple:
    return (
        binary_axis("predecessor", f"What does the {topic} successor refine?", "replace-or-erase-predecessor", "An immutable admitted receipt cannot be rewritten.", "retain-and-version-predecessor", "The successor depends on and preserves every earlier leading and adverse receipt."),
        binary_axis("support", "Which structural carriers enter?", "selected-partial-support", "A selected subset can tune a precision value.", "complete-typed-terminal-support", "Every named down/up, generator, binary, bulk, boundary and terminal carrier is used in its typed role."),
        binary_axis("operation", "How are opposing contributions represented?", "signed-floating-or-complex-series", "Signed, floating, irrational or complex proof values violate the Fold domain.", "ordered-positive-held-parts", "Every opposing contribution is an ordered exact positive Take with its orientation retained."),
        binary_axis("order", "How is correction order chosen?", "selected-or-open-order", "A selected truncation or open series is a free choice.", "finite-carrier-exhaustion-order", "The order ends exactly when every generated typed carrier has been consumed once."),
        binary_axis("composition", "How are the carriers joined?", "untyped-coefficient-list", "An untyped list does not force a relation.", "role-preserving-exact-composition", "Carrier type fixes numerator, denominator, order and held/returned orientation."),
        binary_axis("closure", "What terminates the law?", "unbounded-extra-correction", "An unbounded correction family is not closed.", "no-generated-carrier-remains", "No declared support or return remains after the terminal act."),
        binary_axis("target", "May a measured frequency enter execution?", "measurement-readable-execution", "A target-readable execution cannot issue a prediction seal.", "target-inaccessible-until-seal", "The executable relation contains only admitted exact Fold carriers."),
        binary_axis("provenance", "How is observational development recorded?", "hidden-fit-or-forward-claim", "Hiding prior target knowledge or calling it blind forward forcing is invalid.", "disclosed-observational-prediction-protocol", "Observation informs the explicit law; target-inaccessible enumeration and sealing precede exact comparison."),
        binary_axis("trace", "What proof chain is retained?", "result-without-root-trace", "An untraced value is inadmissible.", "complete-root-directed-trace", "Every dependency returns through admitted receipts to the foundational theorem."),
        binary_axis("extension", "May another coefficient be appended?", "free-extra-term", "An extra term is a parameter.", "no-extra-rule", "The declared grammar is exhausted and halted."),
    )


LAMB_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_LAMB_ID,
    title="Terminal exact hydrogen Lamb-shift successor",
    statement=(
        "The immutable leading live-vacuum direction and alpha-four hierarchy are retained.  The terminal "
        "n=2 Lamb frequency is the admitted Rydberg carrier multiplied by alpha cubed and the positive held "
        "support 53/64, after the down-depth/binary return 10 alpha/109, the complete colour-heavy-support "
        "return alpha squared/(3*53*64), and the terminal alpha-cubed return/(53*64) have each acted once."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-CORRECTION-HIERARCHY-004",
        "SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003",
        "SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004",
        "SFT-PHYS-MATTER-MASS-RATIO-FAMILY-003",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis terminal Lamb successor product and exhaust the typed heavy/support/bridge/return carriers.",
    grammar_boundary="All first terminal alpha-cubed completions of the admitted live-vacuum n=2 Lamb direction using depth-three heavy complement, predecessor-up binary support, down-depth transport, generator support and the sole terminal return exactly once.",
    axes=precision_axes("Lamb"),
    exact_result="The unique target-inaccessible ratio is alpha^3[53/64-(10/109)alpha-alpha^2/(3*53*64)-alpha^3/(53*64)].",
    induction_base="The live-vacuum direction and the positive depth-three heavy share over predecessor-up support supply 53/64.",
    induction_step="Transport the complete down/binary return, the generator-heavy-support return and the sole terminal return in order; all remain positive held parts and no typed carrier remains.",
    exclusions=("no measured Lamb frequency or Rydberg value in execution", "no imported QED coefficient series", "no fitted coefficient or selected truncation", "no negative, irrational, imaginary or floating proof value", "no rewriting of the leading alpha-four receipt"),
    witnesses=(
        Witness("heavy-support", "Depth three and predecessor-up support force 53 and 64.", depth_three_heavy_complement() == 53 and predecessor_up_support() == 64),
        Witness("bridge", "Binary heavy support plus generator closes at 109.", binary_count() * depth_three_heavy_complement() + generator_period_three() == 109),
        Witness("positive-terminal-carrier", "The terminal Lamb/Rydberg ratio is one exact positive part.", Fraction(1, 10 ** 7) < terminal_lamb_carrier() < Fraction(1, 10 ** 6)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


FINE_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_FINE_ID,
    title="Terminal exact hydrogen fine-structure successor",
    statement=(
        "The n=2 fine splitting begins at alpha squared distributed over the complete sixteen-cell terminal "
        "support.  The binary-squared first return adds alpha/4; the terminal-turn denominator over down "
        "support times the generator boundary holds 113 alpha squared/288; the down-support return holds "
        "alpha cubed/32; and binary-through-down transport over the atomic endpoint holds 10 alpha fourth/137."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-CORRECTION-HIERARCHY-004",
        "SFT-PHYS-RELATIVITY-FULL-DIRAC-SQUARE-003",
        "SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004",
        "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis terminal n=2 fine-structure product and exhaust the turn, down-support, boundary, endpoint and terminal-support carriers.",
    grammar_boundary="All first terminal completions of the admitted alpha-squared fine/gross scale on the n=2 sixteen-cell support, using the exact turn, down cover, generator boundary and atomic endpoint once in their typed roles.",
    axes=precision_axes("fine-structure"),
    exact_result="The unique target-inaccessible ratio is alpha^2/16[1+alpha/4-(113/288)alpha^2-alpha^3/32-(10/137)alpha^4].",
    induction_base="The two handed Fold directions force alpha squared and four terminal promotion rungs force support sixteen.",
    induction_step="Apply the binary-squared return, then hold the turn/boundary, down-support and endpoint returns in generated order; the endpoint closes the grammar.",
    exclusions=("no measured fine splitting or Rydberg value in execution", "no consensus Ritz value as a premise", "no fitted coefficient or selected correction", "no negative, irrational, imaginary or floating proof value", "no rewriting of the leading fine/gross receipt"),
    witnesses=(
        Witness("turn-support", "Terminal turn denominator and support are 113 and 16.", terminal_turn_projection().denominator == 113 and terminal_binary_support() == 16),
        Witness("down-boundary", "Down support times generator boundary closes at 288.", positive_power(2, 5) * positive_power(3, 2) == 288),
        Witness("endpoint", "The terminal atomic whole endpoint is 137.", atomic_endpoint() == 137),
        Witness("positive-terminal-carrier", "The terminal fine/Rydberg ratio is one exact positive part.", Fraction(1, 10 ** 6) < terminal_fine_carrier() < Fraction(1, 100000)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


HYPERFINE_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_HYPERFINE_ID,
    title="Terminal exact hydrogen hyperfine and twenty-one-centimetre successor",
    statement=(
        "The terminal proton/electron algebraic enclosure supplies the inverse mass carrier and exact cubic "
        "reduced-mass retention.  Both spin ends over generator three force 16/3 alpha squared.  The proton "
        "magnetic projection is the finite turn held by one generator share and both alpha hands, returned by "
        "5 alpha/16, held by 16 alpha squared/53 and 7 alpha cubed/80, and closed by alpha fourth/135."
    ),
    dependencies=(
        "SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",
        "SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004",
        "SFT-PHYS-QUANTUM-SPIN-001",
        "SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004",
        "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis terminal ground-state hyperfine product and exhaust the mass, reduced-mass, spin, finite-turn, down/up, support and terminal-volume carriers.",
    grammar_boundary="All first terminal hyperfine completions using the admitted algebraic proton/electron enclosure, its exact reduced-mass transport, both spin hands, generator distribution, terminal finite turn, depth-three complement and terminal support exactly once.",
    axes=precision_axes("hyperfine"),
    exact_result="For each exact terminal proton/electron ratio rho, nu_hfs/(R-infinity*c)=(16/3)alpha^2 rho^-1[rho/(rho+1)]^3 M, where M=T-1/3-2alpha+(5/16)alpha-(16/53)alpha^2-(7/80)alpha^3+alpha^4/135; exact algebraic rho isolation gives a strict rational prediction enclosure.",
    induction_base="The terminal proton/electron algebraic graph supplies a positive exact rho enclosure and one inverse-mass magnetic carrier.",
    induction_step="Apply the cubic reduced-mass retention, both spin ends and every finite magnetic return in order; all opposing terms are held positive Takes and the colour-volume terminal cell halts the relation.",
    exclusions=("no measured 21-cm frequency or Rydberg value in execution", "no imported proton magnetic moment", "no fitted magnetic coefficient or hidden target knowledge", "no negative, irrational, imaginary or floating proof value", "no collapse of the algebraic rho enclosure to a decimal"),
    witnesses=(
        Witness("proton-enclosure", "The terminal proton/electron graph remains a strict exact rational enclosure above the One.", terminal_proton_ratio_interval()[0] > 1800 and terminal_proton_ratio_interval()[0] < terminal_proton_ratio_interval()[1]),
        Witness("reduced-mass", "Reduced-mass transport remains a strict positive part of the One.", Fraction(9, 10) < reduced_mass_retention(terminal_proton_ratio_interval()[0]) < Fraction(1, 1)),
        Witness("magnetic-projection", "The terminal proton magnetic projection is an exact positive carrier between two and three.", Fraction(2, 1) < terminal_proton_magnetic_projection() < Fraction(3, 1)),
        Witness("hyperfine-enclosure", "The exact hyperfine/Rydberg enclosure is strict and positive.", Fraction(1, 10 ** 7) < terminal_hyperfine_carrier_interval()[0] < terminal_hyperfine_carrier_interval()[1] < Fraction(1, 10 ** 6)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ATOMIC_PRECISION_SPECS = (LAMB_SPEC, FINE_SPEC, HYPERFINE_SPEC)
SPEC_BY_ID = {spec.claim_id: spec for spec in ATOMIC_PRECISION_SPECS}
for _spec in ATOMIC_PRECISION_SPECS:
    _spec.validate()


__all__ = (
    "ATOMIC_PRECISION_SPECS",
    "FINE_SPEC",
    "HYPERFINE_SPEC",
    "LAMB_SPEC",
    "SPEC_BY_ID",
    "TERMINAL_FINE_ID",
    "TERMINAL_HYPERFINE_ID",
    "TERMINAL_LAMB_ID",
    "depth_three_heavy_complement",
    "hyperfine_carrier_at",
    "predecessor_up_support",
    "reduced_mass_retention",
    "terminal_binary_support",
    "terminal_fine_carrier",
    "terminal_hyperfine_carrier_interval",
    "terminal_lamb_carrier",
    "terminal_proton_magnetic_projection",
    "terminal_proton_ratio_interval",
)
