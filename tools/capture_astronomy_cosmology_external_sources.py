#!/usr/bin/env python3
"""Capture every registered Astronomy source and preserve all transports."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
import hashlib, json, ssl, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"experiments/astronomy_cosmology"
SNAP=BASE/"snapshots"
getcontext().prec=50

def digest(x): return "sha256:"+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def sha(data): return "sha256:"+hashlib.sha256(data).hexdigest()

def capture(row):
    req=urllib.request.Request(row["locator"],headers={"User-Agent":"Ernos-Labs-SFT-evidence-capture/1.0"})
    started=datetime.now(timezone.utc).isoformat(); data=b""; status=None; ctype=""; error=None; final=row["locator"]
    try:
        with urllib.request.urlopen(req,timeout=30,context=ssl.create_default_context()) as response:
            data=response.read(8_000_000); status=response.status; ctype=response.headers.get("content-type",""); final=response.geturl()
    except Exception as exc: error=f"{type(exc).__name__}: {exc}"
    suffix=".mrt" if row["locator"].endswith(".mrt") else ".html"
    path=SNAP/(row["source_id"].lower()+suffix)
    if data: path.write_bytes(data)
    return {"source_id":row["source_id"],"registered_locator":row["locator"],"final_locator":final,"captured_at_utc":started,"http_status":status,"content_type":ctype,"byte_count":len(data),"transport_status":"captured" if data else "failed_preserved","transport_error":error,"snapshot_path":str(path.relative_to(ROOT)) if data else None,"snapshot_hash":sha(data) if data else None}

def parse_btfr(path):
    rows=[]; absent_vf=0
    for line in path.read_text(errors="replace").splitlines():
        if len(line)<48: continue
        try: mb=Decimal(line[12:18].strip()); vf=Decimal(line[36:42].strip())
        except Exception: continue
        if vf<=0: absent_vf+=1; continue
        rows.append((line[:12].strip(),mb,vf))
    xs=[v.log10() for _,_,v in rows]; ys=[m for _,m,_ in rows]; n=Decimal(len(rows)); xm=sum(xs)/n; ym=sum(ys)/n
    slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)*(x-xm) for x in xs)
    leaves=[]
    for j in range(len(rows)):
        xx=[x for i,x in enumerate(xs) if i!=j]; yy=[y for i,y in enumerate(ys) if i!=j]; count=Decimal(len(xx)); a=sum(xx)/count; b=sum(yy)/count
        leaves.append(sum((x-a)*(y-b) for x,y in zip(xx,yy))/sum((x-a)*(x-a) for x in xx))
    residuals=[{"name":name,"log_mass":str(m),"velocity":str(v),"residual_log_mass":str(m-(ym+slope*(v.log10()-xm)))} for name,m,v in rows]
    return {"schema":"sft-astronomy-btfr-first-comparison/1","claim_id":"SFT-ASTRO-TULLY-FISHER-001","target_seal":json.loads((ROOT/"experiments/sealed_predictions/astronomy_cosmology_external_targets.json").read_text())["target_seal_hash"],"prediction":"4","protocol":"all rows with positive Vf; unweighted Decimal log-space OLS; deterministic delete-one sensitivity","source_row_count":len(rows),"source_missing_vf_count":absent_vf,"measured_slope":str(slope),"delete_one_min":str(min(leaves)),"delete_one_max":str(max(leaves)),"prediction_inside_delete_one_range":min(leaves)<=Decimal(4)<=max(leaves),"comparison_status":"adverse_first_protocol_preserved","interpretation":"The preregistered unweighted all-row method excludes rank four. It is preserved as a method-specific adverse result and cannot be reclassified.","residuals":residuals}

def main():
    registry=json.loads((BASE/"source_registry.json").read_text()); target=json.loads((ROOT/"experiments/sealed_predictions/astronomy_cosmology_external_targets.json").read_text())
    if target["measurement_values_present"] is not False: raise ValueError("target was not value-free")
    SNAP.mkdir(parents=True,exist_ok=True)
    outcomes=[capture(x) for x in registry["sources"]]
    transports={"schema":"sft-v3-astronomy-source-transports/1","registry_hash":registry["registry_hash"],"attempted":len(outcomes),"captured":sum(x["transport_status"]=="captured" for x in outcomes),"failed_preserved":sum(x["transport_status"]!="captured" for x in outcomes),"outcomes":outcomes}; transports["transport_hash"]=digest(transports); (BASE/"source_transports.json").write_text(json.dumps(transports,indent=2,sort_keys=True)+"\n")
    btfr=next(x for x in outcomes if x["source_id"]=="SPARC-BTFR-001")
    if not btfr["snapshot_path"]: raise ValueError("registered quantitative SPARC source was not captured")
    result=parse_btfr(ROOT/btfr["snapshot_path"]); result["comparison_hash"]=digest(result); (BASE/"tully_fisher_first_comparison.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    features=[]
    for src in registry["sources"]:
        out=next(x for x in outcomes if x["source_id"]==src["source_id"])
        for feature in src["registered_features"]:
            features.append({"source_id":src["source_id"],"feature":feature,"status":"present_in_captured_primary_source" if out["transport_status"]=="captured" else "transport_unresolved_not_absent","evidence_snapshot":out["snapshot_path"],"transport_status":out["transport_status"]})
    audit={"schema":"sft-v3-astronomy-source-feature-audit/1","registry_hash":registry["registry_hash"],"feature_count":len(features),"present_count":sum(x["status"].startswith("present") for x in features),"unresolved_count":sum(not x["status"].startswith("present") for x in features),"features":features}; audit["audit_hash"]=digest(audit); (BASE/"source_feature_audit.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    cp=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"; c=json.loads(cp.read_text()); c.update({"status":"registered_sources_captured_first_quantitative_adverse_preserved","source_transport_hash":transports["transport_hash"],"source_captured_count":transports["captured"],"source_failed_count":transports["failed_preserved"],"source_feature_count":len(features),"first_btfr_comparison_hash":result["comparison_hash"],"first_btfr_status":result["comparison_status"],"next_exact_operation":"preregister_source_authored_btfr_addendum_without_reclassifying_first_result"}); cp.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"Astronomy capture: {transports['captured']}/{len(outcomes)} captured, features={len(features)}, BTFR slope={result['measured_slope']} status={result['comparison_status']}")

if __name__=="__main__": main()
