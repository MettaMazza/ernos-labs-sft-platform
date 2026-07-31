#!/usr/bin/env python3
"""Render the audit layer for the preliminary SFT V3 ToE synthesis."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INVENTORY = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"
OUTPUT = HERE / "SCIENTIFIC_AUDIT_LAYER.md"


BRANCH_LABELS = {
    "foundation": "Foundation",
    "mathematics": "Mathematics",
    "information_science": "Information Science",
    "computation": "Classical Computation",
    "quantum_computation": "Reversible and Quantum Computation",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "materials": "Materials Science",
    "biology": "Biology and Life Sciences",
    "medicine": "Medicine and Health Sciences",
    "consciousness_cognitive_science": "Consciousness and Cognitive Science",
    "earth_environment": "Earth and Environmental Sciences",
    "astronomy_cosmology": "Astronomy and Cosmology",
    "social_collective_systems": "Social and Collective Systems",
    "social_collective": "Social prior-return continuation",
    "engineering_translation": "Engineering Translation",
    "cross_branch_synthesis": "Cross-Branch Synthesis",
}


PROGRAMME_BOUNDARIES = {
    "foundation": "16/16 current Foundation boundary complete; extension-open",
    "mathematics": "323/323 dated full-field boundary complete",
    "information_science": "262/262 dated full-field boundary complete",
    "computation": "369/369 dated full-field boundary complete",
    "quantum_computation": "288/288 dated full-field boundary complete",
    "physics": "368/368 current categorical boundary complete",
    "chemistry": "272/272 registered obligations plus nine separately retained returns; 281 live claims",
    "materials": "289/289 dated full-field boundary complete",
    "biology": "82/424 full-field obligations closed; continuation active",
    "medicine": "published foundation and prior-return family complete; full-field census not frozen",
    "consciousness_cognitive_science": "published foundation and prior-return family complete; full-field census not frozen",
    "earth_environment": "published foundation and prior-return family complete; full-field census not frozen",
    "astronomy_cosmology": "published foundation and prior-return family complete; full-field census not frozen",
    "social_collective_systems": "published 72-law foundation",
    "social_collective": "four admitted prior-return claims retained separately",
    "engineering_translation": "published foundation and prior-return family complete; full-field census not frozen",
    "cross_branch_synthesis": "12/12 inherited-return claims admitted; final global current-graph merge remains open",
}


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    inventory = json.loads(INVENTORY.read_bytes())
    ledger = inventory["claim_ledger"]
    lines = [
        "# Scientific Audit Layer",
        "",
        "## Smithian Fold Theory of Everything V3 preliminary synthesis",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Organisation:** Ernos Labs  ",
        "**Version:** 0.1.0  ",
        "**Version DOI:** 10.5281/zenodo.21717584  ",
        "**Date:** 31 July 2026  ",
        "**Status:** Scientific audit for the authorised first standalone V3 preliminary publication. Final computational proofs, downstream full-field censuses, canonical current-graph reconciliation and final Grand Lock verification remain open.",
        "",
        "This layer preserves complete claim identities and current evidence classes. It does not promote implementation tests to empirical confirmation, historical programme results to current V3 proof authority, or foundational closure to full-field closure.",
        "",
        "## 1. Global direct-source verification",
        "",
        "| Quantity | Verified value |",
        "|---|---:|",
        f"| Live claims | {ledger['claim_count']:,} |",
        f"| Model-admitted claims | {ledger['model_admitted_count']:,} |",
        f"| Generated candidates | {ledger['candidate_count']:,} |",
        f"| Unique survivors | {ledger['survivor_count']:,} |",
        f"| Adverse controls | {ledger['control_count']:,} |",
        f"| Passed adverse controls | {ledger['passed_control_count']:,} |",
        f"| Receipt identities matched | {ledger['receipt_identity_match_count']:,}/{ledger['claim_count']:,} |",
        f"| Candidate censuses reconstructed | {ledger['candidate_census_match_count']:,}/{ledger['claim_count']:,} |",
        f"| Claims with a path to the root theorem | {ledger['root_traced_count']:,}/{ledger['claim_count']:,} |",
        f"| Missing declared dependencies | {ledger['missing_dependency_count']:,} |",
        f"| Unclassified obligations in the live claim ledger | {len(ledger['unclassified_obligations']):,} |",
        "",
        "The candidate total is reconstructed directly from every current `candidate_census.json`, including the larger Foundation and Physics grammars. Receipt validation compares the registered claim row with the receipt's internal identity and status fields; the file SHA-256 is retained separately.",
        "",
        "## 2. Branch status and exact totals",
        "",
        "| Branch | Current boundary | Claims | Candidates | Survivors | Controls | Root-traced |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for branch, summary in ledger["branch_summary"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    esc(BRANCH_LABELS[branch]),
                    esc(PROGRAMME_BOUNDARIES[branch]),
                    f"{summary['claim_count']:,}",
                    f"{summary['candidate_count']:,}",
                    f"{summary['survivor_count']:,}",
                    f"{summary['control_count']:,}",
                    f"{summary['root_traced_count']:,}/{summary['claim_count']:,}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 3. Active paper registry",
            "",
            "| Corpus role | Active source | SHA-256 | Lines | Headings | DOI tokens |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    for role, record in inventory["active_papers"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    esc(role),
                    f"`{esc(record['path'])}`",
                    f"`{record['sha256']}`",
                    f"{record['line_count']:,}",
                    f"{record['heading_count']:,}",
                    esc(", ".join(record["doi_tokens"]) or "none in source"),
                ]
            )
            + " |"
        )

    historical = inventory["historical_computational_programmes"]
    lines.extend(
        [
            "",
            "## 4. Computational proof and programme chronology",
            "",
            "### 4.1 Historical versioned programme evidence",
            "",
            "Historical programme manifests are evidence for their producing versions. They are not imported as V3 proof authority.",
            "",
            "| Programme | Frozen version | Principal retained result | Current use |",
            "|---|---|---|---|",
            f"| Chess Fold | {esc(historical['chess_v2_2']['manifest']['version'])} | 1700: 54.2%; 1900: 62.5%; latest completed 2100 batch: 41.7%; legality/endgame verification retained | Read-only evidence and recreation target |",
            f"| Go Fold | {esc(historical['go_v2_2']['manifest']['version'])} | Exact small-board census; two replayed 2-0 GNU Go 9x9 batches; one recovered 19x19 harness-reported 2-0 point-at-cutoff record with disclosed Round-1 synchronisation defect | Read-only evidence and recreation target |",
            f"| Protein Fold | historical release dated {esc(historical['protein_blind_76_v3_7']['manifest']['release_date'])} | Sealed 76-residue run: whole-chain TM {historical['protein_blind_76_v3_7']['manifest']['complete_prediction']['tm_score']}; three strong local windows preserved | Read-only evidence and V3 provenance target |",
            f"| Unison AI | {esc(historical['unison_v6_3']['manifest']['version'])} | 326 suites, 2,002 checks, zero main-corpus failures; standalone 21/21; weak generation benchmarks preserved | Read-only evidence and clean-rebuild target |",
            "",
            "### 4.2 Current V3 recreation status",
            "",
            "| Programme | Current V3 status | Publication or empirical boundary |",
            "|---|---|---|",
            "| Protein Fold | Preliminary v0.9.4 published; 42,173,082-candidate parent and 583-state high-attraction slice independently verified; complete 21-record claim audit added; lower bands, global frontier and whole-chain recurrence remain open | Frozen 100-target AlphaFold parity campaign has not started |",
            "| Chess Fold | Clean V3 workspace not yet created in the current repository | Historical results remain historical until independently recreated |",
            "| Go Fold | Clean V3 workspace not yet created in the current repository | Historical results remain historical until independently recreated |",
            "| Unison Fold AI | V3 clean-rebuild scaffold present; mathematical closure open; empirical validation not run | Discord deployment and sealed generalisation remain unauthorised and unexecuted |",
            "",
            "## 5. Current corrections, adverse results and unresolved boundaries",
            "",
            "- Biology retains corrections to rigid-one-shape protein language, inevitable beneficial fixation, universal three-quarter allometry, strong scale-free-network universality, parity-selected homochirality, and denominator-only accounts of ageing, cancer and ecosystems.",
            "- Earth retains the adverse first mixed-magnitude earthquake catalogue and the later compatible homogeneous holdout as different registered records.",
            "- Astronomy retains the adverse unweighted SPARC rank-four comparison and the separate uncertainty-aware source result without conflating them.",
            "- Protein Fold retains adverse historical 4APD, 4B19 and 8HJC selector outcomes beside the stronger six-axis successor machinery; the current full relation has not yet received its primary blind empirical test.",
            "- Chess and Go retain disclosed benchmark losses, cut-offs and synchronisation defects; historical victories are not relabelled as V3 results.",
            "- Unison retains weak or null generation benchmarks; passing architectural checks are not conversational validation.",
            "- The complete final ToE remains downstream of the open full-field programme, canonical current-graph reconciliation, final computational proofs and a new heavy global verification run.",
            "",
            "## 6. Complete current claim inventory",
            "",
            "The following table is generated from all 2,751 live claim packages. Full statements, dependency arrays and file identities remain in `AUTHORITATIVE_CORPUS_INVENTORY.json`.",
            "",
            "| # | Branch | Claim ID | Title | Formal closure | External status | Candidates | Controls | Receipt ID |",
            "|---:|---|---|---|---|---|---:|---:|---|",
        ]
    )
    for index, claim in enumerate(ledger["claims"], start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    esc(BRANCH_LABELS[str(claim["branch"])]),
                    f"`{esc(claim['claim_id'])}`",
                    esc(claim["title"]),
                    esc(claim["closure_status"]),
                    esc(claim["external_status"]),
                    f"{claim['candidate_count']:,}",
                    f"{claim['control_count']:,}",
                    f"`{esc(claim['registered_receipt_id'])}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 7. Publication boundary",
            "",
            "Maria Smith has authorised this conceptual monograph, audit layer and machine inventory for first publication as standalone V3 version 0.1.0 under reserved DOI 10.5281/zenodo.21717584. This publication creates a new Zenodo record rather than updating the deprecated V2 ToE lineage. After the new V3 concept exists, the later complete version must update the V3 lineage, preserve this chronology and re-run the final publication and verification gates after the computational programmes and global programme requirements close.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines))
    print(
        json.dumps(
            {
                "path": str(OUTPUT.relative_to(ROOT)),
                "bytes": OUTPUT.stat().st_size,
                "claims": ledger["claim_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
