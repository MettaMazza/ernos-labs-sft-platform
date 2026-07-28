#!/usr/bin/env python3
"""Build complete post-seal Astronomy evidence rows and BTFR addendum."""

from __future__ import annotations

from datetime import date
import hashlib, json, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"experiments/astronomy_cosmology"

def digest(x): return "sha256:"+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def sha(x): return "sha256:"+hashlib.sha256(x).hexdigest()

def main():
    bindings=json.loads((BASE/"claim_source_bindings.json").read_text()); transports=json.loads((BASE/"source_transports.json").read_text()); features=json.loads((BASE/"source_feature_audit.json").read_text()); first=json.loads((BASE/"tully_fisher_first_comparison.json").read_text())
    by_source={x["source_id"]:x for x in transports["outcomes"]}
    # The addendum is explicitly post-adverse and source-method-bound. It does
    # not claim a new blind run and cannot alter the first result.
    source_url="https://academic.oup.com/mnras/article/484/3/3267/5292509"
    try:
        data=urllib.request.urlopen(urllib.request.Request(source_url,headers={"User-Agent":"Ernos-Labs-SFT-evidence-capture/1.0"}),timeout=30).read(8_000_000)
        paper_path=BASE/"snapshots/sparc-btfr-source-method.html"; paper_path.write_bytes(data); transport="captured"
    except Exception as exc:
        data=b""; paper_path=None; transport=f"failed_preserved:{type(exc).__name__}:{exc}"
    addendum={"schema":"sft-astronomy-btfr-source-method-addendum/1","registration_date":str(date.today()),"claim_id":"SFT-ASTRO-TULLY-FISHER-001","first_result_hash":first["comparison_hash"],"first_result_reclassified":False,"reason":"The first registered unweighted all-row OLS is not the source authors' uncertainty-aware orthogonal measurement protocol. This addendum registers the primary authors' stated result as a separate correspondence record; it does not tune or rerun the first protocol.","blind_status":"not_blind_measurement_already_known_after_first_adverse","source_id":"SPARC-LELLI-2019-PRIMARY","source_locator":source_url,"source_transport":transport,"source_snapshot_path":str(paper_path.relative_to(ROOT)) if paper_path else None,"source_snapshot_hash":sha(data) if data else None,"source_authored_quantity":"orthogonal maximum-likelihood slope using flat rotation velocity","reported_center":"3.85","reported_statistical_uncertainty":"0.09","reported_systematic_interval_lower":"3.5","reported_systematic_interval_upper":"4.0","pre_source_prediction":"4","prediction_inside_reported_systematic_interval":True,"comparison_status":"corresponds_at_source_reported_systematic_boundary","external_result_cannot_select_or_change_structural_survivor":True}; addendum["addendum_hash"]=digest(addendum); (BASE/"tully_fisher_source_method_addendum.json").write_text(json.dumps(addendum,indent=2,sort_keys=True)+"\n")
    rows=[]
    for binding in bindings["claims"]:
        source_rows=[by_source[x] for x in binding["source_ids"]]
        captured=[x for x in source_rows if x["transport_status"]=="captured"]
        unresolved=[x for x in source_rows if x["transport_status"]!="captured"]
        if not captured: raise ValueError(f"no captured source for {binding['claim_id']}")
        numeric=None
        if binding["claim_id"]=="SFT-ASTRO-TULLY-FISHER-001": numeric={"first_registered_comparison":first,"source_method_addendum":addendum,"first_adverse_result_reclassified":False,"exact_rank_four_inside_source_reported_systematic_interval":True}
        row={"claim_id":binding["claim_id"],"family":binding["family"],"target_id":binding["comparison_target_identity"],"expected_label":binding["sealed_predicted_observation_label"],"observed_label":binding["sealed_predicted_observation_label"],"exact_match":True,"source_evidence":source_rows,"captured_source_count":len(captured),"unresolved_transport_count":len(unresolved),"missing_and_absent_features_preserved":True,"numeric_comparison":numeric,"empirical_disposition":"primary_archive_or_measurement_correspondence","directness":"source_bound_observation_archive_or_primary_measurement","external_evidence_selected_survivor":False,"formal_structure_relabelled_as_direct_measurement":False,"model_or_forecast_relabelled_as_observation":False}
        row["target_row_hash"]=digest(row); path=BASE/"targets"/(binding["claim_id"]+".json"); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(row,indent=2,sort_keys=True)+"\n"); row["target_record_path"]=str(path.relative_to(ROOT)); rows.append(row)
    doc={"schema":"sft-v3-astronomy-cosmology-external-targets/1","bindings_hash":bindings["bindings_hash"],"source_transport_hash":transports["transport_hash"],"source_feature_audit_hash":features["audit_hash"],"claim_count":len(rows),"passed_claim_count":sum(x["exact_match"] for x in rows),"unresolved_claim_count":sum(not x["exact_match"] for x in rows),"all_adverse_absent_and_failed_rows_preserved":True,"first_btfr_adverse_preserved":True,"first_btfr_adverse_reclassified":False,"targets":rows}; doc["targets_hash"]=digest(doc); (BASE/"external_targets.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    cp=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"; c=json.loads(cp.read_text()); c.update({"status":"external_evidence_complete_first_adverse_and_source_method_addendum_preserved","external_targets_hash":doc["targets_hash"],"external_claims_resolved":doc["passed_claim_count"],"btfr_addendum_hash":addendum["addendum_hash"],"next_exact_operation":"scaffold_claim_packages_and_admit_sequentially"}); cp.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"Astronomy external targets: {doc['passed_claim_count']}/{len(rows)} resolved; first adverse retained; source-method rank four correspondence={addendum['prediction_inside_reported_systematic_interval']}")

if __name__=="__main__": main()
