from fractions import Fraction

from sft.physics.new_sector_complete_family_law_v1 import (
    KNOWN_FERMION_KINDS,
    SPECS,
    category_clean_particle_census,
    no_extra_boundary,
    sector_beta_slope,
    sector_phenotype,
    smithion_search_signatures,
)
from sft.physics.structural_constants import candidate_rows


def test_whole_family_has_seven_formal_claims_and_complete_grammars():
    assert len(SPECS) == 7
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256


def test_penta_phenotype_is_complete():
    row = sector_phenotype(5)
    assert (row["shortfall"], row["coupling"], row["colours"], row["mediators"], row["confinement_pair_count"]) == (Fraction(1, 5), Fraction(4, 5), 5, 24, 2)
    assert all(value == 1 for value in row["neutral_pairs"])
    assert row["carrier_speed"] == row["tube_closes_to"] == row["neutral_complete_fibre"] == 1


def test_hepta_phenotype_is_complete():
    row = sector_phenotype(7)
    assert (row["shortfall"], row["coupling"], row["colours"], row["mediators"], row["confinement_pair_count"]) == (Fraction(1, 7), Fraction(6, 7), 7, 48, 3)
    assert all(value == 1 for value in row["neutral_pairs"])
    assert row["carrier_speed"] == row["tube_closes_to"] == row["neutral_complete_fibre"] == 1


def test_beta_slopes_are_independently_exact_and_distinct():
    assert sector_beta_slope(5) == 4
    assert sector_beta_slope(7) == 6
    assert sector_beta_slope(5) != sector_beta_slope(7)


def test_category_clean_census_includes_known_fermions_once():
    census = category_clean_particle_census()
    assert len(KNOWN_FERMION_KINDS) == len(set(KNOWN_FERMION_KINDS)) == 12
    assert census["gauge_carriers"] == 83
    assert census["smithion_kind_count"] == 12
    assert census["category_clean_total"] == 110


def test_boundary_and_signatures_are_explicit():
    boundary = no_extra_boundary()
    assert boundary["last_admitted_sector"] == 7
    assert boundary["first_excluded_prime"] == 11
    assert len(boundary["outside_list_falsifiers"]) == 5
    signatures = smithion_search_signatures()
    assert tuple(row["confining_jet_carriers"] for row in signatures.values()) == (24, 48)
    assert all(row["electromagnetic_charge_record"] == row["cross_fibre_nuclear_recoil_carrier"] == "empty-One" for row in signatures.values())
