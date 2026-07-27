#!/usr/bin/env python3
"""Seal all 93 disjoint azide-alkyne source identities before product access."""

from __future__ import annotations

from collections import defaultdict
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
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v8.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v8.json"
V6_SELECTION = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-source-selection-v6.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-source-selection-v8.json"
SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_azide_alkyne_source_selection_v8.json"
EXPECTED = {
    SOURCE: "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a",
    PARSER: "sha256:606792baeda01730c9ff932d1565310184a403284a0617d3f72a57cb71c1d401",
    LAW: "sha256:fb4f8b12698b7800f89a117648b7fb311f7ad733f15e420c33f67f9309aef9c8",
    IDENTITY: "sha256:def92e252e76e3525aaa0f2acf59dc801055d7294b0e010a15615e097003be37",
    PREDICTION: "sha256:b4fc02b305856c8d3efe88a96bfb637b607417e904459957c19e836e935a5571",
    V6_SELECTION: "sha256:c3638fdb2a27d96d548e39ef5c5fd4e1a78381907b0e133e3af7be301d2cfc94",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def mapped_heavy_atoms_are_complete(graphs: list[Graph]) -> bool:
    maps = [atom.atom_map for graph in graphs for atom in graph.atoms if atom.element != "H"]
    return all(atom_map is not None for atom_map in maps) and len(set(maps)) == len(maps)


def unique_three_nitrogen_path(graph: Graph) -> tuple[int, int, int] | None:
    adjacency: dict[int, set[int]] = defaultdict(set)
    for bond in graph.bonds:
        if graph.atoms[bond.left].element == "N" and graph.atoms[bond.right].element == "N":
            adjacency[bond.left].add(bond.right)
            adjacency[bond.right].add(bond.left)
    paths = []
    for middle, neighbors in adjacency.items():
        ordered = sorted(neighbors)
        for left_index in range(len(ordered)):
            for right_index in range(left_index + 1, len(ordered)):
                paths.append((ordered[left_index], middle, ordered[right_index]))
    return paths[0] if len(paths) == 1 else None


def unique_carbon_triple(graph: Graph) -> Bond | None:
    rows = [
        bond
        for bond in graph.bonds
        if bond.order == "triple"
        and graph.atoms[bond.left].element == "C"
        and graph.atoms[bond.right].element == "C"
        and not graph.atoms[bond.left].aromatic
        and not graph.atoms[bond.right].aromatic
    ]
    return rows[0] if len(rows) == 1 else None


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
    azide_rows = [(index, unique_three_nitrogen_path(graph)) for index, graph in enumerate(graphs)]
    azide_rows = [(index, path) for index, path in azide_rows if path is not None]
    alkyne_rows = [(index, unique_carbon_triple(graph)) for index, graph in enumerate(graphs)]
    alkyne_rows = [(index, bond) for index, bond in alkyne_rows if bond is not None]
    pairs = [(azide, alkyne) for azide in azide_rows for alkyne in alkyne_rows if azide[0] != alkyne[0]]
    if len(pairs) != 1:
        return None
    (azide_index, path), (alkyne_index, triple) = pairs[0]
    azide = graphs[azide_index]
    alkyne = graphs[alkyne_index]
    left, middle, right = path
    outer_maps = [azide.atoms[left].atom_map, azide.atoms[right].atom_map]
    alkyne_maps = [alkyne.atoms[triple.left].atom_map, alkyne.atoms[triple.right].atom_map]
    orientations = [
        sorted(((outer_maps[0], alkyne_maps[0]), (outer_maps[1], alkyne_maps[1]))),
        sorted(((outer_maps[0], alkyne_maps[1]), (outer_maps[1], alkyne_maps[0]))),
    ]
    return {
        "reactants": reactants,
        "azide_component_ordinal": azide_index + 1,
        "alkyne_component_ordinal": alkyne_index + 1,
        "azide_outer_nitrogen_maps": outer_maps,
        "azide_middle_nitrogen_map": azide.atoms[middle].atom_map,
        "alkyne_carbon_maps": alkyne_maps,
        "generated_cross_adjacency_orientations": orientations,
        "azide_graph": graph_record(azide),
        "alkyne_graph": graph_record(alkyne),
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha256_file(path) != expected:
            raise SystemExit(f"ORG-009 V8 frozen source-side input changed: {path}")
    if OUTPUT.exists() or SEAL.exists():
        raise SystemExit("ORG-009 V8 source selection already exists; replay prohibited")
    prior_ordinals = {
        row["source_row_ordinal"]
        for row in json.loads(V6_SELECTION.read_text(encoding="utf-8"))["selected_sources_in_original_order"]
    }
    selected = []
    conventional_row_count = 0
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["mapped_rxn", "confident"]:
            raise SystemExit("ORG-009 V8 source schema changed")
        for conventional_row_count, row in enumerate(reader, start=1):
            reaction = row["mapped_rxn"]
            if reaction.count(">") != 2:
                continue
            record = classify_source(reaction.split(">", 1)[0])
            if record is not None:
                selected.append({"source_row_ordinal": conventional_row_count, **record})
    if len(selected) != 93:
        raise SystemExit(f"ORG-009 V8 expected 93 source identities, observed {len(selected)}")
    overlap = sorted(prior_ordinals & {row["source_row_ordinal"] for row in selected})
    if overlap:
        raise SystemExit("ORG-009 V8 selected products overlap the already opened V6 product family")
    output = {
        "schema": "sft-v3-chemistry-org-009-azide-alkyne-source-selection/8",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "complete_conventional_data_row_count": conventional_row_count,
        "complete_selected_source_count": len(selected),
        "generated_orientation_count_per_source": 2,
        "intersection_with_previously_opened_v6_product_ordinals": [],
        "selection_used_product_field": False,
        "product_outcomes_opened_by_selector": False,
        "selected_sources_in_original_order": selected,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    seal = {
        "schema": "sft-v3-chemistry-org-009-azide-alkyne-selection-seal/8",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "selector_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "selector_sha256": sha256_file(Path(__file__).resolve()),
        "selection_path": OUTPUT.relative_to(ROOT).as_posix(),
        "selection_sha256": sha256_file(OUTPUT),
        "complete_selected_source_count": len(selected),
        "previously_opened_product_overlap_count": 0,
        "product_outcomes_opened_before_selection_seal": False,
    }
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(seal, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
