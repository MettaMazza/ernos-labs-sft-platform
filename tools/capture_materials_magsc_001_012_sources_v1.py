#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/materials_magsc_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/materials/magsc_001_012_v1"
REMOTE=(
("NIST-MAGNETIC-SUSCEPTIBILITY-SRM","https://www.nist.gov/mml/materials-science-and-engineering-division/magnetic-moment-and-susceptibility-standard-reference","nist-magnetic-susceptibility-srm.html"),
("NIST-PARAMAGNETIC-DIAMAGNETIC","https://www.nist.gov/publications/intermediate-regime-between-metal-and-superconductor-below-t-100-k-nisi","nist-paramagnetic-diamagnetic.html"),
("NIST-MAGNETIZATION-LAB","https://www.nist.gov/mml/materials-science-and-engineering-division/magnetization-characterization-laboratory","nist-magnetization-lab.html"),
("NIST-MAGNETIC-IMAGING","https://www.nist.gov/programs-projects/magnetic-imaging","nist-magnetic-imaging.html"),
("NIST-HYSTERESIS-STANDARD","https://www.ctcms.nist.gov/~rdm/std2/spec2.html","nist-hysteresis-standard.html"),
("NIST-MAGNETIC-MATERIALS-METROLOGY","https://www.nist.gov/programs-projects/magnetic-materials-metrology","nist-magnetic-materials-metrology.html"),
("NIST-SPIN-ORBIT","https://www.nist.gov/programs-projects/spin-orbit-interaction-devices-and-quantum-materials","nist-spin-orbit.html"),
("NIST-SPIN-TRANSPORT","https://www.nist.gov/publications/spin-transport-memristive-devices","nist-spin-transport.html"),
("NIST-SPIN-SPECTROSCOPY","https://www.nist.gov/programs-projects/optical-and-microwave-spectroscopy-microelectronic-systems","nist-spin-spectroscopy.html"),
("NIST-SC-CRITICAL-FIELDS","https://nvlpubs.nist.gov/nistpubs/jres/090/jresv90n2p95_A1b.pdf","nist-sc-critical-fields.pdf"),
("NIST-SC-FLUX-LATTICE","https://www.nist.gov/ncnr/flux-lattice-superconductors-and-melting","nist-sc-flux-lattice.html"),
("NIST-SUPERFLUID-PERSISTENT-FLOW","https://www.nist.gov/news-events/news/2007/11/nist-announces-first-observation-persistent-flow-gas","nist-superfluid-persistent-flow.html"),)
def dig(b):return "sha256:"+sha256(b).hexdigest()
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REG.read_bytes();reg=json.loads(rb)
 if reg["target_count"]!=12 or reg["target_content_present"] is not False:raise SystemExit("MAGSC registry changed")
 if OUT.exists():raise SystemExit("refusing overwrite")
 OUT.mkdir(parents=True);docs=[]
 for sid,uri,name in REMOTE:
  with urlopen(Request(uri,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as r:b=r.read();st=getattr(r,"status",200);ct=r.headers.get("Content-Type","unreported")
  if st!=200 or len(b)<1000:raise SystemExit(f"MAGSC capture halt {sid} {st} {len(b)}")
  p=OUT/name;p.write_bytes(b);docs.append({"source_id":sid,"source_uri":uri,"snapshot_path":p.relative_to(ROOT).as_posix(),"snapshot_hash":dig(b),"byte_count":len(b),"http_status":st,"content_type":ct,"status":"captured_post_registry","used_for_favourable_comparison":True})
 registered={s for t in reg["targets"] for s in t["source_identities"]};captured={x["source_id"] for x in docs}
 if registered!=captured:raise SystemExit("MAGSC source mismatch")
 p={"schema":"sft-v3-materials-magsc-source-custody/1","target_registry_path":REG.relative_to(ROOT).as_posix(),"target_registry_hash":dig(rb),"target_registry_identity":reg["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True};p["manifest_identity"]=canon(p);(OUT/"source_custody_manifest.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"documents":len(docs),"identity":p["manifest_identity"]},indent=2))
if __name__=="__main__":main()
