#!/usr/bin/env python3
"""Verify the local Classical Computation v1.4 manuscript and release evidence."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"
PDF = ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf"
EVIDENCE = ROOT / "publications/successors/computation/evidence_map_v1_4.json"
METADATA = ROOT / "publications/successors/computation/zenodo_metadata_v1_4.json"
RECON = ROOT / "census/computation_discipline_current_reconciliation_v12.json"
CENSUS = ROOT / "census/computation_discipline_obligations.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def main():
    paper = PAPER.read_text(encoding="utf-8")
    evidence = read(EVIDENCE)
    metadata = read(METADATA)
    recon = read(RECON)
    frozen = read(CENSUS)
    claims = evidence["claims"]
    dependency_cache = {}

    def dependencies(claim_id: str):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return ()
        registration_path = ROOT / "claims" / claim_id / "registration.json"
        require(registration_path.exists(), f"missing lineage registration: {claim_id}")
        return tuple(read(registration_path).get("dependencies", ()))

    def reaches_root(claim_id: str, stack=()):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return True
        if claim_id in dependency_cache:
            return dependency_cache[claim_id]
        require(claim_id not in stack, f"lineage cycle: {claim_id}")
        claim_dependencies = dependencies(claim_id)
        require(bool(claim_dependencies), f"rootless lineage: {claim_id}")
        result = any(reaches_root(dependency, stack + (claim_id,)) for dependency in claim_dependencies)
        dependency_cache[claim_id] = result
        return result

    require("version 1.4.0" in paper, "paper version missing")
    require("369/369 obligations" in paper, "headline completion count missing")
    require("94,464" in paper and "1,476" in paper, "headline candidate/control totals missing")
    require("## 130. Complete-field execution - version 1.4" in paper, "complete-field section missing")
    require("## 133. Complete-field conclusion" in paper, "complete-field conclusion missing")
    require("Version 1.4 DOI: pending archival deposit" in paper, "prepublication DOI state missing")
    require("Maria.Smith.Sftoe@gmail.com" in paper, "author contact missing")
    require("https://discord.gg/ucwGryVxGr" in paper, "community submission link missing")
    require("https://github.com/MettaMazza" in paper, "GitHub link missing")
    require("Ernos Labs" in paper and "standards-conformance" in paper, "Ernos Labs designation boundary missing")
    require("financial gatekeeping" in paper and "credential" in paper, "editorial access argument missing")
    require("open to lawful" in paper, "extension-open boundary missing")
    require("BB_F(k)=k" in paper and "P_F=NP_F" in paper and "16,384" in paper, "native headline results missing")
    require("not silently exported" in paper, "native/external grammar boundary missing")
    require("quantum" in paper.lower() and "downstream" in paper.lower(), "quantum handoff missing")

    require(evidence["claim_count"] == 369 and len(claims) == 369, "evidence-map claim count mismatch")
    require(evidence["candidate_count"] == 94464, "evidence-map candidate count mismatch")
    require(evidence["control_count"] == 1476, "evidence-map control count mismatch")
    require(evidence["frozen_census_identity"] == frozen["census_identity"], "evidence/census identity mismatch")
    require(evidence["reconciliation_identity"] == recon["reconciliation_identity"], "evidence/reconciliation identity mismatch")
    require(len({row["claim_id"] for row in claims}) == 369, "duplicate evidence claim")
    require(len({row["obligation_id"] for row in claims}) == 369, "duplicate evidence obligation")
    require(sum(row["candidate_count"] for row in claims) == 94464, "claim candidate total mismatch")
    require(sum(row["control_count"] for row in claims) == 1476, "claim control total mismatch")
    require(all(row["unique_survivor_count"] == 1 for row in claims), "nonunique evidence survivor")
    require(all(row["root_trace_registered"] for row in claims), "missing registered root/dependency trace")
    require(all(reaches_root(row["claim_id"]) for row in claims), "a computation claim does not reach There Is No Nothing")
    require(all((ROOT / row["receipt_path"]).exists() for row in claims), "missing receipt path")
    require(all(f"#### `{row['obligation_id']}`" in paper for row in claims), "paper omits an obligation section")
    require(all(f"`{row['claim_id']}`" in paper for row in claims), "paper omits a claim identity")

    require(metadata["metadata"]["version"] == "1.4.0", "metadata version mismatch")
    require(metadata["publication_authorized"] is False, "new version must remain unpublished")
    require(metadata["ready_to_publish"] is False, "new version must remain unauthorized")
    require("10.5281/zenodo.21627721" in json.dumps(metadata), "previous DOI relation missing")

    reader = PdfReader(str(PDF))
    require(len(reader.pages) > 100, "PDF unexpectedly short")
    require(reader.metadata.title == "After Turing: The Fold Machine", "PDF title metadata mismatch")
    require(reader.metadata.author == "Maria Smith", "PDF author metadata mismatch")
    first = "\n".join((reader.pages[index].extract_text() or "") for index in range(min(6, len(reader.pages))))
    require("After Turing" in first and "369" in first and "Maria Smith" in first, "PDF front matter missing")
    require(all("None" not in str(row.get(key)) for row in claims for key in ("claim_id", "engine_receipt_hash", "receipt_path")), "null controlling evidence value")

    print(f"PASS computation paper v1.4: 369 claims, 94,464 candidates, 1,476 controls, {len(reader.pages)} PDF pages")


if __name__ == "__main__":
    main()
