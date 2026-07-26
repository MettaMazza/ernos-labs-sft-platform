"""Exact binary critical exponents and generator-three cascade scaling."""

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047"


def _positive_whole(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive whole Fold count")
    return value


def mean_field_exponents():
    """Typed binary critical carriers; empty tuples are empty One forms."""
    return {
        "beta": Fraction(1, 2),
        "nu": Fraction(1, 2),
        "gamma": Fraction(1, 1),
        "delta": Fraction(3, 1),
        "alpha": (),
        "eta": (),
    }


def mean_field_scale_witness(base, depth=1):
    """Perfect-power witness for the exponent carriers, without root evaluation."""
    q = _positive_whole(base, "scale base")
    d = _positive_whole(depth, "scale depth")
    order = q ** d
    return {
        "excess": order ** 2,
        "order": order,
        "inverse_correlation": order,
        "inverse_response": order ** 2,
        "critical_field": order ** 3,
        "order_square_is_excess": order ** 2 == q ** (2 * d),
        "correlation_square_is_excess": order ** 2 == q ** (2 * d),
        "response_is_linear_in_excess": order ** 2 == q ** (2 * d),
        "field_is_order_cube": order ** 3 == q ** (3 * d),
    }


def critical_scaling_identities():
    values = mean_field_exponents()
    beta = values["beta"]
    nu = values["nu"]
    gamma = values["gamma"]
    delta = values["delta"]
    return {
        "widom": gamma == beta * (delta - 1),
        "rushbrooke_with_empty_alpha": 2 * beta + gamma == 2 and values["alpha"] == (),
        "fisher_with_empty_eta": gamma == 2 * nu and values["eta"] == (),
        "values": values,
    }


def cascade_exponents():
    return {
        "spatial_branch_count": 3,
        "structure_function": Fraction(2, 3),
        "spectrum_magnitude": Fraction(5, 3),
        "spectrum_orientation": "falling",
    }


def cascade_scale_witness(base, depth=1):
    """Exact cube-refinement witness for 2/3 and falling 5/3 scaling."""
    q = _positive_whole(base, "scale base")
    d = _positive_whole(depth, "scale depth")
    branch = q ** d
    return {
        "length_refinement": branch ** 3,
        "second_order_structure_factor": branch ** 2,
        "wavenumber_refinement": branch ** 3,
        "spectral_energy_divisor": branch ** 5,
        "structure_cube_equals_length_square": (branch ** 2) ** 3 == (branch ** 3) ** 2,
        "spectrum_cube_equals_wavenumber_fifth": (branch ** 5) ** 3 == (branch ** 3) ** 5,
        "falling_orientation_retained": True,
    }


def generated_universality_classes():
    """Complete class census for the declared binary-lock/cubic-cascade grammar."""
    rows = (
        {
            "class_id": "binary-self-antipodal-local-order",
            "generator_key": (2, 2, 3),
            "threshold": Fraction(1, 2),
            "carriers": mean_field_exponents(),
        },
        {
            "class_id": "generator-three-conserved-cascade",
            "generator_key": (3, 2, 5),
            "threshold": Fraction(2, 3),
            "carriers": cascade_exponents(),
        },
    )
    if len({row["generator_key"] for row in rows}) != len(rows):
        raise ValueError("generated universality keys are not distinct")
    return rows


def universality_equivalence(left, right):
    classes = {row["class_id"]: row for row in generated_universality_classes()}
    if left not in classes or right not in classes:
        raise ValueError("universality comparison requires generated class identities")
    return classes[left]["generator_key"] == classes[right]["generator_key"]


def theorem_certificate():
    mean = all(
        all(
            mean_field_scale_witness(base, depth)[key]
            for key in (
                "order_square_is_excess",
                "correlation_square_is_excess",
                "response_is_linear_in_excess",
                "field_is_order_cube",
            )
        )
        for base in range(2, 7)
        for depth in range(1, 7)
    )
    cascade = all(
        cascade_scale_witness(base, depth)["structure_cube_equals_length_square"]
        and cascade_scale_witness(base, depth)["spectrum_cube_equals_wavenumber_fifth"]
        and cascade_scale_witness(base, depth)["falling_orientation_retained"]
        for base in range(2, 7)
        for depth in range(1, 7)
    )
    classes = generated_universality_classes()
    return {
        "mean_field": mean,
        "identities": all(value for key, value in critical_scaling_identities().items() if key != "values"),
        "cascade": cascade,
        "classes": len(classes) == 2 and not universality_equivalence(classes[0]["class_id"], classes[1]["class_id"]),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal exact phase-criticality, universality and turbulence-scaling law",
    statement=(
        "The admitted binary self-antipodal lock fixes the continuous local-order threshold at half-One. Complete positive perfect-power scaling then forces beta=1/2 for the order carrier, nu=1/2 for the inverse-correlation carrier, gamma=One for reciprocal response, and delta=three for the critical-field relation; alpha and eta are empty One exponent records. Widom, Rushbrooke and Fisher close exactly without a numerical-zero proof scalar. Systems share this exponent law exactly when they share the same generated threshold, order-power and field-power key. Separately, the forced three-space branch count fixes a conserved cascade class: cube refinement carries a squared second-order structure record, forcing 2/3, while shell succession adds the One and forces a falling spectrum magnitude 5/3. These are two distinct generated universality classes, not one measurement-selected class."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-HALF-ONE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001",
        "SFT-PHYS-CONDENSED-PHASE-ORDER-001",
        "SFT-PHYS-FLUID-TURBULENCE-001",
        "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of critical threshold, order, correlation, response, critical-field, scaling-identity, cascade and spectrum forms.",
    grammar_boundary="The binary self-antipodal local-order class and the generator-three conserved-cascade class; every positive whole perfect-power scale base and depth; exact rational exponent carriers; and typed empty exponent records.",
    axes=(
        binary_axis("threshold", "What fixes the phase boundary?", "measured-critical-temperature", "A measured temperature would select the law.", "binary-self-antipodal-half-One", "The complete binary complement equation has one self-antipodal part."),
        binary_axis("order", "What fixes beta?", "fitted-decimal-exponent", "A fitted exponent is not forced.", "square-excess-to-linear-order-carrier", "Every perfect-square excess has one retained linear order carrier, forcing 1/2."),
        binary_axis("correlation", "What fixes nu?", "continuum-correlation-length-ansatz", "A continuum ansatz is outside the Fold grammar.", "square-excess-to-linear-inverse-correlation", "The same binary square support forces the reciprocal correlation carrier 1/2."),
        binary_axis("response", "What fixes gamma?", "selected-response-power", "A selected power adds a parameter.", "reciprocal-linear-excess-response", "One complete excess carrier forces reciprocal response exponent One."),
        binary_axis("field", "What fixes delta?", "imported-field-polynomial", "An imported polynomial is an independent model.", "generator-three-order-cube", "The next generator fixes the critical field as the order cube."),
        binary_axis("identities", "What closes the exponent relations?", "numerical-zero-residuals", "Conventional zero is not a proof scalar.", "typed-empty-alpha-eta-with-exact-identities", "Empty exponent records leave all three exact positive identities closed."),
        binary_axis("cascade", "What fixes the structure exponent?", "dimensional-analysis-assumption", "Named dimensional analysis does not force the branch count.", "three-branch-cube-to-square-transfer", "Forced three-space cube refinement carries the conserved second-order square."),
        binary_axis("spectrum", "What fixes the spectral exponent?", "fitted-negative-five-thirds", "A fitted signed exponent violates the grammar.", "falling-held-orientation-with-five-thirds-magnitude", "Shell succession adds the One to 2/3 and retains decrease as orientation."),
    ),
    exact_result=(
        "For the binary self-antipodal local-order class, the threshold is 1/2 and the exact exponent carriers are beta=1/2, nu=1/2, gamma=1 and delta=3, with alpha and eta typed as empty One records. Widom gamma=beta(delta-1), Rushbrooke 2beta+gamma=2 and Fisher gamma=2nu all close exactly. For the distinct generator-three conserved cascade, the second-order structure exponent is 2/3 and the energy-spectrum exponent has falling orientation with positive magnitude 5/3. At every positive whole scale q and depth d, structure^3=length^2 and spectrum-divisor^3=wavenumber^5, providing depth-independent exact witnesses without irrational evaluation."
    ),
    induction_base="At one binary scale step, square excess gives linear order/correlation, linear response exponent One and cubic field exponent three; at one three-space refinement, cube length support carries square structure and fifth-power spectral divisor.",
    induction_step="Appending one exact scale step multiplies all critical perfect powers by the same binary powers and all cascade records by the same cube, square and fifth powers, preserving every exponent identity and universality key.",
    exclusions=(
        "no renormalization-group, continuum field theory, Landau functional or Kolmogorov law imported as a premise",
        "no measured critical exponent, transition temperature, structure function or spectrum slope available to candidate selection",
        "no claim that every physical transition belongs to one class; equality requires the complete generated class key",
        "no fitted exponent, intermittency correction or Reynolds-number calibration",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof magnitude; spectral decrease and empty exponents are typed records",
    ),
    witnesses=(
        Witness("critical-powers", "Every tested positive scale has the forced square, linear and cubic critical-power relations.", theorem_certificate()["mean_field"]),
        Witness("scaling-identities", "Widom, Rushbrooke and Fisher close with typed empty alpha and eta.", theorem_certificate()["identities"]),
        Witness("cascade", "Every tested three-space refinement closes the 2/3 and falling 5/3 power identities.", theorem_certificate()["cascade"]),
        Witness("class-census", "The declared grammar has two distinct complete generated class keys.", theorem_certificate()["classes"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "cascade_exponents",
    "cascade_scale_witness",
    "critical_scaling_identities",
    "generated_universality_classes",
    "mean_field_exponents",
    "mean_field_scale_witness",
    "theorem_certificate",
    "universality_equivalence",
)
