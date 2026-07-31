#!/usr/bin/env python3
"""Build the exhaustive current-source matrix for the SFT V3 ToE monograph."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INVENTORY_PATH = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"
OUTPUT_JSON = HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.json"
OUTPUT_MD = HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.md"


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


PREFIXES = {
    "foundation": ("SFT-FOUNDATION-", "SFT-ROOT-"),
    "mathematics": ("SFT-MATH-",),
    "information_science": ("SFT-INFO-",),
    "computation": ("SFT-COMP-",),
    "quantum_computation": ("SFT-QUANTUM-",),
    "physics": ("SFT-PHYS-",),
    "chemistry": ("SFT-CHEM-",),
    "materials": ("SFT-MAT-",),
    "biology": ("SFT-BIO-",),
    "medicine": ("SFT-MED-",),
    "consciousness_cognitive_science": ("SFT-CONSC-",),
    "earth_environment": ("SFT-EARTH-",),
    "astronomy_cosmology": ("SFT-ASTRO-",),
    "social_collective_systems": ("SFT-SOCIAL-",),
    "social_collective": ("SFT-SOCIAL-",),
    "engineering_translation": ("SFT-ENG-",),
    "cross_branch_synthesis": ("SFT-SYNTH-",),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> object | None:
    if not path.exists():
        return None
    return json.loads(path.read_bytes())


def section(text: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1).strip() if match else None


def family_key(branch: str, claim_id: str) -> str:
    remainder = claim_id
    for prefix in PREFIXES[branch]:
        if claim_id.startswith(prefix):
            remainder = claim_id[len(prefix) :]
            break
    token = remainder.split("-")[0]
    if branch == "foundation":
        return "root" if claim_id.startswith("SFT-ROOT-") else "foundation"
    return token.lower()


def family_label(key: str) -> str:
    aliases = {
        "ab": "Acid-Base Chemistry",
        "alg": "Algorithms",
        "astro": "Astronomy",
        "cbl": "Computability Boundaries",
        "cplx": "Computational Complexity",
        "cryst": "Crystallography",
        "dist": "Distributed Computation",
        "elem": "Elements and Periodicity",
        "eq": "Equilibrium",
        "kin": "Kinetics",
        "meas": "Measurement and Metrology",
        "mol": "Molecular Structure",
        "rxn": "Reaction Structure",
        "sci": "Scientific Computation",
        "sec": "Security and Cryptography",
        "sem": "Semantics and Programming Theory",
        "stoich": "Stoichiometry",
        "sust": "Sustainability and Lifecycle",
        "thermo": "Thermodynamics",
    }
    return aliases.get(key, key.replace("-", " ").title())


def clean_family(value: str) -> str:
    value = re.sub(r"^\d+\.\s*", "", value.strip())
    value = value.strip("`* ")
    return value.replace("_", " ").strip().title()


def active_paper_sections(inventory: dict) -> tuple[dict[str, list[str]], dict[str, dict]]:
    appearances: dict[str, list[str]] = defaultdict(list)
    claim_sections: dict[str, dict] = {}
    for role, record in inventory["active_papers"].items():
        path = ROOT / record["path"]
        text = path.read_text(encoding="utf-8")
        h2_headings = list(re.finditer(r"(?m)^##\s+([^\n]+)\s*$", text))
        for claim_id in set(re.findall(r"SFT-[A-Z0-9-]+", text)):
            appearances[claim_id].append(role)
        headings = list(re.finditer(r"(?m)^###\s+([^\n]+)\s*$", text))
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            body = text[heading.start() : end]
            claim_match = re.search(
                r"(?m)^\*\*Claim(?: identity)?(?::\*\*|:)\s+`([^`]+)`\s*$"
                r"|^Claim(?: identity)?:\s+`([^`]+)`\s*$",
                body,
            )
            if not claim_match:
                continue
            claim_id = claim_match.group(1) or claim_match.group(2)
            declared_family = re.search(
                r"(?m)^\*\*(?:Family|Field):\*\*\s+`?([^`\n]+)`?\s*$"
                r"|^(?:Family|Field):\s+`?([^`\n]+)`?\s*$",
                body,
            )
            preceding_h2 = [row for row in h2_headings if row.start() < heading.start()]
            h2_family = preceding_h2[-1].group(1).strip() if preceding_h2 else None
            publication_family = (
                (declared_family.group(1) or declared_family.group(2)).strip()
                if declared_family
                else h2_family
            )
            forced = re.search(
                r"(?ms)^\*\*Question, law and forced result\.\*\*\s*(.*?)"
                r"(?=^\*\*|^###|\Z)",
                body,
            )
            claim_sections[claim_id] = {
                "active_paper_role": role,
                "heading": heading.group(1).strip(),
                "question_law_forced_result": forced.group(1).strip() if forced else None,
                "publication_family": clean_family(publication_family)
                if publication_family
                else None,
                "section_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            }
    return dict(appearances), claim_sections


def main() -> int:
    inventory_bytes = INVENTORY_PATH.read_bytes()
    inventory = json.loads(inventory_bytes)
    appearances, paper_sections = active_paper_sections(inventory)
    enriched = []
    family_summary: dict[str, dict[str, Counter]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    package_presence = Counter()

    for claim in inventory["claim_ledger"]["claims"]:
        claim_id = claim["claim_id"]
        package = ROOT / "claims" / claim_id
        registration = read_json(package / "registration.json") or {}
        certificate = read_json(package / "certificate.json") or {}
        census = read_json(package / "candidate_census.json") or {}
        elimination = read_json(package / "elimination_receipt.json") or {}
        controls_document = read_json(package / "controls.json") or {}
        empirical = read_json(package / "empirical_validation.json") or {}
        why_path = package / "WHY_DERIVATION_CHECK.md"
        why_text = why_path.read_text(encoding="utf-8") if why_path.exists() else ""
        status_path = package / "STATUS.md"
        status_text = status_path.read_text(encoding="utf-8") if status_path.exists() else ""

        for name, path in (
            ("registration", package / "registration.json"),
            ("certificate", package / "certificate.json"),
            ("candidate_census", package / "candidate_census.json"),
            ("controls", package / "controls.json"),
            ("elimination_receipt", package / "elimination_receipt.json"),
            ("empirical_validation", package / "empirical_validation.json"),
            ("why_derivation_check", why_path),
            ("status", status_path),
        ):
            package_presence[f"{name}_present"] += path.exists()

        decisions = elimination.get("decisions", [])
        survivors = [row for row in decisions if row.get("survives")]
        survivor_ids = {row.get("candidate_id") for row in survivors}
        survivor_records = [
            row
            for row in census.get("candidates", [])
            if row.get("candidate_id") in survivor_ids
        ]
        control_rows = controls_document.get("controls", [])
        branch = claim["branch"]
        package_family = family_key(branch, claim_id)
        paper_section = paper_sections.get(claim_id)
        publication_family = (
            paper_section.get("publication_family") if paper_section else None
        ) or family_label(package_family)
        family = publication_family.lower().replace(" ", "_")
        family_summary[branch][family].update(
            claims=1,
            candidates=claim["candidate_count"],
            controls=claim["control_count"],
            empirical_packages=bool(empirical),
            why_records=bool(why_text),
            active_paper_sections=claim_id in paper_sections,
        )

        files = {}
        for path in (
            package / "registration.json",
            package / "certificate.json",
            package / "candidate_census.json",
            package / "controls.json",
            package / "elimination_receipt.json",
            package / "empirical_validation.json",
            why_path,
            status_path,
        ):
            if path.exists():
                files[str(path.relative_to(ROOT))] = sha256(path)

        record = {
            "branch": branch,
            "branch_label": BRANCH_LABELS[branch],
            "family": family,
            "family_label": publication_family,
            "claim_id": claim_id,
            "title": claim["title"],
            "statement": claim["statement"],
            "formal_status": claim["closure_status"],
            "empirical_status": claim["external_status"],
            "model_admitted": claim["model_admitted"],
            "dependencies": registration.get("dependencies", claim["dependencies"]),
            "provenance_classes": registration.get("provenance_classes", []),
            "candidate_grammar": registration.get("candidate_grammar", {}),
            "excluded_inputs": registration.get("excluded_inputs", []),
            "required_controls": registration.get("required_controls", []),
            "intended_certificate": registration.get("intended_certificate"),
            "registration_date": registration.get("registration_date"),
            "candidate_count": claim["candidate_count"],
            "candidate_generation_rule": census.get("generation_rule"),
            "candidate_boundary": census.get("grammar_boundary"),
            "unique_survivor_count": claim["unique_survivor_count"],
            "survivors": survivors,
            "survivor_records": survivor_records,
            "closure": elimination.get("closure", {}),
            "exact_result": certificate.get("exact_result"),
            "certificate": certificate,
            "controls": control_rows,
            "control_count": claim["control_count"],
            "passed_control_count": claim["passed_control_count"],
            "falsification_condition": empirical.get("falsification_condition"),
            "evidence_source_ids": empirical.get("data_source_ids", []),
            "measurements": empirical.get("measurements", []),
            "target_opened_after_seal": empirical.get("target_opened_after_seal"),
            "all_rows_preserved": empirical.get("all_rows_preserved"),
            "empirical_comparison_passed": empirical.get("passed"),
            "measurement_receipt_hash": empirical.get("measurement_receipt_hash"),
            "why": section(why_text, "WHY") if why_text else None,
            "derivation_narrative": section(why_text, "DERIVATION") if why_text else None,
            "check_narrative": section(why_text, "CHECK") if why_text else None,
            "status_record": status_text.strip() or None,
            "active_paper_appearances": appearances.get(claim_id, []),
            "active_paper_claim_section": paper_section,
            "registered_receipt_id": claim["registered_receipt_id"],
            "receipt_path": claim["receipt_path"],
            "package_files": files,
        }
        enriched.append(record)

    family_rows = []
    for branch in BRANCH_ORDER:
        for family, counts in sorted(family_summary[branch].items()):
            family_rows.append(
                {
                    "branch": branch,
                    "branch_label": BRANCH_LABELS[branch],
                    "family": family,
                    "family_label": next(
                        record["family_label"]
                        for record in enriched
                        if record["branch"] == branch and record["family"] == family
                    ),
                    **dict(counts),
                }
            )

    result = {
        "schema": "sft-v3-exhaustive-toe-content-matrix/1",
        "date": "2026-07-31",
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "source_inventory": str(INVENTORY_PATH.relative_to(ROOT)),
        "source_inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "claim_count": len(enriched),
        "family_count": len(family_rows),
        "branch_order": BRANCH_ORDER,
        "package_presence": dict(package_presence),
        "active_paper_any_appearance_count": sum(
            bool(record["active_paper_appearances"]) for record in enriched
        ),
        "active_paper_claim_section_count": sum(
            bool(record["active_paper_claim_section"]) for record in enriched
        ),
        "claims_without_active_paper_appearance": [
            record["claim_id"]
            for record in enriched
            if not record["active_paper_appearances"]
        ],
        "claims_without_claim_section_or_why": [
            record["claim_id"]
            for record in enriched
            if not record["active_paper_claim_section"] and not record["why"]
        ],
        "family_summary": family_rows,
        "claims": enriched,
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Exhaustive ToE content matrix",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Date:** 31 July 2026  ",
        "**Role:** Direct-source completeness control for the exhaustive SFT V3 ToE monograph.",
        "",
        "## Global coverage",
        "",
        "| Surface | Count |",
        "|---|---:|",
        f"| Live claims | {result['claim_count']:,} |",
        f"| Derived family groups | {result['family_count']:,} |",
        f"| Claims appearing in an active paper | {result['active_paper_any_appearance_count']:,} |",
        f"| Claims with an extracted active-paper claim section | {result['active_paper_claim_section_count']:,} |",
        f"| Claims absent from active papers | {len(result['claims_without_active_paper_appearance']):,} |",
        f"| Claims lacking both an active-paper claim section and a WHY record | {len(result['claims_without_claim_section_or_why']):,} |",
        "",
        "Every live claim is retained in the JSON matrix with its complete statement, dependencies, grammar, count, survivor, controls, evidence, chronology fields, receipt identity and package file hashes. Complete candidate members and machine traces remain in the claim packages and machine archive.",
        "",
        "## Branch and family coverage",
        "",
        "| Branch | Family | Claims | Candidates | Controls | Empirical packages | Narrative records |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in family_rows:
        lines.append(
            f"| {row['branch_label']} | {row['family_label']} | {row['claims']:,} | "
            f"{row['candidates']:,} | {row['controls']:,} | "
            f"{row['empirical_packages']:,} | "
            f"{max(row['why_records'], row['active_paper_sections']):,} |"
        )
    lines.extend(
        [
            "",
            "## Claims absent from the active paper set",
            "",
            "These current claims entered after the active branch-paper surfaces or belong to Cross-Branch Synthesis. They must receive full generated monograph sections rather than being omitted.",
            "",
        ]
    )
    for claim_id in result["claims_without_active_paper_appearance"]:
        lines.append(f"- `{claim_id}`")
    lines.extend(
        [
            "",
            "## Machine identity",
            "",
            f"- Source inventory: `{result['source_inventory_sha256']}`",
            f"- Exhaustive matrix JSON: `{sha256(OUTPUT_JSON)}`",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "claims": result["claim_count"],
                "families": result["family_count"],
                "active_paper_appearances": result[
                    "active_paper_any_appearance_count"
                ],
                "active_paper_claim_sections": result[
                    "active_paper_claim_section_count"
                ],
                "missing_active_paper": len(
                    result["claims_without_active_paper_appearance"]
                ),
                "json_bytes": OUTPUT_JSON.stat().st_size,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
