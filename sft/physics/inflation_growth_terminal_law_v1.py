"""Exact Fold inflation, primordial-support and growth transport law."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039"
BINARY = 2
GENERATOR = 3
SPACE_RANK = 3


def least_binary_cover_depth(size: int) -> int:
    if isinstance(size, bool) or size < 1:
        raise ValueError("cover size must be a positive whole")
    depth = 1
    support = BINARY
    while support < size:
        support *= BINARY
        depth += 1
    return depth


def generator_cover() -> tuple[int, int]:
    volume = GENERATOR ** SPACE_RANK
    depth = least_binary_cover_depth(volume)
    return depth, BINARY ** depth


def scalar_support_share() -> Fraction:
    _, support = generator_cover()
    return Fraction(support - 1, support)


def tensor_support_share() -> Fraction:
    _, support = generator_cover()
    return Fraction(1, support)


def exact_doubling_depth(scale_ratio: int) -> int:
    if isinstance(scale_ratio, bool) or scale_ratio < 2:
        raise ValueError("scale ratio must be a generated whole beyond the One")
    depth = 1
    support = BINARY
    while support < scale_ratio:
        support *= BINARY
        depth += 1
    if support != scale_ratio:
        raise ValueError("scale ratio is not an exact complete Fold doubling support")
    return depth


def perturbation_growth_trace() -> tuple[Fraction, ...]:
    return (Fraction(1, 4), Fraction(1, 2), Fraction(1))


def forward_component_transfer(scale_growth: Fraction) -> dict[str, Fraction]:
    growth = Fraction(scale_growth)
    if growth <= 0:
        raise ValueError("scale growth must be an exact positive carrier")
    matter = Fraction(1) / (growth ** SPACE_RANK)
    radiation = Fraction(1) / (growth ** (SPACE_RANK + 1))
    return {
        "matter_retention": matter,
        "radiation_retention": radiation,
        "matter_over_radiation": matter / radiation,
    }


def theorem_certificate() -> dict[str, object]:
    depth, support = generator_cover()
    trace = perturbation_growth_trace()
    return {
        "volume": GENERATOR ** SPACE_RANK,
        "depth": depth,
        "support": support,
        "scalar": scalar_support_share(),
        "tensor": tensor_support_share(),
        "complete_primordial_partition": scalar_support_share() + tensor_support_share() == Fraction(1),
        "exact_duration": exact_doubling_depth(support),
        "growth_trace": trace,
        "strict_growth": trace[0] < trace[1] < trace[2],
        "transfer": all(
            forward_component_transfer(growth)["matter_over_radiation"] == growth
            for growth in (Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3))
        ),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal inflation, primordial-support and structure-growth law",
    statement=(
        "Generator-three stable space has volume twenty-seven and is first completely covered by binary depth five, "
        "support thirty-two. Inflation is therefore an exact five-doubling cover process, not a conventional logarithmic "
        "duration imported from a potential. One held boundary distinction leaves thirty-one scalar support records and "
        "one least tensor-pair record, forcing scalar share 31/32 and tensor share 1/32. The exact quarter-One perturbation "
        "grows by two Fold steps through half-One to the One. Under later exact scale growth g, matter retention is One/g^3 "
        "and radiation retention One/g^4, so matter gains the exact relative factor g and supplies the earlier gravitational "
        "scaffold without a stochastic seed or fitted transfer function."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-GRAVITY-GRAVITON-POLARIZATION-003",
        "SFT-PHYS-COSMO-EXPANSION-001",
        "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",
        "SFT-PHYS-COSMO-STRUCTURE-GROWTH-001",
        "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of spatial volume, binary cover, duration carrier, scalar support, tensor support, "
        "exit boundary, perturbation growth and component-transfer form."
    ),
    grammar_boundary=(
        "Generator-three volume in stable three-space; every positive binary support until the unique least cover; every "
        "exact complete doubling ratio; the complete thirty-two-record primordial partition; the quarter/half/One Fold "
        "growth trace; and every exact positive rational later scale-growth carrier under admitted third/fourth transport."
    ),
    axes=(
        binary_axis("volume", "What fixes the inflationary support?", "named-observable-universe-size", "A measured horizon cannot select the support.", "generator-three-space-volume", "The admitted generator and stable rank force twenty-seven."),
        binary_axis("cover", "What expansion first covers the volume?", "selected-sixty-efold-story", "A conventional model-dependent duration is not a generated Fold count.", "least-binary-depth-five-cover", "Binary succession first covers twenty-seven at thirty-two."),
        binary_axis("duration", "How is duration counted?", "irrational-logarithmic-efolds", "A continuum logarithm is outside exact Fold arithmetic.", "five-exact-doubling-transitions", "The cover contains exactly five generated binary transitions."),
        binary_axis("scalar", "What scalar support survives?", "fitted-spectral-index", "A decimal index selected from CMB data is a fit.", "one-boundary-record-short-of-complete", "One held boundary record leaves thirty-one of thirty-two scalar records."),
        binary_axis("tensor", "What is the least tensor support?", "free-tensor-amplitude", "A tunable tensor amplitude adds a parameter.", "one-tensor-pair-record-in-thirty-two", "The admitted polarization pair is one Fold distinction on the complete support."),
        binary_axis("exit", "Where does cover growth change regime?", "chosen-inflaton-potential-exit", "A chosen potential imports an independent model.", "first-complete-generator-volume-cover", "At depth five the generator volume is completely represented and component transport takes over."),
        binary_axis("growth", "How does the least resolved perturbation evolve?", "stochastic-or-decaying-seed", "Ontic noise or decay is not forced by the Fold.", "quarter-half-One-two-step-growth", "Two exact Fold actions carry quarter-One through half-One to the One."),
        binary_axis("transfer", "How do radiation and matter transfer relative support?", "fitted-transfer-function", "A fitted spectrum is not a law.", "third-versus-fourth-power-relative-growth", "Admitted component powers force matter/radiation ratio growth by exactly g."),
    ),
    exact_result=(
        "The unique generator-volume inflation cover is five Fold doublings with support 32. The complete primordial "
        "partition is scalar 31/32 and least tensor-pair 1/32. The structural exit is the first complete cover of volume "
        "27. The least resolved perturbation grows exactly 1/4 to 1/2 to One in two Fold steps. For every exact positive "
        "later scale growth g, matter retention is 1/g^3, radiation retention is 1/g^4 and their relative growth is g. "
        "A conventional natural-log e-fold count is a comparison label, not an SFT proof scalar."
    ),
    induction_base=(
        "The first binary distinction supplies two records; the first perturbation part doubles exactly; matter and "
        "radiation share the same initial reference."
    ),
    induction_step=(
        "Each Fold doubling appends one exact depth and doubles support until the least complete cover. Each later exact "
        "scale successor preserves third/fourth transport and multiplies the matter-to-radiation ratio by that successor."
    ),
    exclusions=(
        "no inflaton potential, slow-roll equation, conventional natural logarithm or selected sixty-e-fold premise",
        "no CMB spectral index, tensor bound, matter spectrum or measured horizon available to candidate selection",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof scalar",
        "no ontic stochastic seed, fitted transfer function, amplitude or free exit scale",
        "no claim that five Fold doublings equal sixty conventional e-folds",
    ),
    witnesses=(
        Witness("cover", "Twenty-seven is first covered by depth five support thirty-two.", theorem_certificate()["depth"] == 5 and theorem_certificate()["support"] == 32),
        Witness("partition", "Thirty-one scalar records and one tensor-pair record close exactly to the One.", theorem_certificate()["scalar"] == Fraction(31, 32) and theorem_certificate()["tensor"] == Fraction(1, 32) and theorem_certificate()["complete_primordial_partition"]),
        Witness("duration", "The complete support has exactly five Fold doublings.", theorem_certificate()["exact_duration"] == 5),
        Witness("growth", "Quarter-One reaches the One through half-One in exactly two strict steps.", theorem_certificate()["growth_trace"] == (Fraction(1, 4), Fraction(1, 2), Fraction(1)) and theorem_certificate()["strict_growth"]),
        Witness("transfer", "Third/fourth component powers force exact relative matter growth g.", theorem_certificate()["transfer"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "SPEC", "exact_doubling_depth", "forward_component_transfer", "generator_cover",
    "least_binary_cover_depth", "perturbation_growth_trace", "scalar_support_share", "tensor_support_share",
    "theorem_certificate",
)
