#!/usr/bin/env python3
"""Seal all 47 source-only cycloaddition identities before any product opens."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from select_chemistry_org_009_localmapper_sources_v5 import (
    Bond,
    Graph,
    UnsupportedSmiles,
    graph_record,
    parse_component,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
PARSER = ROOT / "tools/select_chemistry_org_009_localmapper_sources_v5.py"
LAW = ROOT / "sft/chemistry/addition_reaction_law_v3.py"
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v6.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v6.json"
V5_SELECTION = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-only-selection-v5.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-source-selection-v6.json"
SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_cycloaddition_source_selection_v6.json"
EXPECTED = {
    SOURCE: "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a",
    PARSER: "sha256:606792baeda01730c9ff932d1565310184a403284a0617d3f72a57cb71c1d401",
    LAW: "sha256:fb4f8b12698b7800f89a117648b7fb311f7ad733f15e420c33f67f9309aef9c8",
    IDENTITY: "sha256:0d2af65fe149ff2cc9e345c883dc6f8fde99d0b15bcbbc2d169d2ea118e3de09",
    PREDICTION: "sha256:df33eb9572c08af0a88824c221889a8f8ea4399a77223f48a36cf41ae49f3895",
    V5_SELECTION: "sha256:ffec1d71690c09f9329e6ed5aec848a06528eefb7cfb373abdc57b0f13fcabf6",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def carbon_double_bonds(graph: Graph) -> list[Bond]:
    return [
        bond
        for bond in graph.bonds
        if bond.order == "double"
        and graph.atoms[bond.left].element == "C"
        and graph.atoms[bond.right].element == "C"
        and not graph.atoms[bond.left].aromatic
        and not graph.atoms[bond.right].aromatic
    ]


def mapped_heavy_atoms_are_complete(graphs: list[Graph]) -> bool:
    maps = [atom.atom_map for graph in graphs for atom in graph.atoms if atom.element != "H"]
    return all(atom_map is not None for atom_map in maps) and len(set(maps)) == len(maps)


def classify_source(reactants: str) -> dict | None:
    components = reactants.split(".")
    if len(components) != 2:
        return None
    try:
        graphs = [parse_component(component) for component in components]
    except UnsupportedSmiles:
        return None
    if not mapped_heavy_atoms_are_complete(graphs):
        return None
    doubles = [carbon_double_bonds(graph) for graph in graphs]
    if sorted(len(rows) for rows in doubles) != [1, 2]:
        return None
    diene_index = 0 if len(doubles[0]) == 2 else 1
    alkene_index = 1 - diene_index
    diene = graphs[diene_index]
    alkene = graphs[alkene_index]
    diene_left, diene_right = doubles[diene_index]
    left_endpoints = {diene_left.left, diene_left.right}
    right_endpoints = {diene_right.left, diene_right.right}
    if not left_endpoints.isdisjoint(right_endpoints):
        return None
    connecting = [
        bond
        for bond in diene.bonds
        if bond.order == "single"
        and diene.atoms[bond.left].element == "C"
        and diene.atoms[bond.right].element == "C"
        and (
            (bond.left in left_endpoints and bond.right in right_endpoints)
            or (bond.right in left_endpoints and bond.left in right_endpoints)
        )
    ]
    if len(connecting) != 1:
        return None
    internal = connecting[0]
    if internal.left in left_endpoints:
        left_inner, right_inner = internal.left, internal.right
    else:
        left_inner, right_inner = internal.right, internal.left
    left_outer = next(iter(left_endpoints - {left_inner}))
    right_outer = next(iter(right_endpoints - {right_inner}))
    alkene_bond = doubles[alkene_index][0]
    diene_outer_maps = [diene.atoms[left_outer].atom_map, diene.atoms[right_outer].atom_map]
    diene_inner_maps = [diene.atoms[left_inner].atom_map, diene.atoms[right_inner].atom_map]
    alkene_maps = [alkene.atoms[alkene_bond.left].atom_map, alkene.atoms[alkene_bond.right].atom_map]
    orientations = [
        sorted(((diene_outer_maps[0], alkene_maps[0]), (diene_outer_maps[1], alkene_maps[1]))),
        sorted(((diene_outer_maps[0], alkene_maps[1]), (diene_outer_maps[1], alkene_maps[0]))),
    ]
    return {
        "reactants": reactants,
        "diene_component_ordinal": diene_index + 1,
        "alkene_component_ordinal": alkene_index + 1,
        "diene_outer_atom_maps": diene_outer_maps,
        "diene_inner_atom_maps": diene_inner_maps,
        "alkene_atom_maps": alkene_maps,
        "generated_cross_adjacency_orientations": orientations,
        "diene_graph": graph_record(diene),
        "alkene_graph": graph_record(alkene),
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha256_file(path) != expected:
            raise SystemExit(f"ORG-009 V6 frozen source-side input changed: {path}")
    if OUTPUT.exists() or SEAL.exists():
        raise SystemExit("ORG-009 V6 source selection already exists; replay prohibited")
    selected = []
    conventional_row_count = 0
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["mapped_rxn", "confident"]:
            raise SystemExit("ORG-009 V6 source schema changed")
        for conventional_row_count, row in enumerate(reader, start=1):
            reaction = row["mapped_rxn"]
            if reaction.count(">") != 2:
                continue
            reactants = reaction.split(">", 1)[0]
            record = classify_source(reactants)
            if record is not None:
                selected.append({"source_row_ordinal": conventional_row_count, **record})
    if len(selected) != 47:
        raise SystemExit(f"ORG-009 V6 frozen source-only selector expected 47 identities, observed {len(selected)}")
    output = {
        "schema": "sft-v3-chemistry-org-009-cycloaddition-source-selection/6",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "complete_conventional_data_row_count": conventional_row_count,
        "complete_selected_source_count": len(selected),
        "generated_orientation_count_per_source": 2,
        "selection_used_product_field": False,
        "product_outcomes_opened_by_selector": False,
        "selected_sources_in_original_order": selected,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    seal = {
        "schema": "sft-v3-chemistry-org-009-cycloaddition-selection-seal/6",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "selector_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "selector_sha256": sha256_file(Path(__file__).resolve()),
        "selection_path": OUTPUT.relative_to(ROOT).as_posix(),
        "selection_sha256": sha256_file(OUTPUT),
        "complete_selected_source_count": len(selected),
        "product_outcomes_opened_before_selection_seal": False,
    }
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(seal, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
