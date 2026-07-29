from pathlib import Path
from sft.materials.elec_001_012_external_v1 import load_complete_vector
from sft.materials.elec_001_012_laws_v1 import ORDER,SPECS,band_alignment,conductivity_resistivity,electrochemical_insertion,finite_barrier,ionic_transference,screening_depletion
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_elec_complete_grammars():
 assert len(ORDER)==12
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]);assert len(rows)==len({x["candidate_id"] for x in rows})==256;assert sum(x["candidate_id"]==survivor_id(SPECS[cid]) for x in rows)==1;assert all(w.passed for w in SPECS[cid].witnesses)
def test_elec_native_relations():
 assert conductivity_resistivity(2,4,2)["reciprocal_closure"];assert ionic_transference((("a",2),("b",3)))["closes"];assert finite_barrier(5,2,3,4)["closes"];assert band_alignment(5,3,"first-above","junction")["offset"]==2;assert screening_depletion(10,2,3,5,"depletion")["closes"];assert electrochemical_insertion(8,5,3,("in","out"))["retained"]==2
def test_elec_complete_external_vector():
 v=load_complete_vector(Path(__file__).resolve().parents[1]);assert v["claim_count"]==12;assert v["captured_source_count"]==10;assert v["unavailable_source_count"]==0;assert {x["claim_id"] for x in v["claims"]}==set(ORDER);assert all(x["all_comparisons_preserved"] and x["all_registered_fragments_present"] for x in v["claims"])
