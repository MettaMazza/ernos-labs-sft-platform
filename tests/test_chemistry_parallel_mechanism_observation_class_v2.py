from fractions import Fraction

from sft.chemistry.parallel_mechanism_observation_class_v2 import reconstruct_peak_x_observation_class


def test_peak_x_is_complete_two_member_observation_class() -> None:
    result = reconstruct_peak_x_observation_class()
    assert result.source_page == 49
    assert len(result.members) == 2
    assert len(set(result.members)) == 2
    assert result.preferred_member is None
    assert result.calculated_mass_to_charge == Fraction(500807, 625)
    assert result.observed_mass_to_charge == Fraction(8012921, 10000)
    assert result.mass_difference == Fraction(9, 10000)
    assert result.maximum_extent_millimolar == Fraction(2, 5)


def test_peak_x_cannot_be_reduced_to_one_member() -> None:
    result = reconstruct_peak_x_observation_class()
    assert result.members == (
        "supplementary-figure-31-depicted-structure-one",
        "supplementary-figure-31-depicted-structure-two",
    )
