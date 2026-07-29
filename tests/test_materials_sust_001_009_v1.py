from fractions import Fraction
from pathlib import Path
from sft.materials.sust_001_009_external_v1 import load_complete_vector
from sft.materials.sust_001_009_laws_v1 import ORDER,SPECS,embodied_ledger,availability_boundary,reuse_remanufacture,recovery_yield,circular_flow,durability_extension,toxicity_handoff,substitution,end_of_life
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_sust_complete_grammars():
 assert len(ORDER)==9
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]); assert len(rows)==len({r["candidate_id"] for r in rows})==256; assert sum(r["candidate_id"]==survivor_id(SPECS[cid]) for r in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_sust_native_relations():
 assert embodied_ledger((("a","material",1,"s"),("b","energy",2,"s")),"scope")["total"]==3
 assert availability_boundary("m",2,3,"period","source")["relation"]=="shortfall"
 assert reuse_remanufacture("i",("a","b"),("repair",),("ia","ib"))["identity_retained"]
 assert recovery_yield(3,2,1,"method","scope")["fraction"]==Fraction(2,3)
 assert circular_flow(("a","b"),(("a","b",1,"m"),),"boundary")["material_custody_held"]
 assert durability_extension("i",1,2,("repair",),("test",))["extension"]==1
 assert toxicity_handoff("m",("e",),("o",),"materials","medicine")["handoff_explicit"]
 assert substitution("a","b",("f1","f2"),("f1","f2"),("f2","f1"),"same")["function_preserved"]
 assert end_of_life((("i","m","recycle","r","s"),),"boundary")["all_fates_residuals_held"]
def test_sust_complete_external_vector():
 v=load_complete_vector(Path(__file__).resolve().parents[1]); assert v["claim_count"]==9; assert v["captured_source_count"]==9; assert v["unavailable_source_count"]==0; assert {r["claim_id"] for r in v["claims"]}==set(ORDER); assert all(r["all_comparisons_preserved"] and r["all_registered_fragments_present"] for r in v["claims"])
