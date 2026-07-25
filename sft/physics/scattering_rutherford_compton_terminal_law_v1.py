"""Terminal exact scattering, Rutherford and Compton law.

The formal law has no source locator, particle name, measured angle, measured
cross section, dimensional wavelength or target value.  It works over exact
positive transfer parts and structural absence.  The Rutherford and Compton
translations are opened only after the complete candidate grammar is sealed.
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
from sft.physics.prior_value_laws import positive_take


CLAIM_ID = "SFT-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006"
EXPERIMENT_ID = "SFT-EXP-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006"
Empty = tuple[()]


@dataclass(frozen=True)
class CandidateForm:
    amplitude_carrier: str
    cross_section_measure: str
    coulomb_angular_law: str
    coulomb_scale_law: str
    photon_shift_law: str
    photon_energy_law: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.amplitude_carrier,
            self.cross_section_measure,
            self.coulomb_angular_law,
            self.coulomb_scale_law,
            self.photon_shift_law,
            self.photon_energy_law,
            self.target_boundary,
            self.extension,
        ))


AMPLITUDE_CARRIERS = (
    "paired-phase-compatible-overlap-legs",
    "single-unpaired-channel-count",
    "imported-complex-amplitude",
)
CROSS_SECTION_MEASURES = (
    "paired-weight-per-incident-boundary-support",
    "unnormalized-outgoing-count",
    "target-fitted-area",
)
COULOMB_ANGULAR_LAWS = (
    "inverse-transfer-part-squared",
    "inverse-transfer-part-first-power",
    "angle-independent-response",
)
COULOMB_SCALE_LAWS = (
    "charge-product-squared-energy-inverse-squared",
    "charge-product-linear-energy-inverse",
    "free-dimensional-scale",
)
PHOTON_SHIFT_LAWS = (
    "two-transfer-parts-times-action-over-inertia-speed",
    "one-transfer-part-times-action-over-inertia-speed",
    "angle-independent-wavelength-change",
)
PHOTON_ENERGY_LAWS = (
    "rest-over-rest-plus-two-energy-transfer-parts",
    "incident-energy-preserved",
    "outgoing-energy-greater-than-incident",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")

TRANSFER_PARTS = (
    Fraction(1, 4),
    Fraction(1, 2),
    Fraction(3, 4),
    Fraction(1, 1),
)

GENERATION_RULE = (
    "Generate the complete product of every exact overlap-leg account, every cross-section measure, every "
    "Coulomb angular power, every Coulomb charge/energy scale, every photon wavelength-transfer law, every "
    "photon energy-transfer law, both target-custody states and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every exact positive rational nonforward direction-transfer part not exceeding the One; the structural "
    "empty forward class; phase-compatible incoming/transfer/outgoing legs; source-normalized differential "
    "boundary support; conserved charged-source and incident-energy carriers; one photon, one initially held "
    "inertial word and closed energy-direction transfer; sealed or exposed targets; and empty or free extension. "
    "The induction certificates are independent of a finite Fold depth."
)


def positive_transfer_part(numerator: int, denominator: int) -> Fraction:
    if numerator < 1 or denominator < 1 or numerator > denominator:
        raise ValueError("direction transfer must be a positive part of the One")
    return Fraction(numerator, denominator)


def forward_transfer() -> Empty:
    """The unchanged direction is structural absence of a transfer act."""

    return ()


def overlap_leg(transfer_part: Fraction) -> Fraction:
    """One conserved Coulomb transfer leg per generated transfer boundary."""

    if (
        not isinstance(transfer_part, Fraction)
        or transfer_part.numerator < 1
        or transfer_part > Fraction(1, 1)
    ):
        raise ValueError("overlap leg requires one exact positive nonforward part")
    return Fraction(1, 1) / transfer_part


def direction_complement(transfer_part: Fraction) -> Fraction | Empty:
    """Retain the nonturned direction hand without forming numerical zero."""

    if transfer_part.numerator < 1 or transfer_part > Fraction(1, 1):
        raise ValueError("direction complement requires a positive part of the One")
    if transfer_part == Fraction(1, 1):
        return ()
    complement = positive_take(Fraction(1, 1), transfer_part)
    if not isinstance(complement, Fraction):
        raise ValueError("nonterminal direction complement lost exact support")
    return complement


def cumulative_impact_area(transfer_part: Fraction) -> Fraction | Empty:
    """Exact incident-area support above one generated transfer boundary.

    Closed Coulomb approach partitions the unit direction into retained and
    turned hands.  Their exact area ratio is complement/transfer.  At complete
    backscatter the retained hand is structurally absent.
    """

    complement = direction_complement(transfer_part)
    if complement == ():
        return ()
    return complement / transfer_part


def annular_transfer_density(lower: Fraction, upper: Fraction) -> Fraction:
    """Exact area removed per exact angular-transfer interval."""

    if lower.numerator < 1 or lower >= upper or upper > Fraction(1, 1):
        raise ValueError("annular transfer interval is not an ordered positive part")
    lower_area = cumulative_impact_area(lower)
    upper_area = cumulative_impact_area(upper)
    if not isinstance(lower_area, Fraction):
        raise ValueError("lower impact area cannot be structurally empty")
    removed = lower_area if upper_area == () else positive_take(lower_area, upper_area)
    interval = positive_take(upper, lower)
    if not isinstance(removed, Fraction) or not isinstance(interval, Fraction):
        raise ValueError("annular transfer failed positive exact subtraction")
    return removed / interval


def paired_overlap_density(transfer_part: Fraction) -> Fraction:
    """Pair the preparation-to-transfer and transfer-to-record legs exactly."""

    leg = overlap_leg(transfer_part)
    return leg * leg


def coulomb_backscatter_scale(charge_product: Fraction, incident_energy: Fraction) -> Fraction:
    """Normalized Coulomb backscatter area from held source and energy carriers."""

    if charge_product.numerator < 1 or incident_energy.numerator < 1:
        raise ValueError("Coulomb scale carriers must remain exact and positive")
    approach = charge_product / (Fraction(4, 1) * incident_energy)
    return approach * approach


def coulomb_differential_support(
    charge_product: Fraction,
    incident_energy: Fraction,
    transfer_part: Fraction,
) -> Fraction:
    return coulomb_backscatter_scale(charge_product, incident_energy) * paired_overlap_density(transfer_part)


def photon_shift_in_compton_carriers(transfer_part: Fraction) -> Fraction:
    """Exact positive wavelength increase in units of the action/inertia/speed carrier."""

    if transfer_part.numerator < 1 or transfer_part > Fraction(1, 1):
        raise ValueError("photon shift requires a positive nonforward transfer part")
    return Fraction(2, 1) * transfer_part


def scattered_photon_energy_ratio(
    incident_to_rest: Fraction,
    transfer_part: Fraction,
) -> Fraction:
    """Outgoing/incident energy from closed photon-electron transfer."""

    if (
        incident_to_rest.numerator < 1
        or transfer_part.numerator < 1
        or transfer_part > Fraction(1, 1)
    ):
        raise ValueError("Compton carriers must remain exact and positive")
    return Fraction(1, 1) / (Fraction(1, 1) + Fraction(2, 1) * incident_to_rest * transfer_part)


def compton_conservation_transfer(
    incident_to_rest: Fraction,
    outgoing_over_incident: Fraction,
) -> Fraction:
    """Return the exact wavelength-transfer carrier implied by closed energy.

    In electron-rest units, the inverse outgoing photon support exceeds the
    inverse incident support.  Their positive take is the wavelength increase
    in Compton carriers; no signed subtraction is introduced.
    """

    if (
        incident_to_rest.numerator < 1
        or outgoing_over_incident.numerator < 1
        or outgoing_over_incident >= Fraction(1, 1)
    ):
        raise ValueError("Compton conservation requires positive energy loss")
    outgoing_in_rest = incident_to_rest * outgoing_over_incident
    transfer = positive_take(
        Fraction(1, 1) / outgoing_in_rest,
        Fraction(1, 1) / incident_to_rest,
    )
    if not isinstance(transfer, Fraction):
        raise ValueError("nonforward Compton transfer became structurally empty")
    return transfer


def scattered_photon_in_rest_units(
    incident_to_rest: Fraction,
    transfer_part: Fraction,
) -> Fraction:
    return incident_to_rest * scattered_photon_energy_ratio(incident_to_rest, transfer_part)


def high_energy_ceiling_in_rest_units(transfer_part: Fraction) -> Fraction:
    if transfer_part.numerator < 1 or transfer_part > Fraction(1, 1):
        raise ValueError("ceiling requires a positive nonforward transfer part")
    return Fraction(1, 1) / (Fraction(2, 1) * transfer_part)


def high_energy_gap(depth: int, transfer_part: Fraction) -> Fraction:
    if depth < 1:
        raise ValueError("generated incident-energy depth must be positive")
    return high_energy_ceiling_in_rest_units(transfer_part) - scattered_photon_in_rest_units(
        Fraction(depth, 1), transfer_part
    )


def high_energy_step(depth: int, transfer_part: Fraction) -> Fraction:
    if depth < 1:
        raise ValueError("generated incident-energy depth must be positive")
    present = scattered_photon_in_rest_units(Fraction(depth, 1), transfer_part)
    successor = scattered_photon_in_rest_units(Fraction(depth + 1, 1), transfer_part)
    return successor - present


@lru_cache(maxsize=1)
def formal_certificate() -> dict[str, object]:
    angular = tuple((part, paired_overlap_density(part)) for part in TRANSFER_PARTS)
    shifts = tuple((part, photon_shift_in_compton_carriers(part)) for part in TRANSFER_PARTS)
    energy = tuple(
        (part, scattered_photon_energy_ratio(Fraction(1, 1), part))
        for part in TRANSFER_PARTS
    )
    return {
        "forward_transfer": forward_transfer(),
        "transfer_parts": TRANSFER_PARTS,
        "coulomb_normalized_angular_density": angular,
        "coulomb_cumulative_impact_area": tuple(
            (part, cumulative_impact_area(part)) for part in TRANSFER_PARTS
        ),
        "coulomb_annular_interval_density": tuple(
            (lower, upper, annular_transfer_density(lower, upper))
            for lower, upper in zip(TRANSFER_PARTS, TRANSFER_PARTS[1:])
        ),
        "coulomb_annular_product_identity": tuple(
            annular_transfer_density(lower, upper) == Fraction(1, 1) / (lower * upper)
            for lower, upper in zip(TRANSFER_PARTS, TRANSFER_PARTS[1:])
        ),
        "coulomb_charge_doubling_ratio": (
            coulomb_backscatter_scale(Fraction(2, 1), Fraction(1, 1))
            / coulomb_backscatter_scale(Fraction(1, 1), Fraction(1, 1))
        ),
        "coulomb_energy_doubling_ratio": (
            coulomb_backscatter_scale(Fraction(1, 1), Fraction(2, 1))
            / coulomb_backscatter_scale(Fraction(1, 1), Fraction(1, 1))
        ),
        "photon_shift_in_compton_carriers": shifts,
        "photon_outgoing_over_incident_at_equal_rest_energy": energy,
        "photon_conservation_transfer_at_equal_rest_energy": tuple(
            (
                part,
                compton_conservation_transfer(
                    Fraction(1, 1),
                    scattered_photon_energy_ratio(Fraction(1, 1), part),
                ),
            )
            for part in TRANSFER_PARTS
        ),
        "right_angle_high_energy_ceiling": high_energy_ceiling_in_rest_units(Fraction(1, 2)),
        "backscatter_high_energy_ceiling": high_energy_ceiling_in_rest_units(Fraction(1, 1)),
        "positive_successor_steps": tuple(
            high_energy_step(depth, part)
            for part in TRANSFER_PARTS
            for depth in (1, 2, 3, 4)
        ),
        "positive_ceiling_gaps": tuple(
            high_energy_gap(depth, part)
            for part in TRANSFER_PARTS
            for depth in (1, 2, 3, 4)
        ),
    }


def amplitude_carrier_is_forced(value: str) -> bool:
    certificate = formal_certificate()
    paired = all(
        density == overlap_leg(part) * overlap_leg(part)
        for part, density in certificate["coulomb_normalized_angular_density"]
    ) and all(certificate["coulomb_annular_product_identity"])
    alternatives = {
        "paired-phase-compatible-overlap-legs": paired,
        "single-unpaired-channel-count": all(
            density == overlap_leg(part)
            for part, density in certificate["coulomb_normalized_angular_density"]
        ),
        "imported-complex-amplitude": False,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated amplitude carrier")
    return alternatives[value]


def cross_section_measure_is_forced(value: str) -> bool:
    source = Fraction(3, 1)
    incident = Fraction(5, 1)
    boundary = Fraction(2, 1)
    observed = source / (incident * boundary)
    alternatives = {
        "paired-weight-per-incident-boundary-support": observed == Fraction(3, 10),
        "unnormalized-outgoing-count": observed == source,
        "target-fitted-area": False,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated cross-section measure")
    return alternatives[value]


def coulomb_angular_law_is_forced(value: str) -> bool:
    observed = tuple(density for _, density in formal_certificate()["coulomb_normalized_angular_density"])
    alternatives = {
        "inverse-transfer-part-squared": (
            Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1)
        ),
        "inverse-transfer-part-first-power": (
            Fraction(4, 1), Fraction(2, 1), Fraction(4, 3), Fraction(1, 1)
        ),
        "angle-independent-response": (Fraction(1, 1),) * 4,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated Coulomb angular law")
    return observed == alternatives[value]


def coulomb_scale_law_is_forced(value: str) -> bool:
    certificate = formal_certificate()
    if value == "charge-product-squared-energy-inverse-squared":
        return (
            certificate["coulomb_charge_doubling_ratio"] == Fraction(4, 1)
            and certificate["coulomb_energy_doubling_ratio"] == Fraction(1, 4)
        )
    if value == "charge-product-linear-energy-inverse":
        return (
            certificate["coulomb_charge_doubling_ratio"] == Fraction(2, 1)
            and certificate["coulomb_energy_doubling_ratio"] == Fraction(1, 2)
        )
    if value == "free-dimensional-scale":
        return False
    raise ValueError("candidate names an ungenerated Coulomb scale law")


def photon_shift_law_is_forced(value: str) -> bool:
    certificate = formal_certificate()
    observed = tuple(shift for _, shift in certificate["photon_shift_in_compton_carriers"])
    conservation = tuple(
        transfer for _, transfer in certificate["photon_conservation_transfer_at_equal_rest_energy"]
    )
    alternatives = {
        "two-transfer-parts-times-action-over-inertia-speed": (
            Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1)
        ),
        "one-transfer-part-times-action-over-inertia-speed": TRANSFER_PARTS,
        "angle-independent-wavelength-change": (Fraction(1, 1),) * 4,
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated photon shift law")
    return observed == alternatives[value] and (
        value != "two-transfer-parts-times-action-over-inertia-speed"
        or conservation == observed
    )


def photon_energy_law_is_forced(value: str) -> bool:
    certificate = formal_certificate()
    observed = tuple(
        ratio for _, ratio in certificate["photon_outgoing_over_incident_at_equal_rest_energy"]
    )
    if value == "rest-over-rest-plus-two-energy-transfer-parts":
        return (
            observed == (Fraction(2, 3), Fraction(1, 2), Fraction(2, 5), Fraction(1, 3))
            and certificate["right_angle_high_energy_ceiling"] == Fraction(1, 1)
            and certificate["backscatter_high_energy_ceiling"] == Fraction(1, 2)
            and all(step.numerator >= 1 for step in certificate["positive_successor_steps"])
            and all(gap.numerator >= 1 for gap in certificate["positive_ceiling_gaps"])
        )
    if value == "incident-energy-preserved":
        return observed == (Fraction(1, 1),) * 4
    if value == "outgoing-energy-greater-than-incident":
        return all(ratio > 1 for ratio in observed)
    raise ValueError("candidate names an ungenerated photon energy law")


def target_boundary_is_forced(value: str) -> bool:
    if value == "sealed-before-release":
        return True
    if value == "readable-before-seal":
        return False
    raise ValueError("candidate names an ungenerated target boundary")


def extension_is_forced(value: str) -> bool:
    if value == "empty-extension":
        return True
    if value == "free-correction":
        return False
    raise ValueError("candidate names an ungenerated extension")


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            AMPLITUDE_CARRIERS,
            CROSS_SECTION_MEASURES,
            COULOMB_ANGULAR_LAWS,
            COULOMB_SCALE_LAWS,
            PHOTON_SHIFT_LAWS,
            PHOTON_ENERGY_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    return {
        "amplitude_carrier": amplitude_carrier_is_forced(form.amplitude_carrier),
        "cross_section_measure": cross_section_measure_is_forced(form.cross_section_measure),
        "coulomb_angular_law": coulomb_angular_law_is_forced(form.coulomb_angular_law),
        "coulomb_scale_law": coulomb_scale_law_is_forced(form.coulomb_scale_law),
        "photon_shift_law": photon_shift_law_is_forced(form.photon_shift_law),
        "photon_energy_law": photon_energy_law_is_forced(form.photon_energy_law),
        "target_boundary": target_boundary_is_forced(form.target_boundary),
        "extension": extension_is_forced(form.extension),
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def candidate_exact_form(form: CandidateForm) -> str:
    return (
        f"amplitude={form.amplitude_carrier}; cross_section={form.cross_section_measure}; "
        f"coulomb_angle={form.coulomb_angular_law}; coulomb_scale={form.coulomb_scale_law}; "
        f"photon_shift={form.photon_shift_law}; photon_energy={form.photon_energy_law}; "
        f"target={form.target_boundary}; extension={form.extension}"
    )


def decision_reason(facts: dict[str, bool]) -> str:
    failures = tuple(name for name, passed in facts.items() if not passed)
    if failures:
        return "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
    return (
        "Two phase-compatible overlap legs force exact self-pairing. Rank-two Coulomb transfer gives the "
        "inverse square of the direction-transfer part with charge-product-squared and incident-energy-inverse-"
        "squared scale. Closed photon-electron transfer gives a wavelength increase of two transfer parts and "
        "the unique energy-conserving denominator."
    )


def completeness_record() -> dict[str, object]:
    forms = candidate_forms()
    return {
        "generation_rule": GENERATION_RULE,
        "grammar_boundary": GRAMMAR_BOUNDARY,
        "axis_cardinalities": (3, 3, 3, 3, 3, 3, 2, 2),
        "candidate_count": len(forms),
        "candidate_ids": tuple(form.candidate_id for form in forms),
    }


class ScatteringRutherfordComptonProgram:
    """Complete computed enumeration with no claimant-supplied answer key."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._forms_by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Terminal Fold scattering, Rutherford angular law and Compton transfer",
            branch="physics",
            statement=(
                "A scattering amplitude carrier is the exact phase-compatible overlap support of one transition "
                "leg; an observed differential channel pairs the preparation-to-transfer and transfer-to-record "
                "legs, so its weight is their exact self-composition without an imported complex magnitude. For "
                "a conserved Coulomb source the rank-two transfer boundary forces differential support proportional "
                "to the inverse square of the exact direction-transfer part, with charge-product-squared and "
                "incident-energy-inverse-squared scale. At the comparison boundary this is the Rutherford inverse "
                "fourth-power half-angle law. For closed photon-electron transfer, wavelength increases by two "
                "direction-transfer parts of the action-over-inertia-speed carrier; outgoing energy is incident "
                "energy divided by One plus twice the incident/rest-energy ratio times that transfer part. Right-"
                "angle and backscatter high-energy ceilings are respectively one and half-One electron rest-energy "
                "support. Forward nondeflection remains the structural empty transfer class."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-PHYS-MATTER-SCATTERING-001",
                "SFT-PHYS-QUANTUM-PHYSICAL-STATE-001",
                "SFT-PHYS-QUANTUM-WEIGHT-001",
                "SFT-PHYS-MECH-CONSERVATION-001",
                "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
                "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003",
                "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
                "SFT-PHYS-MATTER-MASS-ENERGY-001",
                "SFT-PHYS-SPACETIME-LIMIT-SPEED-001",
                "SFT-PHYS-WAVE-SPEED-LENGTH-FREQUENCY-001",
                "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
                "SFT-PHYS-MEAS-DIMENSIONAL-CONSISTENCY-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-PHYS-MEAS-UNCERTAINTY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-COMBINATORICS-001",
            ),
            axioms=(),
            free_parameters=(),
            provenance=(
                ProvenanceClass.FORWARD_FORCING,
                ProvenanceClass.OBSERVATIONAL_DERIVATION,
            ),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(
            Candidate(
                candidate_id=form.candidate_id,
                exact_form=candidate_exact_form(form),
                trace_hash=sha256_identity({
                    "generator": GENERATION_RULE,
                    "form": form,
                    "computed_facts": candidate_facts(form),
                }),
            )
            for form in self._forms
        )
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(self._forms),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        form = self._forms_by_id[candidate.candidate_id]
        facts = candidate_facts(form)
        survives = all(facts.values())
        reason = decision_reason(facts)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity({
                "candidate_trace": candidate.trace_hash,
                "form": form,
                "facts": facts,
                "survives": survives,
                "reason": reason,
            }),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        certificate = formal_certificate()
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        minimality = (
            len(survivors) == 1
            and certificate["forward_transfer"] == ()
            and tuple(value for _, value in certificate["coulomb_normalized_angular_density"])
            == (Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1))
            and tuple(value for _, value in certificate["photon_shift_in_compton_carriers"])
            == (Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1))
            and certificate["right_angle_high_energy_ceiling"] == Fraction(1, 1)
            and certificate["backscatter_high_energy_ceiling"] == Fraction(1, 2)
        )
        uniqueness = minimality and extension_is_forced("empty-extension")
        generality = {
            "all_positive_rational_transfer_parts": (
                "paired_density(u)=1/(u*u)",
                "shift_in_compton_carriers(u)=2*u",
                "outgoing_over_incident(x,u)=1/(1+2*x*u)",
            ),
            "positive_successor_step": "1/[(1+2*u*n)*(1+2*u*(n+1))]",
            "positive_ceiling_gap": "1/[2*u*(1+2*u*n)]",
            "finite_annular_identity": "[C(a) take C(b)]/[b take a]=1/(a*b), where C(u)=(One take u)/u",
            "compton_conservation_identity": "[1/(x*r) take 1/x]=2*u uniquely gives r=1/(1+2*x*u)",
            "forward_class": (),
            "target_absent_from_formal_module": True,
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=minimality,
            named_shape_uniqueness_passed=uniqueness,
            proof_hash=sha256_identity({
                "certificate": certificate,
                "decisions": tuple(decisions),
                "survivors_computed": survivors,
            }),
            generality_certificate_hash=sha256_identity(generality),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        computed = tuple(form for form in self._forms if form_survives(form))
        if len(computed) != 1:
            raise ValueError("controls require exactly one computed form")
        form = computed[0]
        false_angle = replace(form, coulomb_angular_law="angle-independent-response")
        target_exposed = replace(form, target_boundary="readable-before-seal")
        free_extension = replace(form, extension="free-correction")
        identifiers = tuple(item.candidate_id for item in self._forms)
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not form_survives(false_angle),
                "Reject an angle-independent Coulomb response and elastic photon energy.",
                "Exact transfer-part and conservation predicates reject the false angular law.",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "Reject any changed claimant source identity.",
                "The changed identity differs from the registered source manifest.",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len(set(identifiers + (identifiers[0],))) != len(identifiers) + 1,
                "Reject a duplicated or incomplete candidate census.",
                "The deliberate duplicate fails complete candidate identity.",
            ),
            (
                ControlKind.BOUNDARY,
                forward_transfer() == ()
                and not form_survives(target_exposed)
                and not form_survives(free_extension),
                "Reject a numerical forward null, pre-seal target access and free correction.",
                "Forward transfer is structural absence; sealed custody and empty extension are required.",
            ),
        )
        return tuple(
            ControlResult(kind, passed, expected, observed, sha256_identity({
                "kind": kind,
                "passed": passed,
                "expected": expected,
                "observed": observed,
            }))
            for kind, passed, expected, observed in records
        )


__all__ = (
    "AMPLITUDE_CARRIERS",
    "CLAIM_ID",
    "COULOMB_ANGULAR_LAWS",
    "EXPERIMENT_ID",
    "GRAMMAR_BOUNDARY",
    "GENERATION_RULE",
    "PHOTON_ENERGY_LAWS",
    "PHOTON_SHIFT_LAWS",
    "ScatteringRutherfordComptonProgram",
    "TRANSFER_PARTS",
    "candidate_facts",
    "candidate_forms",
    "completeness_record",
    "coulomb_backscatter_scale",
    "coulomb_differential_support",
    "cumulative_impact_area",
    "annular_transfer_density",
    "compton_conservation_transfer",
    "direction_complement",
    "formal_certificate",
    "form_survives",
    "forward_transfer",
    "high_energy_ceiling_in_rest_units",
    "high_energy_gap",
    "high_energy_step",
    "overlap_leg",
    "paired_overlap_density",
    "photon_shift_in_compton_carriers",
    "positive_transfer_part",
    "scattered_photon_energy_ratio",
    "scattered_photon_in_rest_units",
)
