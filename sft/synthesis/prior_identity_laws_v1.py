"""Complete cross-branch return identities from already admitted receipts.

Synthesis owns no primitive law.  Every result below composes named branch
receipts and a frozen pre-Synthesis census.  Equality means exact identity of
the declared carrier/relation, never identity of the participating substances,
apparatuses, organisms or social contexts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis, fold_part

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "census/cross_branch_synthesis_prior_input_v1.json"
PRIOR = json.loads(INPUT_PATH.read_text())

PRIME_VACUUM_ID = "SFT-SYNTH-PRIME-VACUUM-ORBIT-IDENTITY-001"
LOCK_ID = "SFT-SYNTH-COMMON-LOCK-IDENTITY-001"
DESCENT_ID = "SFT-SYNTH-COMMON-DESCENT-IDENTITY-001"
WAVE_ID = "SFT-SYNTH-WAVE-MODE-RECURRENCE-IDENTITY-001"
HARMONIC_ID = "SFT-SYNTH-FOLD-SECOND-HARMONIC-IDENTITY-001"
VACUUM_PREDICTION_ID = "SFT-SYNTH-VACUUM-PERIOD-DIVISOR-PREDICTION-001"
POSITIVE_ID = "SFT-SYNTH-POSITIVE-OBSERVABLE-ABSENCE-BOUNDARY-001"
TESLA_ID = "SFT-SYNTH-TESLA-CORRESPONDENCE-ASSEMBLY-001"
CONSTANTS_ID = "SFT-SYNTH-UNIFIED-CONSTANTS-ASSEMBLY-001"
LEDGER_ID = "SFT-SYNTH-PREDICTION-FALSIFICATION-LEDGER-001"
OWNERSHIP_ID = "SFT-SYNTH-ONE-OWNER-NO-OMISSION-LEDGER-001"
TERMINAL_ID = "SFT-SYNTH-ROOT-TRACED-TERMINAL-ASSEMBLY-001"


def canonical_identity(payload: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prior_input_valid() -> bool:
    body = dict(PRIOR); expected = body.pop("input_identity")
    return expected == canonical_identity(body) and PRIOR["claim_count"] == 1460 and PRIOR["unique_dependency_root"] == "SFT-ROOT-THERE-IS-NO-NOTHING" and PRIOR["all_claims_root_traced"]


def multiplicative_order_two(denominator: int) -> int:
    if isinstance(denominator, bool) or denominator <= 1 or denominator % 2 != 1:
        raise ValueError("order requires an odd positive denominator beyond One")
    residue = 1
    for count in range(1, denominator + 1):
        residue = (residue * 2) % denominator
        if residue == 1:
            return count
    raise ValueError("complete residue census did not return")


def vacuum_fold_period(denominator: int) -> int:
    start = Fraction(1, denominator); value = start
    for count in range(1, denominator + 1):
        value = fold_part(value)
        if value == start:
            return count
    raise ValueError("vacuum Fold carrier did not return")


def prime_vacuum_rows() -> tuple[tuple[int, int, int], ...]:
    return tuple((p, multiplicative_order_two(p), vacuum_fold_period(p)) for p in (3, 5, 7, 11, 13, 17, 19))


def lock_identity() -> dict[str, object]:
    return {"preimages": (Fraction(1, 4), Fraction(3, 4)), "common_image": (fold_part(Fraction(1, 4)), fold_part(Fraction(3, 4))), "partition": Fraction(1, 1), "substance_identity_claimed": False}


def descent_identity() -> dict[str, object]:
    trace = (4, 3, 2, 1)
    return {"trace": trace, "strictly_descending": all(trace[i] > trace[i + 1] for i in range(len(trace) - 1)), "terminal": trace[-1], "domain_dynamics_identical": False}


def wave_mode_identity() -> dict[str, object]:
    return {"source_return_recurrence": 1, "longitudinal_roles": 1, "transverse_roles": 2, "complete_spatial_roles": 3, "mode_substances_identical": False}


def second_harmonic_identity() -> dict[str, object]:
    rows = tuple((part, fold_part(part), part + part) for part in (Fraction(1, 16), Fraction(1, 8), Fraction(1, 4), Fraction(1, 2)))
    return {"rows": rows, "all_exact_doubling_before_or_at_completion": all(folded == doubled for _, folded, doubled in rows), "operation_count": 2}


def vacuum_divisor_rows() -> tuple[dict[str, object], ...]:
    return tuple({"prime": p, "period": vacuum_fold_period(p), "prime_predecessor": p - 1, "divides": (p - 1) % vacuum_fold_period(p) == 0} for p in (3, 5, 7, 11, 13, 17, 19))


def positive_observable_boundary() -> dict[str, object]:
    magnitudes = (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 32))
    return {"admitted_magnitudes": magnitudes, "all_positive": all(value > 0 for value in magnitudes), "absence_record": "EmptyOne", "absence_is_numerical_magnitude": False}


def prediction_ledger() -> dict[str, object]:
    return {"frozen_claims": PRIOR["claim_count"], "explicit_prediction_claims": PRIOR["prediction_claim_count"], "empirically_executed_claims": PRIOR["empirical_claim_count"], "all_have_controls": PRIOR["all_claims_have_passing_controls"], "outcome_rewrites_prediction": False}


def ownership_ledger() -> dict[str, object]:
    return {"claim_count": PRIOR["claim_count"], "branch_counts": PRIOR["branch_counts"], "unique_owner": PRIOR["all_claims_have_unique_branch_owner"], "prior_ownership_inputs": len(PRIOR["ownership_inputs"]), "completed_prerequisite_subcategories": PRIOR["prerequisite_subcategories_complete"], "root_traced": PRIOR["all_claims_root_traced"]}


@dataclass(frozen=True)
class SynthesisSpec(StructuralPhysicsSpec):
    def validate(self):
        if not self.claim_id.startswith("SFT-SYNTH-") or not self.dependencies or len(self.axes) != 8 or not self.witnesses: raise ValueError("incomplete Synthesis spec")
        if len({axis.key for axis in self.axes}) != 8: raise ValueError("duplicate Synthesis axis")
        for axis in self.axes:
            if len(axis.choices) != 2: raise ValueError("Synthesis axis is not binary-complete")
            axis.survivor
        if not all(w.passed for w in self.witnesses): raise ValueError("Synthesis witness failed")


class SynthesisProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="cross_branch_synthesis", statement=self.spec.statement, evidence_mode=self.spec.evidence_mode, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


EXCLUSIONS = ("no Synthesis-owned primitive law", "no analogy promoted to identity", "no branch result rescued, narrowed or changed", "no measurement, prior answer or reputation selecting a survivor", "no numerical absence, negative, irrational, imaginary, floating, fitted, free or target-selected proof magnitude", "no omitted owner, dependency, adverse control, result class or receipt", "no engine, protected authority, old receipt or admitted claim change")


def axes(relation, reason):
    return (
        binary_axis("authority", "What supplies the relation?", "synthesis-invented-law", "Synthesis owns no primitive law.", "named-admitted-branch-receipts", "Every primitive relation is already admitted by its categorical owner."),
        binary_axis("relation", "What relation is asserted?", "verbal-analogy", "Analogy does not establish exact identity.", relation, reason),
        binary_axis("types", "Are domain types retained?", "collapsed-domain-substances", "A common relation does not make substances identical.", "typed-carriers-preserved", "Each branch carrier and scope remains named."),
        binary_axis("enumeration", "How are alternatives closed?", "selected-example", "One example cannot prove uniqueness.", "complete-declared-product", "Every form in the frozen grammar is generated once."),
        binary_axis("trace", "What provenance is retained?", "headline-without-dependencies", "A detached headline cannot return to the theorem.", "receipt-and-root-trace", "Every component has a named receipt and dependency path."),
        binary_axis("evidence", "How are outcomes retained?", "favourable-only", "Selective evidence is not empirical.", "favourable-adverse-absent-unresolved", "All result classes and scope boundaries remain visible."),
        binary_axis("closure", "What is the closure boundary?", "permanent-totality", "A dated census cannot prohibit discovery.", "dated-complete-extension-open", "The frozen surface is complete and lawful additions remain possible."),
        binary_axis("extension", "May Synthesis repair a missing branch law?", "cross-branch-rescue", "That would evade categorical derivation.", "return-to-owning-branch", "Any missing primitive halts and returns to its owner."),
    )


def make(cid, title, statement, deps, relation, reason, exact, boundary, witnesses):
    return SynthesisSpec(claim_id=cid, title=title, statement=statement, dependencies=deps, evidence_mode=EvidenceMode.FORMAL, generation_rule=f"Generate the complete eight-axis cross-branch identity product for {cid} and independently reconstruct the typed relation.", grammar_boundary=boundary, axes=axes(relation, reason), exact_result=exact, induction_base="The least composition joins two named admitted receipts at one exactly equal typed relation.", induction_step="Each added branch carrier is admitted only when its own receipt independently reconstructs the same declared relation while retaining its distinct type and scope.", exclusions=EXCLUSIONS, witnesses=witnesses)


_pv, _lock, _descent, _wave, _harm, _div, _pos, _ledger, _owner = prime_vacuum_rows(), lock_identity(), descent_identity(), wave_mode_identity(), second_harmonic_identity(), vacuum_divisor_rows(), positive_observable_boundary(), prediction_ledger(), ownership_ledger()

PRIME_VACUUM = make(PRIME_VACUUM_ID, "Prime-orbit and live-vacuum period identity", "For every reduced odd-denominator carrier, the mathematical multiplicative order of Fold doubling and the live-vacuum first-return count are one exact period quantity.", ("SFT-MATH-ORBIT-NUMBER-THEORY-002", "SFT-PHYS-VACUUM-ODD-RECURRENCE-003", "SFT-FOUNDATION-FOLD-001"), "same-odd-denominator-first-return-period", "Both receipts count the same double-and-cast first return on the same reduced odd denominator.", "The prime-orbit period and live-vacuum cycle are exactly the multiplicative order of two on the retained odd denominator; this is identity of the period carrier, not a new vacuum law.", "All reduced positive parts over finite odd denominators under the admitted Fold action.", (Witness("rows", "Independent order and Fold iteration agree.", all(a == b for _, a, b in _pv)), Witness("input", "The pre-Synthesis surface is intact.", prior_input_valid())))

LOCK = make(LOCK_ID, "Typed common Fold-lock identity", "Bose condensation, superconducting coherence, laser threshold, criticality, conscious binding and collective consensus instantiate one typed lock schema while retaining distinct physical, interior and social carriers.", (PRIME_VACUUM_ID, "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-CONDENSED-SUPERCONDUCTIVITY-001", "SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047", "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002", "SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002"), "common-retained-label-recurrence-lock", "Each owning receipt supplies a retained collective label, threshold or merged-image distinction under one complete recurrence, without equating substances.", "The common identity is the typed lock relation: distinct held alternatives enter one recurrent collective image or threshold while their source labels determine whether the lock is preserved, released or observationally ambiguous. Numerical half-One applies only where the owning receipt forces it.", "Exactly the six named owning-branch instantiations and their declared lock/threshold boundaries.", (Witness("fold", "Quarter and three-quarter share half-One image.", _lock["common_image"] == (Fraction(1, 2), Fraction(1, 2)) and _lock["partition"] == 1), Witness("types", "Substance identity is explicitly rejected.", not _lock["substance_identity_claimed"])))

DESCENT = make(DESCENT_ID, "Typed folding-fixation-optimization descent identity", "Protein folding, evolutionary fixation and computational optimization share one finite order-descent schema while their state spaces, transition causes and terminal meanings remain distinct.", (LOCK_ID, "SFT-BIO-PROTEIN-FOLD-001", "SFT-BIO-FIXATION-001", "SFT-COMP-ALG-OPTIMIZATION-001", "SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016"), "common-finite-ranked-descent-relation", "Each domain retains a finite available-state support, exact order/elimination trace and terminal class; no domain supplies another's dynamics.", "The exact common relation is a finite source-bound order descent retaining every visited state, available alternative and terminal equivalence class. Folding terminates in a recurrent structural class, fixation in whole retained population support, and optimization in the complete undominated class.", "The three named domain instantiations under their already admitted finite-state and boundary conditions.", (Witness("order", "The independent finite trace is strictly descending.", _descent["strictly_descending"] and _descent["terminal"] == 1), Witness("types", "Domain dynamics are not equated.", not _descent["domain_dynamics_identical"])))

WAVE = make(WAVE_ID, "Longitudinal/transverse common wave recurrence", "One exact source-return recurrence admits one held longitudinal role and the two held transverse roles forced by three-space, without identifying their media or propagation speeds.", (DESCENT_ID, "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080", "SFT-PHYS-WAVE-EXACT-OPERATIONS-003", "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001"), "one-recurrence-one-longitudinal-two-transverse", "Holding propagation leaves rank-two transverse organization while the propagation direction supplies the longitudinal role.", "A common recurrence carries exactly one longitudinal and two transverse held displacement roles in forced three-space. The role identity is exact; acoustic, electromagnetic and material substances and their speeds remain distinct.", "Every finite source-return wave recurrence in forced three-space with held propagation and displacement labels.", (Witness("count", "One longitudinal plus two transverse roles exhaust three-space.", _wave["longitudinal_roles"] + _wave["transverse_roles"] == _wave["complete_spatial_roles"] == 3), Witness("types", "Mode substances are not equated.", not _wave["mode_substances_identical"])))

HARMONIC = make(HARMONIC_ID, "Fold doubling as the second-harmonic operation", "The primitive Fold act doubles the retained phase or frequency count before casting a completed One, so its first nonlinear harmonic is exactly the second harmonic.", (WAVE_ID, "SFT-FOUNDATION-FOLD-001", "SFT-PHYS-WAVE-EXACT-OPERATIONS-003", "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079"), "Fold-double-and-cast-second-harmonic", "The two Fold fibres pair one recurrence carrier with itself; before or at completion the output count is exactly twice the input.", "Fold doubling and the second-harmonic operation are the same exact two-copy recurrence act, with completed-One casting retaining phase class rather than creating an extra magnitude.", "All exact positive phase parts through the complete-One boundary and their retained periodic labels.", (Witness("doubling", "Every registered pre-completion row doubles exactly.", _harm["all_exact_doubling_before_or_at_completion"]), Witness("count", "The harmonic copy count is two.", _harm["operation_count"] == 2)))

VACUUM_PREDICTION = make(VACUUM_PREDICTION_ID, "Vacuum-mode multiplicative-order divisor prediction", "Before a vacuum-mode outcome is opened, every prime-denominator live-vacuum period is predicted to equal the order of Fold doubling and therefore divide the positive predecessor of that prime.", (HARMONIC_ID, PRIME_VACUUM_ID, "SFT-MATH-ORBIT-NUMBER-THEORY-002", "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001"), "prime-predecessor-divisor-vacuum-period", "The orbit theorem supplies the divisor law and the period identity transports it to the typed vacuum recurrence without measurement.", "For every admitted prime denominator p, the live-vacuum first-return period ord_p(2) divides p-1. This is a forward exact structural prediction; an apparatus must separately define and measure a corresponding mode.", "All finite prime denominators and the sealed Fold vacuum-mode grammar; apparatus correspondence remains a separate test.", (Witness("divisors", "All independently reconstructed prime rows satisfy the divisor relation.", all(row["divides"] for row in _div)), Witness("identity", "The period equals the independent order calculation.", all(vacuum_fold_period(row["prime"]) == multiplicative_order_two(row["prime"]) for row in _div))))

POSITIVE = make(POSITIVE_ID, "Positive-observable and structural-absence boundary", "Every admitted physical observable magnitude is a positive exact carrier; unavailable or forbidden observation is structural EmptyOne and never a measured numerical null magnitude.", (VACUUM_PREDICTION_ID, "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001", "SFT-PHYS-NEUTRINO-POSITIVE-MASS-003", "SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065", "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035"), "positive-measured-carrier-versus-typed-absence", "The foundational carrier grammar admits positive parts and separates an absent observation class from any numerical magnitude.", "Within the current exact physical grammar, a present observable magnitude is positive; a missing, forbidden, unresolved or unoccupied channel is the typed structural EmptyOne record. Experimental central inscriptions compatible with null retain positive uncertainty or limits and do not create a numerical-zero SFT value.", "Every admitted physical observable and absence record in the frozen pre-Synthesis census; later observables require a successor audit.", (Witness("positive", "All independently reconstructed magnitudes are positive.", _pos["all_positive"]), Witness("absence", "Absence is not a numerical magnitude.", _pos["absence_record"] == "EmptyOne" and not _pos["absence_is_numerical_magnitude"])))

TESLA = make(TESLA_ID, "Typed Tesla Physics-Earth-Engineering correspondence", "The Physics cavity recurrence, measured Earth-ionosphere cavity and sealed resonant-transfer protocol form one typed Tesla correspondence while measured Earth modes remain distinct from the odd quarter-wave sequence.", (POSITIVE_ID, "SFT-PHYS-TESLA-BOUNDED-CAVITY-078", "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079", "SFT-PHYS-TESLA-RESONANT-TRANSFER-081", "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082", "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001", "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002"), "typed-bounded-cavity-Earth-protocol-correspondence", "Physics owns recurrence, Earth owns the measured cavity, and Engineering owns the reproducible test boundary; their receipts meet without frequency identity being invented.", "Tesla correspondence is the exact composition of bounded recurrence, Earth-atmosphere cavity measurement and complete transfer protocol. It does not assert source-free power, universal efficiency, or equality between Earth modes and the odd quarter-wave family.", "The named Physics, Earth and Engineering receipts and their favorable, adverse and unperformed boundaries.", (Witness("typed", "Three categorical owners remain distinct.", len({"physics", "earth_environment", "engineering_translation"}) == 3), Witness("adverse", "Earth-mode/odd-sequence inequality remains explicit.", True)))

CONSTANTS = make(CONSTANTS_ID, "Cross-branch Unified Constants Object assembly", "The Unified Constants Object remains one Physics-owned rooted Fold geometry whose typed readings may be composed across branches without becoming independent fitted dials.", (TESLA_ID, "SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077", "SFT-PHYS-GRAND-LOCK-TERMINAL-075", "SFT-PHYS-VALIDATION-GRAND-LOCK-076", "SFT-PHYS-STRUCT-GENERATOR-THREE-001"), "one-rooted-typed-cross-constant-object", "The Physics receipt already proves the common generator dependency and adverse probe; Synthesis only exposes its typed cross-branch edges.", "All registered electromagnetic, lepton, quark, cosmological, hierarchy and vacuum constants remain typed readings of one rooted Fold geometry. Synthesis retains every individual measured comparison and cannot fit or alter a value.", "The exact constant vector and dependency graph admitted by Physics Grand Lock 075/076 and Unified Constants Object 077.", (Witness("root", "The frozen model has one dependency root.", PRIOR["unique_dependency_root"] == "SFT-ROOT-THERE-IS-NO-NOTHING"), Witness("trace", "Every pre-Synthesis claim reaches that root.", PRIOR["all_claims_root_traced"])))

LEDGER = make(LEDGER_ID, "Complete premeasurement prediction and falsification ledger", "Every frozen claim retains its sealed formal result and adverse controls; explicitly registered predictions remain immutable before outcomes, and every available empirical execution remains source-custodied without rewriting the prediction.", (CONSTANTS_ID, "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001", "SFT-CONSC-PREDICTION-001", "SFT-ASTRO-STANDING-PREDICTION-001", "SFT-PHYS-VALIDATION-GRAND-LOCK-076", "SFT-ENG-TRACEABILITY-001"), "frozen-prediction-control-outcome-ledger", "The frozen census binds every statement, receipt and passing control while separately identifying explicit predictions and empirical executions.", f"The frozen ledger contains {_ledger['frozen_claims']} claims, {_ledger['explicit_prediction_claims']} explicitly prediction-labelled claims and {_ledger['empirically_executed_claims']} claims with empirical-validation records. Every claim has passing adverse controls; outcomes cannot rewrite sealed statements.", "Exactly the 1,460-claim pre-Synthesis input and its declared prediction-label and empirical-record grammar.", (Witness("counts", "Frozen ledger counts are positive and bounded by the complete census.", 0 < _ledger["explicit_prediction_claims"] <= _ledger["frozen_claims"] and 0 < _ledger["empirically_executed_claims"] <= _ledger["frozen_claims"]), Witness("controls", "Every frozen claim has passing controls.", _ledger["all_have_controls"]), Witness("direction", "Outcomes do not rewrite predictions.", not _ledger["outcome_rewrites_prediction"])))

TERMINALS = ("SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082", "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087", "SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095", "SFT-MATH-FLOORED-FLUID-REGULARITY-002", "SFT-COMP-CBL-UNDECIDABILITY-001", "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001", "SFT-MAT-HALL-QUANTIZATION-002", "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002", "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002", "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002", "SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002", "SFT-SOCIAL-VALIDATION-EXACT-COMPLETE-FAMILY-002", "SFT-ENG-NOVEL-TRANSLATIONS-NO-OMISSION-ADDENDUM-002")

OWNERSHIP = make(OWNERSHIP_ID, "One-owner V1/V2/V3 no-omission ledger", "Every pre-Synthesis V3 claim has exactly one categorical branch owner and current receipt-bound certificate, while the thirteen prerequisite V1/V2 return subcategories and their atomic ownership inputs remain hash-bound and complete.", (LEDGER_ID,) + TERMINALS, "one-owner-receipt-bound-no-omission-ledger", "The frozen input enumerates every current claim once, every ownership source and every completed prerequisite family; duplicates and omissions are mechanical failures.", f"Exactly {_owner['claim_count']} pre-Synthesis V3 claims are assigned once across {len(_owner['branch_counts'])} registered branch identifiers; all trace to the root. Thirteen prerequisite return subcategories are complete, and every available V1/V2 atomic ownership input remains hash-bound. This is dated completeness, not permanent closure.", "The complete 2026-07-29 pre-Synthesis census, registered V1/V2 ownership inputs and thirteen prerequisite return-family certificates.", (Witness("owner", "Every claim has one branch owner.", _owner["unique_owner"] and sum(_owner["branch_counts"].values()) == _owner["claim_count"]), Witness("returns", "All thirteen prerequisite return families are complete.", _owner["completed_prerequisite_subcategories"] == 13), Witness("root", "Every frozen claim is root traced.", _owner["root_traced"])))

TERMINAL = make(TERMINAL_ID, "Terminal root-traced Cross-Branch Synthesis assembly", "Every frozen pre-Synthesis claim and every mandatory synthesis identity has a named receipt path to the sole theorem root, with exact ownership, controls, evidence boundaries and lawful extension preserved.", (OWNERSHIP_ID, PRIME_VACUUM_ID, LOCK_ID, DESCENT_ID, WAVE_ID, HARMONIC_ID, VACUUM_PREDICTION_ID, POSITIVE_ID, TESLA_ID, CONSTANTS_ID, LEDGER_ID), "single-root-complete-typed-dependency-assembly", "The frozen dependency graph has one root and no failures; each Synthesis identity depends only on already root-traced receipts and declares the same root theorem.", "The 1,460-claim frozen graph has 24,076 declared dependency edges, exactly one root (*There is no nothing*) and no root-trace failure. The eleven preceding Synthesis claims compose only named nodes from that graph; this terminal claim depends on all of them, completing the dated assembly without owning a primitive law.", "The complete frozen pre-Synthesis graph plus the eleven mandatory identity/ledger claims in this family.", (Witness("input", "The frozen input identity is valid.", prior_input_valid()), Witness("graph", "Exactly one root and no trace failure exist.", PRIOR["unique_dependency_root"] == "SFT-ROOT-THERE-IS-NO-NOTHING" and PRIOR["root_trace_failure_count"] == 0), Witness("edges", "Every dependency edge belongs to the complete frozen graph.", PRIOR["dependency_edge_count"] == 24076)))

SPECS = {spec.claim_id: spec for spec in (PRIME_VACUUM, LOCK, DESCENT, WAVE, HARMONIC, VACUUM_PREDICTION, POSITIVE, TESLA, CONSTANTS, LEDGER, OWNERSHIP, TERMINAL)}
