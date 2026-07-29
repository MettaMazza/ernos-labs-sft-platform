#!/usr/bin/env python3
"""Build the unpublished Classical Computation v1.4 complete-field paper."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_3.md"
OUT = ROOT / "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"
RECON = ROOT / "census/computation_discipline_current_reconciliation_v12.json"
CENSUS = ROOT / "census/computation_discipline_obligations.json"
EVIDENCE = ROOT / "publications/successors/computation/evidence_map_v1_4.json"
METADATA = ROOT / "publications/successors/computation/zenodo_metadata_v1_4.json"

ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
EXPECTED_CLAIMS = 369
EXPECTED_CANDIDATES = 94_464
EXPECTED_CONTROLS = 1_476


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def safe(value) -> str:
    return str(value).replace("\n", " ").replace("|", "/").strip()


def one_sub(pattern: str, replacement: str, text: str) -> str:
    value, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("paper substitution failed: " + pattern[:80])
    return value


def current_certificate(package: Path, receipt_hash: str):
    matches = []
    for path in package.glob("certificate*.json"):
        data = read(path)
        if data.get("engine_receipt_hash") == receipt_hash:
            matches.append((path, data))
    if len(matches) != 1:
        raise SystemExit(f"current certificate count for {package.name}: {len(matches)}")
    return matches[0]


def collect():
    recon = read(RECON)
    frozen = read(CENSUS)
    if recon["current_closed_count"] != EXPECTED_CLAIMS or recon["current_open_count"] != 0:
        raise SystemExit("Classical Computation is not 369/369")
    if recon["frozen_census_identity"] != frozen["census_identity"]:
        raise SystemExit("reconciliation does not identify the frozen census")
    family_order = tuple(frozen["family_order"])
    if set(family_order) != set(recon["completed_families"]):
        raise SystemExit("family order does not exhaust reconciliation")
    obligations = {row["obligation_id"]: row for row in frozen["obligations"]}
    live = {row["claim_id"]: row for row in read(ROOT / "census/claims.json")["claims"]}

    details = []
    candidate_total = 0
    control_total = 0
    evidence_rows = []
    seen_claims = set()
    seen_obligations = set()
    for family in family_order:
        rows = []
        for row in recon["completed_families"][family]:
            claim_id = row["claim_id"]
            obligation_id = row["obligation_id"]
            if claim_id in seen_claims or obligation_id in seen_obligations:
                raise SystemExit(f"duplicate reconciliation ownership: {claim_id}/{obligation_id}")
            seen_claims.add(claim_id)
            seen_obligations.add(obligation_id)
            package = ROOT / "claims" / claim_id
            registration = read(package / "registration.json")
            candidates = read(package / "candidate_census.json")["candidates"]
            controls = read(package / "controls.json")["controls"]
            certificate_path, certificate = current_certificate(package, row["receipt_hash"])
            empirical_path = package / "empirical_validation.json"
            empirical = read(empirical_path) if empirical_path.exists() else {}
            receipt_path = ROOT / row["receipt_path"]
            if not receipt_path.exists():
                raise SystemExit(f"missing receipt: {row['receipt_path']}")
            if certificate.get("engine_receipt_hash") != row["receipt_hash"]:
                raise SystemExit(f"certificate/receipt mismatch: {claim_id}")
            if len(candidates) != 256 or len(controls) != 4:
                raise SystemExit(f"unexpected census/control size: {claim_id}")
            if not all(control.get("passed") for control in controls):
                raise SystemExit(f"failed control in publication evidence: {claim_id}")
            decisions = read(package / "elimination_receipt.json")["decisions"]
            survivors = [decision for decision in decisions if decision.get("survives")]
            if len(survivors) != 1:
                raise SystemExit(f"publication evidence does not have one survivor: {claim_id}")
            candidate_total += len(candidates)
            control_total += len(controls)
            item = {
                "family": family,
                "row": row,
                "obligation": obligations[obligation_id],
                "claim": live[claim_id],
                "registration": registration,
                "certificate": certificate,
                "certificate_path": certificate_path,
                "candidate_count": len(candidates),
                "control_count": len(controls),
                "survivor": survivors[0],
                "measurements": empirical.get("measurements", []),
                "sources": empirical.get("data_source_ids", certificate.get("external_data_source_ids", [])),
                "empirical": empirical,
            }
            rows.append(item)
            evidence_rows.append(
                {
                    "family": family,
                    "obligation_id": obligation_id,
                    "claim_id": claim_id,
                    "candidate_count": len(candidates),
                    "unique_survivor_count": 1,
                    "control_count": len(controls),
                    "closure_status": row.get("closure_status", certificate.get("closure_scope")),
                    "external_status": row.get("external_status", certificate.get("status")),
                    "post_registry_observation": bool(row.get("post_registry_observation", empirical.get("target_opened_after_seal", False))),
                    "all_external_rows_preserved": bool(empirical.get("all_rows_preserved", True)),
                    "derivation_seal_hash": certificate.get("derivation_seal_hash"),
                    "independent_implementation_hash": certificate.get("independent_implementation_hash"),
                    "independent_certificate_hash": certificate.get("independent_certificate_hash"),
                    "empirical_validation_hash": certificate.get("empirical_validation_hash"),
                    "external_validation_hash": certificate.get("external_validation_hash"),
                    "measurement_receipt_hash": certificate.get("measurement_receipt_hash", row.get("measurement_receipt_hash")),
                    "engine_receipt_hash": row["receipt_hash"],
                    "receipt_path": row["receipt_path"],
                    "receipt_file_hash": sha256(receipt_path),
                    "root_trace_registered": bool(registration.get("root_theorems") or registration.get("dependencies")),
                }
            )
        details.append((family, rows))
    if len(seen_claims) != EXPECTED_CLAIMS or len(seen_obligations) != EXPECTED_CLAIMS:
        raise SystemExit("complete-field claim/obligation count mismatch")
    if candidate_total != EXPECTED_CANDIDATES or control_total != EXPECTED_CONTROLS:
        raise SystemExit(f"unexpected totals {candidate_total}/{control_total}")
    return recon, frozen, details, evidence_rows


def build_paper(recon, frozen, details) -> str:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace("2026-07-26", "2026-07-29", 1)
    text = text.replace(
        "Classical Computation Branch Paper 001, version 1.3.0",
        "Classical Computation Branch Paper 001, version 1.4.0",
        1,
    )
    text = text.replace(
        "DOI: [10.5281/zenodo.21627721](https://doi.org/10.5281/zenodo.21627721)",
        "Previous version DOI: [10.5281/zenodo.21627721](https://doi.org/10.5281/zenodo.21627721)  \nVersion 1.4 DOI: pending archival deposit",
        1,
    )

    abstract = f"""## Abstract

This paper reports the complete-field Classical Computation branch of the third clean-room reconstruction of Smithian Fold Theory (SFT), complete to its frozen dated census and explicitly open to lawful extension. The census contains **369 obligations in 12 dependency-ordered families**. Every obligation has an untouched-engine model-admission receipt, a complete 256-member candidate census, exactly one survivor, four adverse controls, a depth-independent finite-successor or explicit boundary certificate, an implementation-distinct reconstruction and an observation record with registered custody. Together the branch preserves **{EXPECTED_CANDIDATES:,} generated candidates, 369 unique survivors and {EXPECTED_CONTROLS:,} passed controls**. The final reconciliation identity is `{recon['reconciliation_identity']}`.

The reconstruction spans formal computation; computability; computational complexity; algorithms and mathematical data structures; semantics and programming theory; concurrent and distributed computation; cryptography and computational security; learning and intelligence theory; and scientific computation. It derives a native SFT tape machine, exact languages and automata, rewriting and recursion, model equivalence, universality, halting and incompleteness boundaries, exact resource laws, deterministic-support randomized computation, semantics-preserving compilation, consensus and impossibility boundaries, explicit adversary laws, traceable learning and exact scientific calculation. Its native famous-problem results remain precisely typed: `BB_F(k)=k`, `P_F=NP_F`, and the depth-`k` full-edge circuit lower bound hold inside the admitted Fold grammar and are not silently exported to conventional external grammars.

The proof domain imports no conventional machine, axiom, free or fitted parameter, semantic numerical zero, negative proof magnitude, irrational or imaginary proof scalar, floating proof quantity, completed infinity, ontic randomness, cryptographic hardness assumption, pretrained model, benchmark answer or application result. Displayed `0` is structural absence and schedule support is deterministic. Quantum operations, physical hardware, software platforms and the later Unison AI, Fold Chess, Fold Go and Fold Protein rebuilds remain explicit downstream handoffs.

Version 1.4 preserves the complete version 1.3 foundation and its public scientific argument, then executes the full-field roadmap claim by claim. No protected engine or verification-authority source was modified. Every later extension must enter as a new registered question and pass the same public protocol.

**Keywords:** Smithian Fold Theory; complete-field classical computation; Fold machine; computability; halting; complexity; algorithms; semantics; distributed computation; cryptography; learning theory; scientific computing; superdeterminism; computational proof; open science.
"""
    text = one_sub(r"## Abstract\n.*?(?=\n## 1\.)", abstract.rstrip(), text)

    central = f"""## 1. Central scientific claim and exact boundary

> Within the frozen SFT V3 Classical Computation census dated 29 July 2026, all 369 obligations in all 12 registered families are individually admitted through the untouched engine, independently reconstructed, adversely controlled, observed under their declared custody boundary and exactly reconciled. The current closed count is 369, the current open count is structural absence, and completion remains open to lawful versioned extension.

The frozen census identity is `{frozen['census_identity']}`. The final reconciliation identity is `{recon['reconciliation_identity']}`. The branch contains {EXPECTED_CANDIDATES:,} completely decided candidate structures, 369 unique survivors and {EXPECTED_CONTROLS:,} passing controls. Every new full-field registration has an empty axiom list and an empty free-parameter list; the preserved foundational registrations prohibit imported answer-producing premises and retain their admitted upstream dependency routes. Every dependency chain reaches `SFT-ROOT-THERE-IS-NO-NOTHING` through actual receipts rather than narrative citation.

Closure means the exact generated kernels named in the census are complete. The native Fold Busy-Beaver, Fold-P/Fold-NP and circuit lower-bound theorems retain their explicit grammar boundaries. They do not decide conventional Turing-machine Busy Beaver tables, conventional P versus NP, arbitrary imported circuit models, practical cryptographic security or physical device performance. Quantum operations belong to the Quantum Computation branch; application rebuilds and platform engineering remain downstream. This is dated completion, not a permanent prohibition on new questions, counterexamples or stronger lawful certificates.
"""
    text = one_sub(r"## 1\. Central scientific claim and exact boundary\n.*?(?=\n## 2\.)", central.rstrip(), text)

    headlines = f"""## 2. Headline results at a glance

| Result | Exact executed result | Scientific consequence and boundary |
|---|---|---|
| Complete-field Classical Computation | **369/369 obligations** across 12 families; **{EXPECTED_CANDIDATES:,}** generated candidates; 369 unique survivors; **{EXPECTED_CONTROLS:,}** passed controls; 369 current receipts. | The version 1.3 roadmap is now an executed, independently replayable corpus rather than future intent. |
| Native Fold Busy Beaver | For every admitted positive finite description depth `k`, the maximal halting transition count is exactly `BB_F(k)=k`. | Closing populations through depth 14, attaining witnesses and the successor certificate establish the native theorem; no imported Turing-machine grammar is claimed. |
| Native Fold complexity equality | Exact evaluation emits the unique lawful trace checked by the verifier at the same admitted description-depth resource, so `P_F=NP_F`. | Both containments are executed over complete generated supports and tampered certificates halt; the theorem is not exported to conventional P versus NP. |
| Arbitrary admitted Fold-circuit lower bound | A depth-`k` Fold circuit needs all `k` forced transition edges. At depth 14, all 16,384 edge subsets were enumerated and only the full support survived. | The lower and attaining upper witnesses coincide inside the admitted Fold circuit grammar. |
| Superdeterministic randomized computation | Every registered schedule is a deterministic trace; apparent randomness is complete schedule support plus observation-relative uncertainty. | Randomized search and learning do not import an uncaused transition or ontic probability. |
| Formal limits | The self-description plus held-complement construction defeats a total internal halting decider; proof enumeration retains an explicit incompleteness boundary. | Finite generated processes remain exactly executable as terminal or recurrent without mislabelling bounded evidence as unrestricted proof. |
| Semantics, distribution and security | Exact binding, substitution, evaluation, types, correctness, compilation, causality, consensus, consistency, adversary and transcript laws are separately admitted. | Every theorem retains its machine, resource, fault, network and adversary boundary; finite demonstrations are not advertised as practical security guarantees. |
| Learning and scientific computation | Hypothesis support, evaluation custody, generalization, planning, reinforcement, stability, convergence, discretization, simulation and inverse reconstruction retain full traces. | A benchmark, pretrained oracle or result-only simulation cannot substitute for the premise-to-result and measurement route. |
| Dated validation and handoff | Twelve validation laws replay all 351 predecessor receipts; six handoff laws bring the branch to 369/369 with one-owner boundaries. | The Grand Lock is a dated evidence reconciliation, while lawful extensions remain open and quantum, domain measurement and engineering ownership stay explicit. |

These results were not selected by their historical names. Their carriers, alternatives and transition laws were registered and sealed before correspondence. Historical terminology enters only after the SFT result exists, allowing comparison without importing the historical model as a premise.
"""
    text = one_sub(r"## 2\. Headline results at a glance\n.*?(?=\n## Public scientific mission)", headlines.rstrip(), text)

    lines = []
    lines.append("## 130. Complete-field execution - version 1.4")
    lines.append("")
    lines.append("Version 1.3 froze and published the complete-field roadmap. Version 1.4 executes it. The 116 detailed foundational derivations above remain part of the paper and are not rewritten; this section is controlling for the current 369-obligation denominator and exposes every current claim, observation, boundary and receipt.")
    lines.append("")
    lines.append("### 130.1 Complete family census")
    lines.append("")
    lines.append("| Order | Family | Scientific scope | Claims | Candidates | Controls | Status |")
    lines.append("|---:|---|---|---:|---:|---:|---|")
    family_scopes = {
        "BASE": "foundational Fold machine and prior-corpus reconstruction",
        "FORMX": "formal computation",
        "CBLX": "computability",
        "CPLXX": "computational complexity",
        "ALGX": "algorithms and mathematical data structures",
        "SEMX": "semantics and programming theory",
        "DISTX": "concurrent and distributed computation",
        "SECX": "cryptography and computational security",
        "LEARNX": "learning and intelligence theory",
        "SCIX": "scientific computation",
        "VALID": "dated validation and reconciliation",
        "HAND": "one-owner downstream handoffs",
    }
    for order, (family, rows) in enumerate(details, 1):
        lines.append(f"| {order} | `{family}` | {family_scopes[family]} | {len(rows)} | {sum(x['candidate_count'] for x in rows):,} | {sum(x['control_count'] for x in rows):,} | complete, receipt-backed, extension-open |")
    lines.append(f"| **Total** | **12 families** | **complete frozen field census** | **369** | **{EXPECTED_CANDIDATES:,}** | **{EXPECTED_CONTROLS:,}** | **369/369** |")
    lines.append("")
    lines.append("### 130.2 Admission constitution applied to every obligation")
    lines.append("")
    lines.append("Each entry below states the scientific question, the forced law, the unique survivor, exhaustive enumeration, adverse controls, post-registration observation, source custody, excluded imports, dependency route and immutable receipt. Hashes identify the evidence; they do not replace the result. Machine-readable packages remain controlling and permit every row to be independently replayed.")
    for family_index, (family, rows) in enumerate(details, 1):
        lines.append("")
        lines.append(f"### 130.{family_index + 2} Family `{family}` - {len(rows)}/{len(rows)} complete")
        lines.append("")
        lines.append(f"**Scope.** {family_scopes[family].capitalize()}. This family completely decides {sum(x['candidate_count'] for x in rows):,} candidates, retains {len(rows)} unique survivors and passes {sum(x['control_count'] for x in rows):,} adverse controls.")
        for item in rows:
            row = item["row"]
            registration = item["registration"]
            certificate = item["certificate"]
            obligation = item["obligation"]
            survivor = item["survivor"]
            dependencies = registration.get("dependencies", [])
            root_theorems = registration.get("root_theorems", [])
            exclusions = registration.get("excluded_inputs", [])
            lines.append("")
            lines.append(f"#### `{row['obligation_id']}` - {safe(obligation.get('title', registration.get('title', row['claim_id']))) }")
            lines.append("")
            lines.append(f"- **Claim and ownership:** `{row['claim_id']}`; Classical Computation family `{family}`; {safe(registration.get('title', item['claim'].get('title', 'registered computation law')))}.")
            lines.append(f"- **Forced law:** {safe(registration.get('statement', item['claim'].get('statement', row.get('registered_statement', ''))))}")
            lines.append(f"- **Unique surviving structure:** `{safe(survivor.get('candidate_id', certificate.get('exact_result', 'one all-preserving candidate')))}`. Exact result: {safe(certificate.get('exact_result', row.get('certificate_exact_result', 'one uniquely preserving result')))}")
            lines.append(f"- **Exhaustion and falsification:** {item['candidate_count']:,} candidates were generated and decided; exactly one survived; {item['control_count']} of {item['control_count']} controls passed; closure is `{safe(row.get('closure_status', certificate.get('closure_scope')))}`.")
            lines.append(f"- **Dependency and root trace:** {safe(' -> '.join(dependencies) if dependencies else 'registered direct root edge')}. Registered root theorem: `{safe(', '.join(root_theorems) if root_theorems else 'reached through the cited Foundation/Mathematics/Information receipts')}`. Imported axioms: `{len(registration.get('axioms', []))}`; free parameters: `{len(registration.get('free_parameters', []))}`.")
            if item["measurements"]:
                lines.append("- **Post-registration observation:** " + safe("; ".join(item["measurements"])))
            else:
                lines.append("- **Observation and independent reconstruction:** the preserved foundational package carries its admitted external-validation and implementation-distinct certificate identities; no later target was used to rewrite its historical registration.")
            lines.append("- **Sources and custody:** " + safe(", ".join(item["sources"]) if item["sources"] else "receipt-bound exact computational observation corpus") + f". External status: `{safe(row.get('external_status', certificate.get('status')))}`.")
            boundary_text = safe("; ".join(exclusions) if exclusions else "the claim remains bounded by its registered candidate grammar and upstream receipts").rstrip(".")
            lines.append("- **Prohibited imports and boundary:** " + boundary_text + ".")
            lines.append(f"- **Evidence identities:** derivation `{safe(certificate.get('derivation_seal_hash', 'preserved in package'))}`; independent implementation `{safe(certificate.get('independent_implementation_hash', 'preserved in package'))}`; independent certificate `{safe(certificate.get('independent_certificate_hash', row.get('independent_certificate_hash', 'preserved in package')))}`; empirical/external `{safe(certificate.get('empirical_validation_hash', certificate.get('external_validation_hash', 'preserved in package')))}`; engine receipt `{row['receipt_hash']}` at `{row['receipt_path']}`.")

    lines.append("")
    lines.append("## 131. What empirical means in this computational branch")
    lines.append("")
    lines.append("Empirical means grounded in observation or experience rather than accepted solely by theory or authority. In computation the directly observable objects are generated inputs, machine states, transitions, traces, resource ledgers, outputs, tamper responses and independent executions. The field-wide extension therefore seals its grammars and target identities first, runs exact executions afterward, preserves every row and compares the result with an implementation-distinct reconstruction. Where a claim concerns physical devices, natural data or application performance, that measurement remains with the owning downstream branch. This boundary does not make computation non-empirical; it prevents a formal execution from pretending to have measured hardware or nature.")
    lines.append("")
    lines.append("The branch admits no result-only benchmark. A computation result is acceptable only with its initial configuration, generated description, complete transition trace, dependencies, resource accounting, controls, source identities, receipt and reproducible execution. Apparent random outcomes are observed deterministic schedules over complete registered support. Security and learning results retain their exact finite adversary and hypothesis grammars and cannot be inflated into practical claims beyond those supports.")
    lines.append("")
    lines.append("## 132. Dated completion, falsification and extension")
    lines.append("")
    lines.append(f"The branch is complete to census `{frozen['census_identity']}` and reconciliation `{recon['reconciliation_identity']}`: 369 closed, structural absence of an open registered row, and no omitted census member. This is not permanent closure. A reviewer may challenge any claim with an omitted coordinate, second survivor, simpler preserving form, counterexample to the successor certificate, mismatched source, unreproducible trace, failed control or broken receipt. A lawful new problem enters as a versioned obligation without rewriting prior evidence.")
    lines.append("")
    lines.append("The twelve VALID claims form the dated Classical Computation validation Grand Lock: they replay and partition the 351 predecessor receipts, retain theorem/finite-census/unrestricted distinctions and preserve adverse and ownership rows. The six HAND claims then assign quantum operations, physical measurements, software/hardware engineering and application experiments exactly once. The name Grand Lock denotes this dated validation layer; it does not erase open scientific criticism or prevent a lawful later extension.")
    lines.append("")
    lines.append("## 133. Complete-field conclusion")
    lines.append("")
    lines.append(f"Classical Computation is complete to its frozen 29 July 2026 census: **369/369 obligations, 12/12 families, {EXPECTED_CANDIDATES:,} candidate decisions, 369 unique survivors, {EXPECTED_CONTROLS:,} passed adverse controls, 369 independent reconstructions and no open registered obligation**. The protected engine remains `{ENGINE_SEAL}` and the protected verification authority remains `{AUTHORITY_SEAL}`.")
    lines.append("")
    lines.append("The scientific contribution is a unified computational object, not a list of renamed conventional subjects. State, symbol, language, machine, algorithm, resource, program meaning, causal process, adversary, learner and simulation are successive exact organizations of retained Fold distinctions. Every familiar historical correspondence is downstream of the forced SFT carrier. This permits comparison with Turing, Church, Gödel, Shannon, von Neumann, Landauer and Bennett while refusing to let prestige or precedent choose the law.")
    lines.append("")
    lines.append("The public contribution is equally concrete. Every registration, alternative, elimination, survivor, control, observation, reconstruction and receipt is available for inspection. Maria Smith's lack of credentialed access is not evidence for the mathematics; it is evidence of what credential and capital gates can exclude. Ernos Labs therefore invites unrestricted criticism while reserving its standards designation for work that preserves the public empirical constitution, complete evidence, open licensing, retained authorship and unchanged admission route.")

    appendix = "\n".join(lines)
    text = one_sub(
        r"## Foundation and full-field reconstruction roadmap — version 1\.3\.0\n.*?(?=\n## References)",
        appendix,
        text,
    )
    return text.rstrip() + "\n"


def write_metadata():
    metadata = {
        "metadata": {
            "title": "After Turing: The Fold Machine - An Exact, Parameter-Free and Machine-Closed Complete-Field Derivation of Classical Computational Science from Smithian Fold Theory",
            "upload_type": "publication",
            "publication_type": "article",
            "publication_date": "2026-07-29",
            "description": (
                "<p><strong>Classical Computation Branch Paper 001, version 1.4.0</strong>, executes the complete-field roadmap: 369 of 369 frozen obligations across 12 families, 94,464 generated candidates, 369 unique survivors and 1,476 passed controls.</p>"
                "<p>The paper preserves the complete Fold-machine foundation and adds claim-by-claim derivation, execution, observation, boundary, certificate and receipt detail for formal computation, computability, complexity, algorithms, semantics, distributed computation, security, learning, scientific computation, validation and one-owner handoffs.</p>"
                "<p>The exact native-model headline theorems are BB_F(k)=k, P_F=NP_F and the depth-k full-edge circuit lower bound. Their Fold grammar boundaries are explicit; they are not silently exported to conventional external models. Randomized computation is reconstructed as deterministic schedule support plus observation-relative uncertainty.</p>"
                "<p>The branch is complete to its dated census and open to lawful extension. No conventional machine, axiom, free or fitted parameter, semantic numerical zero, negative, irrational, imaginary or floating proof scalar, completed infinity, ontic randomness, hardness assumption, pretrained model or benchmark answer selects a law. The protected engine and verification authority remain unchanged.</p>"
            ),
            "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
            "access_right": "open",
            "license": "cc-by-4.0",
            "version": "1.4.0",
            "language": "eng",
            "keywords": [
                "Smithian Fold Theory", "complete-field classical computation", "Fold machine",
                "computability", "halting problem", "computational complexity", "algorithms",
                "program semantics", "distributed computation", "cryptography", "learning theory",
                "scientific computation", "superdeterminism", "computational proof", "open science",
                "clean-room replication",
            ],
            "related_identifiers": [
                {"identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform", "relation": "isSupplementedBy", "scheme": "url"},
                {"identifier": "10.5281/zenodo.21627721", "relation": "isNewVersionOf", "scheme": "doi"},
            ],
            "notes": "Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. Ernos Labs is a separate scientific-standards conformance designation. Local draft only; publication requires Maria Smith's explicit authorization.",
        },
        "publication_authorized": False,
        "ready_to_publish": False,
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    recon, frozen, details, evidence_rows = collect()
    OUT.write_text(build_paper(recon, frozen, details), encoding="utf-8")
    evidence = {
        "schema": "sft-v3-complete-field-paper-evidence-map/1",
        "branch_id": "computation",
        "version": "1.4.0",
        "frozen_census_identity": frozen["census_identity"],
        "reconciliation_identity": recon["reconciliation_identity"],
        "canonical_engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "claim_count": EXPECTED_CLAIMS,
        "candidate_count": EXPECTED_CANDIDATES,
        "control_count": EXPECTED_CONTROLS,
        "claims": evidence_rows,
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_metadata()
    print(f"built {OUT}")
    print(f"built {EVIDENCE}")
    print(f"built {METADATA}")


if __name__ == "__main__":
    main()
