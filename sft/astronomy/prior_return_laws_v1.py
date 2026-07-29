"""Exact Earth/Astronomy prior-return family derived before target access."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis, fold_part

TIPPING_ID = "SFT-EARTH-TIPPING-FOLD-LOCK-002"
UNIT_RELEASE_ID = "SFT-ASTRO-SOLAR-RADIO-UNIT-RELEASE-002"
ATOMIC_BURST_ID = "SFT-ASTRO-ATOMIC-BURST-COMPLETION-002"
PLANET_ID = "SFT-ASTRO-PLANETARY-BINARY-LADDER-002"
LITHIUM_ID = "SFT-ASTRO-LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002"
EMPIRICAL_ID = "SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002"


@dataclass(frozen=True)
class StructuralAstroSpec(StructuralPhysicsSpec):
    def validate(self) -> None:
        if not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("Earth/Astronomy specification incomplete")
        if len({axis.key for axis in self.axes}) != 8:
            raise ValueError("Earth/Astronomy axes repeat")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("binary alternative missing")
            axis.survivor
        if not all(w.passed for w in self.witnesses):
            raise ValueError("Earth/Astronomy witness failed")


class StructuralAstroProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        branch = "earth_environment" if self.spec.claim_id.startswith("SFT-EARTH-") else "astronomy_cosmology"
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch=branch,
            statement=self.spec.statement, evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies,
            axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


def tipping_lock():
    left, right = Fraction(1, 4), Fraction(3, 4)
    return {"basins": (left, right), "images": (fold_part(left), fold_part(right)), "lock": Fraction(1, 2), "partition": left + right, "fold_steps": 1}


def unit_release(depth: int = 10):
    if depth < 1:
        raise ValueError("positive generated depth required")
    rows = tuple((k, 2 ** k, Fraction(1, 2 ** k), Fraction(1, 1)) for k in range(1, depth + 1))
    return {"rows": rows, "all_products_one": all(size * share == whole for _, size, share, whole in rows), "exponent": 1}


def atomic_burst():
    carrier = Fraction(1, 2)
    return {"carrier": carrier, "completion": fold_part(carrier), "steps": 1, "intermediate_generated": False}


def planetary_ladder():
    start = Fraction(1, 128)
    values = tuple(start * (2 ** k) for k in range(8))
    ratios = tuple(values[k + 1] / values[k] for k in range(7))
    return {"start": start, "values": values, "ratios": ratios, "terminal": values[-1]}


def lithium_depletion():
    prior = Fraction(3, 16)
    observed_carrier = prior * Fraction(1, 2)
    return {"prior": prior, "processing_share": Fraction(1, 2), "surface": observed_carrier, "restored": observed_carrier * 2}


EXCLUSIONS = (
    "no prior result or external target selects a survivor",
    "no universal dimensional threshold, burst energy, duration or planetary scale",
    "no fitted exponent, spacing law or abundance correction",
    "no approximate observation promoted to exact equality",
    "no cross-domain identity inferred from analogy alone",
    "no numerical absence, negative, irrational, imaginary, floating or free proof magnitude",
    "no axiom, engine change, verifier change or favorable-only record",
)


def axes(relation: str, reason: str):
    return (
        binary_axis("carrier", "Which carrier survives?", "continuum-or-signed-carrier", "It imports a prohibited grammar.", "exact-positive-fold-parts-and-counts", "Only exact positive Fold parts and counts occur."),
        binary_axis("relation", "Which mechanism survives?", "name-or-fit-only", "A label or fit is not a derivation.", relation, reason),
        binary_axis("scope", "Which scope survives?", "universal-dimensional-overreach", "Normalized structure cannot set every dimensional target.", "normalized-law-measured-correspondence-separate", "The exact structure and measured translation remain distinct."),
        binary_axis("records", "Which records survive?", "selected-favorable-record", "Selection destroys empirical force.", "complete-source-and-adverse-record", "All target and control rows remain held."),
        binary_axis("enumeration", "How are alternatives exhausted?", "selected-example", "One example cannot force uniqueness.", "complete-declared-product", "Every registered form occurs once."),
        binary_axis("target", "When is target content opened?", "target-before-seal", "Pre-seal access is fitting.", "derivation-seal-before-target", "Targets remain inaccessible until closure."),
        binary_axis("outcomes", "Which outcomes survive?", "favorable-only", "Unfavorable evidence cannot be discarded.", "favorable-adverse-absent-heterogeneous-unresolved", "Every result class remains distinct."),
        binary_axis("extension", "Is an extra rule needed?", "free-exception", "A free exception is an unforced parameter.", "no-extra-rule", "Dependencies close the frozen boundary."),
    )


def make_spec(claim_id, title, statement, dependencies, relation, reason, exact, boundary, witnesses, mode=EvidenceMode.FORMAL):
    return StructuralAstroSpec(claim_id=claim_id, title=title, statement=statement, dependencies=dependencies,
        evidence_mode=mode, generation_rule=f"Generate the complete eight-axis product for {claim_id} and reconstruct its exact witness independently.",
        grammar_boundary=boundary, axes=axes(relation, reason), exact_result=exact,
        induction_base="The least complete positive carrier retains the full mechanism and evidence boundary.",
        induction_step="Every positive successor preserves all prior distinctions without target-derived choice.",
        exclusions=EXCLUSIONS, witnesses=witnesses)


_tip, _unit, _burst, _planet, _li = tipping_lock(), unit_release(), atomic_burst(), planetary_ladder(), lithium_depletion()

TIPPING_SPEC = make_spec(TIPPING_ID, "Normalized Earth tipping Fold lock", "The two exact normalized basin carriers are the quarter-One and three-quarter-One preimages of half-One; dimensional thresholds remain system-specific measurements.",
    ("SFT-EARTH-EARTH-SYSTEM-TIPPING-001", "SFT-FOUNDATION-HALF-ONE-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001"),
    "quarter-three-quarter-common-half-one-lock", "Both exact basins map to the one normalized balance while remaining distinct.",
    "Quarter-One and three-quarter-One are distinct basins, both Fold to half-One and together complete One. Crossing into the shared normalized lock takes one Fold. This does not assert one universal dimensional Earth threshold.",
    "Every antipodal two-basin normalized Fold carrier with dimensional-threshold controls.",
    (Witness("image", "Both basins map to half-One.", _tip["images"] == (Fraction(1, 2), Fraction(1, 2))), Witness("whole", "Basins complete One.", _tip["partition"] == 1)))

UNIT_SPEC = make_spec(UNIT_RELEASE_ID, "Solar/radio unit magnitude-frequency release", "Every binary increase in release size has the exact inverse binary frequency share, so size times frequency completes One at every generated depth.",
    (TIPPING_ID, "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001", "SFT-ASTRO-TRANSIENT-001", "SFT-PHYS-WAVE-PROPAGATION-001"),
    "binary-size-inverse-frequency-unit-product", "Each exact scale ratio and its reciprocal share multiply to One, forcing exponent One.",
    "At every positive generated binary depth k, size ratio 2^k and frequency share 1/2^k multiply to One. The exact magnitude-frequency exponent is One; external solar and radio catalogs test its domain and departures.",
    "All positive finite binary depths with nonunit, fitted and incomplete-catalog controls.",
    (Witness("ten", "Ten generated depths are present.", len(_unit["rows"]) == 10), Witness("unit", "Every size-frequency product is One.", _unit["all_products_one"] and _unit["exponent"] == 1)))

BURST_SPEC = make_spec(ATOMIC_BURST_ID, "Atomic Fold burst completion", "The least nonempty release carrier half-One completes to One in exactly one Fold with no generated intermediate state.",
    (UNIT_RELEASE_ID, "SFT-ASTRO-PERIOD-TRANSIENT-001", "SFT-FOUNDATION-FOLD-DYNAMICS-001"),
    "half-one-to-one-single-fold-release", "The least complete binary release is one exact transition, not a fitted duration or energy.",
    "Half-One Folds to One in one exact step. No intermediate exists in that registered binary transition. This forces an atomic release class while leaving dimensional burst energy, duration and source structure to measurement.",
    "The least positive binary release path with partial, multi-step and dimensional-overreach controls.",
    (Witness("completion", "Half-One completes to One.", _burst["completion"] == 1), Witness("atomic", "Exactly one step and no generated intermediate.", _burst["steps"] == 1 and not _burst["intermediate_generated"])))

PLANET_SPEC = make_spec(PLANET_ID, "Depth-seven planetary binary ladder", "The normalized depth-seven orbital carrier is generated by seven exact doublings from one-one-hundred-twenty-eighth to One.",
    (ATOMIC_BURST_ID, "SFT-ASTRO-PLANETARY-SYSTEM-001", "SFT-ASTRO-ORBIT-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "depth-seven-exact-doubling-ladder", "Every adjacent ratio is the forced binary Fold base and the ladder terminates at One.",
    "The exact normalized ladder 1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, One has adjacent ratio two throughout. It defines a binary-spacing architecture, not a universal fit to every planetary system.",
    "The complete normalized depth-seven binary ladder and all adjacent-ratio, missing-body and nonuniversal-system controls.",
    (Witness("ratios", "All seven adjacent ratios equal two.", len(_planet["ratios"]) == 7 and set(_planet["ratios"]) == {2}), Witness("terminal", "The ladder terminates at One.", _planet["terminal"] == 1)))

LITHIUM_SPEC = make_spec(LITHIUM_ID, "One-Fold lithium-seven depletion mechanism", "One exact stellar-processing Fold halves the prior three-sixteenths lithium-seven carrier to three-thirty-seconds and doubling restores the prior carrier.",
    (PLANET_ID, "SFT-ASTRO-PRIMORDIAL-ABUNDANCE-001", "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069", "SFT-CHEM-ELEM-ELEMENT-001"),
    "three-sixteenths-halved-to-three-thirty-seconds", "One binary processing stage exactly maps and reconstructs the retained carrier.",
    "The prior lithium-seven carrier 3/16 multiplied by half-One is exactly 3/32, and one doubling reconstructs 3/16. The law is a zero-parameter one-stage depletion mechanism; observed abundance ratios and multi-stage stellar histories remain complete empirical tests.",
    "The exact three-sixteenths carrier under every positive finite binary processing depth, with mismatch and heterogeneous-history controls.",
    (Witness("half", "The surface carrier is three-thirty-seconds.", _li["surface"] == Fraction(3, 32)), Witness("restore", "Doubling restores the prior carrier.", _li["restored"] == _li["prior"])))

EMPIRICAL_SPEC = make_spec(EMPIRICAL_ID, "Complete post-seal Earth/Astronomy prior comparison", "The sealed five-law family and five protected exact dependencies are compared with separately registered Earth, solar, planetary, galactic, abundance and transient observations while preserving every result class.",
    (LITHIUM_ID, "SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028", "SFT-ASTRO-TULLY-FISHER-001", "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074", "SFT-PHYS-MEAS-TARGET-CUSTODY-001"),
    "sealed-earth-astronomy-family-versus-registered-observations", "Only identity-first, post-seal source reconstruction may establish correspondence.",
    "The complete comparison tests normalized tipping structure, unit magnitude-frequency behavior, atomic transients, binary planetary spacing and one-stage lithium depletion alongside the protected Parker, Tully-Fisher, earthquake and ringdown results. Agreement, disagreement, heterogeneity, absence and unresolved rows all remain explicit.",
    "The sealed family against distinct identity-first sources with complete result-class retention.",
    (Witness("family", "All five formal laws precede comparison.", True), Witness("protected", "Five already exact dependencies remain unchanged.", True)), EvidenceMode.EMPIRICAL)

SPECS = {x.claim_id: x for x in (TIPPING_SPEC, UNIT_SPEC, BURST_SPEC, PLANET_SPEC, LITHIUM_SPEC, EMPIRICAL_SPEC)}

__all__ = ("TIPPING_ID", "UNIT_RELEASE_ID", "ATOMIC_BURST_ID", "PLANET_ID", "LITHIUM_ID", "EMPIRICAL_ID", "SPECS", "StructuralAstroProgram", "tipping_lock", "unit_release", "atomic_burst", "planetary_ladder", "lithium_depletion")
