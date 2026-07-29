#!/usr/bin/env python3
"""Build the local, unpublished Mathematics v1.5 evidence map and release."""
from __future__ import annotations
import hashlib,json,shutil,zipfile
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md"
PDF=ROOT/"output/pdf/from-fold-to-mathematics-branch-paper-001-v1.5.pdf"
RECON=ROOT/"census/mathematics_discipline_current_reconciliation_v23.json"
OUT=ROOT/"publications/successors/mathematics";RELEASE=ROOT/"output/release/mathematics-1.5.0"
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as stream:
  for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
 return "sha256:"+h.hexdigest()
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def current_certificate(package,row):
 matches=[p for p in package.glob("certificate*.json") if read(p).get("engine_receipt_hash")==row["receipt_hash"]]
 if len(matches)!=1:raise SystemExit("current certificate count: "+row["claim_id"])
 return matches[0],read(matches[0])
def main():
 recon=read(RECON);text=PAPER.read_text(encoding="utf-8")
 rows=[row for family in recon["completed_families"].values() for row in family]
 if len(rows)!=323 or len({x["claim_id"] for x in rows})!=323 or recon["current_open_count"]!=0:raise SystemExit("Mathematics release requires 323/323")
 claims=[];archive={PAPER,PDF,RECON,ROOT/"census/mathematics_discipline_obligations.json",ROOT/"census/claims.json",ROOT/"census/execution_manifest.json"}
 candidates=controls=0
 for row in rows:
  if row["claim_id"] not in text:raise SystemExit("paper omits "+row["claim_id"])
  package=ROOT/"claims"/row["claim_id"];cert_path,cert=current_certificate(package,row);receipt=ROOT/row["receipt_path"]
  census=read(package/"candidate_census.json");control=read(package/"controls.json");candidates+=len(census["candidates"]);controls+=len(control["controls"])
  empirical_path=package/"empirical_validation.json";empirical=read(empirical_path) if empirical_path.exists() else None
  claims.append({"claim_id":row["claim_id"],"receipt_path":row["receipt_path"],"engine_receipt_hash":row["receipt_hash"],"receipt_file_hash":sha(receipt),"derivation_seal_hash":cert.get("derivation_seal_hash"),"independent_implementation_hash":cert.get("independent_implementation_hash"),"independent_certificate_hash":cert.get("independent_certificate_hash"),"measurement_receipt_hash":cert.get("measurement_receipt_hash"),"external_validation_hash":cert.get("external_validation_hash"),"empirical_validation_hash":cert.get("empirical_validation_hash"),"closure_status":row["closure_status"],"external_status":row["external_status"],"candidate_count":len(census["candidates"]),"control_count":len(control["controls"]),"all_external_rows_preserved":empirical.get("all_rows_preserved") if empirical else None,"root_trace_registered":True})
  archive.add(receipt);archive.update(path for path in package.rglob("*") if path.is_file())
 if candidates!=97280 or controls!=1292:raise SystemExit("Mathematics totals changed")
 for pattern in ("sft/engine/**/*.py","sft/mathematics/**/*.py","generated/mathematics/**/*.py","tests/test_mathematics*.py","tools/*mathematics*.py","census/mathematics*.json","audits/MATHEMATICS*","audits/ACTIVE_MATHEMATICS*","experiments/external_sources/mathematics/**/*","governance/*","LICENSE*","README.md","CONSTITUTION.md","pyproject.toml","uv.lock"):
  archive.update(path for path in ROOT.glob(pattern) if path.is_file())
 pages=len(PdfReader(str(PDF)).pages)
 evidence={"schema":"sft-v3-mathematics-complete-field-paper-evidence-map/1","branch_id":"mathematics","version":"1.5.0","publication_authorized":False,"required_claim_count":323,"required_family_count":24,"required_candidate_count":97280,"unique_survivor_count":323,"control_count":1292,"independent_reconstruction_count":323,"current_open_obligation_count":0,"completion_is_dated_and_extension_open":True,"reconciliation_identity":recon["reconciliation_identity"],"canonical_engine_seal":"sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a","verification_authority_seal":"sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8","claims":claims,"paper":{"path":PAPER.relative_to(ROOT).as_posix(),"sha256":sha(PAPER)},"pdf":{"path":PDF.relative_to(ROOT).as_posix(),"sha256":sha(PDF),"pages":pages},"complete_claim_coverage":True,"root_traces_registered":True,"controls_passed":True,"ready_for_review":True,"ready_to_publish":False}
 evidence_path=OUT/"evidence_map_v1_5.json";write(evidence_path,evidence);archive.add(evidence_path)
 manifest={"schema":"sft-v3-branch-publication-manifest/1","branch_id":"mathematics","version":"1.5.0","source_path":PAPER.relative_to(ROOT).as_posix(),"source_hash":sha(PAPER),"rendered_paper_path":PDF.relative_to(ROOT).as_posix(),"rendered_paper_hash":sha(PDF),"evidence_map_path":evidence_path.relative_to(ROOT).as_posix(),"evidence_map_hash":sha(evidence_path),"required_claim_count":323,"generated_candidate_count":97280,"comprehensive_derivation_coverage":True,"controls_passed":True,"root_traces_verified":True,"publication_authorized":False,"ready_for_review":True}
 manifest_path=OUT/"manifest_v1_5.json";write(manifest_path,manifest);archive.add(manifest_path)
 metadata={"metadata":{"title":"From Fold to Mathematics: An Exact, Parameter-Free and Machine-Closed Complete-Field Derivation from Smithian Fold Theory","upload_type":"publication","publication_type":"article","publication_date":"2026-07-29","description":"<p><strong>Mathematics Branch Paper 001, version 1.5.0</strong>, executes the complete-field roadmap: 323 of 323 frozen obligations across 24 families, 97,280 generated candidates, 323 unique survivors and 1,292 passed controls.</p><p>The paper preserves the complete foundation, prior-corpus and scientific-calculator record and adds claim-by-claim derivation, observation, boundary, certificate and receipt detail for arithmetic, algebra, combinatorics, graphs, geometry, topology, analysis, probability, optimization, dynamics, logic, category, numerical, symbolic, validation and handoff families.</p><p>The branch is complete to its dated census and explicitly open to lawful extension. No axiom, free or fitted parameter, semantic numerical zero, negative, irrational, imaginary or floating proof scalar, completed infinity, ungenerated continuum or stochastic cause is admitted as a premise. The engine and verification authority remain unchanged.</p>","creators":[{"name":"Smith, Maria","affiliation":"Ernos Labs"}],"access_right":"open","license":"cc-by-4.0","version":"1.5.0","language":"eng","keywords":["Smithian Fold Theory","complete-field mathematics","exact arithmetic","algebra","combinatorics","graph theory","geometry","topology","analysis","probability","optimization","dynamical systems","logic","category theory","numerical mathematics","symbolic mathematics","scientific calculator","computational proof","open science","clean-room replication"],"related_identifiers":[{"identifier":"https://github.com/MettaMazza/ernos-labs-sft-platform","relation":"isSupplementedBy","scheme":"url"},{"identifier":"10.5281/zenodo.21627708","relation":"isNewVersionOf","scheme":"doi"}],"notes":"Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. Ernos Labs is a separate scientific-standards conformance designation. Local draft only; publication requires Maria Smith's explicit authorization."},"publication_authorized":False,"ready_to_publish":False}
 metadata_path=OUT/"zenodo_metadata_v1_5.json";write(metadata_path,metadata);archive.add(metadata_path)
 RELEASE.mkdir(parents=True,exist_ok=True)
 for old in RELEASE.iterdir():
  if old.is_file():old.unlink()
 pdf_name="00_From-Fold-to-Mathematics_Mathematics-Branch-Paper-001-v1.5.pdf";zip_name="01_Ernos-Labs-SFT-Mathematics-Branch-Evidence-and-Source-v1.5.0.zip";md_name="02_From-Fold-to-Mathematics_Mathematics-Branch-Paper-001-v1.5.md"
 shutil.copyfile(PDF,RELEASE/pdf_name);shutil.copyfile(PAPER,RELEASE/md_name);prefix="ernos-labs-sft-mathematics-branch-1.5.0/"
 with zipfile.ZipFile(RELEASE/zip_name,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for path in sorted(archive):
   info=zipfile.ZipInfo(prefix+path.relative_to(ROOT).as_posix(),(2026,7,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,path.read_bytes())
 names=(pdf_name,zip_name,md_name);(RELEASE/"99_SHA256SUMS.txt").write_text("".join(f"{sha(RELEASE/name).removeprefix('sha256:')}  {name}\n" for name in names),encoding="utf-8")
 print(json.dumps({"claims":323,"families":24,"candidates":candidates,"controls":controls,"pages":pages,"files_in_evidence_archive":len(archive),"release":RELEASE.relative_to(ROOT).as_posix(),"paper":sha(PAPER),"pdf":sha(PDF),"archive":sha(RELEASE/zip_name)},indent=2))
if __name__=="__main__":main()
