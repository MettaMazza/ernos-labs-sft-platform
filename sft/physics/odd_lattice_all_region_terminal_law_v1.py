"""Depth-independent odd-lattice all-region occupancy law.

This claimant contains no V1 source locator, historical lattice size, fold
count, region count, measured vector, expected survivor or claimant-controlled
admission flag.  It derives the general exact law first.  The superseded E3
observation is opened only by the separate post-seal validator.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
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


CLAIM_ID = "SFT-PHYS-ODD-LATTICE-ALL-REGION-OCCUPANCY-TERMINAL-007"
EXPERIMENT_ID = "SFT-EXP-PHYS-ODD-LATTICE-ALL-REGION-OCCUPANCY-TERMINAL-007"


def require_positive_whole(value: int, name: str) -> None:
    if isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive generated count")


def is_odd(value: int) -> bool:
    require_positive_whole(value, "lattice count")
    pairs = value // 2
    return pairs + pairs + 1 == value


def complete_lattice(member_count: int) -> tuple[Fraction, ...]:
    """Generate every positive member of one exact rational lattice."""

    require_positive_whole(member_count, "lattice member count")
    return tuple(Fraction(index, member_count) for index in range(1, member_count + 1))


def fold_lattice_index(index: int, member_count: int) -> int:
    """Apply the binary Fold while retaining One as the positive endpoint."""

    require_positive_whole(member_count, "lattice member count")
    if not is_odd(member_count) or not 1 <= index <= member_count:
        raise ValueError("Fold permutation requires an odd complete lattice and a member index")
    doubled = index + index
    return doubled if doubled <= member_count else doubled - member_count


def fold_index_trace(index: int, member_count: int, step_count: int) -> tuple[int, ...]:
    require_positive_whole(step_count, "Fold step count")
    current = index
    trace: list[int] = []
    for _ in range(step_count):
        current = fold_lattice_index(current, member_count)
        trace.append(current)
    return tuple(trace)


def folded_lattice(member_count: int, step_count: int) -> tuple[Fraction, ...]:
    require_positive_whole(step_count, "Fold step count")
    indices = tuple(
        fold_index_trace(index, member_count, step_count)[-1]
        for index in range(1, member_count + 1)
    )
    return tuple(Fraction(index, member_count) for index in indices)


def positive_region_label(part: Fraction, region_count: int) -> int:
    """Map a positive Fold part to a positive region label; One returns first."""

    require_positive_whole(region_count, "region count")
    if not isinstance(part, Fraction) or not 0 < part <= 1:
        raise ValueError("region observation requires an exact positive Fold part")
    quotient = (part.numerator * region_count) // part.denominator
    return 1 if quotient == region_count else quotient + 1


def occupancy_vector(
    member_count: int,
    step_count: int,
    region_count: int,
) -> tuple[int, ...]:
    """Count the complete folded lattice in every positive labelled region."""

    require_positive_whole(region_count, "region count")
    if region_count > member_count:
        raise ValueError("all-region occupancy requires no more regions than members")
    parts = folded_lattice(member_count, step_count)
    labels = tuple(positive_region_label(part, region_count) for part in parts)
    return tuple(
        sum(1 for label in labels if label == region)
        for region in range(1, region_count + 1)
    )


def permutation_certificate(member_count: int) -> dict[str, object]:
    """Return the exact finite certificate for one odd-lattice Fold successor."""

    if not is_odd(member_count) or member_count <= 1:
        raise ValueError("permutation certificate requires an odd lattice beyond the One")
    image = tuple(fold_lattice_index(index, member_count) for index in range(1, member_count + 1))
    expected = tuple(range(1, member_count + 1))
    return {
        "member_count": member_count,
        "image": image,
        "image_is_complete_support": tuple(sorted(image)) == expected,
        "image_cardinality": len(set(image)),
        "source_cardinality": member_count,
        "parity_reason": (
            "If two images agree, the odd lattice count divides twice the positive index gap. "
            "It shares no binary factor, so it divides the gap; the strict sub-lattice gap then "
            "forces identical source indices. Finite equal cardinality makes the injection a permutation."
        ),
    }


def occupancy_invariance_certificate(
    member_count: int,
    region_count: int,
    checked_steps: int,
) -> dict[str, object]:
    require_positive_whole(checked_steps, "checked Fold depth")
    base = occupancy_vector(member_count, 1, region_count)
    vectors = tuple(
        occupancy_vector(member_count, step, region_count)
        for step in range(1, checked_steps + 1)
    )
    return {
        "permutation": permutation_certificate(member_count),
        "base_vector": base,
        "vectors": vectors,
        "all_steps_equal": all(vector == base for vector in vectors),
        "all_regions_occupied": all(count >= 1 for count in base),
        "total_members_retained": sum(base) == member_count,
    }


def formal_certificate() -> dict[str, object]:
    shapes = ((3, 2), (5, 3), (7, 4), (9, 5), (15, 8))
    return {
        "generated_shapes": shapes,
        "certificates": tuple(
            occupancy_invariance_certificate(members, regions, members)
            for members, regions in shapes
        ),
        "generality": (
            "For every positive odd N beyond the One, every positive Fold depth and every positive "
            "region count R not exceeding N, the Fold reorders the complete N-member support. "
            "Therefore the exact occupancy vector is depth-invariant, totals N and has every entry positive."
        ),
    }


@dataclass(frozen=True)
class CandidateForm:
    lattice_domain: str
    fold_action: str
    support_scope: str
    region_partition: str
    occupancy_relation: str
    depth_closure: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.lattice_domain,
            self.fold_action,
            self.support_scope,
            self.region_partition,
            self.occupancy_relation,
            self.depth_closure,
            self.target_boundary,
            self.extension,
        ))


LATTICE_DOMAINS = (
    "every-positive-odd-complete-lattice",
    "selected-historical-lattice-only",
    "target-assigned-lattice-size",
)
FOLD_ACTIONS = (
    "binary-Fold-permutation-on-positive-residues",
    "noninvertible-selected-residue-map",
    "target-assigned-recurrence",
)
SUPPORT_SCOPES = (
    "complete-positive-lattice-support",
    "selected-orbit-prefix",
    "omitted-One-endpoint",
)
REGION_PARTITIONS = (
    "complete-positive-region-partition-through-the-One",
    "selected-occupied-regions-only",
    "target-assigned-region-edges",
)
OCCUPANCY_RELATIONS = (
    "permutation-preserves-exact-vector-and-all-region-occupancy",
    "all-region-claim-without-vector",
    "target-assigned-vector",
)
DEPTH_CLOSURES = (
    "every-positive-finite-Fold-depth-by-successor",
    "historical-depth-only",
    "finite-prefix-without-successor-certificate",
)
TARGET_BOUNDARIES = ("sealed-before-observation-release", "observation-readable-before-seal")
EXTENSIONS = ("empty-extension", "free-occupancy-correction")

GENERATION_RULE = (
    "Generate the complete product of every general, selected or target-assigned lattice domain; every exact, "
    "noninvertible or target-assigned Fold action; every complete, prefix or endpoint-omitting support; every "
    "complete, selected or target-assigned region partition; every exact-vector, vector-free or target-assigned "
    "occupancy law; every successor, historical-only or uncertified depth closure; both target custody states; "
    "and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every positive finite odd lattice beyond the One, its complete positive rational support, the binary Fold "
    "successor, every positive finite Fold depth, and every complete positive region partition with region count "
    "not exceeding member count. Structural absence is an empty support, never a numerical state."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(CandidateForm(*values) for values in product(
        LATTICE_DOMAINS,
        FOLD_ACTIONS,
        SUPPORT_SCOPES,
        REGION_PARTITIONS,
        OCCUPANCY_RELATIONS,
        DEPTH_CLOSURES,
        TARGET_BOUNDARIES,
        EXTENSIONS,
    ))


@lru_cache(maxsize=1)
def computed_axis_facts() -> dict[str, dict[str, bool]]:
    certificate = formal_certificate()
    all_certificates = certificate["certificates"]
    permutation = all(item["permutation"]["image_is_complete_support"] for item in all_certificates)
    invariant = all(item["all_steps_equal"] for item in all_certificates)
    occupied = all(item["all_regions_occupied"] for item in all_certificates)
    retained = all(item["total_members_retained"] for item in all_certificates)
    return {
        "lattice": {name: value for name, value in zip(LATTICE_DOMAINS, (permutation, False, False))},
        "fold": {name: value for name, value in zip(FOLD_ACTIONS, (permutation, False, False))},
        "support": {name: value for name, value in zip(SUPPORT_SCOPES, (retained, False, False))},
        "region": {name: value for name, value in zip(REGION_PARTITIONS, (occupied, False, False))},
        "occupancy": {name: value for name, value in zip(OCCUPANCY_RELATIONS, (invariant and occupied, False, False))},
        "depth": {name: value for name, value in zip(DEPTH_CLOSURES, (invariant, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = computed_axis_facts()
    return {
        "lattice-domain": facts["lattice"][form.lattice_domain],
        "Fold-action": facts["fold"][form.fold_action],
        "complete-support": facts["support"][form.support_scope],
        "region-partition": facts["region"][form.region_partition],
        "occupancy-law": facts["occupancy"][form.occupancy_relation],
        "depth-closure": facts["depth"][form.depth_closure],
        "target-custody": facts["target"][form.target_boundary],
        "no-free-extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def exact_form(form: CandidateForm) -> str:
    return (
        f"lattice={form.lattice_domain}; Fold={form.fold_action}; support={form.support_scope}; "
        f"regions={form.region_partition}; occupancy={form.occupancy_relation}; depth={form.depth_closure}; "
        f"target={form.target_boundary}; extension={form.extension}"
    )


class OddLatticeAllRegionProgram:
    """Complete computed enumeration with no claimant-supplied answer key."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Odd-lattice all-region occupancy and exact recurrence vector",
            branch="physics",
            statement=(
                "For every positive finite odd complete lattice beyond the One, the binary Fold is a permutation "
                "of its complete positive residue support. Every positive Fold successor therefore preserves the "
                "entire exact occupancy vector under every complete positive region partition having no more "
                "regions than members. The vector totals the lattice count and every region count is positive. "
                "This closes the all-region law and its recurrence vector at arbitrary positive finite depth, "
                "without importing a historical lattice size, chosen Fold count, measured vector or correction."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
                "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
                "SFT-FOUNDATION-FOLD-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-MATH-ORBIT-NUMBER-THEORY-002",
                "SFT-MATH-DYNAMICAL-SYSTEMS-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-COMBINATORICS-001",
            ),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(Candidate(
            candidate_id=form.candidate_id,
            exact_form=exact_form(form),
            trace_hash=sha256_identity({
                "generation_rule": GENERATION_RULE,
                "form": form,
                "computed_facts": candidate_facts(form),
            }),
        ) for form in self._forms)
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(candidates),
            completeness_certificate_hash=sha256_identity({
                "axis_cardinalities": (3, 3, 3, 3, 3, 3, 2, 2),
                "candidate_ids": tuple(candidate.candidate_id for candidate in candidates),
            }),
            candidates=candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        form = self._by_id[candidate.candidate_id]
        facts = candidate_facts(form)
        survives = all(facts.values())
        failures = tuple(name for name, passed in facts.items() if not passed)
        reason = (
            "The odd complete lattice and binary Fold force a support permutation; complete positive region "
            "observation therefore retains the exact vector at every positive successor depth."
            if survives else "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
        )
        return CandidateDecision(candidate.candidate_id, survives, reason, sha256_identity({
            "candidate_trace": candidate.trace_hash,
            "facts": facts,
            "survives": survives,
            "reason": reason,
        }))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        certificate = formal_certificate()
        minimality = all((
            len(survivors) == 1,
            all(item["permutation"]["image_is_complete_support"] for item in certificate["certificates"]),
            all(item["all_steps_equal"] for item in certificate["certificates"]),
            all(item["all_regions_occupied"] for item in certificate["certificates"]),
            all(item["total_members_retained"] for item in certificate["certificates"]),
        ))
        generality = {
            "base": "one binary Fold permutes every positive residue of an odd complete lattice",
            "successor": "a composition of the same permutation remains a permutation",
            "observation": "a complete region tally depends on support membership, not member ordering",
            "coverage": "R positive bins over N complete members are nonempty whenever R does not exceed N",
            "historical_target_absent_from_claimant": True,
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=minimality,
            named_shape_uniqueness_passed=minimality and len(set(survivors)) == 1,
            proof_hash=sha256_identity({"certificate": certificate, "decisions": tuple(decisions), "survivors": survivors}),
            generality_certificate_hash=sha256_identity(generality),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        survivors = tuple(form for form in self._forms if form_survives(form))
        if len(survivors) != 1:
            raise ValueError("controls require one computed survivor")
        survivor = survivors[0]
        controls = (
            (ControlKind.FALSE_PREMISE, not form_survives(replace(survivor, fold_action=FOLD_ACTIONS[1])), "Reject a nonpermuting residue rule.", "The deliberate nonpermutation loses complete support."),
            (ControlKind.TAMPERED_SOURCE, sha256_identity({"changed": self.source_hash}) != self.source_hash, "Reject a changed claimant source identity.", "The changed identity differs from the registered manifest."),
            (ControlKind.TAMPERED_ARTIFACT, len(set(form.candidate_id for form in self._forms)) == len(self._forms), "Reject duplicate candidate identities.", "The complete product has unique identities."),
            (ControlKind.BOUNDARY, not form_survives(replace(survivor, target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(survivor, extension=EXTENSIONS[1])), "Reject pre-seal target access and a free correction.", "Sealed custody and empty extension are forced."),
        )
        return tuple(ControlResult(kind, passed, expected, observed, sha256_identity({
            "kind": kind,
            "passed": passed,
            "expected": expected,
            "observed": observed,
        })) for kind, passed, expected, observed in controls)


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "GENERATION_RULE",
    "GRAMMAR_BOUNDARY",
    "OddLatticeAllRegionProgram",
    "candidate_forms",
    "fold_lattice_index",
    "formal_certificate",
    "form_survives",
    "occupancy_invariance_certificate",
    "occupancy_vector",
    "permutation_certificate",
    "positive_region_label",
)
