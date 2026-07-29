from fractions import Fraction
from pathlib import Path
from sft.materials.comp_001_012_external_v1 import load_complete_vector
from sft.materials.comp_001_012_laws_v1 import ORDER,SPECS,data_representation,structure_property,finite_simulation,multiscale,error_ledger,inverse_problem,learning_boundary,database,phase_field,molecular_dynamics,electronic_structure,validation_ledger
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_comp_complete_grammars():
 assert len(ORDER)==12
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]); assert len(rows)==len({row["candidate_id"] for row in rows})==256; assert sum(row["candidate_id"]==survivor_id(SPECS[cid]) for row in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_comp_native_relations():
 assert data_representation((("r1",("s",),("p",),"src"),))["provenance_held"]
 assert structure_property(("s",),("p",),"scope","method")["all_inputs_outputs_held"]
 assert finite_simulation("a",("a","b"),("ab",),"held")["trace_complete"]
 assert multiscale(("micro","macro"),("m1","m2"),(("m1","m2"),))["composition_complete"]
 assert error_ledger((Fraction(1,3),Fraction(2,3)),1,"scope")["sum_exact"]
 assert inverse_problem(("a","b"),(("a","x"),("b","y")),"y")["matches"]==("b",)
 assert learning_boundary(("train",),("a","b"),("a","a"),"method")["incorrect"]==1
 assert database((("id","payload","source","v1"),))["identity_provenance_held"]
 assert phase_field(3,("a","b","a"),(("a","b"),),"held")["discrete_correspondence"]
 assert molecular_dynamics(("p1","p2"),("s1","s2"),(("s1","s2"),),"held")["particle_custody_held"]
 assert electronic_structure(("site",),("o1","o2"),(1,2),"method")["total_occupation"]==3
 assert validation_ledger((("r1",1,1,"u","q","s"),("r2",1,2,"u","q","s")))["mismatches"]==1
def test_comp_complete_external_vector():
 vector=load_complete_vector(Path(__file__).resolve().parents[1]); assert vector["claim_count"]==12; assert vector["captured_source_count"]==12; assert vector["unavailable_source_count"]==0; assert {row["claim_id"] for row in vector["claims"]}==set(ORDER); assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
