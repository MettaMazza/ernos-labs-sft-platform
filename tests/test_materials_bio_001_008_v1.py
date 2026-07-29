from fractions import Fraction
from pathlib import Path
from sft.materials.bio_001_008_external_v1 import load_complete_vector
from sft.materials.bio_001_008_laws_v1 import ORDER,SPECS,biofabricated,biocompatibility,bioresorption,cell_adhesion,controlled_release,mechanical_match,mineralized,scaffold
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_bio_complete_grammars():
    assert len(ORDER)==8
    for cid in ORDER:
        rows=candidate_rows(SPECS[cid]); assert len(rows)==len({r["candidate_id"] for r in rows})==256; assert sum(r["candidate_id"]==survivor_id(SPECS[cid]) for r in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_bio_native_relations():
    assert biocompatibility(5,4,1,"sample","cell-contact","held")["closes"]
    assert bioresorption(5,3,2,("product",),("start","end"))["resorbed_part"]==Fraction(2,5)
    assert scaffold(5,3,4,("macro","micro"),("left","right"))["connected"]
    assert cell_adhesion(5,3,2,"cell","surface","contact")["adhesion_part"]==Fraction(3,5)
    assert mechanical_match(8,3,4,1,"layered")["closes"]
    assert controlled_release(5,3,2,"matrix",("loaded","terminal"))["released_part"]==Fraction(3,5)
    assert sum(mineralized(2,5,1,"hydroxyapatite","hierarchical")["parts"])==1
    assert biofabricated(5,3,"cell-derived",("input","fabrication","output"),"viable")["provenance_retained"]
def test_bio_complete_external_vector():
    v=load_complete_vector(Path(__file__).resolve().parents[1]); assert v["claim_count"]==8; assert v["captured_source_count"]==8; assert v["unavailable_source_count"]==0; assert {r["claim_id"] for r in v["claims"]}==set(ORDER); assert all(r["all_comparisons_preserved"] and r["all_registered_fragments_present"] for r in v["claims"])
