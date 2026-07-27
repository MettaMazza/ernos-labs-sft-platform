#!/usr/bin/env python3
"""Capture the complete common NIST-JANAF NO2/N2O4 reaction-direction surface."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT=Path(__file__).resolve().parents[1]
SPEC_PATH=ROOT/"experiments/external_sources/chemistry/reaction_direction_capture_spec_v1.json"
SNAPSHOT_ROOT=ROOT/"experiments/external_sources/chemistry/snapshots/thermo-007-reaction-direction-v1"
IDENTITY_PATH=ROOT/"experiments/external_sources/chemistry/reaction_direction_target_identities_v1.json"
TARGET_PATH=ROOT/"experiments/external_sources/chemistry/reaction_direction_withheld_targets_v1.json"
PRIMARY_PATH=SNAPSHOT_ROOT/"reaction-direction-primary-records-v1.json"
COLUMNS=("temperature-kelvin","heat-capacity-joule-per-mole-kelvin","entropy-joule-per-mole-kelvin","gibbs-function-joule-per-mole-kelvin","enthalpy-increment-kilojoule-per-mole","formation-enthalpy-kilojoule-per-mole","formation-gibbs-kilojoule-per-mole","log10-formation-equilibrium-constant")


def sha_bytes(data:bytes)->str:return "sha256:"+hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:return sha_bytes(path.read_bytes())
def canonical(value)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def write_json(path:Path,payload):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def fetch(url:str)->bytes:
    request=Request(url,headers={"User-Agent":"Ernos-Labs-SFT-Empirical-Capture/1.0 (Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(request,timeout=60) as response:return response.read()


def parse_table(data:bytes)->dict[Fraction,dict[str,str]]:
    lines=data.decode("utf-8").splitlines()
    if len(lines)<4 or lines[1].split("\t")!=(['T(K)','Cp','S','-[G-H(Tr)]/T','H-H(Tr)','delta-f H','delta-f G','log Kf']):raise ValueError("JANAF tabular schema changed")
    rows={}
    for line in lines[2:]:
        cells=line.split("\t")
        if len(cells)!=8:continue
        if cells[0]=="0" or any(value in {"","INFINITE"} for value in (cells[0],cells[6],cells[7])):continue
        try:temperature=Fraction(cells[0])
        except (ValueError,ZeroDivisionError):continue
        if temperature<=0:continue
        if temperature in rows:raise ValueError("duplicate JANAF temperature")
        rows[temperature]=dict(zip(COLUMNS,cells))
    if not rows:raise ValueError("JANAF table returned no finite target rows")
    return rows


def main()->None:
    spec_bytes=SPEC_PATH.read_bytes();spec_hash=sha_bytes(spec_bytes);spec=json.loads(spec_bytes)
    if spec.get("schema")!="sft-v3-reaction-direction-prefetch-capture-spec/1" or spec.get("all_source_values_absent") is not True or spec.get("target_values_or_hashes_present") is not False:raise ValueError("reaction-direction prefetch specification changed")
    SNAPSHOT_ROOT.mkdir(parents=True,exist_ok=True)
    captured={}
    for source in spec["source_tables"]:
        stem=str(source["source_id"]).split("-")[3]
        html=fetch(str(source["url"]));txt=fetch(str(source["url"]).replace(".html",".txt"))
        html_path=SNAPSHOT_ROOT/f"nist-janaf-{stem}.html";txt_path=SNAPSHOT_ROOT/f"nist-janaf-{stem}.txt"
        html_path.write_bytes(html);txt_path.write_bytes(txt)
        captured[str(source["formula"])]=dict(source=source,html_path=html_path,txt_path=txt_path,rows=parse_table(txt))
    no2,n2o4=captured["NO2"],captured["N2O4"];common=tuple(sorted(set(no2["rows"])&set(n2o4["rows"])))
    if len(common)!=64:raise ValueError(f"complete common JANAF surface changed: {len(common)} rows")
    identities=[];targets=[]
    for ordinal,temperature in enumerate(common,start=1):
        target_id=f"SFT-CHEM-THERMO-007-NO2-N2O4-{ordinal:04d}"
        identity={"target_id":target_id,"common_source_row_ordinal":ordinal,"reaction_identity":spec["reaction_identity"],"stoichiometric_identity":spec["stoichiometric_identity"],"standard_state_pressure":spec["standard_state_pressure"],"source_ids":[no2["source"]["source_id"],n2o4["source"]["source_id"]],"source_class":"complete-common-NIST-JANAF-reaction-state-row","all_temperature_thermochemical_direction_and_target_hash_values_absent":True}
        a=no2["rows"][temperature];b=n2o4["rows"][temperature]
        reaction_gibbs=2*Fraction(a["formation-gibbs-kilojoule-per-mole"])-Fraction(b["formation-gibbs-kilojoule-per-mole"])
        reaction_logk=2*Fraction(a["log10-formation-equilibrium-constant"])-Fraction(b["log10-formation-equilibrium-constant"])
        if reaction_gibbs==0 or reaction_logk==0:direction="equilibrium"
        elif reaction_gibbs<0 and reaction_logk>0:direction="forward"
        elif reaction_gibbs>0 and reaction_logk<0:direction="reverse"
        else:raise ValueError("JANAF Gibbs/log-K directions disagree")
        target={"target_id":target_id,"common_source_row_ordinal":ordinal,"temperature-kelvin":a["temperature-kelvin"],"NO2_complete_row":a,"N2O4_complete_row":b,"reaction-gibbs-kilojoule-per-mole-external-signed-inscription":str(reaction_gibbs),"reaction-gibbs-exact-positive-separation-kilojoule-per-mole":str(abs(reaction_gibbs)),"reaction-log10-equilibrium-constant-external-signed-inscription":str(reaction_logk),"held-reaction-direction":direction}
        identities.append(identity);targets.append(target)
    identity_doc={"schema":"sft-v3-reaction-direction-target-identities/1","prefetch_capture_spec_hash":spec_hash,"complete_target_count":len(identities),"all_common_rows_retained":True,"all_temperature_thermochemical_direction_and_target_hash_values_absent":True,"rows":identities}
    identity_hash=sha_bytes(canonical(identity_doc));identity_doc["canonical_identity_hash"]=identity_hash
    target_doc={"schema":"sft-v3-reaction-direction-withheld-targets/1","prefetch_capture_spec_hash":spec_hash,"identity_registry_canonical_hash":identity_hash,"release_requires_complete_identity_prediction_seal":True,"complete_target_count":len(targets),"rows":targets}
    write_json(IDENTITY_PATH,identity_doc);write_json(TARGET_PATH,target_doc)
    primary={"schema":"sft-v3-reaction-direction-primary-records/1","prefetch_capture_spec_hash_before_http_fetch":spec_hash,"capture_rule":spec["capture_rule"],"reaction_identity":spec["reaction_identity"],"complete_common_finite_row_count":len(common),"all_common_rows_and_all_eight_species_columns_preserved":True,"reverse_direction_row_count":sum(row["held-reaction-direction"]=="reverse" for row in targets),"forward_direction_row_count":sum(row["held-reaction-direction"]=="forward" for row in targets),"equilibrium_row_count":sum(row["held-reaction-direction"]=="equilibrium" for row in targets),"direction_crossing_bracket_kelvin":[targets[4]["temperature-kelvin"],targets[5]["temperature-kelvin"]],"external_signed_glyphs_are_source_or_postseal_correspondence_inscriptions_not_SFT_proof_values":True,"external_values_used_as_proof_parameters":False,"sources":[{"source_id":row["source"]["source_id"],"url":row["source"]["url"],"html_snapshot_path":str(row["html_path"].relative_to(ROOT)),"html_snapshot_hash":sha_file(row["html_path"]),"tab_snapshot_path":str(row["txt_path"].relative_to(ROOT)),"tab_snapshot_hash":sha_file(row["txt_path"]),"finite_row_count":len(row["rows"])} for row in (no2,n2o4)],"identity_registry_canonical_hash":identity_hash,"withheld_target_registry_hash":sha_file(TARGET_PATH)}
    write_json(PRIMARY_PATH,primary)
    print(json.dumps({"prefetch_spec_hash":spec_hash,"common_rows":len(common),"reverse":primary["reverse_direction_row_count"],"forward":primary["forward_direction_row_count"],"equilibrium":primary["equilibrium_row_count"],"crossing_bracket_kelvin":primary["direction_crossing_bracket_kelvin"],"identity_hash":identity_hash,"target_hash":sha_file(TARGET_PATH)},sort_keys=True))


if __name__=="__main__":main()
