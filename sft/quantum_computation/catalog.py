"""Frozen dependency-ordered catalog for Reversible and Quantum Computation."""

from __future__ import annotations

from dataclasses import dataclass

from sft.quantum_computation.generated_law import LawSpec, Witness, binary_dimension
from sft.quantum_computation.operations import operational_witnesses


@dataclass(frozen=True)
class Topic:
    slug: str
    title: str
    subject: str
    components: str
    limitations: str
    correspondence: tuple[str, ...]


def T(slug: str, title: str, subject: str, components: str, limitations: str, *terms: str) -> Topic:
    return Topic(slug, title, subject, components, limitations, tuple(terms))


TOPICS = (
    T("REVERSIBLE-MODEL", "Complete Fold reversible-computation model", "reversible computation", "canonical configurations; bijective transition rows; retained held labels; exact inverse traces; universal reversible interpretation; complete resource ledger", "This theorem is formal and does not assign thermodynamic energy without a later physical measurement law.", "reversible computation", "Bennett machine"),
    T("INFORMATION-UNIT", "Fold quantum information-unit law", "quantum information units", "one Fold distinction; two held fibre labels; complete word support; exact observation classes; retained phase-label carrier", "The unit is structural support, not an imported complex vector or conventional qubit.", "qubit", "quantum information unit"),
    T("STATE-COMPOSITION", "Fold quantum state-composition law", "quantum state composition", "complete branch support; exact pair-cell joint words; component identities; phase-label composition; marginal reconstruction; product and correlated classes", "Only finite generated joint supports are admitted.", "tensor product", "composite state"),
    T("SUPERPOSITION", "Superposition-equivalent Fold support law", "superposition-equivalent structure", "complete b^k Fold-word support; one record per branch; held phase label per branch; no selected actual branch before observation; exact support provenance", "No amplitude magnitude, normalization constant or stochastic ontology is imported.", "superposition", "basis support"),
    T("PHASE-INTERFERENCE", "Fold phase and interference operation law", "phase and interference", "period-b held phase cycle; reversible phase action; total branch-to-image relation; complete predecessor fibres; same-image merge ledger; retained phase provenance", "Interference is exact predecessor merging with phase labels; no complex exponential is assumed.", "phase", "interference"),
    T("ENTANGLEMENT", "Fold entangling-composition law", "entanglement", "joint word support; exact marginals; product-support test; nonfactorable pair-cell classes; retained component observations; compositional trace", "Entanglement is structural nonfactorability of registered joint support, not a metaphysical postulate.", "entanglement", "nonseparable state"),
    T("MEASUREMENT", "Fold quantum measurement-semantics law", "measurement", "total observation relation; retained observation class; closed branch distinctions; complete pre-observation record; selected-class state; exact reconstruction boundary", "No stochastic collapse postulate is imported; outcome frequencies require external empirical evidence.", "quantum measurement", "collapse"),
    T("GATE", "Fold reversible transformation and gate law", "quantum transformations and gates", "bijective branch-word map; period-held phase action; complete domain and image support; exact inverse; source-bound gate identity; composition interface", "Physical gate fidelity remains an empirical engineering question.", "quantum gate", "unitary transformation"),
    T("CIRCUIT", "Fold quantum circuit syntax and semantics law", "quantum circuits", "generated wires; information units; reversible gates; causal circuit order; complete branchwise evaluation; inverse circuit; observation boundary; resource ledger", "This derives circuit semantics; hardware timing and noise are external.", "quantum circuit", "circuit semantics"),
    T("UNIVERSALITY", "Fold quantum universality law", "quantum universal computation", "frozen gate-description grammar; exact encoded circuits; one interpreter; branchwise trace simulation; phase and observation preservation; overhead ledger", "Universality is exact for every generated description in the frozen grammar.", "universal quantum computer", "universal gate set"),
    T("ALGORITHMS", "Fold quantum algorithm-family law", "quantum algorithms", "complete input support; reversible branch generation; phase action; interference merge; observation decoder; correctness trace per branch; classical comparison boundary", "Named speedups require their own exact problem family and resource proof.", "quantum algorithm", "quantum speedup"),
    T("COMPLEXITY", "Fold quantum complexity law", "quantum computational resources", "canonical input size; gate count; causal depth; live branch support; query and communication rows; measurement records; lower and upper witness boundary", "No arbitrary separation between conventional complexity classes is claimed without a separate certificate.", "quantum complexity", "BQP"),
    T("COMMUNICATION", "Fold quantum communication law", "quantum communication", "sender and receiver supports; joint state composition; local transformations; channel relation; retained correlations; observation records; resource and loss ledger", "Physical transmission capacity and security require registered media experiments.", "quantum communication", "teleportation"),
    T("CODING", "Fold quantum coding law", "quantum coding", "logical branch support; redundant joint words; reversible encoder; declared error actions; disjoint syndrome supports; decoder and reconstruction trace", "The code theorem applies only to the registered generated error family.", "quantum code", "encoding"),
    T("ERROR-CORRECTION", "Fold quantum error-correction law", "quantum error correction", "forced repetition width 2t+1; exact fault-depth trace; all error masks through t; majority held-label decoder; syndrome ledger; recovery certificate", "The completed census covers generated fault depths one, two and three and the successor law for every positive finite t.", "quantum error correction", "repetition code"),
    T("FAULT-TOLERANCE", "Fold quantum fault-tolerance law", "fault-tolerant quantum computation", "encoded logical support; declared component faults; transversal or contained transformations; recovery after each location; malignant-fault boundary; induction over circuit locations", "No hardware threshold constant is claimed; unlimited thresholds remain dependent on a separately derived physical fault model.", "fault tolerance", "threshold theorem"),
    T("SIMULATION", "Fold quantum simulation law", "quantum simulation", "encoded target state support; reversible update law; phase and interference traces; observation map; exact simulator correspondence; resource ledger; falsification boundary", "A simulator derives consequences of its registered model and cannot establish a natural quantum law by itself.", "quantum simulation", "Hamiltonian simulation"),
    T("VERIFICATION", "Fold quantum verification law", "quantum verification", "claim and witness supports; verifier circuit; challenge schedule; branchwise acceptance; soundness and completeness ledgers; measurement records; tamper controls", "Security and correctness are exact only for the registered prover and resource grammar.", "quantum verification", "QMA"),
    T("LEARNING", "Fold quantum learning law", "quantum learning", "classical or joint example support; reversible hypothesis process; phase/interference search; observation decoder; retained alternatives; sample and gate resources; sealed evaluation", "No pretrained quantum model, fitted amplitude or unexplained speedup is admitted.", "quantum learning", "quantum machine learning"),
    T("CLASSICAL-CORRESPONDENCE", "Full operational classical-quantum correspondence law", "classical and quantum operational correspondence", "common generated descriptions; embedding of classical states; reversible classical submodel; branchwise quantum execution; measurement decoder; bidirectional result preservation; overhead ledger", "Correspondence does not identify the models where phase-sensitive joint support changes the operational trace.", "classical-quantum correspondence", "deferred measurement"),
    T("LIMITS", "Limits of Fold quantum computation law", "limits of quantum computation", "classical computability dependency; finite description grammar; exact quantum execution; self-description support; halting and undecidability transfer; resource and observation boundaries; no hypercomputational oracle", "Quantum computation does not escape the admitted computability and self-reference boundaries; physical claims remain empirical.", "limits of quantum computing", "quantum computability"),
)


BASE_DEPENDENCIES = (
    "SFT-COMP-SCI-MATHEMATICAL-MODELLING-001",
    "SFT-COMP-FORM-CIRCUIT-001",
    "SFT-COMP-FORM-UNIVERSALITY-001",
    "SFT-COMP-CPLX-REVERSIBILITY-COST-001",
    "SFT-COMP-SEC-POST-QUANTUM-BOUNDARY-001",
    "SFT-COMP-LEARN-CLASSICAL-LEARNING-001",
    "SFT-INFO-QUANTUM-CORRESPONDENCE-001",
)


DIMENSIONS = (
    binary_dimension("support", "partial-or-selected-branch-support", "complete-generated-branch-support"),
    binary_dimension("unit", "imported-bit-or-qubit", "one-Fold-distinction-unit"),
    binary_dimension("composition", "sampled-joint-states", "complete-pair-cell-joint-support"),
    binary_dimension("phase", "complex-amplitude-postulate", "period-held-phase-action"),
    binary_dimension("transformation", "partial-or-irreversible-map", "total-reversible-source-bound-map"),
    binary_dimension("observation", "collapse-without-record", "retained-class-and-complete-record"),
    binary_dimension("generality", "fixed-circuit-examples", "branch-and-depth-successor-certificate"),
    binary_dimension("addition", "imported-quantum-model", "no-extra-quantum-premise"),
)


def build_specs() -> tuple[LawSpec, ...]:
    specs = []
    previous = None
    for topic in TOPICS:
        current = f"SFT-QUANTUM-{topic.slug}-001"
        dependencies = BASE_DEPENDENCIES if previous is None else (previous, *BASE_DEPENDENCIES)
        result = (
            f"The forced {topic.subject} kernel retains {topic.components}; branch support, phase, transformation, "
            "observation, composition and resources remain exact, finite, source-bound and free of imported amplitudes or postulates."
        )
        specs.append(LawSpec(
            claim_id=current,
            slug=topic.slug,
            title=topic.title,
            statement=result,
            dependencies=dependencies,
            generation_rule=f"Generate the literal product of eight registered Fold-quantum structural axes for {topic.subject}.",
            grammar_boundary=f"All finite {topic.subject} structures generated from admitted Fold words, distinction ledgers, classical computation and exact held phase labels. {topic.limitations}",
            dimensions=DIMENSIONS,
            exact_result=result,
            laws=(
                f"Support law: {topic.components}.",
                "Phase law: period-held label actions transform branch provenance without imaginary or irrational proof values.",
                "Reversibility law: transformations are total bijections or retain the exact predecessor label needed for inversion.",
                "Observation law: selected support and every closed distinction remain reconstructible from the measurement record.",
                "Composition law: joint pair-cell words preserve component identity and explicitly classify factorable and nonfactorable support.",
            ),
            induction_base=f"One Fold distinction supplies the minimal two-label support and one exact {topic.subject} record.",
            induction_step=f"Adding one generated branch, component, fault position or circuit location appends all new joint cells, phase rows, transformations and observation distinctions while retaining prior records.",
            boundary_exclusions=(
                "no numerical zero, negative, irrational, imaginary or floating proof quantity",
                "no complex amplitude, Hilbert-space axiom or stochastic collapse postulate",
                "no completed infinity or ungenerated continuum",
                "no free, fitted, learned or hardware parameter",
                "no application output or physical measurement may select the law",
                topic.limitations,
            ),
            witnesses=tuple(Witness(*row) for row in operational_witnesses(current)),
            why=f"{topic.title} must be forced from admitted Fold and computation laws before conventional quantum models may be compared.",
            derivation=f"Complete Fold-word support, exact information ledgers, reversible classical processes and pair-cell composition force the registered kernel: {topic.components}.",
            check="Execute all 256 structural candidates, decide every member, verify the sole survivor, replay eight quantum operational witnesses, exhaust fault masks at widths three, five and seven, run four controls and independently regenerate the product.",
            limitations=topic.limitations,
            correspondence_terms=topic.correspondence,
        ))
        previous = current
    return tuple(specs)


SPECS = build_specs()
SPEC_BY_ID = {spec.claim_id: spec for spec in SPECS}


def validate_catalog() -> None:
    if len(SPECS) != 21 or len(SPEC_BY_ID) != 21:
        raise ValueError("the quantum catalog must contain exactly 21 unique obligations")
    available = set(BASE_DEPENDENCIES)
    for spec in SPECS:
        spec.validate()
        missing = tuple(dep for dep in spec.dependencies if dep not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()

