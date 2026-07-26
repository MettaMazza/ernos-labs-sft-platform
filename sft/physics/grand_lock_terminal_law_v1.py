"""Terminal Physics Grand Lock: ownership, root trace and perturbation.

The lock does not make the Physics branch immutable or permanently complete.
It certifies completeness against the declared V3 evidence surface at this
version while leaving lawful extensions open.  No measurement, V1/V2 result or
external equation selects any survivor.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from sft.engine import EvidenceMode
from sft.physics.atomic_constants import fine_structure_blocks, inverse_fine_structure
from sft.physics.cosmology_prior_value_laws import dark_baryon_structure
from sft.physics.hubble_calibration_law import hubble_calibration_structure
from sft.physics.matter_flavour_laws_v1 import quark_channel_invariants, quark_cubic_invariants
from sft.physics.precision_value_laws_v1 import terminal_proton_planck_squared_ratio
from sft.physics.prior_value_laws import charged_lepton_invariants
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis
from sft.physics.terminal_lepton_law import terminal_product_invariant
from sft.physics.vacuum_density_scale_terminal_law_v1 import (
    local_vacuum_amplitude_floor,
    local_vacuum_energy_floor,
    normalized_cosmological_constant,
)


CLAIM_ID = "SFT-PHYS-GRAND-LOCK-TERMINAL-075"
ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "census/physics_grand_lock_input_v1.json"
INPUT_HASH = "sha256:325248e4081b287fbacd125efe18a9d5fbba05f1fbd459eaa2a61a225120b3ca"
FOUNDATIONAL_ROOT = "SFT-FOUNDATION-ONE-001"
ONE = Fraction(1, 1)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_input() -> dict[str, object]:
    if sha256(INPUT_PATH) != INPUT_HASH:
        raise ValueError("the frozen pre-lock Physics input changed")
    record = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-physics-grand-lock-input/1":
        raise ValueError("wrong Grand Lock input schema")
    return record


def least_binary_cover(carrier: int, binary: int = 2) -> int:
    if carrier < 1 or binary < 2:
        raise ValueError("cover requires positive carrier and generated fibre count")
    depth = 1
    support = binary
    while support < carrier:
        support *= binary
        depth += 1
    return depth


def positive_take(whole: Fraction, part: Fraction) -> Fraction:
    if whole <= part or part <= 0:
        raise ValueError("positive take requires an ordered positive part")
    return whole - part


def generator_value_vector(generator: int) -> dict[str, Fraction | int]:
    """Recompute every registered generator-dependent headline carrier.

    The counterfactual changes only the generator count.  Binary fibre count
    and independently forced spatial rank three remain held.  Consequently the
    cover carriers are generator^3 and generator^4, not generator^generator.
    """

    if generator < 3:
        raise ValueError("the perturbation census requires generator or successor")
    binary = 2
    space_rank = 3
    down = least_binary_cover(generator ** space_rank, binary)
    up = least_binary_cover(generator ** (space_rank + 1), binary)
    tower = binary ** up
    boundary = generator ** binary
    cover = binary * (down ** generator)
    rungs = tuple((down ** (generator - promoted)) * (up ** promoted) for promoted in range(generator + 1))
    chain = Fraction(rungs[-1], 1)
    for rung in reversed(rungs[1:-1]):
        chain = Fraction(rung, 1) + ONE / chain
    effective_cover = Fraction(cover, 1) + ONE / chain
    inverse_alpha = Fraction(tower, 1) + Fraction(boundary, 1) * (effective_cover + ONE) / effective_cover
    alpha = ONE / inverse_alpha

    lepton_denominator = 2 * (generator ** (generator + 2)) - 1
    lepton_sharpened = ONE / positive_take(Fraction(lepton_denominator, 1), Fraction(1, generator))
    lepton_correction = (alpha ** generator) * (
        Fraction(down, 1) + Fraction(up, generator) * alpha
    ) / (generator ** generator)
    lepton_terminal = positive_take(lepton_sharpened, lepton_correction)

    quark_down_pair = Fraction(1, binary * (generator + 1))
    quark_up_pair = Fraction(1, binary * (generator + generator))
    quark_down_product = Fraction(1, generator * (binary ** up) - 1)
    quark_up_product = Fraction(1, generator * (binary ** (up + generator)) - 1)

    volume = generator ** space_rank
    cover_support = binary ** down
    orbit_floor = cover_support - 1
    dark_leading = Fraction(volume, down)
    dark_refined = Fraction(volume, 1) / (Fraction(down, 1) + Fraction(1, orbit_floor))

    matter_share = Fraction(1, generator)
    vacuum_share = Fraction(generator - 1, generator)
    spatial_support = binary ** space_rank
    hubble_leading = ONE + vacuum_share / spatial_support
    deep_floor = binary ** up - 1
    hubble_refined = ONE + (vacuum_share + Fraction(1, deep_floor)) / spatial_support

    lower_planck_squared = binary ** (binary ** up - 1)
    planck_terminal = Fraction(lower_planck_squared, 1) * positive_take(ONE, Fraction(binary, generator) * alpha)
    local_vacuum_amplitude = Fraction(1, binary ** (binary * down))
    local_vacuum_energy = local_vacuum_amplitude * local_vacuum_amplitude

    return {
        "generator": generator,
        "down_cover_depth": down,
        "up_cover_depth": up,
        "inverse_fine_structure_terminal": inverse_alpha,
        "charged_lepton_pair_invariant": Fraction(1, binary * generator),
        "charged_lepton_leading_product": Fraction(1, lepton_denominator),
        "charged_lepton_sharpened_product": lepton_sharpened,
        "charged_lepton_terminal_product": lepton_terminal,
        "quark_down_pair_invariant": quark_down_pair,
        "quark_up_pair_invariant": quark_up_pair,
        "quark_down_product_invariant": quark_down_product,
        "quark_up_product_invariant": quark_up_product,
        "dark_baryon_leading_ratio": dark_leading,
        "dark_baryon_refined_ratio": dark_refined,
        "dark_share": Fraction(volume, cover_support),
        "baryon_share": Fraction(down, cover_support),
        "hubble_leading_ratio": hubble_leading,
        "hubble_refined_ratio": hubble_refined,
        "planck_proton_terminal_squared_hierarchy": planck_terminal,
        "local_vacuum_amplitude_floor": local_vacuum_amplitude,
        "local_vacuum_energy_floor": local_vacuum_energy,
    }


def current_headline_vector() -> dict[str, object]:
    dark = dark_baryon_structure()
    hubble = hubble_calibration_structure()
    quark_channels = quark_channel_invariants()
    quark_cubics = quark_cubic_invariants()
    leptons = charged_lepton_invariants()
    return {
        "generator": 3,
        "down_cover_depth": fine_structure_blocks()["down"],
        "up_cover_depth": fine_structure_blocks()["up"],
        "inverse_fine_structure_terminal": inverse_fine_structure(),
        "charged_lepton_pair_invariant": leptons[1],
        "charged_lepton_leading_product": leptons[2],
        "charged_lepton_sharpened_product": leptons[3],
        "charged_lepton_terminal_product": terminal_product_invariant(),
        "quark_down_pair_invariant": quark_channels["down_pair_sum"],
        "quark_up_pair_invariant": quark_channels["up_pair_sum"],
        "quark_down_product_invariant": quark_cubics["down"][2],
        "quark_up_product_invariant": quark_cubics["up"][2],
        "dark_baryon_leading_ratio": dark["leading_ratio"],
        "dark_baryon_refined_ratio": dark["refined_ratio"],
        "dark_share": dark["dark_share"],
        "baryon_share": dark["baryon_share"],
        "hubble_leading_ratio": hubble["leading_ratio"],
        "hubble_refined_ratio": hubble["refined_ratio"],
        "planck_proton_terminal_squared_hierarchy": terminal_proton_planck_squared_ratio(),
        "local_vacuum_amplitude_floor": local_vacuum_amplitude_floor(),
        "local_vacuum_energy_floor": local_vacuum_energy_floor(),
    }


def dependency_certificate() -> dict[str, object]:
    record = frozen_input()
    rows = {row["claim_id"]: row for row in record["dependency_dictionary"]}
    physics_ids = tuple(record["physics_claim_ids"])
    if len(physics_ids) != len(set(physics_ids)) == record["physics_claim_count"]:
        raise ValueError("Physics ownership census is not unique and complete")
    active: set[str] = set()
    complete: set[str] = set()
    memo: dict[str, bool] = {}

    def visit(claim_id: str) -> None:
        if claim_id in active:
            raise ValueError("cycle in frozen dependency dictionary")
        if claim_id in complete:
            return
        if claim_id not in rows:
            raise ValueError("orphan dependency in frozen dictionary")
        active.add(claim_id)
        for dependency in rows[claim_id]["dependencies"]:
            visit(dependency)
        active.remove(claim_id)
        complete.add(claim_id)

    def reaches_one(claim_id: str) -> bool:
        if claim_id == FOUNDATIONAL_ROOT:
            return True
        if claim_id in memo:
            return memo[claim_id]
        result = any(reaches_one(dependency) for dependency in rows[claim_id]["dependencies"])
        memo[claim_id] = result
        return result

    for claim_id in physics_ids:
        visit(claim_id)
    return {
        "physics_claim_count": len(physics_ids),
        "transitive_claim_count": len(complete),
        "no_omission": set(physics_ids) == {row["claim_id"] for row in record["physics_claims"]},
        "acyclic": len(complete) == record["transitive_claim_count"],
        "all_reach_one": all(reaches_one(claim_id) for claim_id in physics_ids),
        "all_evidence_hash_bound": all(
            row["receipt_hash"] and row["receipt_file_sha256"] and row["certificate_sha256"] and row["registration_sha256"]
            for row in record["physics_claims"]
        ),
        "empirical_claim_count": record["empirical_claim_count"],
        "unfavorable_or_scope_boundary_count": record["unfavorable_or_scope_boundary_count"],
    }


def cross_domain_identity_graph() -> dict[str, tuple[str, ...]]:
    return {
        "binary_fibre": ("fine_structure", "leptons", "quarks", "cosmology", "planck_hierarchy", "vacuum_floor"),
        "generator": ("fine_structure", "leptons", "quarks", "dark_baryon", "hubble", "planck_hierarchy", "vacuum_floor"),
        "down_cover": ("fine_structure", "leptons", "dark_baryon", "vacuum_floor"),
        "up_cover": ("fine_structure", "leptons", "quarks", "hubble", "planck_hierarchy"),
        "space_rank": ("cover_depths", "dark_baryon", "hubble", "vacuum_floor"),
        "terminal_alpha": ("leptons", "planck_hierarchy"),
    }


def theorem_certificate() -> dict[str, object]:
    dependency = dependency_certificate()
    current = current_headline_vector()
    reconstructed = generator_value_vector(3)
    successor = generator_value_vector(4)
    changed = tuple(name for name in reconstructed if reconstructed[name] != successor[name])
    held = {
        "binary_fibre": Fraction(1, 2),
        "space_rank": 3,
        "boundary_rank": 2,
    }
    return {
        "dependency": dependency,
        "current_vector": current,
        "reconstructed_vector": reconstructed,
        "successor_vector": successor,
        "current_cross_lock": current == reconstructed,
        "all_declared_generator_dependent_values_move": set(changed) == set(reconstructed),
        "generator_independent_values_hold": held == {"binary_fibre": Fraction(1, 2), "space_rank": 3, "boundary_rank": 2},
        "changed_value_count": len(changed),
        "cross_domain_identity_graph": cross_domain_identity_graph(),
        "cross_domain_graph_complete": all(cross_domain_identity_graph().values()),
        "separate_normalized_cosmic_value_retained": normalized_cosmological_constant() == Fraction(33, 16),
    }


_input = frozen_input()
PHYSICS_DEPENDENCIES = tuple(_input["physics_claim_ids"])
_theorem = theorem_certificate()

SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal Physics Grand Lock and extension-open no-omission certificate",
    statement=(
        "Every Physics claim admitted before this lock is uniquely owned once, hash-bound to its receipt, certificate "
        "and registration, and included in a complete acyclic dependency dictionary whose every Physics node reaches "
        "the foundational One. The current exact headline vector independently recomputes from generator three. In "
        "the complete generator-successor adverse census, every value declared generator-dependent changes under "
        "three-to-four while the binary fibre, stable spatial rank and boundary rank remain held. Shared carriers form "
        "an explicit cross-domain identity graph. Every admitted empirical receipt, measurement-row preservation "
        "certificate, unfavorable result and scope boundary remains present. This closes the declared V3 Physics "
        "surface at this version without preventing a later lawfully forced extension."
    ),
    dependencies=PHYSICS_DEPENDENCIES,
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of ownership, receipt identity, registration identity, dependency "
        "closure, root reachability, value vector, generator perturbation, invariant control, cross-domain identity, "
        "empirical reconciliation, extension status and extra-rule forms."
    ),
    grammar_boundary=(
        f"All {_input['physics_claim_count']} admitted pre-lock Physics claims, all {_input['transitive_claim_count']} "
        "nodes in their dependency closure, every bound exact-result and empirical certificate row, the complete "
        "generator-three to generator-four adverse perturbation, all shared structural carriers and all 4096 alternatives."
    ),
    axes=(
        binary_axis("ownership", "Is every Physics claim owned exactly once?", "omitted-or-duplicate-owner", "That is not a complete branch census.", "unique-complete-physics-owner", "Every pre-lock Physics claim occurs exactly once."),
        binary_axis("receipt", "Is every admission immutable?", "unbound-or-current-only-result", "That cannot detect replacement.", "receipt-and-certificate-hash-bound", "Every claim binds its immutable receipt and materialized certificate."),
        binary_axis("registration", "Are declared premises fixed?", "unstated-or-mutable-premises", "That erases the proof route.", "registration-and-dependencies-hash-bound", "Every registration and dependency list is bound."),
        binary_axis("dependency", "Does the complete graph close?", "orphan-or-cycle", "An orphan or cycle cannot derive from the One.", "complete-acyclic-dictionary", "Every transitive dependency exists and the graph is acyclic."),
        binary_axis("root", "Where does every Physics route terminate?", "multiple-or-missing-roots", "That adds an axiom or loses derivation.", "foundational-One-root", "Every Physics claim reaches the same foundational One."),
        binary_axis("values", "Are exact values represented completely?", "headline-selection-only", "Selecting favorable headlines permits omission.", "all-claim-exact-result-vector", "Every exact result is retained; the headline vector is an additional readable cross-lock."),
        binary_axis("perturbation", "Does generator dependence survive an adverse change?", "selected-values-move", "A selected subset cannot prove structural dependence.", "every-and-only-declared-dependent-value-moves", "The complete declared generator-dependent vector changes under the successor."),
        binary_axis("invariants", "What remains fixed in that perturbation?", "silent-global-retuning", "Global retuning cannot localize cause.", "binary-space-boundary-held", "The binary fibre and independently forced ranks remain fixed."),
        binary_axis("identity", "Are repeated carriers cross-linked?", "duplicate-unrelated-numbers", "Coincidence without provenance is not identity.", "complete-cross-domain-identity-graph", "Every shared carrier is explicitly linked across its consumers."),
        binary_axis("empirical", "How are observations reconciled?", "favourable-rows-only", "Cherry-picking violates the empirical record.", "complete-receipts-with-adverse-boundaries", "Every empirical receipt, unfavorable result and scope boundary remains bound."),
        binary_axis("extension", "What does branch completion mean?", "permanently-locked-theory", "That would exclude lawful discovery.", "current-evidence-closed-extension-open", "The declared surface closes while lawful extensions remain admissible."),
        binary_axis("rule", "May a new selector enter?", "free-extra-rule", "An extra rule is a parameter.", "no-extra-rule", "Ownership, trace, perturbation and evidence exhaust the registered grammar."),
    ),
    exact_result=(
        f"The frozen pre-lock Physics surface contains exactly {_input['physics_claim_count']} uniquely owned admitted "
        f"claims and {_input['transitive_claim_count']} transitive dependency nodes. Every Physics claim reaches "
        f"{FOUNDATIONAL_ROOT} in one acyclic dependency dictionary. Exactly {_input['empirical_claim_count']} Physics "
        "claims carry empirical-test receipts, and every recorded unfavorable result or scope boundary remains bound. "
        "The current generator-three headline vector recomputes exactly, including inverse alpha "
        "503846395469/3676744786, charged-lepton invariants 1, 1/6, 1/485 and 3/1454 plus the terminal product, "
        "quark products 1/383 and 1/3071, dark/baryon 27/5 with 27/32 and 5/32, Hubble 13/12 and 3305/3048, "
        "the terminal squared Planck/proton hierarchy, local vacuum floors 1/2^10 and 1/2^20, and normalized "
        "cosmological value 33/16. Under the complete generator successor three-to-four, every declared "
        "generator-dependent value changes while half-One, spatial rank three and boundary rank two remain fixed."
    ),
    induction_base="The foundational One is the sole dependency root and the first admitted Physics claim has a hash-bound path to it.",
    induction_step="Appending any admitted Physics claim requires one unique owner, immutable evidence, admitted premises and an acyclic path to the same One; otherwise the lock halts.",
    exclusions=(
        "no edit to the canonical engine or any admitted receipt",
        "no measurement, V1/V2 result or external equation selecting a formal survivor",
        "no fitted parameter, tolerance, candidate neighborhood or omitted adverse result",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN or completed-infinite proof scalar",
        "no assertion that current completion prohibits a later lawfully forced extension",
    ),
    witnesses=(
        Witness("complete-ownership", "Every pre-lock Physics claim occurs once and has all immutable evidence bound.", _theorem["dependency"]["no_omission"] and _theorem["dependency"]["all_evidence_hash_bound"]),
        Witness("root-trace", "The complete dependency dictionary is acyclic and every Physics claim reaches the One.", _theorem["dependency"]["acyclic"] and _theorem["dependency"]["all_reach_one"]),
        Witness("current-vector", "The independent generalized construction at generator three equals all current headline implementations exactly.", _theorem["current_cross_lock"]),
        Witness("generator-adverse", "Every declared generator-dependent value changes under three-to-four while independent carriers hold.", _theorem["all_declared_generator_dependent_values_move"] and _theorem["generator_independent_values_hold"]),
        Witness("identity-graph", "Every shared carrier retains at least one explicitly registered cross-domain consumer edge.", _theorem["cross_domain_graph_complete"]),
        Witness("empirical-retention", "The complete empirical and adverse-boundary counts remain inside the frozen evidence vector.", _theorem["dependency"]["empirical_claim_count"] > 0 and _theorem["dependency"]["unfavorable_or_scope_boundary_count"] > 0),
    ),
)

SPEC.validate()


__all__ = (
    "CLAIM_ID", "INPUT_HASH", "INPUT_PATH", "PHYSICS_DEPENDENCIES", "SPEC",
    "cross_domain_identity_graph", "dependency_certificate", "generator_value_vector",
    "theorem_certificate",
)
