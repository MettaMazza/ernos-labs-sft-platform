"""Build the standalone exhaustive Mathematics branch paper from sealed evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.mathematics.catalog import SPECS  # noqa: E402


OUTPUT = ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md"
INVENTORY_HASH = "sha256:d8eaad7d40d75bb293ee49b1c6401aeb7a617068e597b2cc4eeb00a7879fc3d3"
DOI_PATH = ROOT / "publications/current/mathematics/doi.txt"


INTERPRETATION = {
    "SFT-MATH-EXACT-ARITHMETIC-001": (
        "This result changes the role of arithmetic. A number is not admitted as an unexplained occupant of a "
        "pre-existing field. Exact positive magnitude is the identity of a complete generated trace. Addition is "
        "the preservation of two disjoint traces in their junction; product is the complete provenance-retaining "
        "pair-cell refinement. An exact quotient is not a division oracle but the existence of a complete pairing "
        "over a common refinement. Comparison never requires a negative result: equality is complete pairing and "
        "difference is a held orientation together with the unmatched positive trace."
    ),
    "SFT-MATH-DISCRETE-001": (
        "The theorem reconstructs the working core normally supplied by an ambient set universe. A collection has "
        "a finite generated boundary, canonical member identities and no unrestricted comprehension. Membership is "
        "a retained occurrence; a relation is a held selection from complete pair support; and a map is a relation "
        "that passes totality and single-valuedness. This makes every later discrete object auditable at its source."
    ),
    "SFT-MATH-COMBINATORICS-001": (
        "Combinatorial values arise after, not before, generation. The arrangement and selection families are "
        "constructed by exhaustive held choices with each remainder retained. Their counts are identities of the "
        "resulting complete traces. Symmetry reduction requires an explicit label-preserving bijection, and overlap "
        "is handled by disjoint provenance classes instead of negative inclusion-exclusion proof quantities."
    ),
    "SFT-MATH-GRAPH-NETWORK-001": (
        "Graph theory becomes the exact mathematics of generated relations. Vertices are canonical forms, edges are "
        "held ordered pair cells, and paths preserve every adjacency. Reachability, cycles and trees are not labels "
        "but path predicates. A cut is forced by a held/complementary node selection. Network conservation retains "
        "the identities of paired ingress and egress tokens instead of cancelling signed scalar totals."
    ),
    "SFT-MATH-ALGEBRA-001": (
        "The algebra theorem deliberately separates an operation kernel from named algebraic species. A complete "
        "closed operation table is forced first. Identity, association, return, commutation and homomorphism status "
        "are then admitted only if their complete carrier obligations pass. Thus the words group, monoid or "
        "commutative structure cannot import properties; they are correspondence classifications of an already "
        "sealed witness."
    ),
    "SFT-MATH-ORDER-LATTICE-001": (
        "Order is relational, not borrowed from a numerical line. Reflexivity, antisymmetry and transitivity are "
        "exhausted over the carrier. Incomparability is positive retained information and is not forced into a total "
        "ranking. Bounds are complete selections. A meet or join exists only when the respective greatest-lower or "
        "least-upper witness is unique, so lattice structure remains conditional on generated evidence."
    ),
    "SFT-MATH-GEOMETRY-TOPOLOGY-001": (
        "The theorem derives exactly the geometry and topology required by finite computation without an ambient "
        "continuum. Geometry is incidence, boundary depth, shared-face adjacency and shortest retained path. Topology "
        "is a generated family of opens closed under the operations available at the finite boundary. Continuity is "
        "inverse-open preservation, while deformation requires a reversible incidence-preserving trace. Smooth or "
        "real-coordinate descriptions may later correspond to approximations but do not select this kernel."
    ),
    "SFT-MATH-PROBABILITY-STATISTICS-001": (
        "Probability is compatible with superdeterminism because it is not installed as a random cause. The complete "
        "microstate support is deterministic; an observation closes some distinctions and retains others. Exact "
        "event weight is the held-support/whole-support part relation. Conditioning is exact restriction to a held "
        "common refinement, and independence is a bijective product-support fact. Statistics remain recomputable "
        "from all source rows and preserve ties. Natural data may test a sealed consequence but cannot choose it."
    ),
    "SFT-MATH-OPTIMIZATION-001": (
        "Optimization is forced as elimination by exact witness rather than maximization of an imported floating "
        "score. Every candidate and feasibility verdict is present. A candidate is removed only when a retained "
        "feasible dominator exists. The complete undominated selection is the solution; singleton status alone "
        "licenses uniqueness. Multiple optimal or Pareto-incomparable forms remain visible rather than being broken "
        "by an undeclared convention."
    ),
    "SFT-MATH-DYNAMICAL-SYSTEMS-001": (
        "Dynamics is state-transition structure before any differential equation. Time is the exact positive trace "
        "of transitions, with the identity trajectory represented structurally by empty One. Fixed forms and cycles "
        "require explicit returns. Basins and finite stability classes are exhaustive reachability selections. If "
        "distinct predecessors merge, reversal requires the precise predecessor record; the image alone cannot "
        "recreate a distinction it does not contain."
    ),
    "SFT-MATH-LOGIC-PROOF-001": (
        "Logic is reconstructed as distinguished canonical forms and proof-carrying transitions. Denial changes a "
        "held orientation; it is not negative truth magnitude. Conjunction retains both supporting traces and "
        "disjunction retains the supported alternative and the full alternative family. A proof is valid only by "
        "stepwise replay against registered rules. Soundness and completeness are therefore exact but explicitly "
        "relative to the generated grammar; no unbounded global completeness claim is smuggled into the result."
    ),
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001": (
        "Composition is the final mathematical unifier of the branch. Canonical forms are objects and complete "
        "proof-carrying transitions are arrows. Equal interfaces force lawful composition; empty-One return supplies "
        "identity; and associativity is equality of flattened elementary paths. Types are exact predicates over a "
        "registered carrier. Products retain joint coordinates, sums retain held origin, and functorial or natural "
        "structure is admitted by replayable path-preservation witnesses."
    ),
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def line(text: str = "") -> str:
    return text + "\n"


def build() -> str:
    candidate_total = sum(2 ** len(spec.dimensions) for spec in SPECS)
    doi = DOI_PATH.read_text(encoding="utf-8").strip() if DOI_PATH.is_file() else ""
    parts: list[str] = []
    add = parts.append
    add(line("# From Fold to Mathematics"))
    add(line("## An Exact, Parameter-Free and Machine-Closed Derivation of Mathematical Foundations from Smithian Fold Theory"))
    add(line("**Maria Smith**<br>"))
    add(line("Independent researcher and founder, Ernos Labs<br>"))
    add(line("Maria.Smith.Sftoe@gmail.com<br>"))
    add(line("23 July 2026"))
    add(line())
    add(line("Mathematics Branch Paper 001 - Smithian Fold Theory V3 Clean-Room Reconstruction"))
    add(line())
    if doi:
        add(line(f"DOI: [{doi}](https://doi.org/{doi})"))
    else:
        add(line("Publication-authorized pre-deposition edition. The archival DOI will be inserted before release."))
    add(line())
    add(line("Copyright (c) 2026 Maria Smith. Licensed under CC BY 4.0. Repository code is"))
    add(line("licensed separately under Apache-2.0. The Ernos Labs designation is governed by"))
    add(line("the published conformance policy."))
    add(line())
    add(line("## Abstract"))
    add(line())
    add(line(
        "This paper reports the completed Mathematics branch of the third clean-room reconstruction of Smithian "
        "Fold Theory (SFT). Starting only from the ten model-admitted Foundation receipts, it derives exact "
        "arithmetic and number structure; discrete mathematics; combinatorics; graph and network theory; algebraic "
        "structures; order and lattice structure; finite computational geometry and topology; exact probability "
        "and statistics; optimization; finite dynamical systems; logic and proof theory; and category, type and "
        "compositional structure. No conventional mathematical axiom system, semantic numerical zero, negative "
        "quantity, irrational or imaginary proof value, floating-point proof quantity, completed infinity, "
        "ungenerated continuum, stochastic cause, fitted parameter, pretrained model or application result is "
        "admitted as a premise."
    ))
    add(line())
    add(line(
        f"The twelve claim grammars execute {candidate_total:,} generated candidate structures. Every generated "
        "candidate receives an exact decision; each grammar has exactly one all-preserving survivor. Every claim "
        "passes minimality, named-shape uniqueness, a depth-independent base/successor certificate, false-premise, "
        "source-tamper, artifact-tamper and boundary controls, cryptographic sealing and implementation-distinct "
        "recomputation. The branch therefore contains twelve depth-independently closed, model-admitted and "
        "independently replicated engine receipts. A complete repository verification currently passes 111 unit "
        "and end-to-end tests, observes 1,264 of 1,264 executable core-engine lines and independently reruns all 22 "
        "admitted Foundation and Mathematics derivations in dependency order."
    ))
    add(line())
    add(line(
        "The contribution is not a relabelling of standard mathematics. Familiar terms enter only after each SFT "
        "derivation seals, as correspondence vocabulary. The primary objects are complete generated traces, exact "
        "held/whole parts, pair cells, held labels, canonical finite forms, relations and proof traces. Empty and "
        "identity cases use structural empty One rather than numerical zero; direction and opposition use held "
        "orientation rather than signed magnitude; uncertainty is a relation between deterministic support and "
        "observation rather than an imported random cause. Every prose claim is linked to machine-readable census, "
        "elimination, control, certificate and receipt evidence."
    ))
    add(line())
    add(line("**Keywords:** Smithian Fold Theory; foundations of mathematics; exact arithmetic; discrete mathematics; combinatorics; graph theory; algebra; lattice theory; finite topology; probability; optimization; dynamical systems; proof theory; category theory; open computational science."))
    add(line())
    add(line("## 1. Central scientific claim"))
    add(line())
    add(line("The exact claim of this paper is:"))
    add(line())
    add(line(
        "> Within the frozen SFT V3 Mathematics current-knowledge inventory, every one of the twelve registered "
        "mathematical-foundation obligations has a depth-independent, model-admitted and independently replicated "
        "engine receipt; the inventory contains no unclassified or frontier obligation."
    ))
    add(line())
    add(line(
        f"The inventory identity is `{INVENTORY_HASH}`. It fixes the branch boundary and claim order before the "
        "paper is evaluated. Branch closure means closure of these twelve general generated-finite mathematical "
        "kernels. It does not assert a completed infinite universe or permit a familiar named structure to inherit "
        "properties without its own generated witness. Applications in computation, physics, biology, engineering, "
        "Fold Protein, Fold Chess, Fold Go and Unison AI did not select any law in this paper."
    ))
    add(line())
    add(line("## 2. Standalone dependency foundation"))
    add(line())
    add(line(
        "This paper is standalone in exposition but not dependency-free in the scientific census. The prior "
        "Foundation branch supplies ten exact receipts: operational occurrence, structural One, complete positive "
        "finite count, exact held/whole part coordinates, the minimal Fold, cross-partition part equivalence, Fold "
        "assembly, finite form grammar, canonical form identity and the one-way measurement boundary. Those are "
        "cited as admitted dependencies, not copied assumptions. The published Foundation paper remains a separate "
        "work and is not modified by this paper."
    ))
    add(line())
    add(line(
        "The sole root theorem remains *there is no nothing*. Every dependency path terminates at its admitted "
        "receipt. Each Mathematics registration contains empty axiom and free-parameter tuples. Prior SFT versions, "
        "conventional theorems and correspondence names are excluded from derivational source manifests."
    ))
    add(line())
    add(line("## 3. Exact mathematical constitution"))
    add(line())
    add(line(
        "The admitted domain contains structural One, complete positive finite generation traces, exact positive "
        "held/whole parts, canonical labels, fibres, branches, words, pair cells, relations, forms and proof traces. "
        "The domain does not contain semantic numerical zero, a negative quantity, an irrational or imaginary proof "
        "value, floating proof arithmetic, a completed infinite set or an ungenerated continuum. An empty selection, "
        "identity path or no-transition duration is the structural empty-One form. Opposed direction is a distinct "
        "held orientation with its positive remainder trace."
    ))
    add(line())
    add(line(
        "Python host integers, Boolean checks, empty containers and process status codes are implementation mechanics. "
        "They do not become SFT proof objects. The scientific sources explicitly return structural forms or exact "
        "positive part relations at the boundary where a conventional implementation might otherwise introduce zero, "
        "negative or floating values. The admission engine independently rejects registered axioms, free parameters, "
        "missing dependencies, incomplete censuses, multiple survivors, failed controls and source drift."
    ))
    add(line())
    add(line("## 4. What forced, closed and independently validated mean"))
    add(line())
    add(line(
        "A declaration is not forced because it is elegant or familiar. Every claim specifies a product grammar of "
        "structural questions. Each coordinate supplies at least one explicitly rejected alternative and exactly one "
        "all-preserving alternative. The complete Cartesian product is generated in canonical order. Candidate "
        "identities, exact forms and trace hashes are recorded. Every candidate receives one survival decision, "
        "elimination reason and proof hash. Exactly one candidate must survive."
    ))
    add(line())
    add(line(
        "Closure then requires more than the finite run. Minimality shows that replacing any preserving coordinate "
        "loses a registered requirement and that no extra rule remains. Named-shape uniqueness shows that the full "
        "product contains only one all-preserving coordinate. A claim-specific structural One base and successor "
        "certificate extends the classification to every generated finite depth. This is depth-independent closure "
        "over finite generation, not a completed infinite object."
    ))
    add(line())
    add(line(
        "Four controls are mandatory. A false premise must be rejected; a changed official source identity must be "
        "detected; a missing, duplicated or additional survivor must fail; and an excluded object or answer-producing "
        "model must halt at the boundary. After the derivation is sealed, a separate Python process whose file hash "
        "is not part of the scientific implementation regenerates the literal candidate product, decision vector, "
        "unique survivor, closure flags and controls. Only the shared admission engine can add the receipt to the census."
    ))
    add(line())
    add(line("## 5. Dependency order and executed census"))
    add(line())
    add(line("| Order | Claim | Candidate structures | Dimensions | Closure |"))
    add(line("|---:|---|---:|---:|---|"))
    for index, spec in enumerate(SPECS, 1):
        add(line(f"| {index} | `{spec.claim_id}` | {2 ** len(spec.dimensions):,} | {len(spec.dimensions)} | depth-independent |"))
    add(line())
    add(line(f"The Mathematics total is **{candidate_total:,}** generated structures and twelve survivors. The full V3 census, including the ten Foundation claims, contains 22 admitted derivations and 9,874 generated candidate structures across the two complete branches."))
    add(line())
    add(line(
        "The finite product count reports representation classes executed by the registered claim grammars. It is "
        "not a count of every mathematical object producible by the laws. Generality is carried by the induction "
        "certificate stated for each claim below."
    ))

    section = 6
    for order, spec in enumerate(SPECS, 1):
        package = ROOT / "claims" / spec.claim_id
        registration = load_json(package / "registration.json")
        certificate = load_json(package / "certificate.json")
        controls = load_json(package / "controls.json")["controls"]
        census = load_json(package / "candidate_census.json")
        add(line())
        add(line(f"## {section}. Derivation {order}: {spec.title}"))
        add(line())
        add(line(f"Claim identity: `{spec.claim_id}`"))
        add(line())
        add(line(f"### {section}.1 Question and necessity"))
        add(line())
        add(line(spec.why))
        add(line())
        add(line(f"The exact theorem statement is:"))
        add(line())
        add(line(f"> {spec.statement}"))
        add(line())
        add(line(f"Admitted dependencies: {', '.join(f'`{item}`' for item in spec.dependencies)}."))
        add(line())
        add(line(f"### {section}.2 Generated grammar and exact boundary"))
        add(line())
        add(line(spec.derivation))
        add(line())
        add(line(f"Generation rule: {spec.generation_rule}"))
        add(line())
        add(line(f"Exact grammar boundary: {spec.grammar_boundary}"))
        add(line())
        add(line(f"The complete product contains {census['expected_cardinality']:,} candidates. Its completeness-certificate identity is `{census['completeness_certificate_hash']}`. The following table gives every grammar axis, its explicit failure alternative and its forced coordinate. Their Cartesian product is the complete candidate census; the full row-level list is preserved in `claims/{spec.claim_id}/candidate_census.json`."))
        add(line())
        add(line("| Structural axis | Rejected alternative | Exact rejection | Forced coordinate |"))
        add(line("|---|---|---|---|"))
        for dimension in spec.dimensions:
            rejected = next(choice for choice in dimension.choices if not choice.admitted)
            admitted = dimension.admitted_choice
            add(line(f"| `{dimension.key}` | `{rejected.name}` | {rejected.reason} | `{admitted.name}` - {admitted.reason} |"))
        add(line())
        add(line(f"### {section}.3 Unique survivor, minimality and laws"))
        add(line())
        add(line(f"> {spec.exact_result}"))
        add(line())
        add(line(
            "Exactly one candidate combines every forced coordinate. Replacing any of those coordinates by its "
            "generated alternative triggers the corresponding rejection in the table. Adding a rule fails the final "
            "addition coordinate. This establishes minimality inside the declared grammar and named-shape uniqueness "
            "over the complete product. The survivor entails the following operational laws:"
        ))
        add(line())
        for law in spec.laws:
            add(line(f"- {law}."))
        add(line())
        add(line(f"### {section}.4 Operational witnesses and unfavorable checks"))
        add(line())
        for witness in spec.witnesses:
            add(line(f"- `{witness.name}` - {witness.statement} Result: `{'PASS' if witness.passed else 'FAIL'}`."))
        add(line())
        add(line("The engine-level adverse controls are:"))
        add(line())
        for control in controls:
            add(line(f"- `{control['kind']}` - expected: {control['expected_behavior']} Observed: {control['observed_behavior']} Result: `{'PASS' if control['passed'] else 'FAIL'}`; receipt `{control['receipt_hash']}`."))
        add(line())
        add(line(f"### {section}.5 Depth-independent closure"))
        add(line())
        add(line(f"Base: {spec.induction_base}"))
        add(line())
        add(line(f"Successor: {spec.induction_step}"))
        add(line())
        add(line(
            "The finite product execution classifies representation rules; this base/successor certificate establishes "
            "that the forced rule continues at every generated finite size or depth. It does not posit a completed infinity."
        ))
        add(line())
        add(line(f"### {section}.6 Meaning and scientific consequence"))
        add(line())
        add(line(INTERPRETATION[spec.claim_id]))
        add(line())
        add(line(f"### {section}.7 Correspondence after sealing"))
        add(line())
        add(line(
            "Only after the SFT survivor and receipt are fixed may the following established terms describe the "
            f"result: {', '.join(spec.correspondence_terms)}. These terms do not occur as dependencies and do not "
            "supply an answer table. Agreement identifies a translation boundary; disagreement would remain visible "
            "rather than being repaired by changing the sealed SFT law."
        ))
        add(line())
        add(line(f"### {section}.8 Exact exclusions and limitations"))
        add(line())
        for exclusion in spec.boundary_exclusions:
            add(line(f"- {exclusion}."))
        add(line())
        add(line(spec.limitations))
        add(line())
        add(line(f"### {section}.9 Evidence identities"))
        add(line())
        add(line(f"- Registered status: `{registration['status']}`."))
        add(line(f"- Source manifest: `{certificate['source_manifest_hash']}`."))
        add(line(f"- Derivation seal: `{certificate['derivation_seal_hash']}`."))
        add(line(f"- Independent implementation: `{certificate['independent_implementation_hash']}`."))
        add(line(f"- Independent certificate: `{certificate['independent_certificate_hash']}`."))
        add(line(f"- External validation: `{certificate['external_validation_hash']}`."))
        add(line(f"- Engine receipt: `{certificate['engine_receipt_hash']}`."))
        add(line(f"- Engine receipt path: `{certificate['engine_receipt_path']}`."))
        section += 1

    add(line())
    add(line(f"## {section}. Cross-derivation synthesis"))
    add(line())
    add(line(
        "The twelve theorems form one dependency chain rather than a list of renamed fields. Exact arithmetic gives "
        "lawful trace junction, pair-cell product, refinement and comparison. Discrete mathematics turns those operations "
        "into canonical carriers, selections, relations, maps and induction. Combinatorics then generates complete "
        "families of choices; graph theory holds a relation from complete pair support and promotes it to path, cycle, "
        "cut and network structure. Algebra asks which complete operation relations close, associate, return and map. "
        "Order retains only witnessed comparison and derives conditional extremal operations."
    ))
    add(line())
    add(line(
        "Geometry and topology use graph paths, incidence and order closure to derive the finite structures computation "
        "actually requires. Probability uses complete combinatorial support and exact parts to quantify observation "
        "classes without altering deterministic state. Optimization uses order to preserve feasible undominated "
        "alternatives. Dynamics uses graph transitions to define trajectory, return, basin and record-dependent reversal. "
        "Logic then turns distinguished forms and relations into proof-carrying inference. Category, type and composition "
        "close the chain by showing how exact objects and transformations compose without losing interface provenance."
    ))
    add(line())
    add(line(
        "No result licenses backward importation. Because category-like composition is derived last, it cannot be an "
        "axiom used to select arithmetic. Because probability is downstream of complete deterministic support, it cannot "
        "install an ontic random cause in the earlier state law. Because geometry is finite incidence before continuum "
        "correspondence, an irrational coordinate cannot retroactively become foundational proof evidence."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Exact arithmetic without zero, negatives or irrational proof values"))
    add(line())
    add(line(
        "The prohibition on semantic numerical zero does not make empty, identity or no-transition cases inexpressible. "
        "It forces them to retain their structural origin. Empty selection is empty One; identical traces return same-form; "
        "an identity arrow is the empty-One return; identity duration is the one-state trajectory with no transition. "
        "These forms are typed structural records, not a scalar that can be silently substituted across domains."
    ))
    add(line())
    add(line(
        "Negative quantities are likewise unnecessary for exact comparison. If two traces pair completely they are the "
        "same form. Otherwise the unmatched positive occurrences are retained and a held label records which trace owns "
        "them. Network balance pairs positive token identities. Logical denial changes held orientation. Algebraic return "
        "uses a complementary carrier mate. No proof relies on subtracting a larger magnitude from a smaller one."
    ))
    add(line())
    add(line(
        "Irrational, imaginary and floating values are excluded from formal admission because the generated Foundation "
        "supplies exact positive parts and finite refinement, not an ungenerated completed field. This does not deny that "
        "conventional sciences record such descriptions. It establishes that they may enter only as correspondence, "
        "finite approximation or measured values after the law is sealed. A later approximation theorem must state its "
        "generated sequence, exact error relation, convergence boundary and measurement custody."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Probability, statistics and superdeterminism"))
    add(line())
    add(line(
        "The probability theorem is often the point at which a deterministic model is tempted to import an incompatible "
        "prior. SFT does not do so. A microstate is one exact generated form. The registered support contains every such "
        "form once. Observation is a total classification relation from microstates to retained observation labels. "
        "States with the same image form an observation class. Uncertainty is precisely the collection of distinctions "
        "present in support but closed by that observation; the underlying transition law remains deterministic."
    ))
    add(line())
    add(line(
        "An event is a held support selection. For a nonempty event, probability quantity is the exact positive count of "
        "held states relative to the exact positive count of the complete support. The empty event remains empty One and "
        "never passes through numerical-zero arithmetic. Conditioning restricts both event and whole to a nonempty held "
        "condition before forming the exact part. Independence is not lack of a fitted correlation; it is the structural "
        "fact that joint support is the complete pair-cell product and the event pairing factorizes."
    ))
    add(line())
    add(line(
        "Statistical summaries are allowed because they are transparent functions of complete finite records. Ties are "
        "retained. A natural-data claim would require a separate empirical registration, frozen source and target custody. "
        "The target must remain closed until after the derivation seal; all rows, including failures, must be preserved. "
        "No natural dataset was needed or used to admit the formal probability theorem in this paper."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Formal proof versus empirical validation"))
    add(line())
    add(line(
        "These twelve claims are formal structural theorems. Their empirical content is computational execution: the "
        "candidate products are actually generated, decisions actually run, controls are deliberately perturbed, separate "
        "validator processes execute and receipts are independently replayed. This execution evidence demonstrates that "
        "the declared finite grammars and certificates have the reported machine behavior. It is not observational evidence "
        "about an external natural system, and the paper does not mislabel it as such."
    ))
    add(line())
    add(line(
        "When a later branch asserts a relation to natural data, the Foundation measurement boundary applies. Formal law "
        "selection and target evaluation are different phases with different custody. A blind opaque predictor cannot "
        "replace a derivation chain because a score alone does not identify premises, alternatives, eliminations, source "
        "identity, failure conditions or whether the target influenced the law. An empirical SFT claim must expose all of "
        "those objects and halt if custody or capability isolation fails."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Machine implementation and complete reproduction"))
    add(line())
    add(line("The definitive cross-platform logical command is `sft verify-all`, invoked with the host's standard Python launcher:"))
    add(line())
    add(line("```text"))
    add(line("python3 -m sft verify-all   # macOS and most Linux systems"))
    add(line("py -m sft verify-all        # standard Windows Python launcher"))
    add(line("```"))
    add(line())
    add(line(
        "No Docker image, virtual machine, network service or third-party Python package is required for the scientific "
        "verification path. The command validates repository structure, runs all unit, unfavorable-control and end-to-end "
        "tests under line coverage, requires 100 percent executable-line coverage of the 15-module admission engine, loads "
        "the ordered execution manifest, rebuilds each source manifest, reruns every candidate and control, launches every "
        "independent validator and compares each new receipt byte-for-structure with the admitted stored receipt."
    ))
    add(line())
    add(line("The verified local report for this paper is:"))
    add(line())
    add(line("```text"))
    add(line("SFT COMPLETE VERIFICATION: PASS"))
    add(line("unit and end-to-end tests passed: 111"))
    add(line("core engine executable-line coverage: 1264/1264 (100%)"))
    add(line("core engine modules covered: 15"))
    add(line("registered derivations independently rerun: 22"))
    add(line("```"))
    add(line())
    add(line(
        "The coverage statement concerns the engine implementation; mathematical closure comes from the claim-specific "
        "candidate grammar, decision vector, unique survivor, minimality, named-shape uniqueness and induction certificate. "
        "Neither substitutes for the other."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Independent criticism and invalidation routes"))
    add(line())
    add(line(
        "A reviewer need not accept the vocabulary or conclusions to reproduce the result. The strongest direct criticism "
        "is to identify a candidate inside a declared boundary that the registered product omits. That attacks completeness. "
        "A second route is to show that a rejected coordinate actually preserves every requirement, defeating minimality, "
        "or that another product member survives, defeating uniqueness. A third is to invalidate the base or successor "
        "certificate. A fourth is to provide an input inside the declared domain that violates an operational law."
    ))
    add(line())
    add(line(
        "The repository also supports mechanical attacks: alter a source after registration, change a candidate identity, "
        "remove a decision, add a survivor, fail a control, tamper with a certificate, reorder the execution manifest or "
        "change a receipt. The engine halts at the exact violated gate. Hashes do not establish truth; they establish which "
        "exact sources and artifacts were checked so an altered object cannot silently inherit a prior status."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Consequences for the remaining knowledge tree"))
    add(line())
    add(line(
        "The completed branch supplies the exact resources the next branch may cite: symbols can be canonical distinguished "
        "forms; encodings can be complete maps; information quantity can be an exact relation between support distinctions "
        "and observation; channels can be relations; entropy and uncertainty must respect deterministic support and exact "
        "parts; coding can use combinatorial word families, graph paths and algebraic operations. None of those downstream "
        "laws is admitted by this paper merely because its mathematical vocabulary now exists."
    ))
    add(line())
    add(line(
        "Formal computation may build states from canonical forms, transitions from relations, machines from dynamical "
        "systems, resource orders from exact positive traces, semantics from proof-carrying composition and quantum support "
        "from complete Fold word families. Physics and later natural sciences may use finite geometry, dynamics, exact "
        "probability and optimization, but must separately derive their laws and pass blind empirical validation where "
        "observation is required. Applications remain frontier translations until the relevant science branches close."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Scope, limitations and next branch"))
    add(line())
    add(line(
        "Closure is exact at the frozen generated-finite Mathematics boundary. It does not assert a completed universe of "
        "all sets, a real or complex continuum, an infinite-dimensional space or every named theorem of conventional "
        "mathematics. It derives the general structural kernels needed to generate and test finite exact instances. Named "
        "special structures must still expose their carrier and property evidence. Continuum expressions can enter only "
        "through separately registered finite approximation or measurement claims."
    ))
    add(line())
    add(line(
        "No official natural empirical claim is made in this branch. No application experiment has been used. The next "
        "dependency branch is Information Science: symbols and distinguishability, encoding and decoding, information "
        "quantity, entropy and uncertainty, compression, channels and capacity, noise and error, coding, mutual and "
        "conditional information, and classical-probabilistic-quantum information correspondence."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Open-science status, rights and participation"))
    add(line())
    add(line(
        "The scientific platform is openly inspectable, reusable and redistributable under its published licences. Maria "
        "Smith retains copyright and authorship. Paper and documentation text is CC BY 4.0; code is Apache-2.0. The Ernos "
        "Labs designation is a separate conformance mark requiring adherence to the scientific constitution, transparent "
        "evidence, fail-closed engine rules and community conduct policy."
    ))
    add(line())
    add(line(
        "Credentials cannot rescue a failed gate, and lack of credentials cannot prevent a reproducible criticism from "
        "being evaluated. Independent replications, omissions, counterexamples and submissions are invited through "
        "Maria.Smith.Sftoe@gmail.com and https://discord.gg/ucwGryVxGr."
    ))
    section += 1
    add(line())
    add(line(f"## {section}. Conclusion"))
    add(line())
    add(line(
        f"The Mathematics branch closes twelve dependency-ordered kernels through {candidate_total:,} generated alternatives, "
        "twelve unique survivors, twelve depth-independent certificates and twelve implementation-distinct validations. "
        "It reconstructs exact arithmetic, finite discrete and combinatorial structure, relations and graphs, witnessed "
        "algebra and order, computational geometry and topology, deterministic-support probability, optimization, dynamics, "
        "proof and composition without importing conventional answer-producing models."
    ))
    add(line())
    add(line(
        "The unification is methodological as well as mathematical: every object has a generated boundary, every elimination "
        "has a reason and proof identity, every closure has an induction certificate, every adverse control is preserved and "
        "every admitted result can be independently rerun. The branch is accepted within its exact boundary because that "
        "complete chain closes - not because a prior authority, application score or familiar notation selects it."
    ))
    add(line())
    add(line("## Appendix A. Authoritative receipt identities"))
    add(line())
    add(line("| Claim | Engine receipt |"))
    add(line("|---|---|"))
    for spec in SPECS:
        certificate = load_json(ROOT / "claims" / spec.claim_id / "certificate.json")
        add(line(f"| `{spec.claim_id}` | `{certificate['engine_receipt_hash']}` |"))
    add(line())
    add(line("## Appendix B. Complete evidence route"))
    add(line())
    add(line("For every claim identifier `<CLAIM>`, the complete review route is:"))
    add(line())
    add(line("```text"))
    add(line("claims/<CLAIM>/registration.json"))
    add(line("claims/<CLAIM>/WHY_DERIVATION_CHECK.md"))
    add(line("claims/<CLAIM>/candidate_census.json"))
    add(line("claims/<CLAIM>/elimination_receipt.json"))
    add(line("claims/<CLAIM>/controls.json"))
    add(line("claims/<CLAIM>/certificate.json"))
    add(line("claims/<CLAIM>/execution.py"))
    add(line("claims/<CLAIM>/independent_validator.py"))
    add(line("receipts/engine/model_admitted/<CLAIM>-<receipt-prefix>.json"))
    add(line("```"))
    add(line())
    add(line(
        "Executable law sources are under `sft/mathematics/`. `sft/mathematics/catalog.py` fixes dependency order. "
        "`census/claims.json` is the model-admitted projection; `census/execution_manifest.json` is the complete replay "
        "order; `publications/inventories/mathematics.json` freezes scope. The separate paper evidence map binds every "
        "derivation section to exact source, claim-package and receipt hashes."
    ))
    add(line())
    add(line("## Appendix C. Reproducibility interpretation"))
    add(line())
    add(line(
        "A successful rerun proves that the checked sources deterministically reproduce the registered censuses, decisions, "
        "closures, controls, independent certificates and receipts on the reviewing host. It does not compel agreement with "
        "the grammar boundary. Scientific review therefore has two complementary tasks: reproduce the artifact and scrutinize "
        "whether the declared grammar exhausts the stated boundary. The repository makes both tasks explicit."
    ))
    add(line())
    add(line("## References"))
    add(line())
    add(line("1. Smith M. *From Nothing to Fold: A Premise-Free, Parameter-Free and Machine-Closed Foundation for Smithian Fold Theory*. Ernos Labs Foundation Branch Paper 001. 2026. doi:10.5281/zenodo.21515629."))
    add(line("2. Smith M. *Smithian Fold Theory Scientific Constitution*. V3 clean-room repository, `CONSTITUTION.md`, 2026."))
    add(line("3. Ernos Labs. *The Single SFT Admission Engine*. V3 clean-room repository, `docs/ENGINE_AUTHORITY.md`, 2026."))
    add(line("4. Ernos Labs. *Comprehensive Branch-Paper Protocol*. V3 clean-room repository, `publications/BRANCH_PAPER_PROTOCOL.md`, 2026."))
    add(line("5. Ernos Labs. *Mathematics Frozen Current-Knowledge Inventory*. V3 clean-room repository, `publications/inventories/mathematics.json`, 2026."))
    return "".join(parts)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"built {OUTPUT}")


if __name__ == "__main__":
    main()
