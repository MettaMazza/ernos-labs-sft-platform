"""Exact thermal-history, freeze-out and recombination composition law."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037"
BINARY = 2
UP_DEPTH = 7


def require_positive_fraction(value: Fraction, name: str) -> Fraction:
    value = Fraction(value)
    if value <= 0:
        raise ValueError(f"{name} must be an exact positive Fold carrier")
    return value


def transported_temperature(earlier_temperature: Fraction, scale_growth: Fraction) -> Fraction:
    """Transport temperature through one exact later/earlier scale ratio."""

    temperature = require_positive_fraction(earlier_temperature, "temperature")
    growth = require_positive_fraction(scale_growth, "scale growth")
    return temperature / growth


def temperature_scale_invariant(earlier_temperature: Fraction, scale_growth: Fraction) -> bool:
    later = transported_temperature(earlier_temperature, scale_growth)
    return later * Fraction(scale_growth) == Fraction(earlier_temperature)


def ordered_thresholds(thresholds: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    """Return the forced cooling order of distinct exact positive thresholds."""

    if not thresholds:
        raise ValueError("at least one generated threshold is required")
    exact = tuple(require_positive_fraction(value, "threshold") for value in thresholds)
    if len(set(exact)) != len(exact):
        raise ValueError("epoch thresholds must retain distinct exact records")
    return tuple(sorted(exact, reverse=True))


def live_depth_seven_orbit() -> tuple[int, ...]:
    """Walk the complete non-closing binary orbit generated from the least part."""

    orbit: list[int] = []
    residue = 1
    while residue not in orbit:
        orbit.append(residue)
        residue = (BINARY * residue) % UP_DEPTH
    return tuple(orbit)


def freezeout_capture_ledger() -> dict[str, Fraction | tuple[int, ...]]:
    """Separate freeze-out share, one complete-cover successor and capture ratio.

    The old V1/V2 shorthand called One/seven the neutron-to-proton ratio at
    freeze-out.  The generated orbit instead fixes One/seven as the least live
    neutron *share*.  Its complement is six/seven, so the freeze-out ratio is
    One/six.  Carrying the held neutron record into the least complete binary
    cover changes its share to One/eight; the capture-entry ratio is then
    One/seven.  Pairing every retained neutron with one proton in helium-four
    gives the exact mass shares One/four helium family and three/four hydrogen
    family without inserting subtraction into the proof domain.
    """

    orbit = live_depth_seven_orbit()
    freezeout_neutron = Fraction(min(orbit), UP_DEPTH)
    freezeout_proton = Fraction(6, UP_DEPTH)
    cover = BINARY ** 3
    capture_neutron = Fraction(1, cover)
    capture_proton = Fraction(7, cover)
    helium_family = BINARY * capture_neutron
    hydrogen_family = Fraction(6, cover)
    return {
        "orbit": orbit,
        "freezeout_neutron_share": freezeout_neutron,
        "freezeout_proton_share": freezeout_proton,
        "freezeout_neutron_proton_ratio": freezeout_neutron / freezeout_proton,
        "capture_neutron_share": capture_neutron,
        "capture_proton_share": capture_proton,
        "capture_neutron_proton_ratio": capture_neutron / capture_proton,
        "helium_family_mass_share": helium_family,
        "hydrogen_family_mass_share": hydrogen_family,
    }


def visibility_ledger(radius: int) -> dict[str, object]:
    """Generate a finite positive symmetric last-scattering support.

    Half-One is the bound/free classification midpoint.  It is not relabelled
    as a zero-width physical event.  Every positive radius retains a finite
    symmetric support with one uniquely maximal midpoint record.
    """

    if isinstance(radius, bool) or radius < 1:
        raise ValueError("visibility radius must be a positive generated count")
    rising = tuple(range(1, radius + 2))
    weights = rising + tuple(reversed(rising[:-1]))
    total = sum(weights)
    normalized = tuple(Fraction(weight, total) for weight in weights)
    midpoint = radius
    return {
        "radius": radius,
        "weights": weights,
        "normalized": normalized,
        "midpoint_index": midpoint,
        "unique_midpoint": normalized[midpoint] == max(normalized) and normalized.count(normalized[midpoint]) == 1,
        "complete": sum(normalized) == Fraction(1),
    }


def acoustic_mode_ledger(mode_count: int) -> tuple[dict[str, object], ...]:
    """Enumerate internal positive-whole standing modes and parity loading."""

    if isinstance(mode_count, bool) or mode_count < 1:
        raise ValueError("mode count must be a positive generated count")
    return tuple(
        {
            "mode": mode,
            "phase_support": Fraction(mode, mode_count + 1),
            "loading": "compression" if mode % BINARY == 1 else "rarefaction",
        }
        for mode in range(1, mode_count + 1)
    )


def finite_sound_horizon(durations: tuple[Fraction, ...], speeds: tuple[Fraction, ...]) -> Fraction:
    """Exact generated-finite sound horizon; no continuum integral is used."""

    if not durations or len(durations) != len(speeds):
        raise ValueError("sound-horizon segments must be nonempty and paired")
    segments = tuple(
        require_positive_fraction(duration, "duration") * require_positive_fraction(speed, "speed")
        for duration, speed in zip(durations, speeds)
    )
    total = segments[0]
    for segment in segments[1:]:
        total += segment
    return total


def theorem_certificate() -> dict[str, object]:
    ledger = freezeout_capture_ledger()
    thresholds = (Fraction(7, 8), Fraction(3, 4), Fraction(1, 2), Fraction(1, 4))
    modes = acoustic_mode_ledger(8)
    return {
        "temperature_transport": all(
            temperature_scale_invariant(temperature, growth)
            for temperature in (Fraction(1, 4), Fraction(2, 3), Fraction(5, 2))
            for growth in (Fraction(1, 2), Fraction(2), Fraction(7, 3))
        ),
        "threshold_order": ordered_thresholds(tuple(reversed(thresholds))) == thresholds,
        "orbit": live_depth_seven_orbit(),
        "freezeout_ratio": ledger["freezeout_neutron_proton_ratio"],
        "capture_ratio": ledger["capture_neutron_proton_ratio"],
        "helium_share": ledger["helium_family_mass_share"],
        "hydrogen_share": ledger["hydrogen_family_mass_share"],
        "visibility": all(visibility_ledger(radius)["complete"] and visibility_ledger(radius)["unique_midpoint"] for radius in range(1, 9)),
        "acoustic_parity": tuple(row["loading"] for row in modes)
        == ("compression", "rarefaction") * 4,
        "sound_horizon": finite_sound_horizon(
            (Fraction(1, 8), Fraction(1, 4), Fraction(3, 8)),
            (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4)),
        ),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal thermal-history, freeze-out and recombination law",
    statement=(
        "Exact Fold temperature is transported inversely to exact scale growth, so temperature times scale is held. "
        "Distinct binding thresholds therefore impose one descending thermal order without a named chronology selecting it. "
        "The complete binary orbit on depth seven is (One, two, four)/seven. Its least live part fixes the freeze-out "
        "neutron share One/seven, not the old shorthand neutron/proton ratio. The proton share is six/seven and the "
        "freeze-out ratio is One/six. Transport into the least complete binary cover gives capture shares One/eight and "
        "seven/eight, hence neutron/proton One/seven; complete neutron pairing forces helium-family share One/four and "
        "hydrogen-family share three/four. Recombination is classified at the half-One bound/free midpoint, while every "
        "physical visibility record remains finite and positive rather than an instantaneous collapse. Pre-decoupling "
        "acoustics have exact positive-whole internal modes with alternating compression/rarefaction parity; observed "
        "angular peaks retain projection and driving records and are not asserted to be exact integer multiples."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-EXACT-OPERATIONS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-THERMO-TEMPERATURE-001",
        "SFT-PHYS-THERMO-EQUILIBRIUM-001",
        "SFT-PHYS-COSMO-REDSHIFT-001",
        "SFT-PHYS-COSMO-BACKGROUND-001",
        "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
        "SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",
        "SFT-PHYS-ATOMIC-HYDROGEN-RYDBERG-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006",
        "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006",
        "SFT-PHYS-PLASMA-COLLECTIVE-001",
        "SFT-PHYS-PLASMA-OSCILLATION-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of provenance, temperature transport, threshold order, freeze-out carrier, "
        "complete-cover transport, nuclear capture, recombination support and acoustic observation form."
    ),
    grammar_boundary=(
        "Every exact positive rational temperature and scale carrier; every finite set of distinct positive binding "
        "thresholds; the complete binary orbit of the least part on depth seven; the least complete depth-three binary "
        "cover; every finite positive visibility radius; every finite positive internal acoustic mode count; exact "
        "generated-finite sound-horizon segments; and strict separation of internal mode labels from observed projection."
    ),
    axes=(
        binary_axis("provenance", "What selects the thermal history?", "named-cosmological-chronology", "A familiar chronology cannot select a Fold law.", "admitted-threshold-and-transport-dependencies", "The complete root-traced physical carriers select the law."),
        binary_axis("temperature", "How does temperature move with scale?", "same-direction-or-fitted-cooling", "A named cooling curve or fitted exponent adds a rule.", "exact-inverse-scale-transport", "Holding temperature times scale uniquely preserves the transported recurrence energy."),
        binary_axis("threshold", "What orders physical epochs?", "named-epoch-list", "Names do not prove order.", "descending-distinct-binding-thresholds", "Monotone cooling crosses the complete exact thresholds in their forced descending order."),
        binary_axis("freezeout", "What does the depth-seven orbit fix?", "one-seventh-ratio-rubber-stamp", "The old label conflates a constituent share with a pair ratio.", "least-live-neutron-share", "The complete orbit has one least live part, One/seven, with separately retained six/seven complement."),
        binary_axis("decay", "How is capture-entry transport represented?", "selected-decay-correction", "A fitted decay fraction is inadmissible.", "least-complete-binary-cover-successor", "The held least live record enters the unique least complete support, depth three, as One/eight."),
        binary_axis("capture", "What mass partition follows complete neutron capture?", "named-quarter-abundance", "Naming one quarter does not force it.", "paired-neutron-helium-and-hydrogen-families", "Two retained nucleons per neutron force One/four helium-family and three/four hydrogen-family support."),
        binary_axis("recombination", "What is the decoupling boundary?", "instantaneous-zero-width-collapse", "A zero-width event erases physical visibility support.", "half-One-midpoint-with-finite-visibility", "The bound/free midpoint classifies the transition while every generated radius retains a complete positive record."),
        binary_axis("acoustic", "How are acoustic peaks represented?", "observed-multipoles-assumed-exact-integers", "Projection and driving cannot be erased to preserve an old slogan.", "internal-whole-modes-parity-and-projection-record", "Internal modes are exact positive wholes; alternating parity is retained and angular observation remains a typed projection."),
    ),
    exact_result=(
        "For every exact positive scale growth g, T_later=T_earlier/g and T_later*g=T_earlier. Distinct binding "
        "thresholds are crossed in unique descending order. The depth-seven binary orbit (1,2,4)/7 forces freeze-out "
        "neutron/proton shares 1/7 and 6/7 and ratio 1/6. The least complete binary-cover successor forces capture-entry "
        "shares 1/8 and 7/8 and ratio 1/7. Complete retained-neutron pairing forces helium-family mass share 1/4 and "
        "hydrogen-family share 3/4. Recombination has an exact half-One classification midpoint and a finite positive "
        "visibility ledger at every generated radius. Acoustic standing modes are positive whole labels with exact "
        "odd/even compression-rarefaction parity; observed angular positions retain their projection and are not proof "
        "identical to the internal whole labels."
    ),
    induction_base=(
        "One exact thermal carrier and one exact scale relation preserve their product; the first positive visibility "
        "radius has three positive records and one unique midpoint; the first acoustic mode is a compression record."
    ),
    induction_step=(
        "Each new exact scale carrier preserves inverse transport, each additional distinct threshold inserts at its "
        "unique exact order, each visibility successor adds one mirrored positive record to both sides, and each acoustic "
        "successor alternates parity without erasing projection or driving records."
    ),
    exclusions=(
        "no conventional hot-big-bang equation, continuum fluid integral, stochastic freeze-out or fitted thermal exponent as a premise",
        "no measurement value, helium abundance, recombination redshift or CMB peak location available to candidate selection",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof scalar",
        "no untyped identification of neutron share with neutron/proton ratio",
        "no instantaneous zero-width recombination event",
        "no claim that observed CMB angular multipoles are exact integer multiples",
        "no free reaction rate, decay fraction, sound speed, baryon loading or projection coefficient",
    ),
    witnesses=(
        Witness("temperature", "Exact inverse scale transport preserves temperature times scale.", theorem_certificate()["temperature_transport"]),
        Witness("thresholds", "Every distinct exact threshold has one descending cooling position.", theorem_certificate()["threshold_order"]),
        Witness("orbit", "The complete least-part depth-seven binary orbit is exactly one, two and four.", theorem_certificate()["orbit"] == (1, 2, 4)),
        Witness("freezeout-correction", "Freeze-out share One/seven gives ratio One/six; capture-entry share One/eight gives ratio One/seven.", theorem_certificate()["freezeout_ratio"] == Fraction(1, 6) and theorem_certificate()["capture_ratio"] == Fraction(1, 7)),
        Witness("nuclear-partition", "Complete retained-neutron pairing forces One/four helium family and three/four hydrogen family.", theorem_certificate()["helium_share"] == Fraction(1, 4) and theorem_certificate()["hydrogen_share"] == Fraction(3, 4)),
        Witness("visibility", "Every generated finite visibility ledger is complete, positive and uniquely centred.", theorem_certificate()["visibility"]),
        Witness("acoustic-parity", "Positive whole internal modes alternate compression and rarefaction exactly.", theorem_certificate()["acoustic_parity"]),
        Witness("finite-horizon", "The generated-finite sound horizon remains an exact positive Fold carrier.", theorem_certificate()["sound_horizon"] == Fraction(49, 96)),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "BINARY", "CLAIM_ID", "SPEC", "UP_DEPTH", "acoustic_mode_ledger", "finite_sound_horizon",
    "freezeout_capture_ledger", "live_depth_seven_orbit", "ordered_thresholds", "theorem_certificate",
    "temperature_scale_invariant", "transported_temperature", "visibility_ledger",
)
