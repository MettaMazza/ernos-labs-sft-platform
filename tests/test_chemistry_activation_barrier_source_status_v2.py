from fractions import Fraction

from sft.chemistry.activation_barrier_source_status_v2 import reconstruct_phenol_source_status


def test_phenol_blank_row_is_preserved_source_placeholder_not_failed_measurement() -> None:
    status = reconstruct_phenol_source_status()
    assert status.measured_torsion_indices == ("1",)
    assert status.structural_placeholder_indices == ("2",)
    assert status.measured_state_count == 25
    assert status.preserved_placeholder_row_count == 1
    assert status.greatest_wavenumber == Fraction(1175)
    assert status.reference_wavenumber == Fraction(1175)
    assert status.reference_uncertainty == Fraction(20)
    assert status.greatest_energy_kj_mol == Fraction(703, 50)
    assert status.metadata_torsion_index == "1"
    assert status.metadata_rotor == "OH"
    assert status.unresolved_scientific_target_count == 0


def test_placeholder_row_cannot_be_silently_deleted() -> None:
    status = reconstruct_phenol_source_status()
    assert status.preserved_placeholder_row_count == 1
