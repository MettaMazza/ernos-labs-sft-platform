"""Absence-valued Fold closure law for the prior spatial-flatness result."""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from sft.claim_evidence import EMPTY_ONE
from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


SPATIAL_FLATNESS_CLAIM_ID = "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001"


def closed_partition(parts: Sequence[Fraction]):
    """Return structural absence only when positive parts exhaust the One."""

    if not parts or any(not isinstance(part, Fraction) or part <= 0 for part in parts):
        raise ValueError("a cosmic partition requires exact positive parts")
    if sum(parts[1:], parts[0]) != Fraction(1, 1):
        raise ValueError("the registered component family does not close to the One")
    return EMPTY_ONE


def refine_partition(
    parts: Sequence[Fraction], index: int, first: Fraction, second: Fraction
) -> tuple[Fraction, ...]:
    """Split one positive part while retaining exact total support."""

    if not parts or index not in range(len(parts)):
        raise ValueError("partition refinement requires one retained component")
    if first <= 0 or second <= 0 or first + second != parts[index]:
        raise ValueError("refinement must be a positive exact split of one component")
    return tuple(parts[:index]) + (first, second) + tuple(parts[index + 1 :])


_base = (Fraction(1, 3), Fraction(2, 3))
_refined = refine_partition(_base, 1, Fraction(1, 6), Fraction(1, 2))

SPATIAL_FLATNESS_SPEC = StructuralPhysicsSpec(
    claim_id=SPATIAL_FLATNESS_CLAIM_ID,
    title="Complete-partition spatial flatness and absent curvature remainder",
    statement=(
        "Every generated cosmic component is an exact positive part of one common total carrier. A complete "
        "component family exhausts that One, so a separate curvature remainder is the empty One form rather "
        "than a numerical zero. Every positive repartition preserves the same closure at arbitrary finite depth."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-PHYS-COSMO-BRANCH-BOUNDARY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of total carrier, component identity, normalization, completeness, "
        "remainder role, absence representation, repartition, temporal scope, target custody, provenance and "
        "extension forms."
    ),
    grammar_boundary=(
        "All finite exact positive cosmic-component partitions of one common total carrier and every finite "
        "positive refinement that preserves the parent part."
    ),
    axes=(
        binary_axis("carrier", "What carries total cosmic support?", "independent-component-totals", "Independent totals need not form one conserved whole.", "one-common-total-carrier", "All normalized components are parts of the same One."),
        binary_axis("component", "What is one component?", "signed-or-unbound-density-number", "An unbound number is not a held part.", "exact-positive-held-part", "Each present component is one exact positive part with retained identity."),
        binary_axis("normalization", "How are parts compared?", "separate-normalizations", "Separate normalizations cannot close jointly.", "common-One-normalization", "Every component is referred to the complete common carrier exactly once."),
        binary_axis("completeness", "What does a complete census mean?", "selected-visible-components", "A selected list can leave an unregistered remainder.", "every-generated-part-exhausts-One", "Completeness requires the exact part family to assemble to the One."),
        binary_axis("remainder", "Is curvature another independent contribution?", "extra-curvature-scalar", "An extra scalar after exhaustion double-counts support.", "unassigned-part-remainder", "Curvature is the status of support left outside the complete partition."),
        binary_axis("absence", "How is no remainder represented?", "numerical-zero-curvature", "Numerical zero is not an SFT proof carrier.", "empty-One-form", "Exhaustion leaves structural absence, represented by the empty One form."),
        binary_axis("refinement", "What happens when one component is split?", "epoch-specific-fraction-table", "A table has no general preservation law.", "positive-parent-preserving-split", "Replacing one part by positive children that sum to it preserves total closure."),
        binary_axis("scope", "Does closure depend on epoch?", "single-observed-epoch", "One epoch cannot force persistence.", "all-finite-repartitions", "The refinement induction preserves closure for every finite component redistribution."),
        binary_axis("target", "May a measured curvature value select closure?", "curvature-record-readable-before-seal", "That would import the desired result.", "curvature-record-inaccessible-until-seal", "The absence result and complete grammar seal before the external record opens."),
        binary_axis("provenance", "How is the known V1 result classified?", "mislabel-as-unobserved-discovery", "The prior flatness result was already observed.", "observational-reconstruction-with-independent-runtime", "The prior record creates the obligation but cannot execute or select the survivor."),
        binary_axis("extension", "May another closure rule enter?", "extra-cosmological-closure-rule", "An added rule is a free premise.", "no-extra-rule", "Common normalization, completeness and positive refinement exhaust the registered grammar."),
    ),
    exact_result=(
        "Every finite complete exact positive cosmic-component partition closes to the One; the curvature "
        "remainder is the empty One form, and every positive parent-preserving refinement retains that result."
    ),
    induction_base="A finite complete positive component family is admitted only when its exact assembly is the One; its unassigned remainder is therefore structurally absent.",
    induction_step="Replacing any one positive part by two positive parts whose exact assembly is the parent preserves the complete sum and hence preserves the empty remainder.",
    exclusions=(
        "no measured Omega_K value or standard cosmological field equation in executable forcing",
        "no numerical zero, negative, irrational, imaginary or floating proof value",
        "no curvature remainder treated as a signed proof scalar",
        "no selected epoch, incomplete component list or extra closure rule",
        "no claim that Planck parameter inference is an SFT premise",
    ),
    witnesses=(
        Witness("base-closure", "The exact one-third/two-thirds partition leaves only structural absence.", closed_partition(_base) is EMPTY_ONE),
        Witness("refinement-closure", "A positive split of one component preserves structural absence.", closed_partition(_refined) is EMPTY_ONE),
        Witness("parent-preserved", "The refined children exactly reconstruct their parent and the total One.", _refined[1] + _refined[2] == _base[1] and sum(_refined[1:], _refined[0]) == Fraction(1, 1)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPATIAL_FLATNESS_SPEC.validate()


__all__ = (
    "SPATIAL_FLATNESS_CLAIM_ID",
    "SPATIAL_FLATNESS_SPEC",
    "closed_partition",
    "refine_partition",
)
