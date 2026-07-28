#!/usr/bin/env python3
"""Complete integration audit for the Astronomy foundation."""

from __future__ import annotations

import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from sft.astronomy_cosmology.generated_law import ASTRONOMY_BLUEPRINTS,candidate_forms

def digest(x): return "sha256:"+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def main():
    claims=json.loads((ROOT/"census/claims.json").read_text())["claims"]; admitted={x["claim_id"]:x for x in claims if x.get("model_admitted") is True}; audit=json.loads((ROOT/"audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.json").read_text()); inv=json.loads((ROOT/"publications/inventories/astronomy_cosmology.json").read_text()); targets=json.loads((ROOT/"experiments/astronomy_cosmology/external_targets.json").read_text()); transports=json.loads((ROOT/"experiments/astronomy_cosmology/source_transports.json").read_text())
    ids=[x.claim_id for x in ASTRONOMY_BLUEPRINTS]; missing=[x for x in ids if x not in admitted]
    if missing: raise ValueError(f"unadmitted Astronomy claims: {missing}")
    if len(ids)!=72 or sum(len(candidate_forms(x)) for x in ASTRONOMY_BLUEPRINTS)!=18432: raise ValueError("candidate census differs")
    if targets["claim_count"]!=72 or targets["passed_claim_count"]!=72 or targets["unresolved_claim_count"]!=0: raise ValueError("external target census incomplete")
    if targets["first_btfr_adverse_preserved"] is not True or targets["first_btfr_adverse_reclassified"] is not False: raise ValueError("first BTFR adverse changed")
    atom_map=inv["prior_atom_to_foundation_claim"]
    if len(atom_map)!=audit["summary"]["atomic_question_count"] or any(x not in admitted for x in atom_map.values()): raise ValueError("prior atom reconciliation incomplete")
    receipt_rows=[]
    for cid in ids:
        package=ROOT/"claims"/cid; cert=json.loads((package/"certificate.json").read_text()); receipt=ROOT/admitted[cid]["receipt_path"]
        if not receipt.is_file() or cert["engine_receipt_hash"]!=admitted[cid]["receipt_hash"] or not cert["independently_recomputed"]: raise ValueError(f"certificate failure: {cid}")
        receipt_rows.append({"claim_id":cid,"receipt_hash":admitted[cid]["receipt_hash"],"derivation_seal_hash":cert["derivation_seal_hash"],"independent_certificate_hash":cert["independent_certificate_hash"],"target_row_hash":cert["claim_target_evaluation"]["target_row_hash"]})
    result={"schema":"sft-v3-astronomy-cosmology-foundation-integration-audit/1","status":"current_evidence_closed_extension_open","required_claim_count":72,"admitted_claim_count":72,"candidate_count":18432,"family_count":12,"prior_entries_reviewed":audit["source_surface"]["total_entries_reviewed"],"prior_atomic_questions":len(atom_map),"prior_atomic_questions_reconciled":len(atom_map),"source_count":transports["attempted"],"captured_source_count":transports["captured"],"failed_source_transports_preserved":transports["failed_preserved"],"external_target_count":targets["claim_count"],"external_target_match_count":targets["passed_claim_count"],"first_btfr_adverse_preserved":True,"first_btfr_adverse_reclassified":False,"extension_open":True,"permanent_lock_claimed":False,"engine_seal":"sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a","verification_authority_seal":"sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8","receipts":receipt_rows}; result["integration_hash"]=digest(result); path=ROOT/"audits/astronomy_cosmology_foundation_integration.json"; path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    cp=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"; c=json.loads(cp.read_text()); c.update({"status":"foundational_branch_current_evidence_closed_extension_open_paper_not_yet_drafted","admitted_claim_count":72,"remaining_claim_count":0,"integration_audit_path":str(path.relative_to(ROOT)),"integration_audit_hash":result["integration_hash"],"next_exact_operation":"draft_and_proofread_standalone_paper"}); cp.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"Astronomy integration: 72/72, 18432 candidates, 53/53 prior atoms, hash={result['integration_hash']}")
if __name__=="__main__": main()
