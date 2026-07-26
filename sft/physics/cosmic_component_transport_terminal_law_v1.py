"""Terminal cosmic component transport, expansion and threshold laws."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"
MATTER_TODAY = Fraction(5, 16)
VACUUM_TODAY = Fraction(11, 16)
THREE_SPACE = 3
RADIATION_POWER = 4


def _require_positive_exact(value: Fraction) -> Fraction:
    value = Fraction(value)
    if value <= 0:
        raise ValueError("cosmic transport requires a positive exact Fold stretch")
    return value


def matter_transport(stretch: Fraction) -> Fraction:
    stretch = _require_positive_exact(stretch)
    return stretch ** THREE_SPACE


def radiation_transport(stretch: Fraction) -> Fraction:
    stretch = _require_positive_exact(stretch)
    return stretch ** RADIATION_POWER


def vacuum_transport(stretch: Fraction) -> Fraction:
    _require_positive_exact(stretch)
    return Fraction(1, 1)


def late_squared_expansion(stretch: Fraction) -> Fraction:
    """Exact dimensionless late-time H-squared carrier."""

    stretch = _require_positive_exact(stretch)
    return VACUUM_TODAY + MATTER_TODAY * matter_transport(stretch)


def matter_fraction(stretch: Fraction) -> Fraction:
    stretch = _require_positive_exact(stretch)
    matter = MATTER_TODAY * matter_transport(stretch)
    return matter / (VACUUM_TODAY + matter)


def vacuum_fraction(stretch: Fraction) -> Fraction:
    stretch = _require_positive_exact(stretch)
    return VACUUM_TODAY / late_squared_expansion(stretch)


def matter_vacuum_equality_cube() -> Fraction:
    return VACUUM_TODAY / MATTER_TODAY


def acceleration_onset_cube() -> Fraction:
    return Fraction(2, 1) * VACUUM_TODAY / MATTER_TODAY


def present_acceleration_magnitude() -> Fraction:
    """Typed accelerating separation; never a negative proof scalar."""

    return VACUUM_TODAY - MATTER_TODAY / 2


def component_laws() -> tuple[dict[str, object], ...]:
    return (
        {
            "component": "matter",
            "transport_power": THREE_SPACE,
            "pressure_orientation": "empty-pressure-One-form",
            "conventional_correspondence": "w=0 and forward dilution a^-3",
        },
        {
            "component": "radiation",
            "transport_power": RADIATION_POWER,
            "pressure_orientation": "outward-third-One",
            "conventional_correspondence": "w=1/3 and forward dilution a^-4",
        },
        {
            "component": "vacuum",
            "transport_power": "empty-dilution-One-form",
            "pressure_orientation": "tension-One",
            "conventional_correspondence": "w=-1 and forward dilution a^0",
        },
    )


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal cosmic component transport and expansion law",
    statement=(
        "Generator-three space forces matter transport by the third power of exact past stretch; one additional "
        "wave-recurrence stretch forces radiation by the fourth power; and the vacuum Fold invariant retains the "
        "One. With the admitted terminal present shares matter 5/16 and vacuum 11/16, the exact late squared-rate "
        "carrier is E2(r)=(11+5r^3)/16, the matter fraction is 5r^3/(11+5r^3), equality is r^3=11/5, acceleration "
        "onset is r^3=22/5, and today's accelerating separation has magnitude 17/32. Tension and acceleration are "
        "typed orientations, never negative proof scalars."
    ),
    dependencies=(
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-WAVE-SPEED-LENGTH-FREQUENCY-001",
        "SFT-PHYS-COSMO-REDSHIFT-001",
        "SFT-PHYS-COSMO-EXPANSION-001",
        "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",
        "SFT-PHYS-COSMO-COMPLETE-BUDGET-001",
        "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of spatial carrier, matter transport, radiation transport, vacuum invariant, "
        "terminal expansion, density fractions, equality threshold, acceleration threshold, orientation typing, "
        "physical scale transport, target custody, prior-correction and extension forms."
    ),
    grammar_boundary=(
        "Every positive exact rational stretch; the three matter/radiation/vacuum transport classes; the admitted "
        "terminal 5/16 and 11/16 late-time shares; every exact derived fraction and cube threshold; all thirty-two "
        "registered cosmic-chronometer rows; the registered acceleration, equation-of-state, Planck-ratio and DESI "
        "adverse rows; and no imported continuum or signed proof scalar."
    ),
    axes=(
        binary_axis("space", "What fixes volume transport?", "borrowed-three-dimensional-volume", "Borrowing the exponent imports a premise.", "admitted-generator-three-volume", "The independently admitted stable three-space supplies the complete volume power."),
        binary_axis("matter", "How does retained matter transport?", "selected-matter-power", "A selected exponent is a free law.", "inverse-volume-third-power", "Fixed content over generator-three volume forces the third power of past stretch."),
        binary_axis("radiation", "How does radiation transport?", "selected-radiation-power", "A selected fourth power is not derived.", "volume-plus-one-recurrence-power", "Three-space dilution plus one wave-recurrence stretch forces the fourth power."),
        binary_axis("vacuum", "How does vacuum transport?", "selected-static-density", "A named cosmological constant cannot select invariance.", "Fold-invariant-One", "An unchanged Fold carrier has exactly the One transport factor at every successor."),
        binary_axis("expansion", "What squared-rate relation follows?", "superseded-two-thirds-curve", "The leading budget is rejected by the admitted terminal discriminator.", "terminal-eleven-five-curve", "Exact composition of 11/16 invariant vacuum and 5/16 third-power matter forces (11+5r^3)/16."),
        binary_axis("fractions", "How do epoch fractions follow?", "fitted-epoch-density", "An epoch fit is a parameter.", "component-over-complete-rate", "Each transported component divided by their exact complete carrier forces both fractions."),
        binary_axis("equality", "Where are matter and vacuum equal?", "decimal-root-selected", "A decimal root may be target-selected and irrational.", "exact-cube-eleven-fifths", "Equating 5r^3 and 11 forces r^3=11/5; only certified rational bounds may display the root."),
        binary_axis("acceleration", "Where does acceleration begin?", "old-half-magnitude-and-four-cube", "The old result inherits a superseded budget.", "exact-seventeen-thirty-seconds-and-twenty-two-fifths", "Matter's half-share and vacuum tension force today's 17/32 separation and onset r^3=22/5."),
        binary_axis("orientation", "How are tension and acceleration represented?", "negative-proof-scalars", "Negative scalars violate the Fold proof language.", "positive-magnitude-with-held-orientation", "Magnitude remains an exact positive fraction while tension/acceleration is a typed label."),
        binary_axis("scale", "How is a dimensional H value obtained?", "fitted-Hubble-normalization", "Fitting H0 to the chronometer rows would select the result.", "post-seal-held-reference-transport", "The zero-parameter dimensionless curve seals first; a separately measured H0 interval transports it afterward."),
        binary_axis("target", "May measurements select the curve?", "measurements-readable-before-seal", "Target access can manufacture the law.", "all-targets-open-only-after-seal", "All CCH, acceleration, w, Planck and adverse DESI rows remain outside the forcing runtime."),
        binary_axis("extension", "May another coefficient or exception enter?", "free-component-correction", "An inserted coefficient is a fit.", "no-extra-rule", "Dimension, recurrence, invariant and terminal shares exhaust the declared law."),
    ),
    exact_result=(
        "Matter, radiation and vacuum have respectively third-power, fourth-power and Fold-invariant transport. "
        "The terminal late-time law is E2(r)=(11+5r^3)/16; Omega_m(r)=5r^3/(11+5r^3); Omega_v(r)=11/(11+5r^3); "
        "matter-vacuum equality is r^3=11/5; acceleration onset is r^3=22/5; and the present accelerating magnitude "
        "is 17/32. The static-vacuum correspondence is tension of One magnitude. All quantities are exact positive "
        "whole/fractional Fold forms or typed empty/orientation structures."
    ),
    induction_base=(
        "At present stretch One, the terminal shares close 5/16+11/16 to the One and E2(One)=One; the acceleration "
        "carrier is the positive separation 11/16 from 5/32, exactly 17/32."
    ),
    induction_step=(
        "Appending one exact stretch factor multiplies matter volume support by three copies, radiation by those "
        "three plus one recurrence copy, and vacuum by the unchanged One; exact composition and fraction closure "
        "are preserved for every positive finite rational stretch."
    ),
    exclusions=(
        "no V1/V2 executable, old two-thirds/one-third survivor or external equation in forcing",
        "no numerical-nothing zero, negative, irrational, imaginary, floating, NaN or completed-infinity proof scalar",
        "no continuum scale factor, differential field equation, fitted Hubble value, fitted density or selected redshift",
        "no use of a measured q, w, transition, H row or DESI interpretation before the derivation seal",
        "no erasure of the superseded one-half/four-cube results or the current DESI dynamic-dark-energy tension",
        "no claim that the terminal late matter-vacuum slice supplies a measured present radiation normalization",
    ),
    witnesses=(
        Witness("component-powers", "Three-space, one recurrence and the invariant force matter/radiation/vacuum transport.", component_laws()[0]["transport_power"] == 3 and component_laws()[1]["transport_power"] == 4 and vacuum_transport(Fraction(37, 19)) == 1),
        Witness("present-closure", "The terminal shares and present squared rate close exactly to the One.", MATTER_TODAY + VACUUM_TODAY == 1 and late_squared_expansion(Fraction(1, 1)) == 1),
        Witness("thresholds", "The terminal shares force both exact cube thresholds.", matter_vacuum_equality_cube() == Fraction(11, 5) and acceleration_onset_cube() == Fraction(22, 5)),
        Witness("acceleration", "Today's typed accelerating separation is exactly 17/32.", present_acceleration_magnitude() == Fraction(17, 32)),
        Witness("fraction-closure", "Matter and vacuum fractions close to the One at every sampled exact stretch.", all(matter_fraction(r) + vacuum_fraction(r) == 1 for r in (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3)))),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "MATTER_TODAY", "RADIATION_POWER", "SPEC", "THREE_SPACE", "VACUUM_TODAY",
    "acceleration_onset_cube", "component_laws", "late_squared_expansion", "matter_fraction",
    "matter_transport", "matter_vacuum_equality_cube", "present_acceleration_magnitude",
    "radiation_transport", "vacuum_fraction", "vacuum_transport",
)
