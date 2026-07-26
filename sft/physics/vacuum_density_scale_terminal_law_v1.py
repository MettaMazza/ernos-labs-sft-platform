"""Vacuum floor, cosmic density and exact scale-transport distinctions."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035"
BINARY = 2
GENERATOR = 3
SPACE_RANK = 3
TERMINAL_VACUUM_SHARE = Fraction(11, 16)


def least_binary_cover_depth(size: int) -> int:
    if isinstance(size, bool) or size < 1:
        raise ValueError("cover size must be a positive whole")
    depth = 1
    support = BINARY
    while support < size:
        support *= BINARY
        depth += 1
    return depth


def generation_volume() -> int:
    return GENERATOR ** SPACE_RANK


def boundary_record_depth() -> int:
    """Both held Fold labels occur at every covering depth."""

    return BINARY * least_binary_cover_depth(generation_volume())


def local_vacuum_amplitude_floor() -> Fraction:
    return Fraction(1, BINARY ** boundary_record_depth())


def local_vacuum_energy_floor() -> Fraction:
    amplitude = local_vacuum_amplitude_floor()
    return amplitude * amplitude


def finite_zero_point_ledger(depth: int) -> dict[str, object]:
    """Close the complete finite half-spacing mode ledger at one depth.

    The host count named ``depth`` only enumerates the exact finite Fold
    support.  Structural absence is never inserted as a numerical mode.  The
    complete odd-numerator spectrum sums to support/2, so its common-scale
    per-mode carrier is exactly the half-One at every positive depth.
    """

    if isinstance(depth, bool) or depth < 1:
        raise ValueError("radiative depth must be a positive generated count")
    support = BINARY ** depth
    denominator = BINARY ** (depth + 1)
    modes = tuple(Fraction(BINARY * rank - 1, denominator) for rank in range(1, support + 1))
    total = sum(modes, Fraction())
    mean = total / support
    return {
        "depth": depth,
        "support": support,
        "modes": modes,
        "total": total,
        "mean": mean,
        "closed": total == Fraction(support, BINARY) and mean == Fraction(1, BINARY),
    }


def local_floor_candidates() -> tuple[dict[str, object], ...]:
    """Complete support-scope by observable-composition subgrammar."""

    cover = least_binary_cover_depth(generation_volume())
    rows = []
    for complete_boundary in (False, True):
        for energy_self_composition in (False, True):
            amplitude_depth = cover * (BINARY if complete_boundary else 1)
            observable_depth = amplitude_depth * (BINARY if energy_self_composition else 1)
            rows.append({
                "candidate_id": f"{'complete-boundary' if complete_boundary else 'one-label'}__{'energy-self-composition' if energy_self_composition else 'amplitude-only'}",
                "amplitude_depth": amplitude_depth,
                "observable_depth": observable_depth,
                "survives": complete_boundary and energy_self_composition,
            })
    return tuple(rows)


def normalized_cosmological_constant() -> Fraction:
    """Lambda times the squared Hubble length in limiting-speed units."""

    return SPACE_RANK * TERMINAL_VACUUM_SHARE


def cosmological_constant_scale_transport(rate: Fraction, limiting_speed: Fraction) -> Fraction:
    """Transport the dimensionless law through a held rate and speed reference."""

    rate = Fraction(rate)
    limiting_speed = Fraction(limiting_speed)
    if rate <= 0 or limiting_speed <= 0:
        raise ValueError("scale references must be exact positive carriers")
    return normalized_cosmological_constant() * rate * rate / (limiting_speed * limiting_speed)


def theorem_certificate() -> dict[str, object]:
    candidates = local_floor_candidates()
    return {
        "generation_volume": generation_volume(),
        "cover_depth": least_binary_cover_depth(generation_volume()),
        "boundary_record_depth": boundary_record_depth(),
        "amplitude_floor": local_vacuum_amplitude_floor(),
        "energy_floor": local_vacuum_energy_floor(),
        "candidate_count": len(candidates),
        "survivor_count": sum(bool(row["survives"]) for row in candidates),
        "finite_radiative_ledgers_close": all(finite_zero_point_ledger(depth)["closed"] for depth in range(1, 9)),
        "normalized_cosmological_constant": normalized_cosmological_constant(),
        "floor_and_cosmic_density_are_distinct_types": local_vacuum_energy_floor() != TERMINAL_VACUUM_SHARE,
        "scale_covariance": all(
            cosmological_constant_scale_transport(rate * scale, speed * scale)
            == cosmological_constant_scale_transport(rate, speed)
            for rate, speed, scale in product(
                (Fraction(1, 3), Fraction(2, 3), Fraction(1)),
                (Fraction(1, 2), Fraction(3, 4), Fraction(1)),
                (Fraction(1, 4), Fraction(2), Fraction(3)),
            )
        ),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal vacuum floor, cosmic density and scale-transport law",
    statement=(
        "Generator-three space has volume twenty-seven and unique least binary covering depth five. Both held "
        "Fold labels at every covering level force a complete boundary-record depth ten. Its least nonempty local "
        "vacuum amplitude is One/2^10; energy is the complete two-leg self-composition, uniquely forcing the local "
        "energy floor One/2^20. This local dimensionless cell floor is not the cosmological density fraction. The "
        "terminal cosmic vacuum share is 11/16, and three-space rate geometry forces the separately typed normalized "
        "cosmological magnitude Lambda(c/H)^2=3(11/16)=33/16. A dimensional Lambda follows only after a held external "
        "rate and speed reference: Lambda=(33/16)H^2/c^2."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-EXACT-OPERATIONS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
        "SFT-PHYS-COSMO-COMPLETE-BUDGET-001",
        "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
        "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of generator volume, binary cover, boundary-label scope, observable "
        "composition, local floor, finite radiative ledger, cosmic share, spatial rate multiplicity, typed prior-claim "
        "correction, scale transport, measurement custody and extension form."
    ),
    grammar_boundary=(
        "The generated volume 3^3; every binary support until the unique least cover; one-label versus complete-two-label "
        "boundary support; amplitude versus two-leg energy composition; every finite positive-depth complete "
        "half-spacing mode ledger; exact 11/16 terminal vacuum share; three-space rate transport; every exact positive "
        "rational held rate/speed reference; and no untyped equality between a local floor, density fraction and "
        "dimensional cosmological constant."
    ),
    axes=(
        binary_axis("volume", "What fixes the spatial support?", "borrowed-cosmic-volume", "A borrowed volume imports a model.", "generator-three-cubed-volume", "The independently admitted generator and stable space rank force twenty-seven."),
        binary_axis("cover", "Which binary depth covers that volume?", "selected-depth-ten-or-twenty", "Selecting the desired exponent is circular.", "least-cover-depth-five", "Explicit binary succession first covers twenty-seven at thirty-two."),
        binary_axis("boundary", "Which labels must a complete local record retain?", "one-label-per-depth", "One label omits half the Fold fibre.", "both-held-labels-per-depth", "The Fold has exactly two distinct held labels at every depth."),
        binary_axis("observable", "Is the claimed quantity amplitude or energy?", "amplitude-relabeled-as-energy", "A one-leg support is not a complete energy observation.", "two-leg-energy-self-composition", "Preparation-to-record energy support pairs the exact amplitude with itself."),
        binary_axis("floor", "What is the least nonempty local energy support?", "named-one-over-two-to-twenty", "Naming the prior value does not force it.", "complete-boundary-energy-floor", "Depth five times two labels times two observation legs uniquely gives exponent twenty."),
        binary_axis("radiative", "How is the zero-point mode ledger closed?", "unbounded-mode-sum-as-local-density", "An unbounded sum erases finite support, common scale and quantity type.", "complete-finite-ledger-and-half-One-mean", "Every finite complete odd-numerator spectrum sums exactly to support/2 and normalizes to the half-One."),
        binary_axis("cosmic", "What is the cosmic vacuum density fraction?", "local-floor-equals-cosmic-fraction", "The quantities have different supports and types.", "terminal-eleven-sixteenths-share", "The admitted complete cosmic budget fixes the global fraction."),
        binary_axis("geometry", "What normalizes the cosmological magnitude?", "borrowed-continuum-coefficient", "A conventional field equation cannot be a premise.", "three-space-squared-rate-carrier", "Three generated spatial source directions multiply the admitted squared expansion rate."),
        binary_axis("typing", "May floor, fraction and dimensional Lambda be interchanged or the prior label rubber-stamped?", "untyped-number-identification-or-rubber-stamp", "Equal-looking numbers without scale carriers are not one quantity, and preserving an old label cannot excuse a type error.", "distinct-typed-quantities-and-prior-correction", "Each quantity retains its support, dimension and transport trace; the exact prior floor is retained while its unscaled cosmological relabeling is rejected."),
        binary_axis("transport", "How does Lambda receive units?", "fitted-dimensional-value", "A fitted unit magnitude is a parameter.", "postseal-rate-squared-over-speed-squared", "A held rate and limiting speed transport the sealed normalized relation covariantly."),
        binary_axis("measurement", "May a dark-energy value select the law?", "measurement-readable-before-seal", "That would fit the magnitude.", "postseal-only-comparison", "Floor, share and normalized Lambda seal before external cosmology is opened."),
        binary_axis("extension", "May another scale or coefficient enter?", "free-vacuum-scale", "A second vacuum ruler violates the one-axis law.", "no-extra-rule", "Cover, labels, observation legs, cosmic share and held transport exhaust the grammar."),
    ),
    exact_result=(
        "The unique complete local vacuum boundary-energy floor is One/2^20=(One/2^10)^2. At every finite "
        "radiative depth k, the complete 2^k half-spacing modes sum to 2^(k-1) and have common-scale mean 1/2. "
        "The terminal cosmic vacuum fraction is separately 11/16. The normalized cosmological magnitude is "
        "Lambda(c/H)^2=33/16, and dimensional transport is Lambda=(33/16)H^2/c^2 after held external scale "
        "references are supplied. Equating the local floor, a raw mode total, the global fraction or a dimensional "
        "cosmological density is rejected as a type error."
    ),
    induction_base=(
        "At the first binary support, both held labels are required and a complete energy record pairs its local "
        "amplitude twice; no empty numerical state is introduced."
    ),
    induction_step=(
        "Each additional cover depth appends both held labels once; energy self-composition doubles the accumulated "
        "label depth. Each radiative successor doubles the mode count and total while retaining mean 1/2. Exact "
        "rate/speed rescaling preserves the normalized cosmological ratio at every finite scale."
    ),
    exclusions=(
        "no V1/V2 executable, stored exponent survivor, dark-energy measurement or conventional field equation in forcing",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof scalar",
        "no fitted cosmological density, Hubble value, gravitational value or second vacuum scale",
        "no direct identification of the local One/2^20 cell floor with Omega_v, Lambda or a dimensionful density",
        "no reuse of the withdrawn measurement-influenced 2 alpha^4/H^3 proposal",
        "no claim that a continuum zero-point mode sum is an SFT derivational object",
    ),
    witnesses=(
        Witness("cover", "Twenty-seven is first covered at binary depth five.", generation_volume() == 27 and least_binary_cover_depth(27) == 5),
        Witness("complete-floor-census", "The two-by-two support/composition subgrammar has one complete energy survivor.", len(local_floor_candidates()) == 4 and sum(bool(row["survives"]) for row in local_floor_candidates()) == 1),
        Witness("floor", "Complete boundary amplitude depth ten self-composes to exact energy depth twenty.", boundary_record_depth() == 10 and local_vacuum_amplitude_floor() == Fraction(1, 2 ** 10) and local_vacuum_energy_floor() == Fraction(1, 2 ** 20)),
        Witness("radiative-ledger", "Every generated finite complete mode ledger has total support/2 and mean half-One.", theorem_certificate()["finite_radiative_ledgers_close"]),
        Witness("cosmic-magnitude", "Three-space transport of the terminal vacuum share is exactly 33/16.", normalized_cosmological_constant() == Fraction(33, 16)),
        Witness("typed-separation", "The local floor and global cosmic fraction remain distinct exact quantities.", theorem_certificate()["floor_and_cosmic_density_are_distinct_types"]),
        Witness("scale-covariance", "Common exact rescaling of held rate and speed leaves Lambda invariant.", theorem_certificate()["scale_covariance"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "BINARY", "CLAIM_ID", "GENERATOR", "SPACE_RANK", "SPEC", "TERMINAL_VACUUM_SHARE",
    "boundary_record_depth", "cosmological_constant_scale_transport", "finite_zero_point_ledger", "generation_volume",
    "least_binary_cover_depth", "local_floor_candidates", "local_vacuum_amplitude_floor",
    "local_vacuum_energy_floor", "normalized_cosmological_constant", "theorem_certificate",
)
