from fractions import Fraction
from sft.social.exact_return_laws_v1 import SPECS,consensus_lock,preferential_flow,social_cycle
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_products():
 for s in SPECS.values():
  r=candidate_rows(s);assert len(r)==256;assert sum(x["candidate_id"]==survivor_id(s) for x in r)==1
def test_flow():
 r=preferential_flow();assert r["conserved"] and r["majority_strictly_rises"] and len(r["rows"])==7
def test_lock():
 r=consensus_lock();assert r["images"]==(Fraction(1,2),Fraction(1,2));assert r["partition"]==1;assert not r["image_alone_identifies_preimage"]
def test_cycle():
 r=social_cycle();assert r["images"]==(Fraction(2,3),Fraction(1,3));assert r["partition"]==1;assert r["balance"]==Fraction(1,2);assert not r["reaches_one"]
