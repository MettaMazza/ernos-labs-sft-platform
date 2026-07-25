"""Terminal deuteron and two-nucleon exchange-channel law.

The executable law contains no nuclide name, measured spin, mass, binding
energy, scattering length or source locator.  It enumerates the complete
two-label spin support, retains exchange hand as an exact label, composes the
spatial/spin/charge exchange ledger, and compares each channel with the
already admitted quarter-One residual boundary act.  Structural absence is
the empty tuple and is never a numerical proof value.
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
from sft.foundation.half_one import half_one
from sft.physics.nuclear_residual_force_successor_laws_v1 import (
    residual_boundary_support,
)
from sft.physics.nucleon_binding_successor_laws_v1 import baryon_charge_class
from sft.physics.prior_value_laws import positive_take


CLAIM_ID = "SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006"
EXPERIMENT_ID = "SFT-EXP-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006"
Empty = tuple[()]

PRESERVING = "exchange-preserving"
ALTERNATING = "exchange-alternating"
PAIR_CLASSES = ("proton-neutron", "proton-proton", "neutron-neutron")


@dataclass(frozen=True)
class SpinClass:
    name: str
    exchange_hand: str
    held_word_support: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class PairChannel:
    pair_class: str
    spatial_hand: str
    charge_hand: str
    spin_hand: str
    total_exchange_hand: str
    spin_support: Fraction
    retained_binding_support: Fraction | Empty
    charge_path: Fraction | Empty

    @property
    def binds(self) -> bool:
        return self.retained_binding_support != ()


@dataclass(frozen=True)
class CandidateForm:
    exchange_partition: str
    ground_exchange_ledger: str
    residual_discriminator: str
    binding_table: str
    composite_spin: str
    charged_pair_role: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.exchange_partition,
            self.ground_exchange_ledger,
            self.residual_discriminator,
            self.binding_table,
            self.composite_spin,
            self.charged_pair_role,
            self.target_boundary,
            self.extension,
        ))


EXCHANGE_PARTITIONS = (
    "three-preserving-one-alternating",
    "two-preserving-two-alternating",
    "one-preserving-three-alternating",
)
GROUND_EXCHANGE_LEDGERS = (
    "pn-preserving-spin-ppnn-alternating-spin",
    "pn-alternating-spin-ppnn-preserving-spin",
    "all-pairs-preserving-spin",
)
RESIDUAL_DISCRIMINATORS = (
    "preserving-leaves-half-alternating-empty",
    "quarter-act-binds-both-spin-hands",
    "neither-spin-hand-retains-support",
)
BINDING_TABLES = (
    "pn-only-bound",
    "all-pairs-bound",
    "no-pair-bound",
    "identical-pairs-only-bound",
)
COMPOSITE_SPINS = (
    "complete-One-with-three-readings",
    "empty-spin-with-one-reading",
    "spin-unresolved",
)
CHARGED_PAIR_ROLES = (
    "pp-positive-opposition-secondary-to-singlet-exclusion",
    "charged-path-selects-both-identical-outcomes",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")

GENERATION_RULE = (
    "Generate the complete product of all exchange partitions of the four two-label spin states, every "
    "ground spatial/spin/charge exchange allocation, every quarter-residual binding discriminator, every "
    "three-pair binding table, every composite-spin reading class, both charged-pair roles, both target-custody "
    "states and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every ordered word over the two forced held spin labels; preserving and alternating exchange hands; the "
    "least exchange-preserving spatial recurrence; preserving identical or alternating proton/neutron charge "
    "support; the admitted quarter-One residual boundary act; all proton-neutron, proton-proton and "
    "neutron-neutron ground channels; sealed or exposed target custody; and empty or free extension. The "
    "certificate is independent of a finite Fold search depth."
)


@lru_cache(maxsize=1)
def spin_classes() -> tuple[SpinClass, ...]:
    """Enumerate the complete held exchange classes of two spin labels.

    The mixed preserving and mixed alternating forms use the same ordered
    words but retain different exchange hands.  No irrational normalization,
    signed amplitude or imaginary phase is formed.
    """

    first, second = "first-fibre", "second-fibre"
    classes = (
        SpinClass("first-first", PRESERVING, ((first, first),)),
        SpinClass("preserving-mixed", PRESERVING, ((first, second), (second, first))),
        SpinClass("second-second", PRESERVING, ((second, second),)),
        SpinClass("alternating-mixed", ALTERNATING, ((first, second), (second, first))),
    )
    if len(classes) != 4 or len({item.name for item in classes}) != 4:
        raise ValueError("two-label spin exchange census is incomplete")
    return classes


@lru_cache(maxsize=1)
def exchange_partition() -> dict[str, tuple[str, ...]]:
    classes = spin_classes()
    result = {
        PRESERVING: tuple(item.name for item in classes if item.exchange_hand == PRESERVING),
        ALTERNATING: tuple(item.name for item in classes if item.exchange_hand == ALTERNATING),
    }
    if len(result[PRESERVING]) + len(result[ALTERNATING]) != len(classes):
        raise ValueError("exchange classes do not exhaust two-label support")
    return result


def spin_support(exchange_hand: str) -> Fraction:
    partition = exchange_partition()
    if exchange_hand not in partition:
        raise ValueError("spin support names an ungenerated exchange hand")
    return Fraction(len(partition[exchange_hand]), len(spin_classes()))


def compose_exchange_hands(*hands: str) -> str:
    """Compose held exchange hands without signed parity magnitudes."""

    result = PRESERVING
    for hand in hands:
        if hand not in (PRESERVING, ALTERNATING):
            raise ValueError("exchange composition names an ungenerated hand")
        result = PRESERVING if result == hand else ALTERNATING
    return result


def charge_exchange_hand(pair_class: str) -> str:
    if pair_class == "proton-neutron":
        # The complete pn/np charge-label orbit admits an alternating held hand.
        return ALTERNATING
    if pair_class in ("proton-proton", "neutron-neutron"):
        return PRESERVING
    raise ValueError("charge exchange names an ungenerated pair")


def ground_spin_hand(pair_class: str) -> str:
    """Solve the complete fermionic exchange ledger for the least ground word."""

    spatial = PRESERVING
    charge = charge_exchange_hand(pair_class)
    admissible = tuple(
        spin
        for spin in (PRESERVING, ALTERNATING)
        if compose_exchange_hands(spatial, charge, spin) == ALTERNATING
    )
    if len(admissible) != 1:
        raise ValueError("ground exchange ledger lacks a unique fermionic spin hand")
    return admissible[0]


def retained_after_residual(exchange_hand: str) -> Fraction | Empty:
    """Retain a positive bound recurrence after the two-boundary residual act."""

    support = spin_support(exchange_hand)
    boundary = residual_boundary_support()
    if support > boundary:
        retained = positive_take(support, boundary)
        if not isinstance(retained, Fraction):
            raise ValueError("positive channel remainder lost exact type")
        return retained
    if support == boundary:
        return ()
    raise ValueError("generated spin support fell below the admitted residual boundary")


def pair_charge_path(pair_class: str) -> Fraction | Empty:
    charged = baryon_charge_class(2, 1)
    neutral = baryon_charge_class(1, 2)
    if charged != ("positive-charge-hand", Fraction(1, 1)) or neutral != ():
        raise ValueError("admitted nucleon charge words changed")
    if pair_class == "proton-proton":
        return Fraction(1, 1)
    if pair_class in ("proton-neutron", "neutron-neutron"):
        return ()
    raise ValueError("charge path names an ungenerated pair")


@lru_cache(maxsize=1)
def pair_channels() -> tuple[PairChannel, ...]:
    rows: list[PairChannel] = []
    for pair_class in PAIR_CLASSES:
        spatial = PRESERVING
        charge = charge_exchange_hand(pair_class)
        spin = ground_spin_hand(pair_class)
        total = compose_exchange_hands(spatial, charge, spin)
        rows.append(PairChannel(
            pair_class=pair_class,
            spatial_hand=spatial,
            charge_hand=charge,
            spin_hand=spin,
            total_exchange_hand=total,
            spin_support=spin_support(spin),
            retained_binding_support=retained_after_residual(spin),
            charge_path=pair_charge_path(pair_class),
        ))
    if any(row.total_exchange_hand != ALTERNATING for row in rows):
        raise ValueError("two-nucleon ground ledger violates fermionic exchange")
    return tuple(rows)


def channel_by_pair(pair_class: str) -> PairChannel:
    matches = tuple(row for row in pair_channels() if row.pair_class == pair_class)
    if len(matches) != 1:
        raise ValueError("two-nucleon pair is absent or duplicated")
    return matches[0]


def composite_spin_certificate() -> dict[str, object]:
    half = half_one().value
    complete = half + half
    preserving_readings = len(exchange_partition()[PRESERVING])
    return {
        "constituent_spin": half,
        "preserving_composite_spin": complete,
        "preserving_reading_count": preserving_readings,
        "alternating_reading_count": len(exchange_partition()[ALTERNATING]),
        "preserving_support": spin_support(PRESERVING),
        "alternating_support": spin_support(ALTERNATING),
        "residual_boundary": residual_boundary_support(),
        "preserving_remainder": retained_after_residual(PRESERVING),
        "alternating_remainder": retained_after_residual(ALTERNATING),
    }


def binding_outcomes() -> dict[str, bool]:
    return {row.pair_class: row.binds for row in pair_channels()}


def exchange_partition_is_forced(value: str) -> bool:
    observed = (
        len(exchange_partition()[PRESERVING]),
        len(exchange_partition()[ALTERNATING]),
    )
    alternatives = {
        "three-preserving-one-alternating": (3, 1),
        "two-preserving-two-alternating": (2, 2),
        "one-preserving-three-alternating": (1, 3),
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated exchange partition")
    return observed == alternatives[value]


def ground_exchange_ledger_is_forced(value: str) -> bool:
    observed = {pair: ground_spin_hand(pair) for pair in PAIR_CLASSES}
    alternatives = {
        "pn-preserving-spin-ppnn-alternating-spin": {
            "proton-neutron": PRESERVING,
            "proton-proton": ALTERNATING,
            "neutron-neutron": ALTERNATING,
        },
        "pn-alternating-spin-ppnn-preserving-spin": {
            "proton-neutron": ALTERNATING,
            "proton-proton": PRESERVING,
            "neutron-neutron": PRESERVING,
        },
        "all-pairs-preserving-spin": {pair: PRESERVING for pair in PAIR_CLASSES},
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated ground exchange ledger")
    return observed == alternatives[value]


def residual_discriminator_is_forced(value: str) -> bool:
    observed = {
        PRESERVING: retained_after_residual(PRESERVING),
        ALTERNATING: retained_after_residual(ALTERNATING),
    }
    if value == "preserving-leaves-half-alternating-empty":
        return observed == {PRESERVING: Fraction(1, 2), ALTERNATING: ()}
    if value == "quarter-act-binds-both-spin-hands":
        return all(item != () for item in observed.values())
    if value == "neither-spin-hand-retains-support":
        return all(item == () for item in observed.values())
    raise ValueError("candidate names an ungenerated residual discriminator")


def binding_table_is_forced(value: str) -> bool:
    observed = binding_outcomes()
    alternatives = {
        "pn-only-bound": {
            "proton-neutron": True,
            "proton-proton": False,
            "neutron-neutron": False,
        },
        "all-pairs-bound": {pair: True for pair in PAIR_CLASSES},
        "no-pair-bound": {pair: False for pair in PAIR_CLASSES},
        "identical-pairs-only-bound": {
            "proton-neutron": False,
            "proton-proton": True,
            "neutron-neutron": True,
        },
    }
    if value not in alternatives:
        raise ValueError("candidate names an ungenerated binding table")
    return observed == alternatives[value]


def composite_spin_is_forced(value: str) -> bool:
    certificate = composite_spin_certificate()
    if value == "complete-One-with-three-readings":
        return (
            certificate["preserving_composite_spin"] == Fraction(1, 1)
            and certificate["preserving_reading_count"] == 3
            and channel_by_pair("proton-neutron").spin_hand == PRESERVING
        )
    if value == "empty-spin-with-one-reading":
        return channel_by_pair("proton-neutron").spin_hand == ALTERNATING
    if value == "spin-unresolved":
        return False
    raise ValueError("candidate names an ungenerated composite spin")


def charged_pair_role_is_forced(value: str) -> bool:
    proton_pair = channel_by_pair("proton-proton")
    neutron_pair = channel_by_pair("neutron-neutron")
    if value == "pp-positive-opposition-secondary-to-singlet-exclusion":
        return (
            proton_pair.charge_path == Fraction(1, 1)
            and neutron_pair.charge_path == ()
            and not proton_pair.binds
            and not neutron_pair.binds
            and proton_pair.spin_hand == neutron_pair.spin_hand == ALTERNATING
        )
    if value == "charged-path-selects-both-identical-outcomes":
        return proton_pair.charge_path == neutron_pair.charge_path
    raise ValueError("candidate names an ungenerated charged-pair role")


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
            EXCHANGE_PARTITIONS,
            GROUND_EXCHANGE_LEDGERS,
            RESIDUAL_DISCRIMINATORS,
            BINDING_TABLES,
            COMPOSITE_SPINS,
            CHARGED_PAIR_ROLES,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    return {
        "exchange_partition": exchange_partition_is_forced(form.exchange_partition),
        "ground_exchange_ledger": ground_exchange_ledger_is_forced(form.ground_exchange_ledger),
        "residual_discriminator": residual_discriminator_is_forced(form.residual_discriminator),
        "binding_table": binding_table_is_forced(form.binding_table),
        "composite_spin": composite_spin_is_forced(form.composite_spin),
        "charged_pair_role": charged_pair_role_is_forced(form.charged_pair_role),
        "target_boundary": target_boundary_is_forced(form.target_boundary),
        "extension": extension_is_forced(form.extension),
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def candidate_exact_form(form: CandidateForm) -> str:
    return (
        f"exchange={form.exchange_partition}; ground={form.ground_exchange_ledger}; "
        f"residual={form.residual_discriminator}; binding={form.binding_table}; "
        f"spin={form.composite_spin}; charged_pair={form.charged_pair_role}; "
        f"target={form.target_boundary}; extension={form.extension}"
    )


def decision_reason(form: CandidateForm, facts: dict[str, bool]) -> str:
    failures = tuple(name for name, passed in facts.items() if not passed)
    if failures:
        return "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
    return (
        "Complete two-label exchange enumeration gives preserving support three-quarters and alternating "
        "support one-quarter. The admitted residual boundary act is one-quarter, so only the preserving hand "
        "retains the positive half-One recurrence. The complete spatial/spin/charge exchange ledger assigns "
        "that hand to proton-neutron and the exhausted alternating hand to both identical pairs."
    )


def completeness_record() -> dict[str, object]:
    forms = candidate_forms()
    return {
        "generation_rule": GENERATION_RULE,
        "grammar_boundary": GRAMMAR_BOUNDARY,
        "axis_cardinalities": (3, 3, 3, 4, 3, 2, 2, 2),
        "candidate_count": len(forms),
        "candidate_ids": tuple(form.candidate_id for form in forms),
    }


def closure_record(decisions: Sequence[CandidateDecision]) -> dict[str, object]:
    return {
        "survivors_computed": tuple(item.candidate_id for item in decisions if item.survives),
        "spin_certificate": composite_spin_certificate(),
        "pair_channels": pair_channels(),
        "binding_outcomes": binding_outcomes(),
        "target_absent_from_formal_module": True,
        "extension_absent": extension_is_forced("empty-extension"),
    }


class DeuteronDinucleonProgram:
    """Complete computed enumeration with no claimant-supplied answer key."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._forms_by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Terminal deuteron binding, spin and dinucleon exclusion",
            branch="physics",
            statement=(
                "The complete two-label spin word has three exchange-preserving readings with support three-"
                "quarters and one exchange-alternating reading with support one-quarter. The admitted two-boundary "
                "residual act is one-quarter: preserving support therefore retains exactly half-One as a bound "
                "recurrence, while alternating support is exhausted and closes to the empty form. In the least "
                "spatial ground recurrence, the alternating proton-neutron charge hand permits the preserving "
                "spin channel; identical proton-proton and neutron-neutron charge hands require the alternating "
                "spin channel to preserve total fermionic exchange. Hence the proton-neutron pair alone is bound, "
                "with complete spin One and three readings; both identical two-nucleon pairs are unbound. Proton "
                "Coulomb opposition is an additional pp boundary and cannot explain or alter the nn result. "
                "Dimensional binding energy and scattering records open only after the structural seal."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-FOUNDATION-HALF-ONE-001",
                "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
                "SFT-PHYS-QUANTUM-SPIN-001",
                "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
                "SFT-PHYS-QUANTUM-EXCLUSION-001",
                "SFT-PHYS-MATTER-FERMION-BOSON-001",
                "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005",
                "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
                "SFT-PHYS-NUCLEAR-BINDING-001",
                "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003",
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
        reason = decision_reason(form, facts)
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
        closure = closure_record(decisions)
        spin = closure["spin_certificate"]
        outcomes = closure["binding_outcomes"]
        minimality = (
            len(closure["survivors_computed"]) == 1
            and spin["preserving_remainder"] == Fraction(1, 2)
            and spin["alternating_remainder"] == ()
            and outcomes == {
                "proton-neutron": True,
                "proton-proton": False,
                "neutron-neutron": False,
            }
        )
        uniqueness = minimality and closure["extension_absent"] is True
        generality = {
            "complete_two-label_exchange_classes": spin_classes(),
            "exchange_partition": exchange_partition(),
            "quarter_residual_dependency": "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
            "fermionic_exchange_dependency": "SFT-PHYS-QUANTUM-EXCLUSION-001",
            "pair_channels": pair_channels(),
            "all_future_two-label_ground_pairs_use_same_ledger": True,
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=minimality,
            named_shape_uniqueness_passed=uniqueness,
            proof_hash=sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            generality_certificate_hash=sha256_identity(generality),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        computed = tuple(form for form in self._forms if form_survives(form))
        if len(computed) != 1:
            raise ValueError("controls require exactly one computed form")
        form = computed[0]
        reversed_binding = replace(form, binding_table="identical-pairs-only-bound")
        target_exposed = replace(form, target_boundary="readable-before-seal")
        free_extension = replace(form, extension="free-correction")
        identifiers = tuple(item.candidate_id for item in self._forms)
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not form_survives(reversed_binding),
                "Reject binding of the identical pairs with exclusion of proton-neutron.",
                "The computed exchange and quarter-support ledger rejects the reversed outcome.",
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
                not form_survives(target_exposed) and not form_survives(free_extension),
                "Reject pre-seal target access and every ungenerated correction.",
                "Sealed custody and the empty extension are both required by computed predicates.",
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
    "ALTERNATING",
    "CLAIM_ID",
    "COMPOSITE_SPINS",
    "DeuteronDinucleonProgram",
    "EXPERIMENT_ID",
    "GRAMMAR_BOUNDARY",
    "GENERATION_RULE",
    "PAIR_CLASSES",
    "PRESERVING",
    "PairChannel",
    "binding_outcomes",
    "candidate_facts",
    "candidate_forms",
    "channel_by_pair",
    "completeness_record",
    "composite_spin_certificate",
    "compose_exchange_hands",
    "exchange_partition",
    "form_survives",
    "ground_spin_hand",
    "pair_channels",
    "retained_after_residual",
    "spin_classes",
    "spin_support",
)
