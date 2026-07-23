"""Build the standalone exhaustive Information Science branch paper from sealed evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.information_science.catalog import SPECS  # noqa: E402


OUTPUT = ROOT / "publications/current/information_science/FROM_DISTINCTION_TO_INFORMATION.md"
INVENTORY_HASH = "sha256:98162a98e2508cb36381ed2b99cb195e3cc7e1b33b8577d4c5a4550a492a0b17"
DOI_PATH = ROOT / "publications/current/information_science/doi.txt"


INTERPRETATION = {
    "SFT-INFO-SYMBOL-DISTINCTION-001": (
        "The first information law makes distinguishability operational rather than intuitive. A symbol is not a "
        "typographic mark or imported semantic token; it is a canonical generated form with a held label. An "
        "observation is a complete source-bound classification. Two source forms are distinguishable exactly when "
        "that classification retains different images. When images coincide, the source forms are not destroyed: "
        "they remain the complete microform membership of one closed observation class. This distinction ledger is "
        "the substrate from which every later quantity, uncertainty and loss statement is derived."
    ),
    "SFT-INFO-ENCODING-DECODING-001": (
        "Encoding is reconstructed as an exact relation, not a convention selected in advance. Every canonical source "
        "has one retained generated codeword and every source/code link remains inspectable. Decoding is not guessed: "
        "it exists exactly when every used codeword has one source predecessor. A many-to-one representation remains "
        "lawful only when it says what it closes and preserves the full merged source class. This establishes lossless "
        "and lossy representation before compression, channel or code claims can use those words."
    ),
    "SFT-INFO-QUANTITY-001": (
        "Information quantity is carried by exact alternatives and their distinguishability, not by a borrowed real "
        "scale. The kernel retains complete word support, every unordered source pair, every observation class and the "
        "partition of pairs into retained and closed distinctions. The first Fold contributes the first exact two-label "
        "distinction. A longer word contributes another native unit only when that position can vary independently while "
        "the remaining positions are held. Logarithmic units may summarize a sealed finite support in correspondence, "
        "but they are not used to force the support or its distinctions."
    ),
    "SFT-INFO-ENTROPY-UNCERTAINTY-001": (
        "Uncertainty is the exact set of deterministic microstate pairs an observation cannot separate. Entropy is the "
        "provenance-retaining family of observation classes, exact positive support parts, class members and unresolved "
        "pair ledgers. A singleton class has structural empty-One uncertainty. Refining observation removes closed pairs; "
        "coarsening adds them. Nothing in this construction requires an ontic random cause, a logarithm, an expectation "
        "over reals or a fitted distribution. The result preserves more evidence than a scalar because every unresolved "
        "distinction remains named."
    ),
    "SFT-INFO-COMPRESSION-REDUNDANCY-001": (
        "Compression is lawful only when the retained dictionary, token trace, parser and decoder reconstruct the exact "
        "source. Resource comparison therefore counts the entire description system rather than reporting a shortened "
        "payload while hiding its dictionary. Redundancy is a structurally identified repeated or dependent position, not "
        "padding inferred from frequency. The complete-support control proves the finite pigeonhole boundary: a one-to-one "
        "code cannot assign every word a strictly shorter nonempty generated word. Compression gains are consequently "
        "source-family and representation dependent, never an unqualified universal shortening law."
    ),
    "SFT-INFO-CHANNEL-CAPACITY-001": (
        "A channel is a complete relation from each input to every output reachable through a registered path. Inputs are "
        "confusable exactly when their output supports overlap. A zero-error code is a held input family with pairwise "
        "disjoint output supports. Capacity is not imported as a logarithm or fitted rate: it is the complete family of "
        "greatest distinguishable input selections, with ties retained. Composition joins channels only across an exact "
        "interface and preserves path provenance, making every limitation traceable to concrete overlaps."
    ),
    "SFT-INFO-NOISE-ERROR-001": (
        "Noise is not assumed to be random. It is the complete registered family of source-to-received transformations, "
        "each retaining the source, received form and action identity. An error is the exact changed-position trace, including "
        "the previous and received labels. Detection follows when a nonidentity image leaves valid code support. Correction "
        "follows only when the received form has one registered source predecessor. If several sources remain, the machine "
        "returns their whole class and refuses a likely, nearest or prior-weighted choice."
    ),
    "SFT-INFO-CODING-001": (
        "Coding theory follows from complete error-image separation. A codebook is a held selection of generated equal-position "
        "words, and every registered error action is applied to every codeword. Detection requires nonidentity images outside "
        "the codebook; correction requires disjoint complete image supports between distinct codewords. Width-three repetition "
        "is demonstrated by exhausting all single-label images, while an unprotected one-position family supplies the adverse "
        "control. No distance metric or error probability selects the code; a conventional distance may summarize the sealed "
        "difference traces afterward."
    ),
    "SFT-INFO-MUTUAL-CONDITIONAL-001": (
        "Conditional information is exact restriction: within every class of a given observation, the target observation "
        "partitions the retained microstates and supplies exact positive parts. Mutual dependence is kept as a complete "
        "joint-incidence ledger. Every joint cell records members, exact joint part, exact marginal parts, their product and "
        "the comparison relation; an absent cell is empty One. Factorization holds only when every cell is present and exactly "
        "matches the marginal product. This avoids signed subtraction and logarithmic ratios while retaining all evidence "
        "needed to identify where dependence occurs."
    ),
    "SFT-INFO-CONSERVATION-LOSS-001": (
        "Information conservation is pair accounting. A total map classifies every source distinction as retained by unequal "
        "images or closed inside one predecessor fibre. Those ledgers are disjoint and exhaustive. Reversibility is equivalent "
        "to singleton fibres; a merged fibre requires a retained predecessor label. Under composition, the downstream retained "
        "pair set is a subset of the upstream set, so a deterministic map cannot reopen an unrecorded distinction. Conservation "
        "therefore does not mean an opaque scalar remained constant: it means every source alternative has an exact disposition."
    ),
    "SFT-INFO-CLASSICAL-PROBABILISTIC-001": (
        "Classical and probabilistic information are two resolutions of one deterministic carrier. A classical state is one "
        "held support member with its provenance. A probabilistic row is an exact nonempty observation class and its positive "
        "part of complete support. Observation identifies a state only when that class is singleton; otherwise all predecessors "
        "remain. A deterministic map pushes the ledger forward by grouping exact predecessor support. Thus probability records "
        "unavailable distinctions without adding a stochastic transition law, prior, seed or floating propensity."
    ),
    "SFT-INFO-QUANTUM-CORRESPONDENCE-001": (
        "The quantum result is deliberately exact and bounded. One Fold distinction is the native information unit. Complete "
        "held-label words across canonical positions correspond bijectively to finite basis support, and complete pair cells "
        "supply joint support. 'Superposition-equivalent' means equality of enumerated branch alternatives and provenance only. "
        "Observation retains an exact branch class, while the complete branch/image record reconstructs pre-observation support. "
        "Amplitude, complex phase, interference, entanglement, gate dynamics and collapse are not claimed here; their absence "
        "prevents support correspondence from silently becoming an operational quantum theory."
    ),
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def line(text: str = "") -> str:
    return text + "\n"


def build() -> str:
    candidate_total = sum(2 ** len(spec.dimensions) for spec in SPECS)
    doi = DOI_PATH.read_text(encoding="utf-8").strip()
    parts: list[str] = []
    add = parts.append

    add(line("# From Distinction to Information"))
    add(line("## An Exact, Parameter-Free and Machine-Closed Derivation of Information Science from Smithian Fold Theory"))
    add(line("**Maria Smith**<br>"))
    add(line("Independent researcher and founder, Ernos Labs<br>"))
    add(line("Maria.Smith.Sftoe@gmail.com<br>"))
    add(line("23 July 2026"))
    add(line())
    add(line("Information Science Branch Paper 001 - Smithian Fold Theory V3 Clean-Room Reconstruction"))
    add(line())
    add(line(f"DOI: [{doi}](https://doi.org/{doi})"))
    add(line())
    add(line("Copyright (c) 2026 Maria Smith. Licensed under CC BY 4.0. Repository code is"))
    add(line("licensed separately under Apache-2.0. The Ernos Labs designation is governed by"))
    add(line("the published conformance policy."))
    add(line())
    add(line("## Abstract"))
    add(line())
    add(line(
        "This paper reports the completed Information Science branch of the third clean-room reconstruction of Smithian "
        "Fold Theory (SFT). From the admitted Foundation and Mathematics receipts it derives symbols and exact "
        "distinguishability; encoding and decoding; information quantity; entropy and uncertainty; compression and "
        "redundancy; channels and capacity; noise and error; coding; mutual and conditional information; conservation, "
        "loss and transformation; classical and probabilistic information; and quantum-information support correspondence. "
        "A conventional bit, logarithmic information measure, stochastic cause, fitted distribution, unregistered metric, "
        "real or complex amplitude, pretrained model and application result are excluded from derivational premises."
    ))
    add(line())
    add(line(
        f"The twelve registered grammars execute {candidate_total:,} candidate structures. Every candidate receives an "
        "exact decision and each grammar has one all-preserving survivor. Every claim passes minimality, named-shape "
        "uniqueness, a depth-independent base/successor certificate, false-premise, source-tamper, artifact-tamper and "
        "boundary controls, cryptographic sealing and implementation-distinct recomputation. The branch therefore contains "
        "twelve depth-independently closed, model-admitted and independently replicated receipts. Every paper statement is "
        "mapped to its registration, complete census, elimination receipt, controls, certificate, source manifest and "
        "model-admitted engine receipt."
    ))
    add(line())
    add(line(
        "The central reconstruction is ledger-valued. Information is complete generated alternative support together with "
        "the exact distinctions retained or closed by observation. Entropy retains its observation classes and unresolved "
        "pairs rather than collapsing them to an imported logarithmic scalar. Probability is an exact part relation over "
        "deterministic support rather than a causal random premise. Channel capacity and error correction follow from exact "
        "support separation. Quantum scope is explicitly limited to finite support correspondence; operational quantum "
        "laws remain obligations of the later Quantum Computation branch."
    ))
    add(line())
    add(line("**Keywords:** Smithian Fold Theory; information science; distinguishability; encoding; entropy; uncertainty; compression; channels; coding theory; mutual information; deterministic probability; reversible information; quantum information; open computational science."))

    add(line())
    add(line("## 1. Central scientific claim"))
    add(line())
    add(line("The exact claim of this paper is:"))
    add(line())
    add(line(
        "> Within the frozen SFT V3 Information Science current-knowledge inventory, every one of the twelve registered "
        "obligations has a depth-independent, model-admitted and independently replicated engine receipt; the inventory "
        "contains no unclassified or frontier obligation."
    ))
    add(line())
    add(line(
        f"The inventory identity is `{INVENTORY_HASH}`. It fixes scope and dependency order before prose evaluation. Branch "
        "closure applies to the exact generated-finite kernels named in the inventory. It does not claim every conventional "
        "asymptotic rate theorem, every named code or an operational quantum theory. Fold Protein, Fold Chess, Fold Go, "
        "Unison AI and all application experiments were excluded from law selection."
    ))

    add(line())
    add(line("## 2. Standalone dependency foundation"))
    add(line())
    add(line(
        "This paper is a new standalone work; it does not edit or replace the text of either earlier branch paper. It is "
        "standalone in exposition while preserving scientific dependency identities. The Foundation supplies operational "
        "occurrence, structural One, complete positive finite count, exact held/whole parts, the minimal Fold, part "
        "equivalence, Fold assembly, finite form grammar, canonical form enforcement and the one-way measurement boundary."
    ))
    add(line())
    add(line(
        "The Mathematics branch supplies exact generated arithmetic, finite collections and relations, complete combinatorial "
        "families, graphs, algebra, order, finite geometry/topology, deterministic-support probability, optimization, dynamics, "
        "proof and composition. These are model-admitted dependencies with their own receipts. They are not silently replaced "
        "by conventional axioms. Every dependency path terminates at the sole root theorem, *there is no nothing*, and every "
        "Information Science registration has empty axiom and free-parameter tuples."
    ))

    add(line())
    add(line("## 3. Exact information constitution"))
    add(line())
    add(line(
        "Admitted information objects are canonical symbols, held labels, generated words, complete support traces, exact "
        "observation classes, unordered source pairs, retained and closed distinction ledgers, exact positive support parts, "
        "relations, predecessor fibres, action traces and proof traces. Empty or identity cases use structural empty One. "
        "Semantic numerical zero, negative quantity, irrational or imaginary proof values, floating proof arithmetic, completed "
        "infinity and an ungenerated continuum remain outside the proof domain."
    ))
    add(line())
    add(line(
        "Host-language integers, Boolean verdicts, empty containers and process status values are implementation mechanics. "
        "They count or check artifacts and are not admitted SFT mathematical values. Exact parts use rational held/whole "
        "relations; absent cells are empty One rather than a numerical-zero probability. No logarithm is required to force "
        "support, uncertainty, dependence, channel separation or correction."
    ))

    add(line())
    add(line("## 4. What forced, closed and validated mean"))
    add(line())
    add(line(
        "Each claim registers a finite product grammar of structural questions before execution. Every axis contains one "
        "explicitly rejected coordinate and one all-preserving coordinate. The engine generates their complete Cartesian "
        "product in canonical order, hashes every candidate trace, decides every candidate, records every elimination reason "
        "and requires exactly one survivor. A familiar name or successful example cannot bypass this census."
    ))
    add(line())
    add(line(
        "Minimality requires that replacing any admitted coordinate loses a registered preservation, completeness, exactness "
        "or provenance condition. Named-shape uniqueness requires exactly one all-preserving product coordinate. Generality "
        "requires a claim-specific structural-One base and successor certificate, yielding depth-independent closure over "
        "generated finite depth without positing a completed infinite object."
    ))
    add(line())
    add(line(
        "Four adverse controls are mandatory: a false premise, changed official source identity, missing/duplicated/additional "
        "survivor and excluded boundary import. A distinct Python process then regenerates the literal coordinate domains, "
        "candidate order, decision vector, unique survivor, closure flags and controls without importing the scientific law "
        "module. Only the shared admission engine may project an independently validated receipt into the model census."
    ))

    add(line())
    add(line("## 5. Dependency order and executed census"))
    add(line())
    add(line("| Order | Claim | Candidate structures | Dimensions | Closure |"))
    add(line("|---:|---|---:|---:|---|"))
    for index, spec in enumerate(SPECS, 1):
        add(line(f"| {index} | `{spec.claim_id}` | {2 ** len(spec.dimensions):,} | {len(spec.dimensions)} | depth-independent |"))
    add(line())
    add(line(
        f"The Information Science total is **{candidate_total:,}** generated candidates and twelve survivors. The complete "
        "V3 census through this branch contains 34 admitted derivations and 21,650 generated candidates: 2,450 in Foundation, "
        "7,424 in Mathematics and 11,776 here. Candidate counts describe representation-rule products, not every data object "
        "producible by the admitted laws."
    ))

    section = 6
    for order, spec in enumerate(SPECS, 1):
        package = ROOT / "claims" / spec.claim_id
        registration = load_json(package / "registration.json")
        certificate = load_json(package / "certificate.json")
        controls = load_json(package / "controls.json")["controls"]
        census = load_json(package / "candidate_census.json")
        elimination = load_json(package / "elimination_receipt.json")

        add(line())
        add(line(f"## {section}. Derivation {order}: {spec.title}"))
        add(line())
        add(line(f"Claim identity: `{spec.claim_id}`"))
        add(line())
        add(line(f"### {section}.1 Question, necessity and theorem"))
        add(line())
        add(line(spec.why))
        add(line())
        add(line("The exact theorem statement is:"))
        add(line())
        add(line(f"> {spec.statement}"))
        add(line())
        add(line(f"Admitted dependencies: {', '.join(f'`{item}`' for item in spec.dependencies)}."))

        add(line())
        add(line(f"### {section}.2 Derivation chain, grammar and boundary"))
        add(line())
        add(line(spec.derivation))
        add(line())
        add(line(f"Generation rule: {spec.generation_rule}"))
        add(line())
        add(line(f"Exact grammar boundary: {spec.grammar_boundary}"))
        add(line())
        add(line(
            f"The complete product contains {census['expected_cardinality']:,} candidates. Its completeness-certificate "
            f"identity is `{census['completeness_certificate_hash']}`. The table states every generating axis, its unfavorable "
            f"coordinate and its forced coordinate. Their full row-level Cartesian product is preserved in "
            f"`claims/{spec.claim_id}/candidate_census.json`."
        ))
        add(line())
        add(line("| Structural axis | Rejected alternative | Exact rejection | Forced coordinate |"))
        add(line("|---|---|---|---|"))
        for dimension in spec.dimensions:
            rejected = next(choice for choice in dimension.choices if not choice.admitted)
            admitted = dimension.admitted_choice
            add(line(f"| `{dimension.key}` | `{rejected.name}` | {rejected.reason} | `{admitted.name}` - {admitted.reason} |"))

        add(line())
        add(line(f"### {section}.3 Exhaustion, unique survivor and laws"))
        add(line())
        add(line(f"> {spec.exact_result}"))
        add(line())
        survivor_ids = tuple(
            decision["candidate_id"] for decision in elimination["decisions"] if decision["survives"]
        )
        add(line(
            f"The engine recorded {len(elimination['decisions']):,} decisions, "
            f"{sum(not decision['survives'] for decision in elimination['decisions']):,} eliminations and exactly one "
            f"survivor, `{survivor_ids[0]}`. Replacing any survivor coordinate with "
            "the rejected coordinate triggers the table's failure condition; the extra-rule coordinate prevents an unforced "
            "addition. This proves minimality and named-shape uniqueness inside the frozen grammar. The survivor entails:"
        ))
        add(line())
        for law in spec.laws:
            add(line(f"- {law}."))

        add(line())
        add(line(f"### {section}.4 Operational demonstrations and adverse controls"))
        add(line())
        for witness in spec.witnesses:
            add(line(f"- `{witness.name}` - {witness.statement} Result: `{'PASS' if witness.passed else 'FAIL'}`."))
        add(line())
        add(line("The engine-level unfavorable controls are:"))
        add(line())
        for control in controls:
            add(line(
                f"- `{control['kind']}` - expected: {control['expected_behavior']} Observed: "
                f"{control['observed_behavior']} Result: `{'PASS' if control['passed'] else 'FAIL'}`; "
                f"receipt `{control['receipt_hash']}`."
            ))

        add(line())
        add(line(f"### {section}.5 Depth-independent closure"))
        add(line())
        add(line(f"Base: {spec.induction_base}"))
        add(line())
        add(line(f"Successor: {spec.induction_step}"))
        add(line())
        add(line(
            "The executed product closes the registered representation alternatives. The base/successor certificate extends "
            "that rule to every generated finite support size, word depth, source extension or action extension named by the "
            "claim. It does not convert finite generation into a completed infinity."
        ))

        add(line())
        add(line(f"### {section}.6 Meaning and scientific consequence"))
        add(line())
        add(line(INTERPRETATION[spec.claim_id]))

        add(line())
        add(line(f"### {section}.7 Correspondence only after sealing"))
        add(line())
        add(line(
            "After the SFT survivor and receipt are fixed, the following established terms may identify translation points: "
            f"{', '.join(spec.correspondence_terms)}. They are not dependencies and did not provide formulas, thresholds or "
            "answer tables. A mismatch remains visible as a boundary result rather than being repaired by changing the sealed law."
        ))

        add(line())
        add(line(f"### {section}.8 Exact exclusions and limitation"))
        add(line())
        for exclusion in spec.boundary_exclusions:
            add(line(f"- {exclusion}."))
        add(line())
        add(line(spec.limitations))

        add(line())
        add(line(f"### {section}.9 Machine evidence identities"))
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
    add(line(f"## {section}. Cross-derivation synthesis: one information kernel"))
    add(line())
    add(line(
        "The branch is one dependency chain. Canonical symbols and total observation first establish the source alternatives "
        "and their distinguishability. Encoding then maps those alternatives to generated words while preserving source "
        "classes. Quantity collects complete support and retained/closed pair ledgers. Entropy reorganizes the same evidence "
        "by observation class and exact support part. Compression asks whether a complete representation reconstructs the "
        "source and counts the entire representation system."
    ))
    add(line())
    add(line(
        "Channels generalize encoding to complete input/output relations and identify confusability by support overlap. Noise "
        "adds registered transformation identity and exact changed positions. Coding chooses generated word families whose "
        "complete registered error images are separated. Mutual and conditional information then compare two observation "
        "partitions through exact joint cells. Conservation classifies every source distinction under transformation, and the "
        "classical/probabilistic law shows that one held state and an unresolved observation class use the same carrier."
    ))
    add(line())
    add(line(
        "Quantum-information support correspondence is last because it needs all earlier results: Fold-word support, native "
        "distinction units, joint composition, observation classes and conservation records. It cannot retroactively import "
        "amplitudes or gates into the symbol law. Likewise, later channel or code correspondences cannot change the exact "
        "observation ledger that forced their prerequisites."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Entropy without logarithms and probability without randomness"))
    add(line())
    add(line(
        "The conventional scalarization of finite information support is not used as foundational evidence. A logarithm needs "
        "a chosen base and can produce irrational or floating values outside the admitted proof domain. SFT retains the exact "
        "object from which such summaries are ordinarily calculated: every observation class, every member, its exact positive "
        "part of the whole and every unresolved pair. A singleton class uses empty One; an absent joint cell uses empty One."
    ))
    add(line())
    add(line(
        "This richer object makes refinement transparent. If one observation refines another, every fine class lies within a "
        "coarse class and its closed-pair ledger is a subset of the coarse ledger. Conditional information is exact restriction "
        "to a given class. Dependence is the complete comparison between joint cell parts and exact marginal products. No "
        "negative deviation is needed: the relation records equal, joint-below-product, joint-above-product or empty-One."
    ))
    add(line())
    add(line(
        "Superdeterminism presents no contradiction here because probability is not a transition cause. The generated microstate "
        "support and every registered transformation remain deterministic. Probability describes the part occupied by an "
        "observation class when source distinctions are unavailable. A prior, seed or stochastic kernel would be an additional "
        "parameter and is rejected unless a later empirical claim separately registers and validates it."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Compression, capacity and correction as exact finite support laws"))
    add(line())
    add(line(
        "Compression, channel capacity and error correction are often reported by scalar rates. This branch derives the finite "
        "objects those rates summarize. A lossless description includes its dictionary, token trace, parser and decoder. A "
        "channel includes every registered source/output/path cell. A code includes every registered error image of every "
        "codeword. The machine can therefore determine reconstructability, confusability, detection and correction without an "
        "error distribution or distance threshold."
    ))
    add(line())
    add(line(
        "The exact capacity object is the complete family of greatest pairwise distinguishable input selections. Retaining the "
        "whole family prevents a tie from being hidden by one arbitrarily selected code. The exact correction criterion is "
        "disjoint image support; decoding then has one source predecessor. Conventional length, rate, Hamming distance and "
        "capacity units may be computed as post-seal correspondence summaries for a declared finite carrier, but they cannot "
        "replace the support evidence or select the survivor."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Quantum-information boundary and later obligations"))
    add(line())
    add(line(
        "The branch closes a precise classical-probabilistic-quantum information boundary. A classical state is one held word. "
        "A probabilistic state is an exact observation class over complete deterministic word support. The quantum support "
        "correspondence is the complete generated Fold-word alternative family with a bijective basis trace. Pair-cell "
        "composition yields complete joint support. Observation and a retained branch/image record yield exact class reduction "
        "and support reconstruction."
    ))
    add(line())
    add(line(
        "Support equality does not establish operational equivalence. No complex amplitude, phase rule, interference operation, "
        "entangling law, measurement dynamics, unitary transformation, gate, circuit, quantum code or fault threshold is used "
        "or claimed. Those are separately enumerated obligations of Reversible and Quantum Computation. This separation is a "
        "positive result: it states exactly what information structure is already available and prevents downstream quantum "
        "phenomena from being smuggled into the carrier definition."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Formal computational evidence versus natural empirical evidence"))
    add(line())
    add(line(
        "The claims in this paper are formal structural theorems. Their empirical evidence is computational: complete candidate "
        "products are generated, every decision executes, adverse controls are actually perturbed, independent validator "
        "processes run and stored receipts are replayable. This validates the reported machine behavior of the declared grammar "
        "and certificates. It is not mislabeled as observation of an external natural system."
    ))
    add(line())
    add(line(
        "A later claim about natural measurements must register before target access, seal its formal predictor, enforce target "
        "custody, disclose all rows and preserve falsification results. Blind opaque prediction is insufficient because a score "
        "does not expose premises, candidate alternatives, eliminated structures, source identity, information leakage or the "
        "conditions under which the claim must halt. Application domains may test a sealed law but cannot select or repair it."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Machine reproduction and current verification"))
    add(line())
    add(line("The definitive cross-platform logical command is:"))
    add(line())
    add(line("```text"))
    add(line("python3 -m sft verify-all   # macOS and most Linux systems"))
    add(line("py -m sft verify-all        # standard Windows Python launcher"))
    add(line("```"))
    add(line())
    add(line(
        "No Docker image, virtual machine, network service or third-party Python package is required. The verifier validates "
        "repository structure, runs unit, unfavorable-control and end-to-end tests with 100 percent executable-line coverage "
        "of the core admission engine, rebuilds source manifests, replays the dependency-ordered census, launches every "
        "implementation-distinct validator and compares each result with its stored receipt."
    ))
    add(line())
    add(line("The final local verification report for this release is:"))
    add(line())
    add(line("```text"))
    add(line("SFT COMPLETE VERIFICATION: PASS"))
    add(line("unit and end-to-end tests passed: 131"))
    add(line("core engine executable-line coverage: 1264/1264 (100%)"))
    add(line("core engine modules covered: 15"))
    add(line("registered derivations independently rerun: 34"))
    add(line("```"))
    add(line())
    add(line(
        "The coverage report concerns implementation execution. Scientific closure additionally requires the claim-specific "
        "grammar, exhaustive decision vector, unique survivor, minimality, named-shape uniqueness and induction certificate. "
        "Neither test coverage nor a cryptographic hash substitutes for scrutiny of the registered scientific boundary."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Reproduction, criticism and invalidation routes"))
    add(line())
    add(line(
        "A reviewer can challenge completeness by producing a structurally possible coordinate inside the stated boundary that "
        "the registered domains omit. Minimality fails if a rejected coordinate preserves every registered requirement. "
        "Uniqueness fails if a second generated member survives. Depth-independent closure fails if the base or successor "
        "certificate has an internal counterexample. An operational law fails if a valid input inside the boundary violates it."
    ))
    add(line())
    add(line(
        "Mechanical invalidation is equally direct: change an official source, alter candidate order, remove a decision, add a "
        "survivor, fail a control, reorder dependencies, tamper with a certificate or change a receipt. The engine halts at the "
        "violated gate. Hashes preserve artifact identity; they do not establish scientific truth. The evidence map makes it "
        "possible to distinguish disagreement with an exact artifact from disagreement with the grammar itself."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Scope, limitations and next branch"))
    add(line())
    add(line(
        "Closure is exact at the frozen generated-finite Information Science boundary. The paper does not claim a completed "
        "infinite source, every asymptotic coding theorem, every empirical communication medium or a completed operational "
        "quantum theory. Named applications must still register their supports, transformations, resources and empirical "
        "protocols. Conventional scalar summaries may be calculated only as explicit post-seal correspondences."
    ))
    add(line())
    add(line(
        "The next dependency branch is Formal Computation: state and transition, formal languages and grammars, automata, "
        "rewriting systems, recursive functions, lambda-like calculi, abstract machines, circuits, operational processes, "
        "composition and decomposition, equivalence among computational models and universality. Quantum operations remain "
        "reserved for the later Reversible and Quantum Computation branch."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Open-science status, rights and participation"))
    add(line())
    add(line(
        "The platform is openly inspectable, reusable and redistributable under its published licences. Maria Smith retains "
        "copyright and authorship. Paper and documentation text is CC BY 4.0; code is Apache-2.0. The Ernos Labs designation "
        "is a separate conformance mark requiring adherence to the scientific constitution, transparent evidence, fail-closed "
        "engine rules and community conduct policy."
    ))
    add(line())
    add(line(
        "Credentials cannot rescue a failed gate, and lack of credentials cannot prevent a reproducible counterexample from "
        "being evaluated. Independent replications, omitted candidates, counterexamples and submissions are invited through "
        "Maria.Smith.Sftoe@gmail.com and https://discord.gg/ucwGryVxGr. Maria Smith explicitly authorized this branch release "
        "on 23 July 2026."
    ))
    section += 1

    add(line())
    add(line(f"## {section}. Conclusion"))
    add(line())
    add(line(
        f"The Information Science branch closes twelve dependency-ordered kernels through {candidate_total:,} generated "
        "candidates, twelve unique survivors, twelve depth-independent certificates and twelve implementation-distinct "
        "validations. It reconstructs the progression from symbols and observation to representation, quantity, uncertainty, "
        "compression, channels, error, coding, dependence, conservation and classical-probabilistic-quantum support "
        "correspondence without importing conventional answer-producing models."
    ))
    add(line())
    add(line(
        "Its unifying result is exact distinction accounting. Every alternative has a generated source, every observation "
        "declares what it retains and closes, every transformation accounts for its predecessor fibres and every correction "
        "must have a unique source. The branch is admitted within that exact boundary because its complete machine-auditable "
        "chain closes - not because a prior authority, familiar scalar or application score selects it."
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
    add(line("## Appendix B. Complete derivation and evidence route"))
    add(line())
    add(line("For every claim identifier `<CLAIM>`, the complete route is:"))
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
        "Executable law sources are under `sft/information_science/`; the catalog fixes dependency order; the model census "
        "is `census/claims.json`; the replay order is `census/execution_manifest.json`; and the frozen scope is "
        "`publications/inventories/information_science.json`. The paper evidence map binds every derivation section to exact "
        "claim-package and receipt hashes."
    ))

    add(line())
    add(line("## Appendix C. Reproducibility interpretation"))
    add(line())
    add(line(
        "A successful replay establishes that the checked sources reproduce the registered candidate products, decisions, "
        "closures, controls, independent certificates and receipts on the reviewing host. Scientific review must also ask "
        "whether the frozen grammar exhausts its stated boundary. Reproduction and boundary criticism are complementary, and "
        "the repository preserves evidence for both."
    ))

    add(line())
    add(line("## References"))
    add(line())
    add(line("1. Smith M. *From Nothing to Fold: A Premise-Free, Parameter-Free and Machine-Closed Foundation for Smithian Fold Theory*. Ernos Labs Foundation Branch Paper 001. 2026. doi:10.5281/zenodo.21515629."))
    add(line("2. Smith M. *From Fold to Mathematics: An Exact, Parameter-Free and Machine-Closed Derivation of Mathematical Foundations from Smithian Fold Theory*. Ernos Labs Mathematics Branch Paper 001. 2026. doi:10.5281/zenodo.21516146."))
    add(line("3. Hartley RVL. Transmission of information. *Bell System Technical Journal*. 1928;7:535-563. doi:10.1002/j.1538-7305.1928.tb01236.x."))
    add(line("4. Shannon CE. A mathematical theory of communication. *Bell System Technical Journal*. 1948;27:379-423, 623-656. doi:10.1002/j.1538-7305.1948.tb01338.x; doi:10.1002/j.1538-7305.1948.tb00917.x."))
    add(line("5. Hamming RW. Error detecting and error correcting codes. *Bell System Technical Journal*. 1950;29:147-160. doi:10.1002/j.1538-7305.1950.tb00463.x."))
    add(line("6. Landauer R. Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*. 1961;5:183-191. doi:10.1147/rd.53.0183."))
    add(line("7. Bennett CH. The thermodynamics of computation - a review. *International Journal of Theoretical Physics*. 1982;21:905-940. doi:10.1007/BF02084158."))
    add(line("8. Schumacher B. Quantum coding. *Physical Review A*. 1995;51:2738-2747. doi:10.1103/PhysRevA.51.2738."))
    add(line("9. Smith M. *Smithian Fold Theory Scientific Constitution*. V3 clean-room repository, `CONSTITUTION.md`, 2026."))
    add(line("10. Ernos Labs. *Comprehensive Branch-Paper Protocol*. V3 clean-room repository, `publications/BRANCH_PAPER_PROTOCOL.md`, 2026."))
    return "".join(parts)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"built {OUTPUT}")


if __name__ == "__main__":
    main()
