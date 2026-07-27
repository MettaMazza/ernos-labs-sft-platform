#!/usr/bin/env python3
"""Freeze every ORG-009 V5 source-only qualifying identity before product analysis."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-inventory-v5.json"
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v5.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v5.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-only-selection-v5.json"
SELECTION_SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_localmapper_source_selection_v5.json"
EXPECTED_SNAPSHOT = "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a"
EXPECTED_INVENTORY = "sha256:5f2eebd16d7d1a5c3157ee7b5f1efabd5de1ac066c8e40a0a0935b98b341152c"
EXPECTED_IDENTITY = "sha256:37f7837d807e0406eb9e337d1d0f0150d9c92da73af449376d9cb53151a71b2f"
EXPECTED_PRESEAL = "sha256:7a5cd44ad6eddb12716b4951a79fb9e9e7bbdd5e70758391c302c9f6eb0fa817"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


@dataclass(frozen=True)
class Atom:
    index: int
    element: str
    aromatic: bool
    atom_map: int | None


@dataclass(frozen=True)
class Bond:
    left: int
    right: int
    order: str


@dataclass(frozen=True)
class Graph:
    atoms: tuple[Atom, ...]
    bonds: tuple[Bond, ...]


class UnsupportedSmiles(ValueError):
    pass


def bracket_atom(content: str, index: int) -> Atom:
    element_match = re.match(r"^(?:[0-9]+)?([A-Z][a-z]?|[bcnops])", content)
    if element_match is None:
        raise UnsupportedSmiles("unsupported bracket atom")
    raw_element = element_match.group(1)
    map_matches = re.findall(r":([0-9]+)", content)
    if len(map_matches) > 1:
        raise UnsupportedSmiles("multiple atom-map fields")
    return Atom(index, raw_element.capitalize(), raw_element.islower(), int(map_matches[0]) if map_matches else None)


def bare_atom(text: str, position: int, index: int) -> tuple[Atom, int]:
    token = text[position : position + 2]
    if token in {"Cl", "Br"}:
        return Atom(index, token, False, None), position + 2
    token = text[position]
    if token in "BCNOPSFI":
        return Atom(index, token, False, None), position + 1
    if token in "bcnops":
        return Atom(index, token.upper(), True, None), position + 1
    raise UnsupportedSmiles(f"unsupported atom token {token!r}")


def implicit_order(left: Atom, right: Atom) -> str:
    return "aromatic" if left.aromatic and right.aromatic else "single"


def parse_component(text: str) -> Graph:
    atoms: list[Atom] = []
    bonds: list[Bond] = []
    branches: list[int] = []
    rings: dict[str, tuple[int, str | None]] = {}
    current: int | None = None
    pending: str | None = None
    position = 0
    while position < len(text):
        character = text[position]
        if character == "[":
            end = text.find("]", position + 1)
            if end < 0:
                raise UnsupportedSmiles("unclosed bracket atom")
            new_atom = bracket_atom(text[position + 1 : end], len(atoms))
            position = end + 1
        elif character.isalpha():
            new_atom, position = bare_atom(text, position, len(atoms))
        elif character in "-=#:$/\\":
            if character == "-":
                pending = "single"
            elif character == "=":
                pending = "double"
            elif character == "#":
                pending = "triple"
            elif character == ":":
                pending = "aromatic"
            elif character == "$":
                raise UnsupportedSmiles("quadruple support is outside the registered parser boundary")
            else:
                pending = pending or "single"
            position += 1
            continue
        elif character == "(":
            if current is None:
                raise UnsupportedSmiles("branch without anchor")
            branches.append(current)
            position += 1
            continue
        elif character == ")":
            if not branches:
                raise UnsupportedSmiles("unmatched branch close")
            current = branches.pop()
            position += 1
            continue
        elif character.isdigit() or character == "%":
            if current is None:
                raise UnsupportedSmiles("ring without anchor")
            if character == "%":
                label = text[position + 1 : position + 3]
                if len(label) != 2 or not label.isdigit():
                    raise UnsupportedSmiles("invalid two-digit ring label")
                position += 3
            else:
                label = character
                position += 1
            if label not in rings:
                rings[label] = (current, pending)
            else:
                other, stored = rings.pop(label)
                order = pending or stored or implicit_order(atoms[other], atoms[current])
                bonds.append(Bond(other, current, order))
            pending = None
            continue
        else:
            raise UnsupportedSmiles(f"unsupported component token {character!r}")
        atoms.append(new_atom)
        if current is not None:
            bonds.append(Bond(current, new_atom.index, pending or implicit_order(atoms[current], new_atom)))
        current = new_atom.index
        pending = None
    if branches or rings or pending is not None or not atoms:
        raise UnsupportedSmiles("incomplete component topology")
    return Graph(tuple(atoms), tuple(bonds))


def graph_record(graph: Graph) -> dict:
    return {
        "atoms": [
            {"ordinal": row.index + 1, "element": row.element, "aromatic": row.aromatic, "atom_map": row.atom_map}
            for row in graph.atoms
        ],
        "bonds": [
            {"left_ordinal": row.left + 1, "right_ordinal": row.right + 1, "order": row.order}
            for row in graph.bonds
        ],
    }


def x2_graph(graph: Graph) -> bool:
    return (
        len(graph.atoms) == 2
        and len(graph.bonds) == 1
        and graph.bonds[0].order == "single"
        and graph.atoms[0].element in {"Cl", "Br"}
        and graph.atoms[0].element == graph.atoms[1].element
    )


def source_qualification(reactants: str) -> tuple[str, dict | None]:
    components = reactants.split(".")
    if len(components) != 2:
        return "not-qualifying", None
    parsed: list[Graph] = []
    errors: list[str] = []
    for component in components:
        try:
            parsed.append(parse_component(component))
        except UnsupportedSmiles as error:
            errors.append(str(error))
    x2_text_hint = any(re.search(r"(?:\[?(?:Cl|Br)[^\]]*\]?){2}", component) for component in components)
    if errors:
        if x2_text_hint:
            return "unresolved-candidate", {"reactants": reactants, "errors": errors}
        return "not-qualifying", None
    x2_indices = [index for index, graph in enumerate(parsed) if x2_graph(graph)]
    if len(x2_indices) != 1:
        return "not-qualifying", None
    x2_index = x2_indices[0]
    substrate_index = 1 - x2_index
    x2 = parsed[x2_index]
    substrate = parsed[substrate_index]
    all_atoms = x2.atoms + substrate.atoms
    heavy_maps = [row.atom_map for row in all_atoms if row.element != "H"]
    if any(row is None for row in heavy_maps) or len(set(heavy_maps)) != len(heavy_maps):
        return "not-qualifying", None
    carbon_double = [
        row
        for row in substrate.bonds
        if row.order == "double"
        and substrate.atoms[row.left].element == "C"
        and substrate.atoms[row.right].element == "C"
        and not substrate.atoms[row.left].aromatic
        and not substrate.atoms[row.right].aromatic
    ]
    if len(carbon_double) != 1:
        return "not-qualifying", None
    selected = carbon_double[0]
    return "qualifying", {
        "reactants": reactants,
        "substrate_component_ordinal": substrate_index + 1,
        "x2_component_ordinal": x2_index + 1,
        "halogen_element": x2.atoms[0].element,
        "halogen_atom_maps": [x2.atoms[0].atom_map, x2.atoms[1].atom_map],
        "selected_carbon_atom_maps": [
            substrate.atoms[selected.left].atom_map,
            substrate.atoms[selected.right].atom_map,
        ],
        "substrate_graph": graph_record(substrate),
        "x2_graph": graph_record(x2),
    }


def main() -> None:
    frozen = {
        SNAPSHOT: EXPECTED_SNAPSHOT,
        INVENTORY: EXPECTED_INVENTORY,
        IDENTITY: EXPECTED_IDENTITY,
        PRESEAL: EXPECTED_PRESEAL,
    }
    for path, expected in frozen.items():
        observed = sha256_file(path)
        if observed != expected:
            raise SystemExit(f"ORG-009 V5 frozen input changed: {path}: {observed}")
    if OUTPUT.exists() or SELECTION_SEAL.exists():
        raise SystemExit("ORG-009 V5 source-only selection already exists; replay prohibited")
    selected: list[dict] = []
    unresolved: list[dict] = []
    conventional_row_count = 0
    with SNAPSHOT.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        normalized = {name.lower().replace(" ", "_").replace("-", "_"): name for name in (reader.fieldnames or [])}
        allowed = {"mapped_reaction_smiles", "mapped_rxn_smiles", "localmapper_results", "mapped_rxn", "rxn_smiles", "reaction_smiles", "reaction"}
        matches = [original for normalized_name, original in normalized.items() if normalized_name in allowed]
        if len(matches) != 1:
            raise SystemExit("ORG-009 V5 reaction column resolution did not yield exactly one column")
        reaction_column = matches[0]
        for conventional_row_count, row in enumerate(reader, start=1):
            reaction = row[reaction_column]
            if reaction.count(">") != 2:
                continue
            reactants = reaction.split(">", 1)[0]
            status, record = source_qualification(reactants)
            if status == "qualifying":
                selected.append({"source_row_ordinal": conventional_row_count, **record})
            elif status == "unresolved-candidate":
                unresolved.append({"source_row_ordinal": conventional_row_count, **record})
    output = {
        "schema": "sft-v3-chemistry-org-009-source-only-selection/5",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "source_snapshot_sha256": EXPECTED_SNAPSHOT,
        "target_identity_sha256": EXPECTED_IDENTITY,
        "prediction_seal_sha256": EXPECTED_PRESEAL,
        "selection_used_product_field": False,
        "product_outcomes_opened_by_selector": False,
        "complete_conventional_data_row_count": conventional_row_count,
        "qualifying_source_count": len(selected),
        "unresolved_candidate_count": len(unresolved),
        "qualifying_sources_in_original_order": selected,
        "unresolved_candidates_in_original_order": unresolved,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    selection_seal = {
        "schema": "sft-v3-chemistry-org-009-source-selection-seal/5",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "selector_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "selector_sha256": sha256_file(Path(__file__).resolve()),
        "selection_path": OUTPUT.relative_to(ROOT).as_posix(),
        "selection_sha256": sha256_file(OUTPUT),
        "qualifying_source_count": len(selected),
        "unresolved_candidate_count": len(unresolved),
        "product_outcomes_opened_before_selection_seal": False,
    }
    SELECTION_SEAL.write_text(json.dumps(selection_seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(selection_seal, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
