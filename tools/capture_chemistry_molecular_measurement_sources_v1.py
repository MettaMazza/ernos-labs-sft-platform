#!/usr/bin/env python3
"""Capture the complete NIST CaH+ state-preparation/readout data package."""
from __future__ import annotations
import csv,io,json
from hashlib import sha256
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/"experiments/external_sources/chemistry/snapshots/molecular-measurement-v1"
IDENTITIES=ROOT/"experiments/external_sources/chemistry/molecular_measurement_target_identities_v1.json"
TARGETS=ROOT/"experiments/external_sources/chemistry/molecular_measurement_withheld_targets_v1.json"
META_URL="https://data.nist.gov/od/id/mds2-3389"
EXPECTED={"real_time_state_tracking_data.csv":50,"entry_and_exit_times_J_2.csv":117,"entry_and_exit_times_J_1.csv":55,"sublevel_distribution_J0_to_J1.csv":6,"histogram_of_recoveries_from_J_0_and_J_2.csv":4,"tracking_time_series.csv":71,"pressure_dependence_of_J_0_to_J_1_transitions.csv":4,"appearance_time_histogram_J_0_to_J1.csv":23}
def get(url,accept=None):
 h={"User-Agent":"Ernos-Labs-SFT/3.0 scientific-reproducibility Maria.Smith.Sftoe@gmail.com"}
 if accept:h["Accept"]=accept
 return urlopen(Request(url,headers=h),timeout=180).read()
def h(path):return "sha256:"+sha256(path.read_bytes()).hexdigest()
def main():
 SNAP.mkdir(parents=True,exist_ok=True);meta_bytes=get(META_URL,"application/json");meta_path=SNAP/"mds2-3389-metadata.json";meta_path.write_bytes(meta_bytes);meta=json.loads(meta_bytes);components={c["filepath"]:c for c in meta["components"]};identities=[];targets=[];sources=[]
 if set(EXPECTED)|{"3389_README.txt"}!=set(components):raise RuntimeError("NIST measurement package component inventory changed")
 for name,c in sorted(components.items()):
  path=SNAP/name;path.write_bytes(get(c["downloadURL"]));sources.append({"filepath":name,"download_url":c["downloadURL"],"media_type":c["mediaType"],"description":c.get("description",""),"snapshot_path":str(path.relative_to(ROOT)),"snapshot_hash":h(path)})
  if name not in EXPECTED:continue
  parsed=list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig"))))
  header,data=parsed[0],parsed[1:]
  if len(data)!=EXPECTED[name]:raise RuntimeError(name+": complete row count changed")
  for ordinal,row in enumerate(data,1):
   target_id="MDS2-3389-%s-%04d"%(name.removesuffix(".csv").replace("_","-"),ordinal)
   identities.append({"target_id":target_id,"file":name,"row_ordinal":ordinal,"column_identities":header,"source_description":c.get("description",""),"snapshot_path":str(path.relative_to(ROOT)),"snapshot_hash":h(path),"source_url":c["downloadURL"]})
   targets.append({"target_id":target_id,"file":name,"row_ordinal":ordinal,"cells":row,"snapshot_path":str(path.relative_to(ROOT)),"snapshot_hash":h(path)})
 if len(targets)!=330:raise RuntimeError("complete molecular measurement package must contain 330 data rows")
 source={"source_id":"NIST-MDS2-3389-CAH-QUANTUM-STATE-TRACKING-CONTROL-V1.0.1","title":meta["title"],"doi":"10.18434/mds2-3389","metadata_url":META_URL,"metadata_snapshot_path":str(meta_path.relative_to(ROOT)),"metadata_snapshot_hash":h(meta_path),"components":sources,"retrieval_date":"2026-07-26"}
 IDENTITIES.write_text(json.dumps({"schema":"sft-v3-molecular-measurement-identities/1","source":source,"rows":identities},indent=2,sort_keys=True)+"\n")
 TARGETS.write_text(json.dumps({"schema":"sft-v3-molecular-measurement-withheld-targets/1","source":source,"rows":targets},indent=2,sort_keys=True)+"\n")
 print("complete data rows:",len(targets));print("complete data cells:",sum(len(r["cells"]) for r in targets));print("identity registry:",h(IDENTITIES));print("withheld target registry:",h(TARGETS))
if __name__=="__main__":main()
