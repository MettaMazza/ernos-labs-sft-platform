from fractions import Fraction
from pathlib import Path
from sft.materials.degr_001_010_external_v1 import load_complete_vector
from sft.materials.degr_001_010_laws_v1 import ORDER,SPECS,corrosion,hydrogen_uptake,oxidation,passivation,physical_ageing,radiation_defects,service_life,stress_corrosion,wear,weathering
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_degr_complete_grammars():
 assert len(ORDER)==10
 for cid in ORDER:
  rows=candidate_rows(SPECS[cid]); assert len(rows)==len({row["candidate_id"] for row in rows})==256; assert sum(row["candidate_id"]==survivor_id(SPECS[cid]) for row in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_degr_native_relations():
 assert oxidation(5,3,2,1,("start","scale"))["scale_part"]==Fraction(2,5)
 assert corrosion(5,3,2,("anode","transfer","cathode"),"aqueous")["closes"]
 assert passivation(5,4,1,"oxide","held")["boundary_held"]
 assert stress_corrosion(5,3,2,4,"chloride",("start","front"))["cracked_part"]==Fraction(2,5)
 assert hydrogen_uptake(5,3,2,1,2,("surface","bulk"))["closes"]
 assert sum(wear(1,2,3,4,"surface",("start","end"))["parts"])==1
 assert radiation_defects(5,3,2,("vacancy","interstitial"),"uv",("damaged","annealed"))["closes"]
 assert physical_ageing(2,3,"modulus",("initial","later"),"increase")["ratio"]==Fraction(3,2)
 assert weathering(5,3,2,("light","water"),("initial","exposed"))["closes"]
 assert service_life(3,1,2,(1,2,3),"held","right-censored")["evidence_boundary_held"]
def test_degr_complete_external_vector():
 vector=load_complete_vector(Path(__file__).resolve().parents[1]); assert vector["claim_count"]==10; assert vector["captured_source_count"]==10; assert vector["unavailable_source_count"]==0; assert {row["claim_id"] for row in vector["claims"]}==set(ORDER); assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
