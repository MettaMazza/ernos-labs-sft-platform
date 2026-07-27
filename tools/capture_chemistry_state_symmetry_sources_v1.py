#!/usr/bin/env python3
"""Capture the complete NIST term/symmetry assignment vector for ELEC-005."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/state_symmetry_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/state_symmetry_withheld_targets_v1.json"
TERM = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
AXIS_ORIENTATION_COUNT = {"Σ": 1, "Π": 2, "Δ": 2, "Φ": 2}
AXIS_RANK = {"Σ": "structural-empty-One", "Π": "first-recurrence", "Δ": "second-recurrence", "Φ": "third-recurrence"}


class StateTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.depth=self.row_flag=self.cell_flag=0; self.cell=[]; self.row=[]; self.rows=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="table" and "data" in (a.get("class") or "").split(): self.depth+=1
        elif self.depth and tag=="tr": self.row_flag=1; self.row=[]
        elif self.row_flag and tag in {"td","th"}: self.cell_flag=1; self.cell=[]
        elif self.cell_flag and tag=="sup": self.cell.append("^")
        elif self.cell_flag and tag=="sub": self.cell.append("_")
    def handle_endtag(self,tag):
        if self.cell_flag and tag in {"td","th"}: self.row.append(" ".join(unescape("".join(self.cell)).split())); self.cell_flag=0
        elif self.row_flag and tag=="tr":
            if self.row:self.rows.append(tuple(self.row))
            self.row_flag=0
        elif self.depth and tag=="table":self.depth-=1
    def handle_data(self,data):
        if self.cell_flag:self.cell.append(data)


def file_hash(path: Path) -> str: return "sha256:"+sha256(path.read_bytes()).hexdigest()


def suffix_for(state: str, match: re.Match[str]) -> str:
    candidates=[position for position in (state.find(",",match.end()),state.find(")",match.end()),state.find(" ",match.end())) if position>=0]
    return state[match.end():min(candidates) if candidates else len(state)]


def held_component(suffix: str) -> str:
    match=re.search(r"_([0-9]+)",suffix)
    if match is None:return "absence"
    inscription=match.group(1)
    return "absence" if set(inscription)=={"0"} else "positive-component-"+inscription.lstrip("0")


def held_inversion(suffix: str) -> str:
    labels=[label for label in ("g","u") if label in suffix]
    return labels[-1] if labels else "absence"


def held_reflection(suffix: str) -> str:
    if "+" in suffix:return "plus-fibre"
    if "-" in suffix:return "minus-fibre"
    return "absence"


def held_component_kind(suffix: str) -> str:
    if re.search(r"_(?:g|u)?i",suffix):return "i"
    if "_r" in suffix:return "r"
    if "_o" in suffix:return "o"
    if suffix=="p":return "p"
    return "absence"


def main() -> None:
    inputs=json.loads(INPUTS.read_text(encoding="utf-8"))["rows"]; identities=[]; targets=[]
    for species in inputs:
        path=ROOT/species["snapshot_path"]
        if file_hash(path)!=species["snapshot_hash"]:raise RuntimeError("NIST symmetry snapshot changed")
        parser=StateTableParser();parser.feed(path.read_text(encoding="utf-8"));state_rows=tuple(row for row in parser.rows if len(row)==13 and TERM.search(row[0]))
        for state_ordinal,row in enumerate(state_rows,start=1):
            matches=tuple(TERM.finditer(row[0]))
            for term_ordinal,match in enumerate(matches,start=1):
                multiplicity=int(match.group(1));symbol=match.group(2);suffix=suffix_for(row[0],match);target_id=f"{species['nist_id']}-symmetry-{state_ordinal:03d}-{term_ordinal:02d}"
                identities.append({"target_id":target_id,"species_row_id":species["row_id"],"nist_id":species["nist_id"],"state_row_ordinal":state_ordinal,"term_assignment_ordinal":term_ordinal,"snapshot_path":species["snapshot_path"],"snapshot_hash":species["snapshot_hash"],"source_url":species["source_url"]})
                targets.append({"target_id":target_id,"species_row_id":species["row_id"],"state_record":row[0],"term_assignment_inscription":match.group(0)+suffix,"positive_spin_multiplicity":multiplicity,"axis_support_symbol":symbol,"fold_axis_rank":AXIS_RANK[symbol],"positive_axis_orientation_count":AXIS_ORIENTATION_COUNT[symbol],"positive_combined_degeneracy_count":multiplicity*AXIS_ORIENTATION_COUNT[symbol],"held_inversion_label":held_inversion(suffix),"held_reflection_label":held_reflection(suffix),"held_axis_component":held_component(suffix),"held_component_kind":held_component_kind(suffix),"raw_suffix":suffix,"snapshot_path":species["snapshot_path"],"snapshot_hash":species["snapshot_hash"]})
    if len(targets)!=362 or len({row["target_id"] for row in targets})!=362:raise RuntimeError("complete NIST symmetry census must contain 362 assignments")
    source={"source_id":"NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025","body":"National Institute of Standards and Technology","database":"NIST Chemistry WebBook SRD 69","doi":"10.18434/T4D303","retrieval_date":"2026-07-26","species_count":22,"state_row_count":360}
    IDENTITIES.write_text(json.dumps({"schema":"sft-v3-state-symmetry-identities/1","source":source,"rows":identities},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    TARGETS.write_text(json.dumps({"schema":"sft-v3-state-symmetry-withheld-targets/1","source":source,"rows":targets},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("term assignments:",len(targets));print("inversion labels:",sum(r["held_inversion_label"]!="absence" for r in targets));print("reflection labels:",sum(r["held_reflection_label"]!="absence" for r in targets));print("axis components:",sum(r["held_axis_component"]!="absence" for r in targets));print("source component-absence glyphs:",sum("_0" in r["raw_suffix"] for r in targets));print("identity registry:",file_hash(IDENTITIES));print("withheld target registry:",file_hash(TARGETS))
if __name__=="__main__":main()
