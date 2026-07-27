#!/usr/bin/env python3
"""Build value-free identities for the final INORG-014--017 family batch."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1"
SPECS={
"014":("SFT-CHEM-METAL-CLUSTER-BONDING-014","SFT-CHEM-OBL-INORG-014",(
 ("IUPAC-CT06769","cluster","iupac-ct06769.json","sha256:f13319605c529b7ef3783134dd847ab2382272e39096e3de60d5d44864f68c81","identity_only_unopened",("multiple-metal-centre-support","direct-metal-bond-interaction","bridging-ligand-interaction","interaction-not-necessary-for-cluster-grouping")),
 ("IUPAC-IT06779","iron-sulfur cluster","iupac-it06779.json","sha256:30e3d6f2715a91f06198bc5fdf20ad372835508785b41e86b4b8c62f775db775","identity_only_unopened",("two-or-more-iron-support","bridging-sulfur-ligand-support","iron-sulfur-content-designation","two-iron-two-sulfur-example","three-iron-four-sulfur-example","external-oxidation-level-charge-inscriptions")))),
"015":("SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015","SFT-CHEM-OBL-INORG-015",(
 ("IUPAC-12823","coordination network","iupac-12823.json","sha256:77fd0493785699114e933c4e742ca8f23ce4a12b9425856137e9003cc7579b2a","development_observed",("repeating-coordination-entity-support","one-dimensional-crosslinked-network","chain-loop-spiro-crosslink-classes","two-dimensional-extension","three-dimensional-extension")),
 ("IUPAC-S05735","solid solution","iupac-s05735.json","sha256:c98787d2ded225aa7d79f1f4e0359b3246986f0c92f250656b1639cd98faa796","identity_only_unopened",("registered-solid-solution-returned-mixed-crystal","second-constituent-support","constituent-fits-host-lattice","constituent-distributed-in-host-lattice","amorphous-solid-solution-use-not-recommended")))),
"016":("SFT-CHEM-DEFECT-NONSTOICHIOMETRY-016","SFT-CHEM-OBL-INORG-016",(
 ("IUPAC-S05735","solid solution","iupac-s05735.json","sha256:c98787d2ded225aa7d79f1f4e0359b3246986f0c92f250656b1639cd98faa796","identity_only_unopened",("registered-solid-solution-returned-mixed-crystal","second-constituent-support","constituent-fits-host-lattice","constituent-distributed-in-host-lattice","amorphous-use-boundary")),
 ("IUPAC-13807","crystal lattice defect","iupac-13807.json","sha256:5f0b305b51587b244c1b52ab2a5f23099100b75dd2fd38e85259b34066c7a1d6","identity_only_unopened",("regular-atomic-arrangement-interruption","crystallographic-defect-synonym")),
 ("IUPAC-09464","defect","iupac-09464.json","sha256:b9edae2a8f815ba93e19092bbddd3a3e2075dd787c97c579c39d1367fad3c692","identity_only_unopened",("pattern-formation-imperfection","noncrystal-image-defect-scope-mismatch")),
 ("IUPAC-14011","extrinsic defect","iupac-14011.json","sha256:4bfb9494b636f2035146f9de9b96b7676120bb4e4d77527c0d7426d31a123c22","identity_only_unopened",("extrinsic-chemical-unit-relative-to-formula","adsorbed-species-example","surface-and-near-surface-bulk-role")),
 ("IUPAC-14026","intrinsic defects","iupac-14026.json","sha256:0bad3e09e39b9178e8ba1af1ba468cf7ef2b7a559af3b5a8d8c434cbb1fd4251","identity_only_unopened",("no-extrinsic-chemical-unit-relative-to-formula","point-linear-square-dimensional-defect-classes","vacancy-interstitial-edge-corner-kink-examples")))),
"017":("SFT-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017","SFT-CHEM-OBL-INORG-017",(
 ("IUPAC-L03508","Lewis acid","iupac-l03508.json","sha256:64eaa0268cbeacadcecd3a31679456d3ba901223a34b28c47ed51b7d7b33def3","development_observed",("electron-pair-acceptor","acid-reacts-with-base","shared-base-pair-forms-adduct","acid-example-introduced-rendered-structure-absent")),
 ("IUPAC-L03511","Lewis base","iupac-l03511.json","sha256:9ad07fa85acc8b7ee0f8c0147680382b6ec8c086c4c1974b5aa3cc3af73d980e","development_observed",("electron-pair-provider","base-coordinates-acid","base-produces-adduct")),
 ("IUPAC-L03510","Lewis adduct","iupac-l03510.json","sha256:da6d0f140e2ecf0f601254cec017a0cb52e98e42a40ee87efa16ecb48173fa08","identity_only_unopened",("acid-base-adduct-composition",)),
 ("IUPAC-O04362","oxidation","iupac-o04362.json","sha256:7a7d1a010e6d3b9a68e06839fcd7779815ad66fe7a5a523481747c988a6e7536","identity_only_unopened",("complete-net-electron-removal","external-oxidation-number-increase","oxygen-gain-hydrogen-loss-criterion","all-oxidations-meet-first-two-criteria","primitive-change-pathway-description")),
 ("IUPAC-R05222","reduction","iupac-r05222.json","sha256:1a484820052299d5206ad4855eaa5e6181583e57bcb7db7dd95faacdd84a6141","identity_only_unopened",("complete-electron-transfer-to-entity","reverse-of-oxidation-processes"))))}
def main():
 out=ROOT/"experiments/external_sources/chemistry"
 for num,(claim,obl,sources) in SPECS.items():
  rows=[]
  for sid,identity,file,digest,custody,roles in sources:
   for role in roles:rows.append({"target_id":f"SFT-CHEM-INORG-{num}-{len(rows)+1:03d}","source_record_ordinal":len(rows)+1,"source_id":sid,"authority":"IUPAC","registered_identity":identity,"source_record_role":role,"custody_class":"family-"+custody.replace("_","-"),"snapshot_path":f"{BASE}/{file}","snapshot_sha256":digest})
  payload={"schema":"sft-v3-value-free-target-identities/1","claim_id":claim,"obligation_id":obl,"family_boundary":"SFT-CHEM-FAMILY-INORG-004-017","selection_rule":"Every separately registered definition, example, scope, adverse, absence or correspondence surface is retained in source and surface order.","complete_registered_target_count":len(rows),"target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present":False,"rows":rows};p=out/f"inorg_{num}_target_identities_v1.json";p.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(p.relative_to(ROOT),len(rows))
if __name__=="__main__":main()
