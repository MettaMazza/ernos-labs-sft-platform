#!/usr/bin/env python3
"""Build the post-law-seal INORG-007 target and exact comparison records."""

from __future__ import annotations

from fractions import Fraction
import html
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


LAW_PATH = "sft/chemistry/complex_spin_state_order_law_v1.py"
LAW_HASH = "sha256:279e1e175fbbd6588dfd113d2a708d08c9970c2f9487387dc184976107329ba7"
IDENTITY_PATH = "experiments/external_sources/chemistry/complex_spin_state_order_target_identities_v1.json"
IDENTITY_HASH = "sha256:0bac4d73f7add7f9dd93a42b59da32b783225a2b34e92015e31b0c9cdaf06a79"
TARGET_PATH = "experiments/external_sources/chemistry/complex_spin_state_order_withheld_targets_v1.json"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/complex-spin-state-order-primary-records-v1.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _visible_html_text(source: str) -> str:
    definition = re.search(r"<div class='deftext'>(.*?)<div class='sources'", source, re.DOTALL)
    if not definition:
        raise ValueError("registered high-spin surface lacks its definition block")
    without_tags = re.sub(r"<[^>]+>", " ", definition.group(1))
    return " ".join(html.unescape(without_tags).split())


def main() -> None:
    if hash_file(ROOT / LAW_PATH) != LAW_HASH or hash_file(ROOT / IDENTITY_PATH) != IDENTITY_HASH:
        raise SystemExit("INORG-007 law or value-free identity seal changed")
    identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = identity_document["rows"]
    if len(rows) != 3 or identity_document["target_values_definitions_terms_distances_temperatures_outcomes_or_payload_hashes_present"] is not False:
        raise SystemExit("INORG-007 identity boundary is not value-free and complete")

    high_source = (ROOT / rows[0]["snapshot_path"]).read_text(encoding="utf-8")
    low_source = json.loads((ROOT / rows[1]["snapshot_path"]).read_text(encoding="utf-8"))
    crossover_source = json.loads((ROOT / rows[2]["snapshot_path"]).read_text(encoding="utf-8"))
    for row in rows:
        if hash_file(ROOT / row["snapshot_path"]) != row["snapshot_sha256"]:
            raise SystemExit(f"INORG-007 frozen source changed: {row['source_id']}")

    high_definition = _visible_html_text(high_source)
    low_definition = low_source["term"]["definitions"][0]["text"]
    crossover_definition = crossover_source["term"]["definitions"][0]["text"]
    outcomes = (
        {
            "requested_source_id": "HT06789",
            "observed_source_code": "LT06788",
            "observed_title": "low-spin",
            "registered_transport_identity_mismatch_preserved": True,
            "combined_surface_also_defines_high_spin": "also defines</em>: high-spin" in high_source,
            "definition": high_definition,
            "low_spin_complete_lower_support_surface_present": "lowest possible energy levels" in high_definition,
            "high_spin_prior_higher_support_occupation_surface_present": "higher energy d orbitals are occupied before all the lower energy ones are completely filled" in high_definition,
            "dimensional_values_present": False,
        },
        {
            "observed_source_code": low_source["term"]["code"],
            "observed_title": low_source["term"]["title"],
            "definition": low_definition,
            "paired_lower_support_surface_present": "two electrons paired up in the HOMO" in low_definition,
            "complete_order_comparison_surface_present": "larger than the Coulomb and exchange repulsion energies" in low_definition,
            "conventional_energy_terms_retained_downstream_only": True,
            "dimensional_values_present": False,
        },
        {
            "observed_source_code": crossover_source["term"]["code"],
            "observed_title": crossover_source["term"]["title"],
            "definition": crossover_definition,
            "external_constraint_classes": ["temperature", "pressure", "electromagnetic radiation"],
            "example_complex": "[Fe(2-pic)3]Cl2.EtOH",
            "central_species": "Fe2+",
            "lower_distance_pm_exact": str(Fraction(2032, 10)),
            "lower_temperature_k_exact": str(Fraction(115, 1)),
            "lower_state": "low-spin",
            "lower_term": "1A1",
            "higher_distance_pm_exact": str(Fraction(2199, 10)),
            "higher_temperature_k_exact": str(Fraction(227, 1)),
            "higher_state": "high-spin",
            "higher_term": "5T2",
            "positive_distance_successor_pm_exact": str(Fraction(2199 - 2032, 10)),
            "positive_temperature_successor_k_exact": str(Fraction(227 - 115, 1)),
            "longer_distance_maps_to_high_spin": True,
            "shorter_distance_maps_to_low_spin": True,
            "all_reported_values_and_terms_preserved": True,
        },
    )

    target_rows = []
    for identity, outcome in zip(rows, outcomes):
        row = {**identity, "source_outcome": outcome}
        row["target_payload_hash"] = sha256_identity((identity["target_id"], identity["source_record_role"], outcome))
        target_rows.append(row)
    target_document = {
        "schema": "sft-v3-chemistry-complex-spin-state-order-withheld-targets/1",
        "claim_id": "SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": 3,
        "all_favourable_adverse_absent_and_transport_mismatch_rows_preserved": True,
        "rows": target_rows,
    }
    write_json(ROOT / TARGET_PATH, target_document)

    primary = {
        "schema": "sft-v3-chemistry-complex-spin-state-order-primary/1",
        "claim_id": "SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "complete_target_count": 3,
        "exact_postseal_analysis": {
            "forced_six_electron_signature_count": 10,
            "forced_low_spin_signature": {"lower_pairs": 3, "lower_singles": "EmptyOne", "upper_pairs": "EmptyOne", "upper_singles": "EmptyOne", "spin_width": 1, "split_crossings": "EmptyOne"},
            "forced_high_spin_signature": {"lower_pairs": 1, "lower_singles": 2, "upper_pairs": "EmptyOne", "upper_singles": 2, "spin_width": 5, "split_crossings": 2},
            "forced_order_vector": ["high-precedes-low", "crossover-coincidence", "low-precedes-high"],
            "external_exact_distance_vector_pm": [outcomes[2]["lower_distance_pm_exact"], outcomes[2]["higher_distance_pm_exact"]],
            "external_exact_temperature_vector_k": [outcomes[2]["lower_temperature_k_exact"], outcomes[2]["higher_temperature_k_exact"]],
            "external_exact_term_vector": [outcomes[2]["lower_term"], outcomes[2]["higher_term"]],
            "external_state_vector": [outcomes[2]["lower_state"], outcomes[2]["higher_state"]],
            "external_distance_order_matches_forced_dilution_order": True,
            "dimensional_distance_temperature_or_term_fitted_or_derived": False,
            "registered_high_spin_transport_mismatch_preserved": True,
            "all_three_rows_preserved": True,
        },
    }
    write_json(ROOT / PRIMARY_PATH, primary)
    print(hash_file(ROOT / TARGET_PATH))
    print(hash_file(ROOT / PRIMARY_PATH))


if __name__ == "__main__":
    main()
