#!/usr/bin/env python3
"""Build the 262-law complete-field Information Science paper without changing scientific authority."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_3.md"
OUT = ROOT / "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md"
CURRENT = ROOT / "publications/current/information_science/FROM_DISTINCTION_TO_INFORMATION.md"
FROZEN = ROOT / "census/information_science_discipline_obligations.json"
RECONCILIATION = ROOT / "census/information_science_discipline_current_reconciliation_v20.json"
CLAIMS = ROOT / "census/claims.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value) -> str:
    return str(value).replace("\n", " ").strip()


def bullets(rows) -> str:
    values = tuple(rows)
    return "\n".join(f"- {clean(row)}" for row in values) if values else "- None."


def current_certificate(package: Path, receipt_hash: str):
    matches = [path for path in sorted(package.glob("certificate*.json")) if read(path).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1:
        raise SystemExit(f"{package.name}: expected one current certificate, found {len(matches)}")
    return read(matches[0])


def claim_section(order: int, family: str, obligation: str, claim_id: str, row: dict) -> str:
    package = ROOT / "claims" / claim_id
    registration = read(package / "registration.json")
    census = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    empirical = read(package / "empirical_validation.json")
    certificate = current_certificate(package, row["receipt_hash"])
    survivors = [item for item in elimination["decisions"] if item["survives"]]
    if len(census["candidates"]) != len(elimination["decisions"]) or len(survivors) != 1:
        raise SystemExit(f"incomplete enumeration: {claim_id}")
    if not all(item["passed"] for item in controls) or not empirical["passed"] or not empirical["all_rows_preserved"]:
        raise SystemExit(f"incomplete controls or observation custody: {claim_id}")
    grammar = registration["candidate_grammar"]
    unique = grammar.get("unique_survivor", survivors[0]["candidate_id"])
    coordinates = unique.split("__")
    control_rows = "\n".join(
        f"- `{item['kind']}` - passed; expected: {clean(item['expected_behavior'])}; observed: {clean(item['observed_behavior'])}; receipt `{item['receipt_hash']}`."
        for item in controls
    )
    measurements = bullets(empirical.get("measurements", ()))
    sources = bullets(f"`{source}`" for source in empirical.get("data_source_ids", ()))
    dependencies = bullets(f"`{dependency}`" for dependency in registration.get("dependencies", ()))
    exclusions = bullets(registration.get("excluded_inputs", ()))
    exact = certificate.get("exact_result", registration.get("statement", ""))
    closure = elimination["closure"]
    return f"""### {order}. {registration['title']}

Family: `{family}`  
Obligation: `{obligation}`  
Claim: `{claim_id}`

**Question, law and forced result.** {clean(registration.get('statement', exact))}

> {clean(exact)}

**Trace to the foundational theorem.** This registration names no axioms and no free parameters. It declares `SFT-ROOT-THERE-IS-NO-NOTHING` as its root theorem and consumes only these already admitted receipt identities:

{dependencies}

The current reconciliation binds this obligation to the current model-admitted receipt `{row['receipt_hash']}`. A missing dependency, stale certificate or broken root trace halts rather than being replaced by prose.

**Complete candidate grammar.** {clean(grammar['generator'])}

Boundary: {clean(grammar['boundary'])}

The literal product contains `{len(census['candidates'])}` candidates and the elimination ledger contains exactly `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives and `{len(elimination['decisions']) - 1}` are eliminated. The forced coordinates are:

{bullets(f'`{coordinate}`' for coordinate in coordinates)}

Unique survivor: `{survivors[0]['candidate_id']}`.

Closure: `{closure['scope']}`; minimality `{str(closure['minimality_passed']).lower()}`; named-shape uniqueness `{str(closure['named_shape_uniqueness_passed']).lower()}`; proof `{closure['proof_hash']}`; generality `{closure['generality_certificate_hash']}`.

**Scientific meaning.** This result is the exact information object named by the claim: its support, relation, retained distinctions, closed distinctions, observation conditions, records, provenance, positive-finite extension and explicit downstream boundary remain attached. It does not replace those records with a score, imported named model, fitted magnitude or consensus label. Structural absence is empty One; host display `0` denotes that absence and is not an SFT numerical object.

**Falsification controls.** All four required controls passed:

{control_rows}

**Independent reconstruction and engine admission.** Independent implementation `{certificate['independent_implementation_hash']}` regenerated the declared census and sole survivor; independent certificate `{certificate['independent_certificate_hash']}`. Derivation seal `{certificate['derivation_seal_hash']}`. Source manifest `{certificate['source_manifest_hash']}`. Engine receipt `{row['receipt_hash']}` at `{row['receipt_path']}`. Closure scope `{row['closure_status']}`. External status `{row['external_status']}`.

**Post-registry observation and comparison.** Target opened after seal: `{str(empirical['target_opened_after_seal']).lower()}`. Evaluator verified seal: `{str(empirical['evaluator_verified_seal']).lower()}`. All rows preserved: `{str(empirical['all_rows_preserved']).lower()}`. Comparison passed: `{str(empirical['passed']).lower()}`.

Source identities:

{sources}

Observed, adverse and boundary records:

{measurements}

Falsification condition: {clean(empirical['falsification_condition'])}

Measurement receipt `{empirical['measurement_receipt_hash']}`; empirical validation `{certificate['empirical_validation_hash']}`; external validation `{certificate['external_validation_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.

**Prohibited inputs.**

{exclusions}
"""


def main():
    frozen = read(FROZEN)
    reconciliation = read(RECONCILIATION)
    live = {row["claim_id"]: row for row in read(CLAIMS)["claims"]}
    if reconciliation["current_closed_count"] != 262 or reconciliation["frozen_obligation_count"] != 262 or reconciliation["current_open_count"] != 0:
        raise SystemExit("Information Science complete-field reconciliation is not 262/262")
    mapping = {}
    for rows in reconciliation["completed_families"].values():
        for row in rows:
            mapping[row["obligation_id"]] = row["claim_id"]
    if len(mapping) != 262 or any(item["obligation_id"] not in mapping for item in frozen["obligations"]):
        raise SystemExit("Information Science obligation-to-receipt map is incomplete")

    base = BASE.read_text(encoding="utf-8")
    body_start = base.index("## Public scientific mission and admission boundary")
    body_end = base.index("## 24. External validation at the correct evidential boundary")
    preserved = base[body_start:body_end].rstrip()
    preserved = preserved.replace(
        "Within the frozen SFT V3 Information Science current-knowledge inventory, every one of the twelve registered obligations has a depth-independent, model-admitted and independently replicated engine receipt; all 77 Information Science-owned V1/V2 atomic obligations are closed at equal strength; the inventory contains no unclassified, open or frontier obligation.",
        "Within the frozen SFT V3 Information Science current-knowledge census, all 262 registered obligations have depth-independent, model-admitted and independently reconstructed engine receipts; all 77 Information Science-owned V1/V2 atomic obligations remain closed at equal strength; no obligation in the dated census remains open, while lawful versioned extension remains permitted.",
    )
    preserved = preserved.replace(
        "The inventory identity is `sha256:98162a98e2508cb36381ed2b99cb195e3cc7e1b33b8577d4c5a4550a492a0b17`. It fixes scope and dependency order before prose evaluation. Branch closure applies to the exact generated-finite kernels named in the inventory. It does not claim every conventional asymptotic rate theorem, every named code or an operational quantum theory.",
        f"The complete-field census identity is `{frozen['census_identity']}` and the terminal reconciliation identity is `{reconciliation['reconciliation_identity']}`. They fix scope, ownership and dependency order before prose evaluation. Dated completeness applies to the exact generated-finite laws named in the census and remains open to lawful versioned discovery; operational quantum dynamics remains with its owning branch.",
    )
    preserved = preserved.replace("## 5. Dependency order and executed census", "## 5. Foundational BASE dependency order and executed census")
    preserved = preserved.replace(
        "The Information Science total is **11,776** generated candidates and twelve survivors. The complete V3 census through this branch contains 34 admitted derivations and 21,650 generated candidates: 2,450 in Foundation, 7,424 in Mathematics and 11,776 here. Candidate counts describe representation-rule products, not every data object producible by the admitted laws.",
        "The foundational BASE kernel contains **11,776** generated candidates and twelve survivors. The complete-field extension documented below adds 250 separately admitted laws. Across the dated branch the exact total is **75,776** candidates and decisions, 262 unique survivors and 1,048 passing adverse controls. Candidate counts describe complete grammar products, not every data object producible by the laws.",
    )
    preserved = preserved.replace("Version 1.2 preserves", "Version 1.4 preserves")

    family_rows = "\n".join(
        f"| `{family}` | {frozen['family_counts'][family]} | {len(reconciliation['completed_families'][family])}/{frozen['family_counts'][family]} |"
        for family in frozen["family_order"]
    )
    front = f"""# From Distinction to Information

## An Exact, Parameter-Free and Machine-Closed Derivation of the Complete Dated Information Sciences from Smithian Fold Theory

**Maria Smith**  
Independent researcher and founder, Ernos Labs  
Maria.Smith.Sftoe@gmail.com  
29 July 2026

Information Science Branch Paper 001 - Version 1.4 - Complete-field Smithian Fold Theory V3 Clean-Room Reconstruction

DOI concept chain: [10.5281/zenodo.21627717](https://doi.org/10.5281/zenodo.21627717)

Copyright (c) 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. Authorship and creative rights are retained. The Ernos Labs name is a separate revocable standards-conformance designation.

## Abstract

This paper reports the complete dated Information Science reconstruction in Smithian Fold Theory V3: 262 of 262 frozen obligations admitted through the unchanged engine, with no free or fitted parameter, no imported axiom, no stochastic cause, no numerical-zero ontology, no negative proof quantity, no irrational or imaginary proof value, no floating proof arithmetic and no application-selected law. The branch executes 75,776 exact candidate structures and decisions, retains 262 unique survivors, passes 1,048 adverse controls and supplies 262 implementation-distinct reconstructions. The 250 complete-field successor laws additionally carry post-registry observation packages; the twelve foundational laws retain their original independently reconstructed receipts and are included in the later complete validation vector.

The reconstruction covers symbols, distinguishability and representation; records and provenance; source, process, sequence, spatial and network information; exact measures; signals, sampling and quantization; lossless and bounded-loss compression; channel structure and capacity; noise and error; block, convolutional, network, erasure and adversarial coding; conditional, mutual, directed and shared-information relations; sufficient records and coarse-graining; retrieval and knowledge organization; inference, filtering and estimation; privacy and leakage; information thermodynamics; classical, deterministic-probabilistic and quantum-support correspondence; semantic/reference boundaries; empirical/formal validation; and one-owner cross-branch handoffs.

The central scientific object is not a borrowed scalar. Information is complete generated alternative support together with exact records of what an observation retains, what it closes, how it transforms and what record is required to reverse a merge. Entropy is the full observation-class and unresolved-distinction ledger. Probability is an exact part of deterministic support rather than an uncaused transition. Compression, capacity and correction are exact finite separation laws. Semantic records preserve symbol, reference and context without replacing biological function, cognition or lived qualia. The branch is complete to its frozen dated census and explicitly open to lawful extension.

**Keywords:** Smithian Fold Theory; information science; distinguishability; representation; entropy; uncertainty; compression; channel capacity; noise; coding theory; inference; privacy; information thermodynamics; deterministic probability; quantum information; semantic information; computational proof; open science.

## Results first: the complete information sciences from one exact distinction ledger

| Headline finding | Exact result | Scientific meaning |
|---|---|---|
| Complete dated reconstruction | `262/262` obligations, `20/20` families, `0` open (display `0` denotes absence) | Every frozen question has its own current engine receipt; future discoveries append by version rather than rewriting the record. |
| Exact exhaustive forcing | `75,776` candidates and decisions; `262` sole survivors | Each law survives a complete declared grammar, not fitting, authority, familiarity or target feedback. |
| Falsification and replication | `1,048` passing adverse controls; `262` implementation-distinct reconstructions | False premise, changed source, tampered artifact and boundary import are executable halts, not rhetorical caveats. |
| Information and entropy | Complete support plus retained/closed distinctions; entropy retains every exact observation class and unresolved pair | Uncertainty remains inspectable without importing a logarithm, stochastic cause or floating distribution. |
| Compression, channels and codes | Reconstructible descriptions, complete transport relations, exact confusability classes and disjoint error-image correction | Capacity and recovery are forced by finite support structure; all ties, collisions and adverse images remain visible. |
| Relations, inference and retrieval | Joint-incidence, conditional restriction, coarse-graining, query, ranking, relevance and estimator records retain full provenance | A result cannot hide the observations, contexts or exclusions that produced it. |
| Privacy and thermodynamics | Leakage is retained distinction access; irreversible merging requires predecessor custody for reversal | Maxwell-demon and Landauer/Bennett boundaries become exact information accounting rather than untracked gain or erasure. |
| Classical-probabilistic-quantum correspondence | One held word, an unresolved deterministic class and complete quantum basis support share one exact carrier at their declared boundary | Operational phase, gates, entanglement and fault tolerance remain correctly owned by Quantum Computation. |
| Semantic and lived-experience boundary | Symbol-reference-context records are exact; cognition, consciousness, qualia and red-of-red remain named downstream handoffs | Information quantity does not erase or pretend to replace subjective experience. |
| Empirical/formal Grand Lock | All 244 pre-lock receipts and 976 controls are bound before the twelve validation receipts; six terminal handoffs complete the 262-row ledger | Favorable, adverse, absent, unresolved and scoped-boundary records are preserved under unchanged authority. |

## Complete dependency-ordered family census

| Family | Frozen obligations | Current receipts |
|---|---:|---:|
{family_rows}

"""

    grouped = []
    order = 13
    extension_obligations = frozen["obligations"][12:]
    for family in frozen["family_order"][1:]:
        obligations = [item for item in extension_obligations if item["family"] == family]
        grouped.append(f"## Complete-field family: {family}\n")
        for item in obligations:
            claim_id = mapping[item["obligation_id"]]
            grouped.append(claim_section(order, family, item["obligation_id"], claim_id, live[claim_id]))
            order += 1
    if order != 263:
        raise SystemExit(f"expected 262 claim sections, ended at {order - 1}")

    tail = f"""## External observation and validation at the correct evidential boundary

Empirical means based on observation or experiment. For this formal branch, the directly observable objects are exact generated symbol carriers, records, channel relations, execution traces, error images, reconstruction results, receipt identities and controlled perturbations. Every successor claim freezes a value-free target identity before opening its observation vector, executes the law, preserves all rows and binds the comparison to an engine receipt. Where an information law later produces a natural measured magnitude, the owning physical, biological, social or engineering branch must preregister and compare that magnitude against authoritative external data; this branch cannot invent a measurement value or pre-approve the downstream result.

Opaque prediction is not an admissible substitute. A score without premises, candidate space, eliminated alternatives, source identity, target custody, adverse rows and halt conditions hides the distinctions required to reproduce or falsify the claim. Conventional Hartley, Shannon, Hamming, Landauer, Bennett and Schumacher language is therefore used only after sealing as a declared correspondence boundary. It does not select the Fold carrier, its exact parts or its laws.

The complete validation family binds all 244 pre-lock claims, all current certificates and all 976 pre-lock controls. The terminal HAND family then establishes single-owner downstream dependencies, formal/measurement separation, sealed formal-to-empirical order, conventional correspondence, open extension and cross-branch completeness. Reconciliation v20 records all 262 obligations under identity `{reconciliation['reconciliation_identity']}`.

## Information power, open knowledge and institutional accountability

Ernos Labs is an open-source science movement, verification platform and public tree of knowledge founded by Maria Smith. It does not ask the public to exchange one inaccessible authority for another. Scientific authority is deliberately narrow, inspectable and revocable: a claim enters this corpus only with its derivation chain, generated alternatives, elimination ledger, unique survivor, adverse controls, observation custody, independent reconstruction and unchanged-engine receipt. Open criticism requires no permission. Admission to the scientific corpus is the separate act of satisfying that public standard.

Maria Smith produced this programme outside conventional academic credentials, institutional research employment and grant funding. That fact is not evidence for a theorem; the derivations and observations carry the scientific burden. It is evidence about access. A credential-first, capital-dependent knowledge system does not merely deny individuals opportunity: it loses unknown questions, methods and discoveries from minds it never authorizes to speak. The significance is therefore not special pleading for one author. It is an indictment of every contribution lost when financial and status gates are dressed as scientific rigor.

Paywalls, inaccessible datasets, undisclosed training corpora, proprietary validators and black-box oracle scores close precisely the source distinctions required for independent falsification. Funding, prestige, publication and consensus systems can carry expertise and resources, but none is itself a proof or empirical receipt. Ernos Labs argues for transparent, reproducible and freely inspectable science in which institutions and independent researchers meet the same evidential burden.

Maria Smith retains copyright, scientific authorship and creative rights. CC BY 4.0 permits reading, copying, redistribution, criticism, reproduction and derivative scholarship with attribution; Apache-2.0 governs the code. The “Ernos Labs” designation is separate and revocable: a fork may use the openly licensed work, but may describe itself as Ernos Labs only while it preserves the public empirical constitution, complete adverse evidence, unchanged admission route, critical review and community standards.

## Reproduction, falsification and extension boundary

This complete-field paper is a read-only projection of the claim packages. It does not modify a derivation, verifier, engine receipt or authority seal. Local preparation requires the v20 reconciliation, exact replay of the final HAND family, all focused Information Science tests, lightweight repository validation and both immutable seals. The heavy all-branch command remains reserved for the final global Grand Lock and is not misrepresented as rerun for this paper preparation.

The branch is complete to the registered 29 July 2026 census, not permanently closed. A lawful new result may correct a correspondence, falsify an empirical claim or add a new obligation. It must be preregistered, completely enumerated, independently reconstructed, passed through the same untouched engine, externally compared wherever possible and appended by a versioned reconciliation. Prior receipts remain reproducible historical evidence; they are not silently invalidated or rewritten.

## Conclusion

The complete dated Information Science branch now exposes a continuous, machine-auditable route from the premise-free Fold theorem to 262 separately admitted information laws. Its substantive unification is exact distinction custody: symbols, descriptions, uncertainty, channels, errors, codes, dependence, inference, privacy, thermodynamic records, deterministic probability, quantum support and semantic boundaries are different organizations of the same complete support-and-observation structure. Its methodological claim is equally concrete: trust in Maria Smith, Ernos Labs, an institution or an AI system is unnecessary where the grammar, decisions, controls, sources, receipts and falsifiers are public.

## Publication and repository links

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions and open review: https://discord.gg/ucwGryVxGr
- Paper license: CC BY 4.0; code license: Apache-2.0; authorship and creative rights retained.

## References

- Hartley, R. V. L. *Transmission of Information*. Bell System Technical Journal (1928).
- Shannon, C. E. *A Mathematical Theory of Communication*. Bell System Technical Journal (1948).
- Hamming, R. W. *Error Detecting and Error Correcting Codes*. Bell System Technical Journal (1950).
- Landauer, R. *Irreversibility and Heat Generation in the Computing Process*. IBM Journal of Research and Development (1961).
- Bennett, C. H. *Logical Reversibility of Computation*. IBM Journal of Research and Development (1973).
- Schumacher, B. *Quantum Coding*. Physical Review A (1995).
- UNESCO. *Recommendation on Open Science* (2021).
- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21627717.
"""
    result = front + preserved + "\n\n" + "\n\n".join(grouped) + "\n\n" + tail
    result = result.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(result.rstrip() + "\n", encoding="utf-8")
    CURRENT.write_text(result.rstrip() + "\n", encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)} with 262 complete claim sections")


if __name__ == "__main__":
    main()
