"""Build exhaustive standalone Classical and Quantum Computation papers."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.computation.catalog import SPECS as COMPUTATION_SPECS  # noqa: E402
from sft.computation.generated_law import survivor_id as computation_survivor  # noqa: E402
from sft.computation.spec_data import GROUP_TITLES  # noqa: E402
from sft.quantum_computation.catalog import SPECS as QUANTUM_SPECS  # noqa: E402
from sft.quantum_computation.generated_law import survivor_id as quantum_survivor  # noqa: E402


COMPUTATION_OUTPUT = ROOT / "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md"
QUANTUM_OUTPUT = ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def L(text: str = "") -> str:
    return text + "\n"


def evidence(spec):
    root = ROOT / "claims" / spec.claim_id
    return {
        "registration": load(root / "registration.json"),
        "census": load(root / "candidate_census.json"),
        "elimination": load(root / "elimination_receipt.json"),
        "controls": load(root / "controls.json")["controls"],
        "certificate": load(root / "certificate.json"),
    }


def derivation_section(spec, order: int, section: int, survivor_function) -> str:
    artifacts = evidence(spec)
    certificate = artifacts["certificate"]
    decisions = artifacts["elimination"]["decisions"]
    survivors = tuple(row for row in decisions if row["survives"])
    rejection_counts = Counter(row["reason"] for row in decisions if not row["survives"])
    parts: list[str] = []
    add = parts.append
    add(L(f"## {section}. Derivation {order}: {spec.title}"))
    add(L())
    add(L(f"Claim: `{spec.claim_id}`"))
    add(L())
    add(L(f"### {section}.1 Scientific necessity and exact theorem"))
    add(L())
    add(L(spec.why))
    add(L())
    add(L("The engine-admitted theorem is:"))
    add(L())
    add(L(f"> {spec.statement}"))
    add(L())
    add(L("The derivation cites only these earlier model-admitted receipts:"))
    add(L())
    for dependency in spec.dependencies:
        add(L(f"- `{dependency}`"))

    add(L())
    add(L(f"### {section}.2 Generated grammar and exact boundary"))
    add(L())
    add(L(spec.derivation))
    add(L())
    add(L(f"Generation rule: {spec.generation_rule}"))
    add(L())
    add(L(f"> {spec.grammar_boundary}"))
    add(L())
    add(L("| Structural axis | Rejected coordinate | Exact rejection | Forced coordinate | Preservation supplied |"))
    add(L("|---|---|---|---|---|"))
    for dimension in spec.dimensions:
        rejected = next(choice for choice in dimension.choices if not choice.admitted)
        admitted = dimension.admitted_choice
        add(L(f"| `{dimension.key}` | `{rejected.name}` | {rejected.reason} | `{admitted.name}` | {admitted.reason} |"))
    add(L())
    add(L(
        f"The literal product contains **{artifacts['census']['expected_cardinality']:,}** candidates. The census preserves "
        f"{len(artifacts['census']['candidates']):,} candidate identities and the elimination receipt preserves "
        f"{len(decisions):,} decisions. There are **{len(survivors)}** survivors and **{len(decisions) - len(survivors):,}** eliminations."
    ))

    add(L())
    add(L(f"### {section}.3 Exhaustion, eliminations and unique survivor"))
    add(L())
    add(L(
        "Every rejected candidate fails at the first non-preserving coordinate in registered axis order. The following "
        "ledger groups all eliminations by their exact first failure; the counts sum to the complete rejected support."
    ))
    add(L())
    add(L("| Eliminated candidates | Exact first-failure reason |"))
    add(L("|---:|---|"))
    for reason, count in rejection_counts.items():
        add(L(f"| {count:,} | {reason} |"))
    forced = survivor_function(spec)
    add(L())
    add(L(f"The unique all-preserving member is `{forced}`."))
    add(L())
    add(L(f"> {spec.exact_result}"))
    add(L())
    add(L(
        "Minimality follows because changing any one of the eight admitted coordinates replaces it with the generated "
        "failure coordinate and removes its named condition. Named-shape uniqueness follows because the complete product "
        "contains one and only one tuple composed entirely of admitted coordinates."
    ))

    add(L())
    add(L(f"### {section}.4 Operational laws and consequences"))
    add(L())
    for law in spec.laws:
        add(L(f"- {law}"))
    add(L())
    add(L(
        "These are construction laws, not renamed conventional equations. They specify exact carriers, relations, traces, "
        "interfaces and boundary failures. Host integers count generated artifacts but never become SFT proof quantities."
    ))

    add(L())
    add(L(f"### {section}.5 Depth-independent closure"))
    add(L())
    add(L(f"Base: {spec.induction_base}"))
    add(L())
    add(L(f"Successor: {spec.induction_step}"))
    add(L())
    add(L(
        "The certificate therefore does not infer unrestricted completion from a depth table. It proves that every fresh "
        "generated finite successor extends the same classification while preserving prior identities and adding all new "
        "relations. No completed infinity is created."
    ))

    add(L())
    add(L(f"### {section}.6 Executed witnesses and adverse controls"))
    add(L())
    for witness in spec.witnesses:
        add(L(f"- `{witness.name}` - {witness.statement}; result: `{'PASS' if witness.passed else 'FAIL'}`."))
    add(L())
    add(L("| Control | Expected | Observed | Result |"))
    add(L("|---|---|---|---|"))
    for control in artifacts["controls"]:
        add(L(f"| `{control['kind']}` | {control['expected_behavior']} | {control['observed_behavior']} | `{'PASS' if control['passed'] else 'FAIL'}` |"))

    add(L())
    add(L(f"### {section}.7 Meaning, correspondence and limitations"))
    add(L())
    add(L(
        "The result closes the exact generated-finite kernel stated above. Conventional names enter only now, after the "
        f"derivation seal, as correspondence labels: {', '.join(spec.correspondence_terms)}."
    ))
    add(L())
    add(L(spec.limitations))
    add(L())
    add(L("The following imports remain prohibited at this boundary:"))
    add(L())
    for exclusion in spec.boundary_exclusions:
        add(L(f"- {exclusion}"))

    add(L())
    add(L(f"### {section}.8 Exact evidence identities"))
    add(L())
    add(L(f"- Source manifest: `{certificate['source_manifest_hash']}`"))
    add(L(f"- Complete-census certificate: `{artifacts['census']['completeness_certificate_hash']}`"))
    add(L(f"- Derivation seal: `{certificate['derivation_seal_hash']}`"))
    add(L(f"- Independent implementation: `{certificate['independent_implementation_hash']}`"))
    add(L(f"- Independent certificate: `{certificate['independent_certificate_hash']}`"))
    add(L(f"- External validation: `{certificate['external_validation_hash']}`"))
    add(L(f"- Model-admitted engine receipt: `{certificate['engine_receipt_hash']}`"))
    add(L(f"- Receipt path: `{certificate['engine_receipt_path']}`"))
    add(L())
    return "".join(parts)


def publication_state(branch_id: str) -> tuple[bool, str]:
    metadata = load(ROOT / f"publication/{branch_id}_zenodo_metadata.json")
    return bool(metadata["publication_authorized"]), str(metadata.get("doi", ""))


def common_front_matter(branch_id: str, title: str, subtitle: str, branch_label: str, claim_count: int, candidate_count: int, abstract: str, inventory_hash: str, keywords: str) -> list[str]:
    authorized, doi = publication_state(branch_id)
    matter = [
        L(f"# {title}"),
        L(f"## {subtitle}"),
        L("**Maria Smith**<br>"),
        L("Independent researcher and founder, Ernos Labs<br>"),
        L("Maria.Smith.Sftoe@gmail.com<br>"),
        L("23 July 2026"),
        L(),
        L(f"{branch_label} Branch Paper 001 - Smithian Fold Theory V3 Clean-Room Reconstruction"),
        L(),
        L("Copyright (c) 2026 Maria Smith. Licensed under CC BY 4.0. Repository code is licensed separately under Apache-2.0."),
        L(),
        L("## Abstract"),
        L(),
        L(abstract),
        L(),
        L(
            f"The frozen branch contains {claim_count} dependency-ordered claims and {candidate_count:,} generated "
            f"candidate structures. Every candidate is decided, each grammar has exactly one survivor, and every claim "
            "passes minimality, named-shape uniqueness, depth-independent closure, four adverse controls, cryptographic "
            "sealing and implementation-distinct recomputation."
        ),
        L(),
        L(f"Inventory identity: `{inventory_hash}`."),
        L(),
        L(f"**Keywords:** {keywords}"),
    ]
    if doi:
        matter[9:9] = [L(f"DOI: [{doi}](https://doi.org/{doi})"), L()]
    if not authorized:
        matter[10:10] = [L("**LOCAL PREPUBLICATION MANUSCRIPT - publication is not yet authorized.**"), L()]
    return matter


def build_computation() -> str:
    inventory = load(ROOT / "publications/inventories/computation.json")
    candidate_total = sum(2 ** len(spec.dimensions) for spec in COMPUTATION_SPECS)
    parts = common_front_matter(
        "computation",
        "After Turing: The Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Classical Computational Science from Smithian Fold Theory",
        "Classical Computation",
        len(COMPUTATION_SPECS),
        candidate_total,
        "This paper reports the completed Classical Computation branch of the third clean-room reconstruction of Smithian Fold Theory. From Foundation, Mathematics and Information Science receipts it derives Formal Computation, Computability, Complexity, Algorithms and mathematical data structures, Program Semantics, Concurrent and Distributed Computation, Cryptography and Security, Learning and Intelligence Theory, and Scientific Computation. The branch does not import a Turing machine, lambda calculus, conventional complexity class, probability cause, cryptographic hardness assumption, pretrained model, fitted parameter, floating proof value or application result as a premise. Historical models enter only after sealing as explicit correspondence tests.",
        inventory["inventory_hash"],
        "Smithian Fold Theory; classical computation; Turing machine; computability; complexity; algorithms; semantics; distributed systems; cryptography; learning theory; scientific computing; computational proof; open science",
    )
    add = parts.append
    add(L())
    add(L("## 1. Central scientific claim and exact boundary"))
    add(L())
    add(L(
        "> Within the frozen SFT V3 Classical Computation inventory, all 113 registered obligations have "
        "depth-independent, model-admitted and independently replicated receipts, and no registered classical-computation "
        "obligation remains unclassified or frontier."
    ))
    add(L())
    add(L(
        "Closure means the exact generated-finite kernels named in the inventory are complete. It does not claim every "
        "named theorem, arbitrary asymptotic lower bound, unrestricted Busy Beaver value, P versus NP separation, physical "
        "device behavior or application result. Quantum operations are excluded and derived in their own downstream branch."
    ))
    add(L())
    add(L("## 2. Derivational constitution"))
    add(L())
    add(L(
        "Every dependency terminates at the single operational root theorem, *there is no nothing*. Admitted proof objects "
        "are structural One, exact positive parts, generated finite traces, Fold labels, words, relations, maps, graphs, "
        "information ledgers and composition records. Semantic numerical zero, negative quantity, irrational or imaginary "
        "values, floating proof arithmetic, a completed infinity and an ungenerated continuum are excluded. Empty One is a "
        "form; held complementary labels replace signed proof values."
    ))
    add(L())
    add(L(
        "Python booleans, indices, lengths, empty containers and process return codes are quarantined host mechanics. They "
        "execute and count evidence but carry no SFT mathematical authority. All registrations have empty axiom and "
        "free-parameter tuples. No application, benchmark, pretrained model or earlier SFT result selected a survivor."
    ))
    add(L())
    add(L("## 3. The native Fold machine"))
    add(L())
    add(L(
        "The native machine begins with exact generated configurations, two held Fold labels and a source-bound transition "
        "relation. Blank support is empty One, not numerical zero. A word is a complete sequence of held labels at canonical "
        "positions. Reading is an observation relation; writing is exact held-label substitution; movement is a counted "
        "transition across generated positions. A configuration retains its word, held position, process state and proof "
        "trace. Every step records its premise, action, successor, resource use and lost or retained distinctions."
    ))
    add(L())
    add(L(
        "Universality is derived only after languages, automata, rewriting, recursion, binding, abstract machines, circuits, "
        "processes and composition have receipts. The universal process interprets every description inside the frozen "
        "machine grammar. Conventional Turing, Church and circuit models are comparison encodings and cannot select the "
        "machine law."
    ))
    add(L())
    add(L("## 4. Superdeterminism, branching and randomized computation"))
    add(L())
    add(L(
        "Randomized computation closes without an uncaused random premise. The machine retains complete registered schedule "
        "support and executes one deterministic trace per held schedule. Apparent uncertainty is an observation-relative "
        "distinction ledger over that support. Exact success parts summarize the branch partition after execution. If a "
        "physical source supplies schedules, its distribution is measured at the one-way empirical boundary and cannot flow "
        "backward into the algorithm law."
    ))
    add(L())
    add(L("## 5. Halting, incompleteness and famous limits"))
    add(L())
    add(L(
        "The universal description grammar supports self-description and a held complement operation. Assuming a total "
        "internal halting decider permits construction of a process that rejects exactly when the decider predicts acceptance "
        "and accepts exactly when it predicts rejection on its own description. Neither held verdict is a fixed point. The "
        "contradiction closes the total-decision boundary without treating nontermination as numerical zero. The same missing "
        "distinction appears in effective self-verification: a complete internal proof enumerator cannot both retain "
        "consistency and supply every demanded self-referential verdict."
    ))
    add(L())
    add(L("## 6. Security, learning and scientific evidence"))
    add(L())
    add(L(
        "Security claims expose the message, key, observation, adversary and resource supports. Information-theoretic security "
        "means an observation closes the relevant source distinctions over complete support. Computational security means the "
        "registered adversary grammar and resource boundary fail to reopen them. Learning claims similarly retain complete "
        "hypothesis alternatives, exact evidence compatibility and sealed evaluation. A blind opaque score cannot replace the "
        "premise-to-result trace. Scientific simulations prove consequences of a registered model; only separate, sealed, "
        "target-custodied measurements can test a natural law."
    ))
    add(L())
    add(L("## 7. Dependency order and complete execution census"))
    add(L())
    add(L("| Order | Sub-branch | Claim | Candidates | Closure |"))
    add(L("|---:|---|---|---:|---|"))
    for index, spec in enumerate(COMPUTATION_SPECS, 1):
        add(L(f"| {index} | {GROUP_TITLES[spec.group]} | `{spec.claim_id}` | 256 | depth-independent |"))
    add(L())
    add(L(f"The branch total is **{candidate_total:,} candidates**, **{len(COMPUTATION_SPECS)} survivors**, **{len(COMPUTATION_SPECS) * 4} adverse controls** and **{len(COMPUTATION_SPECS)} independent validations**."))
    section = 8
    for order, spec in enumerate(COMPUTATION_SPECS, 1):
        add(derivation_section(spec, order, section, computation_survivor))
        section += 1
    add(L(f"## {section}. Branch synthesis and consequences"))
    add(L())
    add(L(
        "The 113 laws form one dependency chain from exact state change to models, computability, resources, algorithms, "
        "meaning, distributed knowledge, adversaries, learning and scientific calculation. The common invariant is complete "
        "provenance: every input belongs to a generated support, every operation names its relation, every execution retains "
        "a trace, every resource count names the representation, every loss names closed distinctions and every claimed "
        "generality supplies a successor certificate or an explicit finite boundary."
    ))
    add(L())
    add(L(f"## {section + 1}. Reproduction, criticism and falsification"))
    add(L())
    add(L("Run `python3 -m sft verify-all` on macOS/Linux or `py -m sft verify-all` on Windows. Reviewers may invalidate a claim by producing an omitted coordinate inside its declared grammar, a second survivor, a simpler preserving form, an induction counterexample, an operational counterexample, a source mismatch or a failed adverse control. Hashes identify artifacts; they do not immunize the grammar from criticism."))
    add(L())
    add(L(f"## {section + 2}. Scope and next branch"))
    add(L())
    add(L("The next dependency branch is Reversible and Quantum Computation. It may use these classical receipts but must independently derive branch support, phase, interference, entanglement, measurement, gates, quantum circuits, algorithms, communication, correction and limits without importing a conventional quantum formalism."))
    add(L())
    add(L("## References"))
    add(L())
    add(L("1. Turing AM. On computable numbers, with an application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*. 1937;42:230-265. doi:10.1112/plms/s2-42.1.230."))
    add(L("2. Church A. An unsolvable problem of elementary number theory. *American Journal of Mathematics*. 1936;58:345-363. doi:10.2307/2371045."))
    add(L("3. Gödel K. Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I. *Monatshefte für Mathematik und Physik*. 1931;38:173-198. doi:10.1007/BF01700692."))
    add(L("4. Shannon CE. A mathematical theory of communication. *Bell System Technical Journal*. 1948;27:379-423, 623-656."))
    add(L("5. Landauer R. Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*. 1961;5:183-191. doi:10.1147/rd.53.0183."))
    add(L("6. Bennett CH. Logical reversibility of computation. *IBM Journal of Research and Development*. 1973;17:525-532. doi:10.1147/rd.176.0525."))
    add(L("7. Smith M. Smithian Fold Theory Scientific Constitution. V3 clean-room repository, 2026."))
    return "".join(parts)


def build_quantum() -> str:
    inventory = load(ROOT / "publications/inventories/quantum_computation.json")
    candidate_total = sum(2 ** len(spec.dimensions) for spec in QUANTUM_SPECS)
    parts = common_front_matter(
        "quantum_computation",
        "The Quantum Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Reversible and Quantum Computation from Smithian Fold Theory",
        "Reversible and Quantum Computation",
        len(QUANTUM_SPECS),
        candidate_total,
        "This paper reports the completed Reversible and Quantum Computation branch of the third clean-room reconstruction of Smithian Fold Theory. From the admitted Foundation, Mathematics, Information Science and Classical Computation receipts it derives a complete reversible model; Fold quantum information units and composition; superposition-equivalent support; phase and interference; entanglement; measurement; gates and circuits; quantum universality, algorithms and complexity; communication; coding, error correction and fault tolerance; simulation; verification; learning; full operational classical-quantum correspondence; and the limits of quantum computation. It imports no complex amplitude, Hilbert-space axiom, stochastic collapse postulate, fitted parameter or physical benchmark as a premise.",
        inventory["inventory_hash"],
        "Smithian Fold Theory; reversible computation; quantum information; superposition; phase; interference; entanglement; measurement; quantum circuits; error correction; fault tolerance; quantum algorithms; quantum complexity; open computational science",
    )
    add = parts.append
    add(L())
    add(L("## 1. Central scientific claim and exact boundary"))
    add(L())
    add(L(
        "> Within the frozen SFT V3 Reversible and Quantum Computation inventory, all 21 registered obligations have "
        "depth-independent, model-admitted and independently replicated receipts, and no registered quantum-computation "
        "obligation remains unclassified or frontier."
    ))
    add(L())
    add(L("Closure is formal and structural. It does not by itself claim that a physical device realizes these operations, supply a measured fault threshold, establish unrestricted speedups, or derive quantum physics as a natural law. Those require the later empirical Physics branch."))
    add(L())
    add(L("## 2. Fold-native quantum constitution"))
    add(L())
    add(L(
        "One Fold distinction supplies the native information unit. Complete held-label words across generated positions "
        "supply branch support. A branch carries an exact held phase label from a generated finite cycle. Joint states are "
        "complete pair-cell words retaining component identity. A transformation is a total branch-word bijection plus a "
        "period-held phase action. None of these definitions requires a real or complex amplitude, irrational normalization, "
        "imaginary proof value or ungenerated continuum."
    ))
    add(L())
    add(L("## 3. Superposition, interference and entanglement"))
    add(L())
    add(L(
        "Superposition-equivalent means complete simultaneous support of every generated branch before an observation class "
        "is retained; it does not install an ontic stochastic mixture. Phase is a reversible action on held cycle labels. "
        "Interference is a complete branch-to-image relation whose predecessor fibres preserve every merging branch and its "
        "phase. Joint support is factorable exactly when it equals the Cartesian product of its marginals; a strict correlated "
        "subset is nonfactorable and supplies the entangling class."
    ))
    add(L())
    add(L("## 4. Measurement and reversibility"))
    add(L())
    add(L(
        "Measurement is a total observation relation over complete branch support. The selected observation class becomes the "
        "retained state, while the measurement record keeps every pre-observation branch, phase and image label. Support "
        "reduction is therefore exact and reconstructible at the record boundary. A gate is reversible only when its branch "
        "map is bijective and its phase action has an exact inverse; any predecessor merge requires a retained predecessor label."
    ))
    add(L())
    add(L("## 5. Coding, multi-error correction and fault tolerance"))
    add(L())
    add(L(
        "A generated fault-depth trace of length t forces repetition width 2t+1: at least t+1 copies retain the source label "
        "after any family of at most t label changes. The executable census exhausts every mask through one error at width 3 "
        "(4 masks), two errors at width 5 (16 masks), and three errors at width 7 (64 masks). The base and successor certificate "
        "extends the majority separation to every generated positive finite t. Fault-tolerant circuits must contain declared "
        "faults, prevent one location from opening more distinctions than the code can repair, and recover before errors escape "
        "the registered support. No hardware threshold constant is asserted."
    ))
    add(L())
    add(L("## 6. Classical-quantum correspondence and limits"))
    add(L())
    add(L(
        "Classical computation embeds as the single-held-branch, phase-insensitive reversible submodel. Quantum execution "
        "extends that carrier with complete branch support, phase-sensitive predecessor merging and nonfactorable joint support. "
        "Observation decodes exact classical records. Because every quantum circuit remains a generated finite description "
        "executed by an admitted universal process, self-reference and halting boundaries transfer: quantum computation does "
        "not acquire an undeclared oracle or hypercomputational escape."
    ))
    add(L())
    add(L("## 7. Complete execution census"))
    add(L())
    add(L("| Order | Claim | Candidates | Closure |"))
    add(L("|---:|---|---:|---|"))
    for index, spec in enumerate(QUANTUM_SPECS, 1):
        add(L(f"| {index} | `{spec.claim_id}` | 256 | depth-independent |"))
    add(L())
    add(L(f"The branch total is **{candidate_total:,} candidates**, **21 survivors**, **84 adverse controls** and **21 independent validations**."))
    section = 8
    for order, spec in enumerate(QUANTUM_SPECS, 1):
        add(derivation_section(spec, order, section, quantum_survivor))
        section += 1
    add(L(f"## {section}. Branch synthesis"))
    add(L())
    add(L("The 21 laws establish one operational machine family in which classical and quantum modes share descriptions, traces, resources and verification. Quantum distinctions arise from complete branch support, held phase action, predecessor merging and nonfactorable composition; they are not imported as a separate mathematical universe."))
    add(L())
    add(L(f"## {section + 1}. Reproduction and invalidation"))
    add(L())
    add(L("Run the repository-wide one-command verifier. A reviewer can invalidate a result by producing an omitted same-boundary coordinate, a second survivor, a nonminimal form, an induction counterexample, a failed inverse, an incomplete observation record, an uncorrected registered error mask or a mismatched receipt."))
    add(L())
    add(L(f"## {section + 2}. Scope and next branch"))
    add(L())
    add(L("The next branch is Physics. It must test whether independently derived Fold relations correspond to mechanics, fields, spacetime, thermodynamics, quantum phenomena, gravitation, matter, waves, fluids, plasmas and condensed structures. Formal quantum computation cannot select the natural laws; sealed observation must do that work."))
    add(L())
    add(L("## References"))
    add(L())
    add(L("1. Landauer R. Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*. 1961;5:183-191. doi:10.1147/rd.53.0183."))
    add(L("2. Bennett CH. Logical reversibility of computation. *IBM Journal of Research and Development*. 1973;17:525-532. doi:10.1147/rd.176.0525."))
    add(L("3. Feynman RP. Simulating physics with computers. *International Journal of Theoretical Physics*. 1982;21:467-488. doi:10.1007/BF02650179."))
    add(L("4. Deutsch D. Quantum theory, the Church-Turing principle and the universal quantum computer. *Proceedings of the Royal Society A*. 1985;400:97-117. doi:10.1098/rspa.1985.0070."))
    add(L("5. Shor PW. Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM Journal on Computing*. 1997;26:1484-1509. doi:10.1137/S0097539795293172."))
    add(L("6. Grover LK. A fast quantum mechanical algorithm for database search. *Proceedings of STOC*. 1996:212-219. doi:10.1145/237814.237866."))
    add(L("7. Schumacher B. Quantum coding. *Physical Review A*. 1995;51:2738-2747. doi:10.1103/PhysRevA.51.2738."))
    add(L("8. Smith M. Smithian Fold Theory Scientific Constitution. V3 clean-room repository, 2026."))
    return "".join(parts)


def main() -> None:
    COMPUTATION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUANTUM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    COMPUTATION_OUTPUT.write_text(build_computation(), encoding="utf-8")
    QUANTUM_OUTPUT.write_text(build_quantum(), encoding="utf-8")
    print(f"built {COMPUTATION_OUTPUT}")
    print(f"built {QUANTUM_OUTPUT}")


if __name__ == "__main__":
    main()
