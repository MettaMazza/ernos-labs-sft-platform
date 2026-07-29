from fractions import Fraction
from pathlib import Path
from sft.materials.proc_001_010_external_v1 import load_complete_vector
from sft.materials.proc_001_010_laws_v1 import ORDER,SPECS,additive_build,casting,epitaxy,forming,joining,machining,polymer_processing,powder_processing,process_window,thin_film
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_proc_complete_grammars():
 assert len(ORDER)==10
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]); assert len(rows)==len({row["candidate_id"] for row in rows})==256; assert sum(row["candidate_id"]==survivor_id(SPECS[cid]) for row in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_proc_native_relations():
 assert casting(5,4,1,("gate","cavity"),("pour","solid"))["filled_part"]==Fraction(4,5)
 assert forming(3,("a","a","b"),("a","b","b"),("load1","load2"),("hot","cool"))["texture_changed"]
 assert machining(5,3,2,"grind","tool",("start","end"))["closes"]
 assert additive_build(("l1","l2"),("p1","p2"),("b1","b2"),("start","end"))["ordered"]
 assert thin_film("substrate",("l1","l2"),("i1","i2"),("nucleate","grow"),"deposition")["ordered"]
 assert epitaxy(2,3,"substrate","film","held")["joint_recurrence"]==6
 assert joining(("a","b"),5,4,1,"weld",("start","joined"))["intact_part"]==Fraction(4,5)
 assert polymer_processing(3,("a","a","b"),("a","b","b"),("feed","form"),("hot","cool"))["orientation_changed"]
 assert powder_processing(5,4,1,3,("loose","compact"))["compacted_part"]==Fraction(4,5)
 assert process_window((("t1",("a",),"pass","p1"),("t2",("a",),"pass","p2")))["repeated_condition_outcome"]
def test_proc_complete_external_vector():
 vector=load_complete_vector(Path(__file__).resolve().parents[1]); assert vector["claim_count"]==10; assert vector["captured_source_count"]==10; assert vector["unavailable_source_count"]==0; assert {row["claim_id"] for row in vector["claims"]}==set(ORDER); assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
