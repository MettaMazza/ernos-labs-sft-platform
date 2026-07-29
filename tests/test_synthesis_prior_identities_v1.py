from fractions import Fraction
from sft.synthesis.prior_identity_laws_v1 import SPECS, descent_identity, lock_identity, positive_observable_boundary, prior_input_valid, prime_vacuum_rows, second_harmonic_identity, vacuum_divisor_rows, wave_mode_identity
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_products():
 for s in SPECS.values():
  r=candidate_rows(s);assert len(r)==256;assert sum(x["candidate_id"]==survivor_id(s) for x in r)==1
def test_prior():assert prior_input_valid()
def test_prime_vacuum():assert all(a==b for _,a,b in prime_vacuum_rows());assert all(x["divides"] for x in vacuum_divisor_rows())
def test_lock_descent_wave():assert lock_identity()["common_image"]==(Fraction(1,2),Fraction(1,2));assert descent_identity()["strictly_descending"];assert wave_mode_identity()["complete_spatial_roles"]==3
def test_harmonic_positive():assert second_harmonic_identity()["all_exact_doubling_before_or_at_completion"];assert positive_observable_boundary()["all_positive"] and not positive_observable_boundary()["absence_is_numerical_magnitude"]
