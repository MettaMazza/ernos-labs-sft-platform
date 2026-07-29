#!/usr/bin/env python3
"""Seal four NUCHEM-001–004 laws and targets before quantitative source capture."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROWS=(
("001","SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001","nuclide_chemical_carrier_law_v1.py","5b1cba279810bdd761987c7970c717a881142d20a173320131bb07f29e4dc95b","4ca08fe787a69f03c55002905d835c0dcf012a7b8ff31935430693db2cc3f263","held-element-identity__positive-nucleon-count__held-nuclear-state__held-chemical-species__held-chemical-phase__positive-counted-occurrence__complete-nuclide-species-vector__fresh-occurrence-preserves-identity"),
("002","SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002","radioactive_chemical_transformation_law_v1.py","4484c0c4efdef922aabd3fa14b9b74756305dfb03c6b3d884d96f661dd5ffd95","a9e98d3078a684b6fcad2c64ad764da4f6202bb9a9f8a77d3369479821315b26","held-parent-nuclide__held-daughter-nuclide__held-parent-daughter-species__held-decay-channel__positive-counted-transformations__complete-directed-transformation-network__structural-EmptyOne-no-edge__successor-retains-prior-network"),
("003","SFT-CHEM-ACTIVITY-AMOUNT-TIME-003","activity_amount_time_law_v1.py","186a95d558ac63e883b8af7b60c6c1780fcfb7b042bcfc264d73050ce22f96bd","7f2dbaba26aea9d499aae35ce29a8217e2fdb7c4ef8c60a9d5f4cc453176aa0d","held-nuclide-species__positive-counted-initial-occurrences__positive-counted-transformations__positive-counted-resource-intervals__exact-transformations-per-resource__positive-Take-or-EmptyOne-retained-amount__complete-activity-amount-time-vector__ledger-successor-recomputes-relation"),
("004","SFT-CHEM-RADIOACTIVE-BRANCHING-CHEMICAL-YIELD-004","radioactive_branching_yield_law_v1.py","163218db86c3cbdf11e55babcbcc5a982a3376a4841957f6c6ee05f2dd5ef52c","cb85154e9f9cbd381cd7824c57e63364117df291dc7f3148bcb507a15c9a8787","held-decay-channel__held-daughter-chemical-species__positive-counted-branch-events__positive-counted-recovered-events__exact-recovered-per-branch-ratio__complete-branch-partition-sums-to-One__complete-daughter-yield-vector__new-branch-repartitions-complete-total"))
def h(p):return "sha256:"+hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n,c,l,lh,ih,survivor in ROWS:
  lp=ROOT/"sft/chemistry"/l;ip=ROOT/f"experiments/external_sources/chemistry/nuchem_{n}_target_identities_v1.json";out=ROOT/f"experiments/sealed_predictions/chemistry_nuchem_{n}_pre_source_v1.json"
  if out.exists():raise SystemExit(f"seal exists {n}")
  if h(lp)!="sha256:"+lh or h(ip)!="sha256:"+ih:raise SystemExit(f"law/identity changed {n}")
  p={"schema":"sft-v3-target-value-blind-derivation-seal/1","branch":"chemistry","family":"NUCHEM-001-004","claim_id":c,"obligation_id":f"SFT-CHEM-OBL-NUCHEM-{n}","sealed_date":"2026-07-28","derivation_path":lp.relative_to(ROOT).as_posix(),"derivation_hash":h(lp),"target_identity_path":ip.relative_to(ROOT).as_posix(),"target_identity_hash":h(ip),"candidate_cardinality":256,"operational_witness_count":8,"predicted_unique_survivor":survivor,"complete_source_values_units_uncertainties_corrections_and_outcomes_opened_for_this_claim_before_seal":False,"external_value_or_outcome_used_by_candidate_generator_or_eliminator":False}
  p["sealed_payload_hash"]="sha256:"+hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest();out.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(n,h(out),p["sealed_payload_hash"])
if __name__=="__main__":main()
