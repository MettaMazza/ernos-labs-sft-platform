#!/usr/bin/env python3
"""Build and verify the local Astronomy foundation evidence release."""

from __future__ import annotations

import hashlib,json,shutil,zipfile
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/"output/release/astronomy-cosmology-1.0.0"
MD=ROOT/"publications/current/astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS.md"
PDF=ROOT/"output/pdf/from-one-sky-to-cosmos-astronomy-cosmology-foundation-paper-001-v1.0.pdf"
META=ROOT/"publication/astronomy_cosmology_foundation_zenodo_metadata.json"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    meta=json.loads(META.read_text()); integration=json.loads((ROOT/"audits/astronomy_cosmology_foundation_integration.json").read_text())
    if meta["publication_authorized"] is not False or meta["remote_publish_status"]!="not_authorized": raise ValueError("remote publication state changed")
    if integration["admitted_claim_count"]!=72 or integration["candidate_count"]!=18432: raise ValueError("Astronomy integration incomplete")
    pages=len(PdfReader(str(PDF)).pages); words=len(MD.read_text().split())
    if pages<100 or words<30000: raise ValueError("paper depth gate failed")
    RELEASE.mkdir(parents=True,exist_ok=True)
    md_name="02_From-One-Sky-to-Cosmos_Astronomy-and-Cosmology-Foundation-Paper-001-v1.0.md"; pdf_name="01_From-One-Sky-to-Cosmos_Astronomy-and-Cosmology-Foundation-Paper-001-v1.0.pdf"
    shutil.copy2(MD,RELEASE/md_name); shutil.copy2(PDF,RELEASE/pdf_name); shutil.copy2(META,RELEASE/"03_Zenodo-Metadata.json")
    evidence=[p for base in (ROOT/"claims",ROOT/"experiments/astronomy_cosmology",ROOT/"audits",ROOT/"publications/inventories",ROOT/"census") for p in base.rglob("*") if p.is_file() and ("SFT-ASTRO-" in str(p) or "astronomy_cosmology" in p.name or "astronomy-cosmology" in p.name)]
    zip_path=RELEASE/"04_Astronomy-Cosmology-Foundation-Evidence-1.0.0.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(set(evidence)): z.write(p,p.relative_to(ROOT))
    files=sorted(p for p in RELEASE.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (RELEASE/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    manifest={"schema":"sft-v3-astronomy-cosmology-local-release/1","version":"1.0.0","publication_authorized":False,"remote_actions_performed":False,"paper_words":words,"pdf_pages":pages,"claims":72,"candidates":18432,"evidence_files":len(evidence),"integration_hash":integration["integration_hash"],"files":{p.name:"sha256:"+sha(p) for p in files}}; manifest["release_hash"]="sha256:"+hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",", ":")).encode()).hexdigest(); (RELEASE/"release_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    # Rebuild checksums including the manifest.
    files=sorted(p for p in RELEASE.iterdir() if p.is_file() and p.name!="SHA256SUMS"); (RELEASE/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    cp=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"; c=json.loads(cp.read_text()); c.update({"status":"foundational_branch_current_evidence_closed_extension_open_local_release_ready","paper_path":str(MD.relative_to(ROOT)),"pdf_path":str(PDF.relative_to(ROOT)),"paper_word_count":words,"pdf_page_count":pages,"local_release_path":str(RELEASE.relative_to(ROOT)),"local_release_hash":manifest["release_hash"],"remote_publication_authorized":False,"next_exact_operation":"commit_branch_artifacts_locally_then_begin_social_collective_foundation"}); cp.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"Astronomy local release gate: PASS claims=72 candidates=18432 words={words} pages={pages} evidence={len(evidence)} publication_authorized=false")
if __name__=="__main__": main()
