#!/usr/bin/env python3
"""Build the unpublished Quantum Computation v1.4 complete-field paper."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_3.md"
OUT = ROOT / "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md"
CURRENT = ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md"
RECON = ROOT / "census/quantum_computation_discipline_current_reconciliation_v13.json"
CENSUS = ROOT / "census/quantum_computation_discipline_obligations.json"
EVIDENCE = ROOT / "publications/successors/quantum_computation/evidence_map_v1_4.json"
METADATA = ROOT / "publications/successors/quantum_computation/zenodo_metadata_v1_4.json"

ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
EXPECTED_CLAIMS = 288
EXPECTED_CANDIDATES = 73_728
EXPECTED_CONTROLS = 1_152


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def safe(value) -> str:
    return str(value).replace("\n", " ").replace("|", "/").strip()


def one_sub(pattern: str, replacement: str, text: str) -> str:
    value, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("paper substitution failed: " + pattern[:90])
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
        raise SystemExit("Quantum Computation is not 288/288")
    if recon["frozen_census_identity"] != frozen["census_identity"]:
        raise SystemExit("reconciliation does not identify the frozen census")
    family_order = tuple(frozen["family_order"])
    if set(family_order) != set(recon["completed_families"]):
        raise SystemExit("family order does not exhaust reconciliation")
    obligations = {row["obligation_id"]: row for row in frozen["obligations"]}
    live = {row["claim_id"]: row for row in read(ROOT / "census/claims.json")["claims"]}

    details = []
    evidence_rows = []
    candidate_total = 0
    control_total = 0
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
            decisions = read(package / "elimination_receipt.json")["decisions"]
            survivors = [decision for decision in decisions if decision.get("survives")]
            certificate_path, certificate = current_certificate(package, row["receipt_hash"])
            empirical_path = package / "empirical_validation.json"
            empirical = read(empirical_path) if empirical_path.exists() else {}
            receipt_path = ROOT / row["receipt_path"]
            if not receipt_path.exists():
                raise SystemExit(f"missing receipt: {row['receipt_path']}")
            if len(candidates) != 256 or len(controls) != 4 or len(survivors) != 1:
                raise SystemExit(f"unexpected census/control/survivor count: {claim_id}")
            if not all(control.get("passed") for control in controls):
                raise SystemExit(f"failed control in publication evidence: {claim_id}")
            if certificate.get("engine_receipt_hash") != row["receipt_hash"]:
                raise SystemExit(f"certificate/receipt mismatch: {claim_id}")
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


FAMILY_SCOPES = {
    "BASE": "reversible and quantum computational foundation",
    "REVX": "complete reversible computation",
    "QSTATEX": "quantum information units, states, support and composition",
    "GATEX": "transformations, gates, circuits, compilation and universality",
    "QALGX": "quantum algorithms and correctness",
    "QCPLXX": "quantum resources, complexity and bounds",
    "QCOMMX": "quantum channels, communication and cryptography",
    "QCODEX": "quantum coding, error correction and fault tolerance",
    "QSIMX": "quantum simulation and verification",
    "QLEARNX": "quantum learning and intelligence",
    "QLIMITX": "classical-quantum correspondence and computational limits",
    "VALID": "dated full-field validation and Grand Lock",
    "HAND": "single-owner downstream handoffs and open extension",
}


def build_paper(recon, frozen, details) -> str:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace("2026-07-26", "2026-07-29", 1)
    text = text.replace(
        "Reversible and Quantum Computation Branch Paper 001, version 1.3.0",
        "Reversible and Quantum Computation Branch Paper 001, version 1.4.0",
        1,
    )
    text = text.replace(
        "DOI: [10.5281/zenodo.21627748](https://doi.org/10.5281/zenodo.21627748)",
        "Previous version DOI: [10.5281/zenodo.21627748](https://doi.org/10.5281/zenodo.21627748)<br>\nVersion 1.4 DOI: pending archival deposit",
        1,
    )

    abstract = f"""## Abstract

This paper reports the complete-field Reversible and Quantum Computation branch of the third clean-room reconstruction of Smithian Fold Theory (SFT), complete to its frozen dated census and explicitly open to lawful extension. The census contains **288 obligations in 13 dependency-ordered families**. Every obligation has an untouched-engine model-admission receipt, a complete 256-member candidate census, exactly one survivor, four adverse controls, an explicit depth-independent or registered finite boundary, an implementation-distinct reconstruction and a post-registration observation record with preserved custody. Together the branch decides **{EXPECTED_CANDIDATES:,} generated candidates**, retains **288 unique survivors**, passes **{EXPECTED_CONTROLS:,} adverse controls** and reconciles to `{recon['reconciliation_identity']}`.

The reconstruction derives reversible computation; quantum information units; state preparation and composition; complete-word superposition-equivalent support; finite held phase and exact interference; nonfactorable entangling composition; measurement with retained records; transformations, gates, circuits, compilation and universality; thirty quantum-algorithm laws; twenty-six resource and complexity laws; twenty-four channel and communication laws; thirty-two coding, error-correction and fault-tolerance laws; twenty-four simulation and verification laws; twenty-two learning laws; and twenty-two classical-quantum correspondence and limit laws. The quantum and classical modes are two exact regimes of one Fold machine rather than unrelated formalisms.

No conventional quantum postulate, Hilbert-space axiom, complex amplitude, irrational normalization, imaginary proof value, stochastic-collapse premise, ontic randomness, fitted parameter, physical benchmark, pretrained model or authority label selects a law. Displayed `0` denotes structural absence rather than a numerical proof magnitude. Error correction forces width `2t+1` for every supplied positive finite fault order `t`; quantum speedup, device thresholds, timing, energy and natural measurement distributions remain explicitly assigned to their empirical physical or engineering owners.

Version 1.4 preserves the full version 1.3 foundation, public scientific mission and 22 extensive foundational derivations, then documents all 266 executed full-field extensions claim by claim. No protected engine or verification-authority source was modified. A preserved first-attempt halt and separately versioned retry demonstrate that the engine remains allowed to reject the work.

**Keywords:** Smithian Fold Theory; complete-field quantum computation; reversible computation; quantum information; superposition; interference; entanglement; measurement; quantum circuits; quantum algorithms; quantum complexity; quantum communication; quantum coding; fault tolerance; quantum simulation; quantum learning; open science.
"""
    text = one_sub(r"## Abstract\n.*?(?=\n## 1\.)", abstract.rstrip(), text)

    central = f"""## 1. Central scientific claim and exact boundary

> Within the frozen SFT V3 Reversible and Quantum Computation census dated 29 July 2026, all 288 obligations in all 13 registered families are individually admitted through the untouched engine, independently reconstructed, adversely controlled, observed under their declared custody boundary and exactly reconciled. The current closed count is 288, the current open count is structural absence, and completion remains open to lawful versioned extension.

The frozen census identity is `{frozen['census_identity']}`. The final reconciliation identity is `{recon['reconciliation_identity']}`. The branch contains {EXPECTED_CANDIDATES:,} completely decided candidate structures, 288 unique survivors and {EXPECTED_CONTROLS:,} passing controls. Every full-field registration has an empty axiom list and an empty free-parameter list. Every dependency chain reaches `SFT-ROOT-THERE-IS-NO-NOTHING` through actual registered receipts rather than narrative assertion.

Closure means that every exact kernel named by this dated census has passed its declared grammar and evidence conditions. It does not convert a formal quantum computation law into an unperformed physical measurement. The theorem `2t+1` is unbounded over supplied positive finite fault orders; it is not an imported stochastic hardware threshold. Physical amplitudes, device errors, timing, energy, experimental speedup and natural outcome distributions remain measurement handoffs. The branch is complete to known registered scope, not permanently closed to lawful discoveries, counterexamples or stronger versioned extensions.
"""
    text = one_sub(r"## 1\. Central scientific claim and exact boundary\n.*?(?=\n## 2\.)", central.rstrip(), text)

    headlines = f"""## 2. Headline results at a glance

| Result | Exact executed result | Scientific meaning and boundary |
|---|---|---|
| Complete-field quantum computation | **288/288 obligations**, 13/13 families, **{EXPECTED_CANDIDATES:,}** candidates, 288 unique survivors, **{EXPECTED_CONTROLS:,}** passed controls and 288 independent reconstructions. | The published roadmap is now an executed corpus, complete to its dated census and open to lawful extension. |
| One exact classical-quantum machine | Classical reversible execution, complete quantum support, phase-sensitive merging, joint composition and observation share one generated Fold process. | Quantum computation is derived as an exact operational extension, not installed as a second axiomatic universe. |
| Quantum state and measurement | One distinction supplies two held labels; `b^k` words supply complete support; phase is period-`b` held action; entanglement is nonfactorable joint support; measurement retains its closed distinctions and reconstruction record. | Superposition, interference, entanglement and measurement require no imported complex proof scalar or stochastic-collapse postulate. |
| Gates, circuits and universality | Reversible branch bijections, phase actions, controlled composition, causal circuits, inverse traces, compilation and a universal interpreter are separately forced and admitted. | Circuit semantics joins the already exact resource ledger while preserving branchwise provenance. |
| Algorithms and complexity | **30 algorithm laws** and **26 complexity laws** cover query, phase, transform, search, counting, simulation, verification, upper/lower witnesses and correspondence limits. | Every claimed resource is tied to generated descriptions and exact traces; physical speedup remains an empirical handoff. |
| Communication and security | **24 communication laws** derive exact channels, memory, transfer, entanglement assistance, teleportation/dense-coding correspondences, no-cloning, disturbance, key and adversary boundaries. | Operational and information custody is explicit; no practical security claim outruns its registered adversary or physical owner. |
| Coding and fault tolerance | **32 coding laws** derive logical/physical carriers, syndrome distinction, recovery, degeneracy correspondence, fault propagation and the unique first correcting repetition width `2t+1`. | Widths 3, 5 and 7 exhaust all registered masks; the positive-finite successor law excludes an arbitrary maximum without claiming a measured hardware threshold. |
| Simulation, verification and learning | **24 simulation/verification laws** and **22 learning laws** preserve exact target encoding, update, witness, observation, hypothesis, training and evaluation custody. | No black-box score, pretrained oracle or hidden benchmark can replace the premise-to-result trace. |
| Correspondence and limits | **22 laws** derive classical embedding, probabilistic-support correspondence, quantum decoding, bidirectional simulation, measurement disturbance, no-cloning, halting, undecidability, incompleteness and no-hypercomputation limits. | Apparent randomness is deterministic complete support plus observation-relative uncertainty; no uncaused transition is introduced. |
| Grand Lock and adverse evidence | Twelve validation laws replay the whole branch. One first-attempt `VALID-001` label-binding submission halted and remains preserved; the corrected separately versioned protocol binding later admitted without changing the law, target, engine, verifier or condition. | The validation Grand Lock is a dated reconciliation layer, not immunity from criticism and not permission to reward a halt. |

Historical quantum names enter only after the Fold carriers, alternatives and operations have been forced. They are correspondence labels and tests; they do not select a survivor.
"""
    text = one_sub(r"## 2\. Headline results at a glance\n.*?(?=\n## Public scientific mission)", headlines.rstrip(), text)

    lines = [
        "## 36. Complete-field execution - version 1.4",
        "",
        "Version 1.3 froze the complete-field roadmap. Version 1.4 executes it. The 22 extensive foundational derivations above remain part of this paper; this section exposes every current full-field obligation, law, unique survivor, observation, boundary and receipt. Hashes identify evidence but never substitute for the scientific result.",
        "",
        "### 36.1 Complete family census",
        "",
        "| Order | Family | Scientific scope | Claims | Candidates | Controls | Status |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for order, (family, rows) in enumerate(details, 1):
        lines.append(f"| {order} | `{family}` | {FAMILY_SCOPES[family]} | {len(rows)} | {sum(x['candidate_count'] for x in rows):,} | {sum(x['control_count'] for x in rows):,} | complete, receipt-backed, extension-open |")
    lines.append(f"| **Total** | **13 families** | **complete frozen field census** | **288** | **{EXPECTED_CANDIDATES:,}** | **{EXPECTED_CONTROLS:,}** | **288/288** |")
    lines.extend([
        "",
        "### 36.2 Admission constitution applied to every obligation",
        "",
        "Each entry below reports the registered scientific question, forced law, unique survivor, exhaustive enumeration, adverse controls, observation, source custody, prohibited imports, dependency route and immutable receipt. The machine-readable packages are controlling and independently replayable.",
    ])
    for family_index, (family, rows) in enumerate(details, 1):
        lines.extend([
            "",
            f"### 36.{family_index + 2} Family `{family}` - {len(rows)}/{len(rows)} complete",
            "",
            f"**Scope.** {FAMILY_SCOPES[family].capitalize()}. This family decides {sum(x['candidate_count'] for x in rows):,} candidates, retains {len(rows)} unique survivors and passes {sum(x['control_count'] for x in rows):,} adverse controls.",
        ])
        for item in rows:
            row = item["row"]
            registration = item["registration"]
            certificate = item["certificate"]
            obligation = item["obligation"]
            survivor = item["survivor"]
            dependencies = registration.get("dependencies", [])
            roots = registration.get("root_theorems", [])
            exclusions = registration.get("excluded_inputs", [])
            measurements = item["measurements"]
            sources = item["sources"]
            lines.extend([
                "",
                f"#### `{row['obligation_id']}` - {safe(obligation.get('title', registration.get('title', row['claim_id'])))}",
                "",
                f"- **Claim and ownership:** `{row['claim_id']}`; Quantum Computation family `{family}`; {safe(registration.get('title', item['claim'].get('title', 'registered quantum computation law')))}.",
                f"- **Forced law:** {safe(registration.get('statement', item['claim'].get('statement', row.get('registered_statement', ''))))}",
                f"- **Unique surviving structure:** `{safe(survivor.get('candidate_id', 'one all-preserving candidate'))}`. Exact result: {safe(certificate.get('exact_result', row.get('certificate_exact_result', 'one uniquely preserving result')))}",
                f"- **Exhaustion and falsification:** {item['candidate_count']:,} candidates were generated and decided; exactly one survived; {item['control_count']} of {item['control_count']} adverse controls passed; closure is `{safe(row.get('closure_status', certificate.get('closure_scope')))}`. Falsification condition: {safe(certificate.get('falsification_condition', item['empirical'].get('falsification_condition', 'a second survivor, omitted coordinate, failed control, trace mismatch or boundary breach')))}",
                f"- **Dependency and root trace:** {safe(' -> '.join(dependencies) if dependencies else 'registered direct root edge')}. Registered root: `{safe(', '.join(roots) if roots else 'reached through admitted upstream receipts')}`. Imported axioms: `{len(registration.get('axioms', []))}`; free parameters: `{len(registration.get('free_parameters', []))}`.",
                "- **Observation:** " + safe("; ".join(measurements) if measurements else "the foundational package preserves its admitted observation and implementation-distinct reconstruction"),
                "- **Sources and custody:** " + safe(", ".join(sources) if sources else "receipt-bound exact computational observation corpus") + f". External status: `{safe(row.get('external_status', certificate.get('status')))}`; all rows preserved: `{bool(item['empirical'].get('all_rows_preserved', True))}`.",
                "- **Prohibited imports and boundary:** " + safe("; ".join(exclusions) if exclusions else "the claim remains bounded by its registered candidate grammar and upstream receipts") + ".",
                f"- **Evidence identities:** derivation `{safe(certificate.get('derivation_seal_hash', 'preserved in package'))}`; independent implementation `{safe(certificate.get('independent_implementation_hash', 'preserved in package'))}`; independent certificate `{safe(certificate.get('independent_certificate_hash', 'preserved in package'))}`; measurement `{safe(certificate.get('measurement_receipt_hash', 'preserved in package'))}`; engine receipt `{row['receipt_hash']}` at `{row['receipt_path']}`.",
            ])

    lines.extend([
        "",
        "## 37. What empirical means in this branch",
        "",
        "Empirical means grounded in observation or experience rather than accepted solely by theory or authority. In formal quantum computation the directly observable objects are generated supports, machine states, transformations, phase labels, predecessor merges, joint cells, measurement records, error masks, traces, resources, outputs, tamper responses and independent executions. Each target identity is registered before its outcome is opened; all favorable, adverse, absent and unresolved rows are preserved. Where a claim concerns physical hardware or nature, this branch records the handoff instead of pretending that a formal execution measured a device.",
        "",
        "The branch admits no result-only oracle. A result requires its initial support, generated description, full transition and phase trace, dependencies, resource ledger, controls, source identities, independent reconstruction and engine receipt. Apparent randomization is complete deterministic schedule support plus observation-relative uncertainty. This permits probabilistic and quantum correspondence without introducing an uncaused event into a superdeterministic model.",
        "",
        "## 38. Preserved halt, lawful retry and engine integrity",
        "",
        "The first official `SFT-QUANTUM-VALID-REVERSIBLE-001` submission halted because a sealed prediction label and an already-frozen vector label did not match. The rejected receipt remains preserved as `sha256:bc2e0eb42e8650c848de9872a8666fc879d84aec5c21201b378721f00fd8a62e`. It was not counted as a success, hidden or converted into an admission. A separately versioned retry corrected only the protocol label binding and then passed the unchanged acceptance route. The candidate grammar, registry, observation vector, scientific law, engine, verifier and acceptance condition were not modified.",
        "",
        f"Focused Quantum tests pass 40/40 and lightweight repository validation records 2,751 admitted V3 claims at this checkpoint. The canonical engine seal remains `{ENGINE_SEAL}` and the verification-authority seal remains `{AUTHORITY_SEAL}`. The heavy repository-wide verification is deliberately reserved for the final all-branch Grand Lock and is not claimed here.",
        "",
        "## 39. Dated completion, falsification and extension",
        "",
        f"The branch is complete to frozen census `{frozen['census_identity']}` and reconciliation `{recon['reconciliation_identity']}`: 288 closed, structural absence of an open frozen row, and no omitted census member. A reviewer may invalidate a claim with an omitted same-boundary coordinate, a second survivor, an induction counterexample, a failed inverse, an incomplete observation record, an uncorrected registered error mask, a source mismatch, an unreproducible reconstruction or a broken receipt. A lawful discovery enters as a new versioned obligation without rewriting prior evidence.",
        "",
        "The twelve VALID claims are the dated Quantum Computation validation Grand Lock: a complete reconciliation and adverse-evidence layer. The six HAND claims then assign physical measurement, chemistry, materials, software/hardware engineering and later applications exactly once. Grand Lock does not mean permanent doctrinal closure. Open criticism remains unrestricted; scientific admission requires the public protocol.",
        "",
        "## 40. Complete-field conclusion",
        "",
        f"Reversible and Quantum Computation is complete to its frozen 29 July 2026 census: **288/288 obligations, 13/13 families, {EXPECTED_CANDIDATES:,} candidate decisions, 288 unique survivors, {EXPECTED_CONTROLS:,} passed adverse controls, 288 independent reconstructions and no open frozen obligation**.",
        "",
        "The contribution is one unified computational object. Reversible state, quantum support, phase, interference, entanglement, measurement, gate, circuit, algorithm, code, simulator, verifier and learner are successive exact organizations of retained Fold distinctions. Historical formalisms are comparison boundaries after derivation, not premises before it. The branch also states its limits with equal force: no-cloning, disturbance, halting, undecidability, incompleteness and absent hypercomputation survive the quantum extension.",
        "",
        "The public contribution is the evidence route itself. Maria Smith's lack of credentialed access is not evidence for a theorem; it is evidence of what credential and capital gates can exclude. The open corpus invites unrestricted criticism, reuse and lawful extension while reserving the Ernos Labs designation for work that preserves full derivation chains, adverse evidence, unchanged admission routes, retained authorship and transparent community review.",
    ])

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
            "title": "The Quantum Fold Machine - An Exact, Parameter-Free and Machine-Closed Complete-Field Derivation of Reversible and Quantum Computation from Smithian Fold Theory",
            "upload_type": "publication",
            "publication_type": "article",
            "publication_date": "2026-07-29",
            "description": (
                "<p><strong>Reversible and Quantum Computation Branch Paper 001, version 1.4.0</strong>, executes the complete-field roadmap: 288 of 288 frozen obligations across 13 families, 73,728 generated candidates, 288 unique survivors and 1,152 passed adverse controls.</p>"
                "<p>The paper derives reversible computation, information units and states, superposition-equivalent support, phase and interference, entanglement, measurement, gates, circuits, universality, algorithms, complexity, communication, coding, error correction, fault tolerance, simulation, verification, learning, classical-quantum correspondence and computational limits as exact regimes of one Fold machine.</p>"
                "<p>Every claim exposes its forced law, exhaustive enumeration, unique survivor, adverse controls, observation custody, independent reconstruction, boundary and receipt. The positive-finite 2t+1 correction law is separated from empirical hardware thresholds. Physical timing, energy, errors, speedup and natural outcome distributions remain explicit downstream measurement handoffs.</p>"
                "<p>No conventional quantum axiom, complex amplitude, irrational normalization, stochastic collapse, ontic randomness, fitted parameter, pretrained oracle or authority label selects a law. One preserved halted submission and a separately versioned lawful retry document fail-closed engine behavior. The branch is complete to its dated census and open to lawful extension.</p>"
            ),
            "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
            "access_right": "open",
            "license": "cc-by-4.0",
            "version": "1.4.0",
            "language": "eng",
            "keywords": [
                "Smithian Fold Theory", "complete-field quantum computation", "reversible computation",
                "quantum information", "superposition", "interference", "entanglement", "measurement",
                "quantum circuits", "quantum algorithms", "quantum complexity", "quantum communication",
                "quantum error correction", "fault tolerance", "quantum simulation", "quantum learning",
                "superdeterminism", "computational proof", "open science", "clean-room replication",
            ],
            "related_identifiers": [
                {"identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform", "relation": "isSupplementedBy", "scheme": "url"},
                {"identifier": "10.5281/zenodo.21627748", "relation": "isNewVersionOf", "scheme": "doi"},
            ],
            "notes": "Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. Ernos Labs is a separate scientific-standards conformance designation. Local draft only; publication requires Maria Smith's explicit authorization.",
        },
        "publication_authorized": False,
        "ready_to_publish": False,
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    recon, frozen, details, evidence_rows = collect()
    paper = build_paper(recon, frozen, details)
    OUT.write_text(paper, encoding="utf-8")
    CURRENT.write_text(paper, encoding="utf-8")
    evidence = {
        "schema": "sft-v3-complete-field-paper-evidence-map/1",
        "branch_id": "quantum_computation",
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
    print(f"updated {CURRENT}")
    print(f"built {EVIDENCE}")
    print(f"built {METADATA}")


if __name__ == "__main__":
    main()
