from collections import Counter

from sft.chemistry.nmr_exchange_zero_status_v2 import reconstruct_exchange_absences


def test_all_eleven_zero_glyphs_are_exact_structural_absences() -> None:
    rows = reconstruct_exchange_absences()
    assert len(rows) == 11
    assert Counter(row.saveframe for row in rows) == {
        "H_exch_rate_list_1": 4,
        "H_exch_rate_list_2": 7,
    }
    assert all(row.raw_value_glyph == "0" for row in rows)
    assert all(row.native_status == "structural-absence-of-reported-positive-fitted-rate" for row in rows)


def test_no_numeric_zero_or_unreported_uncertainty_enters_native_rate_arithmetic() -> None:
    rows = reconstruct_exchange_absences()
    assert all((row.value_min, row.value_max, row.value_error) == (".", ".", ".") for row in rows)
    assert {row.residue for row in rows} == {"ASP", "GLY", "ILE", "LEU", "MET", "PHE", "THR"}
