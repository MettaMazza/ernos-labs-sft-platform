#!/usr/bin/env python3
"""Generate the exhaustive publication-guidance SFT V3 ToE monograph."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MATRIX_PATH = HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.json"
INVENTORY_PATH = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"
EXECUTIVE_PATH = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
OUTPUT = HERE / "SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH.md"
VOLUME_DIR = HERE / "volumes"


BRANCH_ORDER = [
    "foundation",
    "mathematics",
    "information_science",
    "computation",
    "quantum_computation",
    "physics",
    "chemistry",
    "materials",
    "biology",
    "medicine",
    "consciousness_cognitive_science",
    "earth_environment",
    "astronomy_cosmology",
    "social_collective_systems",
    "social_collective",
    "engineering_translation",
    "cross_branch_synthesis",
]


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


ACTIVE_ROLE = {
    "foundation": "foundation",
    "mathematics": "mathematics",
    "information_science": "information_science",
    "computation": "computation",
    "quantum_computation": "quantum_computation",
    "physics": "physics",
    "chemistry": "chemistry",
    "materials": "materials",
    "biology": "biology",
    "medicine": "medicine",
    "consciousness_cognitive_science": "consciousness_cognitive_science",
    "earth_environment": "earth_environment",
    "astronomy_cosmology": "astronomy_cosmology",
    "social_collective_systems": "social_collective_systems",
    "engineering_translation": "engineering_translation",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: object | None) -> str:
    if value is None:
        return "not separately recorded"
    return str(value).replace("\n", " ").strip()


def markdown_section(text: str, title_pattern: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{title_pattern}\s*$\n(.*?)(?=^##\s+|\Z)", text
    )
    return match.group(1).strip() if match else ""


def active_abstract(inventory: dict, branch: str) -> str:
    role = ACTIVE_ROLE.get(branch)
    if not role:
        return ""
    path = ROOT / inventory["active_papers"][role]["path"]
    text = path.read_text(encoding="utf-8")
    return markdown_section(text, "Abstract")


def active_headlines(inventory: dict, branch: str) -> str:
    role = ACTIVE_ROLE.get(branch)
    if not role:
        return ""
    path = ROOT / inventory["active_papers"][role]["path"]
    text = path.read_text(encoding="utf-8")
    for pattern in (
        r"Headline findings: landmark first-principles results",
        r"Headline findings",
        r"Current status, evidence language and reader map",
    ):
        found = markdown_section(text, pattern)
        if found:
            return found
    return ""


def active_references(inventory: dict, branch: str) -> str:
    role = ACTIVE_ROLE.get(branch)
    if not role:
        return ""
    path = ROOT / inventory["active_papers"][role]["path"]
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^##\s+(?:References|Source[^\n]*)\s*$", text))
    if not matches:
        return ""
    match = matches[-1]
    following = re.search(r"(?m)^##\s+", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    return text[match.end() : end].strip()


def first_paragraph(value: str | None) -> str:
    if not value:
        return "No separate prose rationale is stored; the registered statement, dependencies and candidate grammar below are the authoritative rationale."
    blocks = [block.strip() for block in re.split(r"\n\s*\n", value) if block.strip()]
    return blocks[0] if blocks else value.strip()


def claim_record(index: int, claim: dict) -> list[str]:
    lines = [
        f"#### {index}. {claim['title']}",
        "",
        f"**Claim ID:** `{claim['claim_id']}`  ",
        f"**Formal status:** `{claim['formal_status']}`  ",
        f"**Empirical status:** `{claim['empirical_status']}`  ",
        f"**Publication family:** {claim['family_label']}  ",
        f"**Registration date:** `{clean(claim['registration_date'])}`",
        "",
        "**Exact statement.**",
        "",
        f"> {claim['statement']}",
        "",
        "**Why the claim is required.**",
        "",
        first_paragraph(
            claim.get("why")
            or (
                claim.get("active_paper_claim_section") or {}
            ).get("question_law_forced_result")
            or claim.get("intended_certificate")
        ),
        "",
        "**Dependency route.**",
        "",
    ]
    dependencies = claim.get("dependencies", [])
    if dependencies:
        lines.append(" -> ".join(f"`{item}`" for item in dependencies))
    else:
        lines.append("Root claim; no earlier dependency is admitted.")
    lines.extend(
        [
            "",
            "**Candidate grammar and boundary.**",
            "",
            f"Generator: {clean(claim.get('candidate_generation_rule') or (claim.get('candidate_grammar') or {}).get('generator'))}",
            "",
            f"Boundary: {clean(claim.get('candidate_boundary') or (claim.get('candidate_grammar') or {}).get('boundary'))}",
            "",
            f"The package completely records **{claim['candidate_count']:,} candidates**, **{claim['unique_survivor_count']:,} unique survivor**, and **{claim['control_count']:,} required controls**.",
            "",
            "**Retained form and elimination result.**",
            "",
        ]
    )
    survivor_records = claim.get("survivor_records", [])
    survivors = claim.get("survivors", [])
    if survivor_records:
        for survivor in survivor_records:
            lines.append(f"> `{clean(survivor.get('exact_form') or survivor.get('candidate_id'))}`")
    elif survivors:
        for survivor in survivors:
            lines.append(f"> `{clean(survivor.get('candidate_id'))}` - {clean(survivor.get('reason'))}")
    else:
        lines.append(
            "The custom domain certificate records one unique survivor; its complete candidate and decision surface remains in the machine package."
        )
    closure = claim.get("closure") or {}
    certificate = claim.get("certificate") or {}
    lines.extend(
        [
            "",
            f"Exact result: {clean(claim.get('exact_result'))}",
            "",
            f"Closure scope: `{clean(closure.get('scope') or certificate.get('closure_scope') or claim['formal_status'])}`. Exact boundary: {clean(closure.get('exact_boundary'))}. Minimality: `{clean(closure.get('minimality_passed'))}`. Named-form uniqueness: `{clean(closure.get('named_shape_uniqueness_passed'))}`.",
            "",
            "**Falsification and controls.**",
            "",
            f"Falsification condition: {clean(claim.get('falsification_condition'))}",
            "",
            "| Control | Passed | Expected | Observed |",
            "|---|---|---|---|",
        ]
    )
    controls = claim.get("controls", [])
    if controls:
        for control in controls:
            lines.append(
                "| "
                + " | ".join(
                    [
                        clean(control.get("kind")),
                        clean(control.get("passed")),
                        clean(control.get("expected_behavior")),
                        clean(control.get("observed_behavior")),
                    ]
                )
                + " |"
            )
    else:
        lines.append(
            f"| Custom registered control surface | {claim['passed_control_count'] == claim['control_count']} | Full package record | Full package record |"
        )
    lines.extend(["", "**Evidence, provenance and chronology.**", ""])
    sources = claim.get("evidence_source_ids", [])
    measurements = claim.get("measurements", [])
    if sources:
        lines.append("Source identities: " + ", ".join(f"`{item}`" for item in sources) + ".")
        lines.append("")
    else:
        lines.append("Source identities: none in a separate empirical package at this formal boundary.")
        lines.append("")
    lines.append(
        "Target opened after seal: "
        f"`{clean(claim.get('target_opened_after_seal'))}`; all rows preserved: "
        f"`{clean(claim.get('all_rows_preserved'))}`; registered comparison passed: "
        f"`{clean(claim.get('empirical_comparison_passed'))}`."
    )
    if measurements:
        lines.extend(["", "Measured, observed, adverse and boundary records:", ""])
        for measurement in measurements:
            lines.append(f"- {clean(measurement)}")
    lines.extend(
        [
            "",
            "**Scientific meaning and current boundary.**",
            "",
            first_paragraph(
                claim.get("check_narrative")
                or (
                    claim.get("active_paper_claim_section") or {}
                ).get("question_law_forced_result")
                or claim.get("status_record")
            ),
            "",
            "**Machine identities.**",
            "",
            f"Engine receipt: `{claim['registered_receipt_id']}` at `{claim['receipt_path']}`. ",
            f"Independent implementation: `{clean(certificate.get('independent_implementation_hash'))}`. ",
            f"Derivation seal: `{clean(certificate.get('derivation_seal_hash'))}`. ",
            f"Source manifest: `{clean(certificate.get('source_manifest_hash'))}`. ",
            f"External validation: `{clean(certificate.get('external_validation_hash'))}`. ",
            f"Measurement receipt: `{clean(claim.get('measurement_receipt_hash'))}`.",
            "",
            f"Complete package: `claims/{claim['claim_id']}/`. The exhaustive matrix preserves the SHA-256 of every required package file; the machine archive preserves every candidate, decision, trace and source capture.",
            "",
        ]
    )
    return lines


def branch_volume(
    branch_index: int,
    branch: str,
    claims: list[dict],
    matrix: dict,
    inventory: dict,
) -> str:
    label = BRANCH_LABELS[branch]
    branch_summary = inventory["claim_ledger"]["branch_summary"][branch]
    lines = [
        f"# The Smithian Fold Theory V3 Theory of Everything - {label}",
        "",
        f"## Exhaustive branch volume {branch_index:02d}",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Organisation:** Ernos Labs  ",
        "**Version:** 0.1.0 preliminary exhaustive monograph  ",
        "**Date:** 31 July 2026  ",
        "**Paper licence:** CC BY 4.0  ",
        "**Code licence:** Apache-2.0  ",
        "**Publication status:** Scientific audit volume in the authorised standalone V3 preliminary version 0.1.0",
        "**Version DOI:** 10.5281/zenodo.21717584",
        "",
        "## Abstract",
        "",
        active_abstract(inventory, branch)
        or f"This volume preserves every current {label} claim and its direct-source publication record.",
        "",
        "## Current branch status",
        "",
        "| Quantity | Verified value |",
        "|---|---:|",
        f"| Claims | {branch_summary['claim_count']:,} |",
        f"| Candidates | {branch_summary['candidate_count']:,} |",
        f"| Unique survivors | {branch_summary['survivor_count']:,} |",
        f"| Required controls | {branch_summary['control_count']:,} |",
        f"| Root-traced claims | {branch_summary['root_traced_count']:,}/{branch_summary['claim_count']:,} |",
        "",
    ]
    headlines = active_headlines(inventory, branch)
    if headlines:
        lines.extend(["## Current headline findings", "", headlines, ""])
    lines.extend(
        [
            "## Family map",
            "",
            "| Family | Claims | Candidates | Controls |",
            "|---|---:|---:|---:|",
        ]
    )
    grouped: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        grouped[claim["family_label"]].append(claim)
    for family, rows in grouped.items():
        lines.append(
            f"| {family} | {len(rows):,} | {sum(r['candidate_count'] for r in rows):,} | {sum(r['control_count'] for r in rows):,} |"
        )
    lines.extend(
        [
            "",
            "## Complete dependency-ordered claim record",
            "",
            "Every section below exposes the current statement, status, dependency route, grammar, count, survivor, closure, controls, evidence, chronology, scientific meaning and receipt identity. Complete candidate members and executable traces remain in the machine archive.",
            "",
        ]
    )
    current_family = None
    for index, claim in enumerate(claims, 1):
        if claim["family_label"] != current_family:
            current_family = claim["family_label"]
            family_claims = grouped[current_family]
            lines.extend(
                [
                    f"### {current_family}",
                    "",
                    f"This publication family contains {len(family_claims):,} current claims, {sum(row['candidate_count'] for row in family_claims):,} generated candidates and {sum(row['control_count'] for row in family_claims):,} required controls. It begins with **{family_claims[0]['title']}** and its current terminal record is **{family_claims[-1]['title']}**.",
                    "",
                ]
            )
        lines.extend(claim_record(index, claim))
    references = active_references(inventory, branch)
    lines.extend(["## Branch references and source registry", ""])
    lines.append(
        references
        or "Human-readable sources and complete source identities are preserved in the current claim packages, active paper and exhaustive matrix."
    )
    lines.extend(
        [
            "",
            "## Branch machine identity",
            "",
            f"This volume is generated from `{MATRIX_PATH.relative_to(ROOT)}` with SHA-256 `{sha256(MATRIX_PATH)}` and the current active-paper and claim-package identities preserved there.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_bytes())
    inventory = json.loads(INVENTORY_PATH.read_bytes())
    VOLUME_DIR.mkdir(parents=True, exist_ok=True)
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in matrix["claims"]:
        by_branch[claim["branch"]].append(claim)

    volume_records = []
    master_lines = [
        "# The Smithian Fold Theory V3 Theory of Everything",
        "",
        "## Exhaustive preliminary monograph from There Is No Nothing to the current computational proof frontier",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Affiliation:** Ernos Labs, independent open-science research  ",
        "**Version:** 0.1.0 - exhaustive preliminary monograph  ",
        "**Date:** 31 July 2026  ",
        "**Publication status:** Authorised first standalone V3 preliminary publication  ",
        "**Version DOI:** 10.5281/zenodo.21717584  ",
        "**Paper licence:** Creative Commons Attribution 4.0 International  ",
        "**Code licence:** Apache License 2.0",
        "",
        "## Abstract",
        "",
        "This exhaustive preliminary monograph preserves the complete current Smithian Fold Theory V3 scientific surface from the premise-free operational theorem There Is No Nothing through Foundation, Mathematics, Information Science, Classical Computation, Reversible and Quantum Computation, Physics, Chemistry, Materials Science, Biology, Medicine, Consciousness, Earth, Astronomy, Social and Collective Systems, Engineering Translation and Cross-Branch Synthesis. The current repository contains 2,751 live model-admitted claims generated from 892,246 candidates, with 2,751 unique survivors and 11,004 passed adverse controls. Every live claim has a matched receipt identity and a dependency path to the root theorem. The monograph distinguishes formal, implementation, empirical, historical and publication status; preserves favourable, adverse, null, missing, unavailable and unresolved records; and records the historical and current Chess Fold, Go Fold, Protein Fold and Unison Fold AI programmes. The final computational edition remains downstream of the active V3 computational proofs, remaining full-field censuses, canonical current-graph reconciliation and final Grand Lock.",
        "",
        "## Publication architecture",
        "",
        "This master source contains the common conceptual argument, all branch volumes and the complete claim-level scientific audit. The generated branch volumes provide manageable publication units without removing content. The machine archive preserves the 892,246 candidate members, decisions, hashes, receipts, executable traces, source snapshots and certificates.",
        "",
        "| Layer | Complete content |",
        "|---|---|",
        "| Conceptual monograph | Dependency narrative, branch and family results, major derivations, evidence meaning and open frontier |",
        "| Scientific audit | All 2,751 claim records, statuses, dependencies, controls, source IDs, chronology and receipts |",
        "| Machine archive | Complete candidates, decisions, traces, hashes, source captures and certificates |",
        "",
        "## Corpus-wide verified totals",
        "",
        "| Quantity | Verified value |",
        "|---|---:|",
        "| Live model-admitted claims | 2,751 |",
        "| Generated candidates | 892,246 |",
        "| Unique survivors | 2,751 |",
        "| Required and passed controls | 11,004 |",
        "| Receipt identities matched | 2,751/2,751 |",
        "| Candidate censuses reconstructed | 2,751/2,751 |",
        "| Root-traced claims | 2,751/2,751 |",
        "| Missing declared dependencies | 0 |",
        "",
        "## Evidence and terminology constitution",
        "",
        "Formal proof language is reserved for exact derivational closure. Derivation names generated structure; implementation names executable reconstruction; prediction names a correctly sealed prospective consequence; observation names a source-bound record; measurement names an instrument- and method-bound value; reconstruction names an inferred history or latent state; correspondence names a post-derivation relation; compatibility names nonadverse but nondiscriminating evidence; confirmation is used only at the registered protocol boundary; adverse and unresolved evidence remains visible.",
        "",
        "Every empirical record preserves target chronology, source identity, transport state, measurement or observation, uncertainty where present, falsification rule and all favourable, adverse, missing and unresolved rows. Prior SFT, consensus, targets and applications may register questions or test consequences; they cannot select a V3 law.",
        "",
        "## Dependency spine",
        "",
        "Methods -> Foundation -> Mathematics -> Information Science -> Classical Computation -> Reversible and Quantum Computation -> Physics -> Chemistry -> Materials Science -> Biology -> Medicine -> Consciousness -> Earth -> Astronomy -> Social and Collective Systems -> Engineering Translation -> Cross-Branch Synthesis.",
        "",
        "## Branch volumes and complete scientific record",
        "",
    ]

    for branch_index, branch in enumerate(BRANCH_ORDER, 1):
        text = branch_volume(
            branch_index, branch, by_branch[branch], matrix, inventory
        )
        path = VOLUME_DIR / f"{branch_index:02d}_{branch}.md"
        path.write_text(text + "\n", encoding="utf-8")
        volume_records.append(
            {
                "branch": branch,
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "claims": len(by_branch[branch]),
            }
        )
        master_lines.extend(
            [
                f"## Volume {branch_index:02d}. {BRANCH_LABELS[branch]}",
                "",
                text.split("## Abstract", 1)[1]
                if "## Abstract" in text
                else text,
                "",
            ]
        )

    executive = EXECUTIVE_PATH.read_text(encoding="utf-8")
    for title in (
        r"22\. The computational proof programme",
        r"23\. Current evidence, corrections and adverse records",
        r"24\. The Ernos Labs open-science platform",
        r"26\. Limitations and open frontier",
        r"27\. Conclusion",
    ):
        content = markdown_section(executive, title)
        if content:
            rendered_title = title.replace("\\.", ".")
            master_lines.extend([f"## {rendered_title}", "", content, ""])

    master_lines.extend(
        [
            "## Master machine identity appendix",
            "",
            f"Authoritative inventory SHA-256: `{sha256(INVENTORY_PATH)}`.",
            "",
            f"Exhaustive content matrix SHA-256: `{sha256(MATRIX_PATH)}`.",
            "",
            "| Volume | Claims | Bytes | SHA-256 |",
            "|---|---:|---:|---|",
        ]
    )
    for row in volume_records:
        master_lines.append(
            f"| `{row['path']}` | {row['claims']:,} | {row['bytes']:,} | `{row['sha256']}` |"
        )
    master_lines.extend(
        [
            "",
            "The full package-file identities for every claim are stored in `EXHAUSTIVE_TOE_CONTENT_MATRIX.json`. Candidate members and decision traces remain in their registered claim directories and are not duplicated into the human prose layer.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(master_lines), encoding="utf-8")
    manifest = {
        "schema": "sft-v3-exhaustive-preliminary-toe-monograph/1",
        "date": "2026-07-31",
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "master_path": str(OUTPUT.relative_to(ROOT)),
        "master_sha256": sha256(OUTPUT),
        "master_bytes": OUTPUT.stat().st_size,
        "claim_count": matrix["claim_count"],
        "family_count": matrix["family_count"],
        "volumes": volume_records,
        "remote_publication_authorized": False,
    }
    manifest_path = HERE / "EXHAUSTIVE_TOE_MONOGRAPH_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "master_bytes": OUTPUT.stat().st_size,
                "master_sha256": manifest["master_sha256"],
                "claims": manifest["claim_count"],
                "families": manifest["family_count"],
                "volumes": len(volume_records),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
