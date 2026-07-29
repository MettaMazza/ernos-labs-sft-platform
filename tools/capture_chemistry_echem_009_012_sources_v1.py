#!/usr/bin/env python3
"""Capture ECHEM-009–012 sources after all four separate seals."""
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"experiments/external_sources/chemistry/snapshots/echem-009-012-polarization-v1";INV=OUT/"source-inventory-v1.json"
CLAIMS=(("009","d5d4bfd5988f0fd8d6b81edcc0d81cfa74d77c98f82590b24d4eb11fd6f71b60","c10192ff2384d083d9e77d84cb9fe0575afff4c94a312fbcdaab16305a4f9581"),("010","f24bcb12e48aac155380ff426a6b64e32b4a4274ca92d78770f4303e2287b2db","c26a77df3955524deaf82a2dba2c0e3e599916bbbdeb002e3d3a19cb7d78be5c"),("011","dd809a7f1cadc7f14e83b4dfdf54cc15ef7d66792783121acacd98a9896801f5","823ab8786bf5eb66115b22b0110395505a93f00f4d0270bc75cd5cf582be3274"),("012","4a483b5d23af4f193dc1aeaf9442ed6dde16f8c116103e134682e2837da30f99","682ddfeb4e4053e01cb12e7ea17c45b9a5b0621c6e417dfdf820015eec086b8a"))
SOURCES=(("NBS-JRES-GALVANIC-COUPLES-1950","https://nvlpubs.nist.gov/nistpubs/jres/045/jresv45n5p373_A1b.pdf","nbs-galvanic-couples-1950.pdf"),("NBS-JRES-IRON-CORROSION-1957","https://nvlpubs.nist.gov/nistpubs/jres/58/jresv58n3p145_A1b.pdf","nbs-iron-corrosion-1957.pdf"),("NIST-GRAPHENE-DOUBLE-LAYER-2020","https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=929222","nist-graphene-double-layer-2020.pdf"),("NIST-TN-1253-COATING-POLARIZATION-1988","https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1253.pdf","nist-tn1253-coating-polarization.pdf"))
def h(b):return "sha256:"+hashlib.sha256(b).hexdigest()
def main():
 if OUT.exists():raise SystemExit("capture exists")
 sealed=[]
 for key,sealhash,payloadhash in CLAIMS:
  sp=ROOT/f"experiments/sealed_predictions/chemistry_echem_{key}_pre_source_v1.json";p=json.loads(sp.read_text());recorded=p.pop("sealed_payload_hash")
  if h(sp.read_bytes())!="sha256:"+sealhash or recorded!="sha256:"+payloadhash or h(json.dumps(p,sort_keys=True,separators=(",",":")).encode())!=recorded:raise SystemExit(f"seal changed {key}")
  sealed.append({"claim":key,"seal_sha256":"sha256:"+sealhash,"payload_sha256":recorded})
 OUT.mkdir(parents=True);rows=[]
 for sid,uri,name in SOURCES:
  with urlopen(Request(uri,headers={"User-Agent":"Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"}),timeout=180) as r:data,status,ctype=r.read(),r.status,r.headers.get("Content-Type")
  if status!=200 or not data.startswith(b"%PDF"):raise SystemExit(f"capture failed {sid}")
  p=OUT/name;p.write_bytes(data);rows.append({"source_id":sid,"authority":"National Bureau of Standards / National Institute of Standards and Technology","uri":uri,"snapshot_path":p.relative_to(ROOT).as_posix(),"snapshot_sha256":h(data),"snapshot_bytes":len(data),"content_type":ctype,"capture_status":"captured_once_after_all_four_claim_seals"})
 inv={"schema":"sft-v3-chemistry-echem-009-012-source-inventory/1","family":"ECHEM-009-012","all_four_claims_sealed_separately_before_source_capture":True,"sealed_claims":sealed,"rows":rows};INV.write_text(json.dumps(inv,indent=2,sort_keys=True)+"\n");print(json.dumps({"inventory":h(INV.read_bytes()),"sources":rows},indent=2))
if __name__=="__main__":main()
