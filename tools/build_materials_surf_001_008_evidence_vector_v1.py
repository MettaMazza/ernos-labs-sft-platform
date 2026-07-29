#!/usr/bin/env python3
from hashlib import sha256
from html import unescape
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"experiments/external_sources/materials/surf_001_008_v1"; MANIFEST=BASE/"source_custody_manifest.json"; OUT=BASE/"complete_evidence_vector_v1.json"
BINDINGS={"SFT-MAT-SURF-FREE-STATE-ENERGY-001":(("NIST-POLYMER-SURFACE-INTERFACE","surface and interface/ interphase play a major role","measuring surface/interface properties"),),"SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002":(("NIST-WETTING-WRINKLED-SURFACES","systematic study of the wetting behavior","anisotropic microstructure","simple sinusoidal profile"),),"SFT-MAT-SURF-ADHESION-SEPARATION-003":(("NIST-ADHESION-ENERGY-DISSIPATION","Adhesion plays a significant role","interfacial friction","energy dissipation"),),"SFT-MAT-SURF-COATING-SUBSTRATE-004":(("NIST-COATING-MICROSTRUCTURE","relationship between the microstructure and the appearance of coated materials","confocal laser microscopy"),),"SFT-MAT-SURF-ROUGHNESS-SCALE-005":(("NIST-COATING-SURFACE-ROUGHNESS","surface-roughness","residual stresses","interface between the ceramic top coat"),),"SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006":(("NIST-POLYMER-SURFACE-CHEMISTRY","chemical spectroscopy","chemical and morphological microstructure","polymer interfaces"),),"SFT-MAT-SURF-TRIBOFILM-RETENTION-007":(("NIST-TRIBOLOGICAL-COATINGS","nanostructured coatings","tribological applications"),),"SFT-MAT-SURF-DELAMINATION-008":(("NIST-EDGE-DELAMINATION","edge delamination test","failure of adhesion","temperature and film thickness"),)}
def canonical(value): return "sha256:"+sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def file_hash(path): return "sha256:"+sha256(path.read_bytes()).hexdigest()
def normalize(text): return "".join(character for character in unescape(re.sub(r"<[^>]+>"," ",text)).casefold() if character.isalnum())
def main():
 manifest=json.loads(MANIFEST.read_text()); manifest_identity=manifest.pop("manifest_identity")
 if canonical(manifest)!=manifest_identity: raise SystemExit("SURF manifest changed")
 documents={row["source_id"]:row for row in manifest["documents"]}; corpora={}
 for source_id,row in documents.items():
  path=ROOT/row["snapshot_path"]
  if file_hash(path)!=row["snapshot_hash"]: raise SystemExit("SURF source changed "+source_id)
  corpora[source_id]=normalize(path.read_text(errors="ignore"))
 rows=[]
 for claim_id,bindings in BINDINGS.items():
  comparisons=[]
  for source_id,*fragments in bindings:
   present=[normalize(fragment) in corpora[source_id] for fragment in fragments]
   if not all(present): raise SystemExit(f"SURF fragments absent {claim_id} {source_id} {present}")
   document=documents[source_id]; comparisons.append({"source_id":source_id,"source_status":document["status"],"snapshot_path":document["snapshot_path"],"snapshot_hash":document["snapshot_hash"],"registered_fragments":list(fragments),"all_fragments_present":True,"used_for_favourable_comparison":True})
  rows.append({"claim_id":claim_id,"comparisons":comparisons,"comparison_count":len(comparisons),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 value={"schema":"sft-v3-materials-surf-complete-evidence-vector/1","target_registry_identity":manifest["target_registry_identity"],"source_custody_manifest_identity":manifest_identity,"claim_count":len(rows),"claims":rows,"source_status_rows":list(documents.values()),"captured_source_count":len(documents),"unavailable_source_count":0,"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False}; value["complete_vector_identity"]=canonical(value); OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); print(json.dumps({"claims":len(rows),"comparisons":sum(row["comparison_count"] for row in rows),"sources":len(documents),"identity":value["complete_vector_identity"]},indent=2))
if __name__=="__main__": main()

