#!/usr/bin/env python3
from hashlib import sha256
import json,time
from pathlib import Path
from urllib.parse import quote,urlencode
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"evidence/external/social/exact_return_2026-07-28"
QUERIES=(("inequality","cumulative advantage preferential attachment wealth inequality empirical"),("polarization","political polarization consensus aggregation hidden disagreement empirical"),("cycles","business cycles boom bust political cycles recurrent empirical"))
def get(u):
 with urlopen(Request(u,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=40) as r:return r.read()
def main():
 OUT.mkdir(parents=True,exist_ok=True);selected=[]
 for family,q in QUERIES:
  d=json.loads(get("https://api.openalex.org/works?"+urlencode({"search":q,"per-page":"7","select":"id,doi,title,publication_year"})))
  selected += [{"class":family,"query":q,"openalex_id":x["id"].rsplit("/",1)[-1],"doi":x.get("doi"),"title":x.get("title"),"publication_year":x.get("publication_year")} for x in d["results"]];time.sleep(.3)
 reg={"schema":"sft-v3-social-exact-target-identities/1","selection_rule":"All identity-only query results registered before any full record or abstract was opened; every selected identity retained.","selected":selected,"target_content_present":False,"formal_predecessor_receipts":{"flow":"sha256:04a60e9ee095d1a90f1a9802b18ab38a4a98ee3ef7c5072d87db95aeed474896","lock":"sha256:02d9e32e8d89c68b88668db175e2d8de4cdacba0f3adaef2a40b3fe2b0d3ee56","cycle":"sha256:fcfeb4b70b7ccc725e116368b85180508377d5cad166860b6a1c72d88a666d07"}};rb=(json.dumps(reg,indent=2,sort_keys=True)+"\n").encode();(OUT/"target_identities.json").write_bytes(rb);docs=[]
 for x in selected:
  body=get("https://api.openalex.org/works/"+quote(x["openalex_id"]));p=OUT/("openalex_"+x["openalex_id"]+".json");p.write_bytes(body);docs.append({"class":x["class"],"openalex_id":x["openalex_id"],"snapshot_path":p.relative_to(ROOT).as_posix(),"snapshot_hash":"sha256:"+sha256(body).hexdigest(),"source_uri":"https://openalex.org/"+x["openalex_id"]});time.sleep(.2)
 obs={"schema":"sft-v3-social-exact-source-custody/1","target_identity_registration_path":(OUT/"target_identities.json").relative_to(ROOT).as_posix(),"target_identity_registration_hash":"sha256:"+sha256(rb).hexdigest(),"documents":docs,"all_documents_retained":True};(OUT/"observations.json").write_text(json.dumps(obs,indent=2,sort_keys=True)+"\n");print(json.dumps({"registered":len(selected),"captured":len(docs)}))
if __name__=="__main__":main()
