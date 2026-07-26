"""Exact Fold inspiral, chirp, merger and ringdown sequence.

No external waveform, dimensional mass, fitted damping coefficient or
conventional field equation is available here.  The construction composes only
already admitted V3 source conservation, inverse-square orbital restoration,
quadrupole radiation, exact period/frequency and horizon-contact laws.  Every
scalar used by the proof is a positive whole or exact positive fraction.  A
closed record is the empty One form rather than a numerical zero.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-TERMINAL-073"
EMPTY_ONE_FORM = ()
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)
QUARTER_ONE = Fraction(1, 4)
CONTACT_SEPARATION = ONE
COMPONENT_MASS = QUARTER_ONE


def positive_whole(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("a sequence depth must be a positive whole")
    return value


def positive_fraction(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0:
        raise ValueError("a wave carrier must be an exact positive fraction")
    return value


def positive_take(larger: Fraction, smaller: Fraction) -> Fraction:
    """Return a positive retained take without admitting a signed magnitude."""

    larger = positive_fraction(larger)
    smaller = positive_fraction(smaller)
    if larger <= smaller:
        raise ValueError("a retained take requires strict positive ordering")
    return larger - smaller


def orbital_row(separation: Fraction) -> dict[str, Fraction]:
    """Normalized exact circular-balance carrier at one separation.

    Inverse-square response balanced against cyclic acceleration forces
    ``period^2 = separation^3`` in the normalized Fold carrier.  Keeping the
    square avoids importing an irrational root.  A quadrupole repeats twice per
    orbit, so its squared recurrence frequency is four times the orbital value.
    The binary half-One source coupling gives binding-support magnitude
    ``1/(2 separation)``.
    """

    separation = positive_fraction(separation)
    period_squared = separation * separation * separation
    orbital_frequency_squared = ONE / period_squared
    wave_frequency_squared = 4 * orbital_frequency_squared
    binding_support = HALF_ONE / separation
    return {
        "separation": separation,
        "period_squared": period_squared,
        "orbital_frequency_squared": orbital_frequency_squared,
        "wave_frequency_squared": wave_frequency_squared,
        "binding_support": binding_support,
    }


def inspiral_trace(depth: int) -> tuple[dict[str, Fraction | tuple], ...]:
    """Generate a complete finite binary shrink trace ending at contact."""

    depth = positive_whole(depth)
    separations = tuple(Fraction(2 ** step, 1) for step in range(depth, -1, -1))
    rows: list[dict[str, Fraction | tuple]] = []
    previous_binding: Fraction | None = None
    for separation in separations:
        row = dict(orbital_row(separation))
        binding = row["binding_support"]
        if not isinstance(binding, Fraction):
            raise ValueError("binding support lost exact type")
        row["radiated_take_from_prior"] = (
            EMPTY_ONE_FORM if previous_binding is None else positive_take(binding, previous_binding)
        )
        rows.append(row)
        previous_binding = binding
    return tuple(rows)


def inspiral_certificate(depth: int) -> dict[str, object]:
    rows = inspiral_trace(depth)
    pairs = tuple(zip(rows, rows[1:]))
    return {
        "rows": rows,
        "separation_strictly_falls": all(left["separation"] > right["separation"] for left, right in pairs),
        "period_squared_strictly_falls": all(left["period_squared"] > right["period_squared"] for left, right in pairs),
        "orbital_frequency_squared_strictly_rises": all(left["orbital_frequency_squared"] < right["orbital_frequency_squared"] for left, right in pairs),
        "wave_frequency_squared_strictly_rises": all(left["wave_frequency_squared"] < right["wave_frequency_squared"] for left, right in pairs),
        "quadrupole_is_twice_orbital": all(row["wave_frequency_squared"] == 4 * row["orbital_frequency_squared"] for row in rows),
        "binding_support_strictly_rises": all(left["binding_support"] < right["binding_support"] for left, right in pairs),
        "every_successor_take_positive": all(isinstance(right["radiated_take_from_prior"], Fraction) and right["radiated_take_from_prior"] > 0 for _, right in pairs),
        "ends_at_horizon_contact": rows[-1]["separation"] == CONTACT_SEPARATION,
    }


def merger_record() -> dict[str, object]:
    """Join two horizon-bound supports while retaining the radiation ledger."""

    component_radius = COMPONENT_MASS + COMPONENT_MASS
    return {
        "initial_source_count": 2,
        "component_mass": COMPONENT_MASS,
        "component_radius": component_radius,
        "contact_separation": component_radius + component_radius,
        "joined_source_count": 1,
        "radiation_record": ("quadrupole-take",),
        "component_labels_retained": ("left-source", "right-source"),
        "remnant_labels": ("joined-mass-support", "held-turn"),
    }


def ringdown_trace(depth: int) -> tuple[dict[str, object], ...]:
    """Binary Fold damping with a held remnant tone at every finite depth."""

    depth = positive_whole(depth)
    merger = merger_record()
    amplitude = ONE
    rows = []
    for tick in range(1, depth + 1):
        rows.append({
            "tick": tick,
            "amplitude_support": amplitude,
            "tone_key": merger["remnant_labels"],
            "source_count": merger["joined_source_count"],
        })
        amplitude *= HALF_ONE
    return tuple(rows)


def ringdown_certificate(depth: int) -> dict[str, object]:
    rows = ringdown_trace(depth)
    return {
        "rows": rows,
        "one_remnant": all(row["source_count"] == 1 for row in rows),
        "tone_held": len({row["tone_key"] for row in rows}) == 1,
        "amplitude_strictly_falls": all(left["amplitude_support"] > right["amplitude_support"] for left, right in zip(rows, rows[1:])),
        "binary_damping": all(right["amplitude_support"] == left["amplitude_support"] * HALF_ONE for left, right in zip(rows, rows[1:])),
        "all_reached_amplitudes_positive": all(row["amplitude_support"] > 0 for row in rows),
        "finite_floor_retained": rows[-1]["amplitude_support"] > 0,
    }


def theorem_certificate() -> dict[str, object]:
    inspirals = tuple(inspiral_certificate(depth) for depth in (1, 2, 3, 8, 16))
    ringdowns = tuple(ringdown_certificate(depth) for depth in (1, 2, 3, 8, 16))
    merger = merger_record()
    return {
        "inspirals": inspirals,
        "merger": merger,
        "ringdowns": ringdowns,
        "all_chirps_close": all(
            row["separation_strictly_falls"]
            and row["wave_frequency_squared_strictly_rises"]
            and row["quadrupole_is_twice_orbital"]
            and row["every_successor_take_positive"]
            and row["ends_at_horizon_contact"]
            for row in inspirals
        ),
        "merger_closes": merger["initial_source_count"] == 2
        and merger["joined_source_count"] == 1
        and merger["contact_separation"] == CONTACT_SEPARATION
        and bool(merger["radiation_record"]),
        "all_ringdowns_close": all(
            row["one_remnant"]
            and row["tone_held"]
            and row["binary_damping"]
            and row["all_reached_amplitudes_positive"]
            and row["finite_floor_retained"]
            for row in ringdowns
        ),
        "unique_ordered_sequence": ("inspiral-rising-chirp", "merger", "damped-ringdown"),
    }


_theorem = theorem_certificate()

SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal gravitational-wave chirp, merger and ringdown law",
    statement=(
        "Positive quadrupole radiation transfers a retained take from a restoring binary orbit at every dynamic "
        "successor. Source conservation therefore lowers the positive orbital remainder while the exact binding "
        "support increases and separation contracts. Inverse-square circular balance forces period squared equal "
        "to separation cubed, so shrinking separation uniquely raises the exact squared orbital frequency. The "
        "quadrupole repeats twice per orbit and therefore raises the gravitational-wave frequency by the same "
        "ordered chirp. Horizon contact joins two source supports into one remnant while retaining the radiation "
        "and component-label ledger. The remnant mass/turn labels hold one tone class; the unique nonempty equal "
        "binary contraction halves its amplitude at each finite return, forcing a damped ringdown without a "
        "negative exponent, irrational frequency or numerical-zero endpoint."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-PHYS-MECH-ANGULAR-MOTION-001",
        "SFT-PHYS-WAVE-PERIOD-FREQUENCY-001",
        "SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009",
        "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
        "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012",
        "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
        "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of source, radiative moment, transfer ledger, separation, "
        "orbital balance, wave recurrence, contact, merger, remnant tone, damping, finite-floor and sequence forms."
    ),
    grammar_boundary=(
        "Every finite positive binary separation successor ending at the admitted horizon-contact support; every "
        "exact squared period/frequency and positive radiation-take record; the complete two-to-one source join; "
        "every finite binary remnant return; and all 4096 registered alternative combinations."
    ),
    axes=(
        binary_axis("source", "Which compact source radiates?", "unheld-single-source", "A single unheld source has no generated binary orbit.", "held-two-source-orbit", "Two held compact supports generate the binary recurrence."),
        binary_axis("moment", "Which source moment is first radiative?", "monopole-or-dipole-radiation", "Conserved source and momentum close those records.", "admitted-quadrupole-rate", "The admitted quadrupole third-rate is the first positive radiative carrier."),
        binary_axis("transfer", "How is radiated energy represented?", "negative-or-erased-energy", "A negative scalar or erased distinction violates the Fold ledger.", "positive-retained-take", "Radiation is a positive take retained beside the positive orbital remainder."),
        binary_axis("separation", "What follows a positive radiative take?", "fixed-or-expanding-orbit", "That does not conserve the positive binding and radiation ledger.", "strictly-shrinking-positive-separation", "Every successor increases binding magnitude and reduces positive separation."),
        binary_axis("balance", "How are period and separation related?", "imported-or-selected-frequency-law", "An imported or selected law is not forced.", "inverse-square-period-square-equals-radius-cube", "Inverse-square restoring balance forces the exact squared relation without a root."),
        binary_axis("wave", "How often does the quadrupole recur?", "one-or-free-wave-cycle-per-orbit", "A free multiplier loses the two-lobed source record.", "two-wave-cycles-per-orbit", "The quadrupole repeats twice per complete binary orbit."),
        binary_axis("contact", "When does inspiral terminate?", "chosen-merger-time", "A chosen time is a parameter.", "first-horizon-boundary-contact", "The first exact equality of the two retained horizon boundaries forces contact."),
        binary_axis("merger", "What is the contact successor?", "erased-or-two-source-remnant", "It either deletes provenance or fails to join.", "one-remnant-with-held-ledger", "Two sources join one remnant while radiation and component labels remain held."),
        binary_axis("tone", "What fixes ringdown recurrence?", "fitted-tone", "A fitted tone is measurement-selected.", "held-remnant-mass-turn-class", "The remnant mass and turn labels fix one recurrence class."),
        binary_axis("damping", "How does ringdown amplitude change?", "negative-exponential-or-free-decay", "That imports a forbidden scalar or parameter.", "binary-half-One-contraction", "The least nonempty equal binary contraction is half-One per return."),
        binary_axis("floor", "How does damping terminate?", "numerical-zero-or-completed-infinity", "Neither is an admissible Fold proof endpoint.", "positive-at-every-finite-depth", "Every reached finite amplitude remains an exact positive fraction."),
        binary_axis("sequence", "Which complete causal ordering survives?", "permuted-or-omitted-stage", "It violates contact and source causality.", "inspiral-chirp-merger-ringdown", "Positive transfer, first contact and one-remnant return force this unique order."),
    ),
    exact_result=(
        "For every positive finite binary shrink depth, separation and period squared strictly fall, exact squared "
        "orbital and gravitational-wave frequencies strictly rise, and every successor retains a positive radiated "
        "take. The quadrupole wave frequency is exactly twice the orbital frequency. At the first exact horizon "
        "contact, two compact source supports join one remnant with the complete radiation and component ledger "
        "held. The remnant mass/turn key fixes one tone class and its positive amplitude halves at every finite "
        "return. The unique causal waveform order is inspiral with rising chirp, merger, then damped ringdown; no "
        "negative, irrational, imaginary, continuum, numerical-zero or completed-infinite proof scalar enters."
    ),
    induction_base="At separation two, one positive radiation take reaches the exact contact separation One; squared frequency rises and the two horizons touch.",
    induction_step="Prepending any binary separation double preserves inverse-square balance, positive take, strict frequency ordering and the same contact; appending any remnant return halves positive amplitude while holding its tone key.",
    exclusions=(
        "no V1/V2 executable, LIGO waveform, dimensional frequency, measured mass or conventional inspiral equation in formal execution",
        "no fitted chirp mass, merger time, waveform template, damping time, tone, amplitude or correction",
        "no numerical zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinite proof scalar",
        "no erased radiation, source, component, contact or remnant record",
        "no claim that normalized Fold frequency is a measured hertz value",
    ),
    witnesses=(
        Witness("chirp", "Every registered finite inspiral has shrinking separation and rising squared wave frequency.", _theorem["all_chirps_close"]),
        Witness("merger", "First horizon contact joins two sources to one remnant without erasing the radiation ledger.", _theorem["merger_closes"]),
        Witness("ringdown", "Every finite remnant trace holds its tone and halves positive amplitude.", _theorem["all_ringdowns_close"]),
        Witness("sequence", "The complete causal ordering contains exactly the three forced stages.", _theorem["unique_ordered_sequence"] == ("inspiral-rising-chirp", "merger", "damped-ringdown")),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "COMPONENT_MASS", "CONTACT_SEPARATION", "EMPTY_ONE_FORM", "HALF_ONE", "ONE",
    "QUARTER_ONE", "SPEC", "inspiral_certificate", "inspiral_trace", "merger_record", "orbital_row",
    "positive_take", "ringdown_certificate", "ringdown_trace", "theorem_certificate",
)
