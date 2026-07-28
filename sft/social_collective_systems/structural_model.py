"""Exact pre-source witnesses for Social and Collective Sciences."""
from fractions import Fraction
def fold(x):
    y=x*2
    return y if y<=1 else y-1
def structural_witnesses():
    p2=(Fraction(1,3),Fraction(2,3)); p3=(Fraction(1,7),Fraction(2,7),Fraction(4,7)); allocation=(Fraction(1,7),Fraction(2,7),Fraction(4,7))
    return {"agents_distinct":len({"agent-a","agent-b"})==2,"directed_relation_retained":("agent-a","agent-b")!=("agent-b","agent-a"),"period_two_reciprocity":tuple(fold(x) for x in p2)==(p2[1],p2[0]),"three_member_partition":sum(p3,Fraction())==1,"period_three_collective_recurrence":tuple(fold(x) for x in p3)==(p3[1],p3[2],p3[0]),"allocation_closes":sum(allocation,Fraction())==1,"ordered_history":all(Fraction(i,8)<Fraction(i+1,8) for i in range(1,7)),"joint_group_product":2*3==6,"aggregation_loses_unheld_predecessor":fold(Fraction(1,4))==fold(Fraction(3,4)),"evidence_classes_distinct":len({"observation","report","record","model","forecast","missing"})==6}
if not all(structural_witnesses().values()): raise ValueError("Social structural witness failed")
