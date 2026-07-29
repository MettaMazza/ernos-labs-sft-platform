from fractions import Fraction
from pathlib import Path
from sft.materials.mech_001_014_external_v1 import load_complete_vector
from sft.materials.mech_001_014_laws_v1 import ORDER,SPECS,fracture_ledger,friction_contact,impact_partition,memory_recovery,rheology,yield_path
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_mech_complete_grammars():
 assert len(ORDER)==14
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]);assert len(rows)==len({x["candidate_id"] for x in rows})==256;assert sum(x["candidate_id"]==survivor_id(SPECS[cid]) for x in rows)==1;assert all(w.passed for w in SPECS[cid].witnesses)
def test_mech_native_relations():
 assert memory_recovery((2,5),2)["unrecovered"]==3;assert yield_path(((1,"recoverable"),(2,"retained")))["yield_load"]==2;assert fracture_ledger(6,3)["work_per_surface"]==2;assert impact_partition(10,2,3,5)["closes"];assert friction_contact(2,8,3)["friction_part"]==Fraction(1,4);assert rheology(6,3,4)["resistance_part"]==2
def test_mech_complete_external_vector():
 v=load_complete_vector(Path(__file__).resolve().parents[1]);assert v["claim_count"]==14;assert v["captured_source_count"]==8;assert v["unavailable_source_count"]==0;assert {x["claim_id"] for x in v["claims"]}==set(ORDER);assert all(x["all_comparisons_preserved"] and x["all_registered_fragments_present"] for x in v["claims"])
