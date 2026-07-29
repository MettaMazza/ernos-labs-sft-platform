#!/usr/bin/env python3
"""Verify the local Quantum Computation v1.4 manuscript and evidence."""

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md"
CURRENT = ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md"
PDF = ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001-v1.4.pdf"
EVIDENCE = ROOT / "publications/successors/quantum_computation/evidence_map_v1_4.json"
METADATA = ROOT / "publications/successors/quantum_computation/zenodo_metadata_v1_4.json"
RECON = ROOT / "census/quantum_computation_discipline_current_reconciliation_v13.json"
CENSUS = ROOT / "census/quantum_computation_discipline_obligations.json"


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

    def dependencies(claim_id):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return ()
        registration = ROOT / "claims" / claim_id / "registration.json"
        require(registration.exists(), f"missing lineage registration: {claim_id}")
        return tuple(read(registration).get("dependencies", ()))

    def reaches_root(claim_id, stack=()):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return True
        if claim_id in dependency_cache:
            return dependency_cache[claim_id]
        require(claim_id not in stack, f"lineage cycle: {claim_id}")
        deps = dependencies(claim_id)
        require(bool(deps), f"rootless lineage: {claim_id}")
        result = any(reaches_root(dep, stack + (claim_id,)) for dep in deps)
        dependency_cache[claim_id] = result
        return result

    require("version 1.4.0" in paper, "paper version missing")
    require("288/288 obligations" in paper, "headline completion missing")
    require("73,728" in paper and "1,152" in paper, "headline totals missing")
    require("## 36. Complete-field execution - version 1.4" in paper, "complete-field section missing")
    require("## 40. Complete-field conclusion" in paper, "conclusion missing")
    require("Version 1.4 DOI: pending archival deposit" in paper, "DOI state missing")
    require("Maria.Smith.Sftoe@gmail.com" in paper and "https://discord.gg/ucwGryVxGr" in paper and "https://github.com/MettaMazza" in paper, "mission contacts missing")
    require("financial gatekeeping" in paper and "credential" in paper, "editorial argument missing")
    require("open to lawful" in paper and "standards-conformance" in paper, "extension/designation boundary missing")
    require("2t+1" in paper and "no-cloning" in paper and "halting" in paper, "headline quantum results missing")
    require("bc2e0eb42e8650c8" in paper, "preserved halt missing")
    require(CURRENT.read_text(encoding="utf-8") == paper, "current landing paper differs from v1.4 source")

    require(evidence["claim_count"] == 288 and len(claims) == 288, "evidence count mismatch")
    require(evidence["candidate_count"] == 73728 and evidence["control_count"] == 1152, "evidence totals mismatch")
    require(evidence["frozen_census_identity"] == frozen["census_identity"], "census identity mismatch")
    require(evidence["reconciliation_identity"] == recon["reconciliation_identity"], "reconciliation identity mismatch")
    require(len({row["claim_id"] for row in claims}) == 288, "duplicate claim")
    require(len({row["obligation_id"] for row in claims}) == 288, "duplicate obligation")
    require(sum(row["candidate_count"] for row in claims) == 73728, "candidate total mismatch")
    require(sum(row["control_count"] for row in claims) == 1152, "control total mismatch")
    require(all(row["unique_survivor_count"] == 1 for row in claims), "nonunique survivor")
    require(all(row["root_trace_registered"] and reaches_root(row["claim_id"]) for row in claims), "broken root trace")
    require(all((ROOT / row["receipt_path"]).exists() for row in claims), "missing receipt")
    require(all(f"#### `{row['obligation_id']}`" in paper for row in claims), "paper omits obligation")
    require(all(f"`{row['claim_id']}`" in paper for row in claims), "paper omits claim")

    require(metadata["metadata"]["version"] == "1.4.0", "metadata version mismatch")
    require(metadata["publication_authorized"] is False and metadata["ready_to_publish"] is False, "draft authorization mismatch")
    require("10.5281/zenodo.21627748" in json.dumps(metadata), "previous DOI relation missing")

    reader = PdfReader(str(PDF))
    require(len(reader.pages) > 80, "PDF unexpectedly short")
    require(reader.metadata.title == "The Quantum Fold Machine" and reader.metadata.author == "Maria Smith", "PDF metadata mismatch")
    first = "\n".join((reader.pages[index].extract_text() or "") for index in range(min(7, len(reader.pages))))
    last = "\n".join((reader.pages[index].extract_text() or "") for index in range(max(0, len(reader.pages) - 5), len(reader.pages)))
    require("The Quantum Fold Machine" in first and "288" in first and "Maria Smith" in first, "PDF front matter missing")
    require("Complete-field conclusion" in last or "References" in last, "PDF ending missing")
    print(f"PASS quantum paper v1.4: 288 claims, 73,728 candidates, 1,152 controls, {len(reader.pages)} PDF pages")


if __name__ == "__main__":
    main()
