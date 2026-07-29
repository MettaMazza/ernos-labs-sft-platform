from fractions import Fraction
from pathlib import Path
from sft.materials.soft_001_010_external_v1 import load_complete_vector
from sft.materials.soft_001_010_laws_v1 import ORDER,SPECS,active_material,colloid,emulsion,foam,gel_network,granular,jamming,liquid_crystal,membrane,responsive
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_soft_complete_grammars():
    assert len(ORDER)==10
    for cid in ORDER:
        rows=candidate_rows(SPECS[cid]); assert len(rows)==len({r["candidate_id"] for r in rows})==256; assert sum(r["candidate_id"]==survivor_id(SPECS[cid]) for r in rows)==1; assert all(w.passed for w in SPECS[cid].witnesses)
def test_soft_native_relations():
    assert colloid(5,3,2,"repulsion","held")["closes"]
    assert gel_network(4,5,("left","right"),"elastic")["percolated"]
    assert foam(5,3,2,4,"air")["drained_part"]==Fraction(2,5)
    assert liquid_crystal(("a","b"),(3,2),"nematic",("defect",))["orientational_order_retained"]
    assert emulsion((3,2),("oil","water"),"interface",("high","low"))["closes"]
    assert membrane(5,3,2,("active","support"),"boundary")["transport_part"]==Fraction(3,5)
    assert granular(5,7,(2,3),"dense")["force_chain_retained"]
    assert jamming("flow","jammed",5,4,("flow","jammed"))["boundary_retained"]
    assert responsive("heat","compact","expanded",2,3,("before","stimulus","after"))["response_ratio"]==Fraction(3,2)
    assert active_material(5,3,2,4,("input","motion","terminal"))["motion_part"]==Fraction(3,5)
def test_soft_complete_external_vector():
    v=load_complete_vector(Path(__file__).resolve().parents[1]); assert v["claim_count"]==10; assert v["captured_source_count"]==10; assert v["unavailable_source_count"]==0; assert {r["claim_id"] for r in v["claims"]}==set(ORDER); assert all(r["all_comparisons_preserved"] and r["all_registered_fragments_present"] for r in v["claims"])
