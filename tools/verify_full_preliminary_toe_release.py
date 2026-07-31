#!/usr/bin/env python3
"""Verify the authorised full-scale SFT V3 preliminary ToE publication.

The verifier is publication-inert.  It requires the manuscript, claim audit,
publication-guidance gate, rendered PDFs and a separate human visual-QA record
to pass before it emits a publication dossier.  It records Maria Smith's
existing authority but performs no remote action itself.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "publications/preliminary_toe"
PUBLICATION = HERE / "publication"
MASTER = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
CLAIMS_JSON = HERE / "appendices/COMPLETE_CLAIM_INVENTORY.json"
FREEZE = PUBLICATION / "CORPUS_FREEZE.json"
GUIDANCE_AUDIT = PUBLICATION / "PUBLICATION_GUIDANCE_COMPLIANCE.json"
VISUAL_QA = PUBLICATION / "PDF_VISUAL_QA.json"
REPORT = PUBLICATION / "PUBLICATION_VERIFICATION.json"
REPORT_MD = PUBLICATION / "PUBLICATION_APPROVAL_DOSSIER.md"

PDF_SPECS = (
    {
        "role": "conceptual_monograph",
        "path": ROOT
        / "output/pdf/smithian-fold-theory-v3-preliminary-theory-of-everything-v0.1.0.pdf",
        "orientation": "portrait",
        "minimum_pages": 200,
        "required": (
            "The Smithian Fold Theory of Everything",
            "2,751 model-admitted claims",
            "Historical trajectory and V3 reconciliation",
            "Protein Fold V3",
            "Conclusion",
            "New standalone V3 Zenodo record",
        ),
    },
    {
        "role": "complete_claim_inventory",
        "path": ROOT
        / "output/pdf/sft-v3-preliminary-toe-complete-claim-inventory-v0.1.0.pdf",
        "orientation": "landscape",
        "minimum_pages": 200,
        "required": (
            "Smithian Fold Theory V3 Complete Claim Inventory",
            "SFT-ROOT-THERE-IS-NO-NOTHING",
            "Cross-Branch Synthesis",
            "Machine identity boundary",
        ),
    },
    {
        "role": "scientific_audit_layer",
        "path": ROOT
        / "output/pdf/sft-v3-preliminary-toe-scientific-audit-layer-v0.1.0.pdf",
        "orientation": "landscape",
        "minimum_pages": 100,
        "required": (
            "Smithian Fold Theory V3 Scientific Audit Layer",
            "2,751",
            "892,246",
            "11,004",
        ),
    },
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pdf_record(spec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    path: Path = spec["path"]
    failures = []
    if not path.is_file():
        return {"role": spec["role"], "path": str(path.relative_to(ROOT))}, [
            f"missing PDF: {path.relative_to(ROOT)}"
        ]
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        failures.append(f"encrypted PDF: {path.relative_to(ROOT)}")
    page_count = len(reader.pages)
    if page_count < spec["minimum_pages"]:
        failures.append(
            f"{spec['role']} has {page_count} pages; expected at least {spec['minimum_pages']}"
        )
    page_sizes = []
    blank_pages = []
    replacement_pages = []
    extracted = []
    for index, page in enumerate(reader.pages, 1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        page_sizes.append((round(width, 3), round(height, 3)))
        text = page.extract_text() or ""
        extracted.append(text)
        if len(text.strip()) < 20 and index not in (1, 2, page_count):
            blank_pages.append(index)
        if "\ufffd" in text or "■" in text:
            replacement_pages.append(index)
    unique_sizes = sorted(set(page_sizes))
    for width, height in unique_sizes:
        actual = "landscape" if width > height else "portrait"
        if actual != spec["orientation"]:
            failures.append(
                f"{spec['role']} unexpected {actual} page {width}x{height}"
            )
    full_text = "\n".join(extracted)
    missing_text = [value for value in spec["required"] if value not in full_text]
    failures.extend(f"{spec['role']} missing extracted text: {value}" for value in missing_text)
    if len(blank_pages) > max(3, page_count // 100):
        failures.append(f"{spec['role']} has excessive blank pages: {blank_pages[:30]}")
    if replacement_pages:
        failures.append(f"{spec['role']} has replacement glyphs on pages {replacement_pages[:30]}")
    metadata = reader.metadata or {}
    if metadata.get("/Author") != "Maria Smith":
        failures.append(f"{spec['role']} PDF author metadata is not Maria Smith")
    return (
        {
            "role": spec["role"],
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            "pages": page_count,
            "page_sizes": [list(value) for value in unique_sizes],
            "blank_page_candidates": blank_pages,
            "replacement_glyph_pages": replacement_pages,
            "missing_required_text": missing_text,
            "author_metadata": metadata.get("/Author"),
        },
        failures,
    )


def main() -> int:
    failures = []
    for path in (MASTER, CLAIMS_JSON, FREEZE, GUIDANCE_AUDIT, VISUAL_QA):
        if not path.is_file():
            failures.append(f"missing verification input: {path.relative_to(ROOT)}")
    if failures:
        raise SystemExit("\n".join(failures))

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    guidance = json.loads(GUIDANCE_AUDIT.read_text(encoding="utf-8"))
    visual = json.loads(VISUAL_QA.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS_JSON.read_text(encoding="utf-8"))

    if freeze.get("status") != "PASS_LOCAL_BUILD":
        failures.append("corpus freeze is not PASS_LOCAL_BUILD")
    if freeze.get("proposed_version") != "0.1.0":
        failures.append("corpus freeze is not the first standalone V3 version 0.1.0")
    if freeze.get("publication_operation") != "create_new_standalone_v3_record":
        failures.append("corpus freeze does not require a new standalone V3 record")
    if freeze.get("concept_doi") is not None:
        failures.append("corpus freeze assigns a concept DOI before Zenodo publication")
    if freeze.get("concept_record_id") != 21717583:
        failures.append("corpus freeze does not bind Zenodo concept record 21717583")
    if freeze.get("zenodo_draft_id") != 21717584:
        failures.append("corpus freeze does not bind Zenodo draft 21717584")
    if freeze.get("version_doi") != "10.5281/zenodo.21717584":
        failures.append("corpus freeze does not bind reserved version DOI 10.5281/zenodo.21717584")
    if not freeze.get("remote_publication_authorised"):
        failures.append("corpus freeze does not record Maria Smith's publication authority")
    if guidance.get("status") != "PASS" or guidance.get("failure_count"):
        failures.append("publication-guidance audit is not PASS")
    if not guidance.get("remote_publication_authorised"):
        failures.append("publication-guidance audit does not record publication authority")
    if visual.get("status") != "PASS" or not visual.get("human_visual_inspection_completed"):
        failures.append("human PDF visual-QA record is not PASS")
    if visual.get("publication_operation") != "create_new_standalone_v3_record":
        failures.append("visual-QA record does not bind the standalone V3 publication operation")
    if not visual.get("remote_publication_authorised"):
        failures.append("visual-QA record does not bind the authorised publication")
    if len(claims.get("claims", [])) != 2751:
        failures.append("complete claim JSON does not contain 2,751 claims")

    command = [
        sys.executable,
        "-m",
        "unittest",
        "publications.preliminary_toe.tests.test_full_preliminary_toe_release_candidate",
    ]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if run.returncode != 0:
        failures.append("strict manuscript tests failed")

    pdfs = []
    for spec in PDF_SPECS:
        row, row_failures = pdf_record(spec)
        pdfs.append(row)
        failures.extend(row_failures)

    visual_roles = {row.get("role") for row in visual.get("artifacts", [])}
    expected_roles = {spec["role"] for spec in PDF_SPECS}
    if visual_roles != expected_roles:
        failures.append(
            f"visual-QA roles {sorted(visual_roles)} do not match {sorted(expected_roles)}"
        )
    for row in visual.get("artifacts", []):
        if len(row.get("inspected_pages", [])) < 5:
            failures.append(f"visual-QA sample too small for {row.get('role')}")
        source = next((pdf for pdf in pdfs if pdf.get("role") == row.get("role")), None)
        if source and row.get("sha256") != source.get("sha256"):
            failures.append(f"visual-QA hash is stale for {row.get('role')}")

    report = {
        "schema": "sft-v3-preliminary-toe-local-publication-verification/v1",
        "status": "PASS" if not failures else "HALT",
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "proposed_version": "0.1.0",
        "version": "0.1.0",
        "publication_operation": "create_new_standalone_v3_record",
        "create_new_concept": True,
        "concept_doi": None,
        "concept_record_id": 21717583,
        "zenodo_draft_id": 21717584,
        "version_doi": "10.5281/zenodo.21717584",
        "historical_pre_v3_concept_doi": "10.5281/zenodo.21182468",
        "remote_publication_authorised": True,
        "protected_authority_edited": False,
        "master_sha256": digest(MASTER),
        "claim_inventory_sha256": digest(CLAIMS_JSON),
        "corpus_freeze_sha256": digest(FREEZE),
        "publication_guidance_audit_sha256": digest(GUIDANCE_AUDIT),
        "visual_qa_sha256": digest(VISUAL_QA),
        "strict_test_command": " ".join(command),
        "strict_test_exit_code": run.returncode,
        "strict_test_stdout": run.stdout,
        "strict_test_stderr": run.stderr,
        "pdfs": pdfs,
        "failure_count": len(failures),
        "failures": failures,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Preliminary ToE publication dossier",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Standalone V3 version:** 0.1.0  ",
        "**Publication operation:** create a new standalone Zenodo record  ",
        "**Zenodo draft:** 21717584  ",
        "**Concept record:** 21717583; concept DOI assigned when public  ",
        "**Version DOI:** 10.5281/zenodo.21717584  ",
        "**Deprecated V2 ToE concept DOI:** 10.5281/zenodo.21182468; historical reference only  ",
        f"**Local verification:** `{report['status']}`  ",
        "**Remote publication:** authorised by Maria Smith",
        "",
        "| Artifact | Pages | SHA-256 |",
        "|---|---:|---|",
    ]
    for row in pdfs:
        lines.append(
            f"| {row['role']} | {row.get('pages', 0):,} | `{row.get('sha256', 'missing')}` |"
        )
    lines.extend(
        [
            "",
            f"Strict manuscript tests: `{run.returncode}`. Publication-guidance checks: "
            f"`{guidance.get('status')}` ({len(guidance.get('checks', []))}/23 recorded).",
            "",
        ]
    )
    if failures:
        lines.extend(["## Publication halts", ""] + [f"- {value}" for value in failures])
    else:
        lines.extend(
            [
                "## Authorisation boundary",
                "",
                "Maria Smith authorised the GitHub and Zenodo publication transaction.",
                "This verifier records that authority and verifies the exact artifacts;",
                "it does not itself perform or broaden the remote operation.",
            ]
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": len(failures), "pdfs": len(pdfs)}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
