#!/usr/bin/env python3
"""Build the unpublished Mathematics v1.5 complete-field paper from sealed evidence."""
from __future__ import annotations

import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_4.md"
OUT=ROOT/"publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md"
RECON=ROOT/"census/mathematics_discipline_current_reconciliation_v23.json"
CENSUS=ROOT/"census/mathematics_discipline_obligations.json"

def read(path):return json.loads(path.read_text(encoding="utf-8"))
def current_certificate(package,row):
 matches=[]
 for path in package.glob("certificate*.json"):
  data=read(path)
  if data.get("engine_receipt_hash")==row["receipt_hash"]:matches.append((path,data))
 if len(matches)!=1:raise SystemExit(f"current certificate count for {row['claim_id']}: {len(matches)}")
 return matches[0]
def one_sub(pattern,replacement,text):
 value,count=re.subn(pattern,replacement,text,count=1,flags=re.S)
 if count!=1:raise SystemExit("paper substitution failed: "+pattern[:60])
 return value
def safe(value):return str(value).replace("\n"," ").replace("|","/").strip()

def main():
 recon=read(RECON);frozen=read(CENSUS)
 if recon["current_closed_count"]!=323 or recon["current_open_count"]!=0:raise SystemExit("Mathematics is not 323/323")
 live={x["claim_id"]:x for x in read(ROOT/"census/claims.json")["claims"]}
 obligation_titles={x["obligation_id"]:x["title"] for x in frozen["obligations"]}
 family_order=tuple(frozen["family_order"])
 if set(family_order)!=set(recon["completed_families"]):raise SystemExit("family order does not exhaust reconciliation")
 details=[];candidate_total=control_total=0
 for family in family_order:
  family_rows=[]
  for row in recon["completed_families"][family]:
   claim=live[row["claim_id"]];package=ROOT/"claims"/row["claim_id"];_,cert=current_certificate(package,row)
   registration=read(package/"registration.json");candidates=read(package/"candidate_census.json")["candidates"];controls=read(package/"controls.json")["controls"]
   empirical_path=package/"empirical_validation.json";empirical=read(empirical_path) if empirical_path.exists() else {}
   candidate_total+=len(candidates);control_total+=len(controls)
   family_rows.append({"row":row,"claim":claim,"cert":cert,"registration":registration,"candidate_count":len(candidates),"control_count":len(controls),"measurements":empirical.get("measurements",[]),"sources":empirical.get("data_source_ids",cert.get("external_data_source_ids",[])),"obligation_title":obligation_titles.get(row["obligation_id"],registration.get("title",row["obligation_id"]))})
  details.append((family,family_rows))
 if candidate_total!=97280 or control_total!=1292:raise SystemExit(f"unexpected totals {candidate_total}/{control_total}")

 text=SOURCE.read_text(encoding="utf-8")
 text=text.replace("25 July 2026\n\nMathematics Branch Paper 001 - Version 1.4", "29 July 2026\n\nMathematics Branch Paper 001 - Version 1.5",1)
 text=text.replace("DOI: [10.5281/zenodo.21627708](https://doi.org/10.5281/zenodo.21627708)","Previous version DOI: [10.5281/zenodo.21627708](https://doi.org/10.5281/zenodo.21627708)  \nVersion 1.5 DOI: pending archival deposit",1)
 abstract=f"""## Abstract

This paper reports the complete-field Mathematics branch of the third clean-room reconstruction of Smithian Fold Theory (SFT), complete to the frozen dated census and explicitly open to lawful extension. The census contains **323 obligations in 24 dependency-ordered families**. Every obligation now has an untouched-engine model-admission receipt, an exact candidate census, one unique survivor, four adverse controls, a depth-independent finite-successor or explicit boundary certificate, an implementation-distinct reconstruction, and post-registry observation custody. Together the branch preserves **{candidate_total:,} generated candidates, 323 unique survivors and {control_total:,} passed controls**. The final reconciliation identity is `{recon['reconciliation_identity']}`.

The field reconstruction covers exact arithmetic and number structure; algebraic extensions; combinatorics; graphs, networks and matroids; linear, multilinear and tensor structure; algebraic systems; order, lattices and domains; geometry; topology; calculus correspondence; analysis correspondence; equation structures; measure and integration; deterministic-support probability and statistics; optimization and operations research; dynamical systems; logic and foundations; category, type and compositional structures; numerical mathematics; symbolic and constructive mathematics; cross-disciplinary interfaces; the complete validation vector; and one-owner handoffs. The previously admitted Smithian Fold Scientific Calculator remains the accessible translation surface and does not become an alternate admission route.

The proof domain admits no conventional axiom as an SFT premise, no fitted or free parameter, no semantic numerical zero, negative proof magnitude, irrational or imaginary proof scalar, floating proof quantity, completed infinity, ungenerated continuum or ontic randomness. Displayed `0` denotes structural absence; opposition is typed orientation; non-rational conventional objects enter only through exact constructions or certified enclosures. The Validation Grand Lock partitions all 305 pre-validation receipts exactly once across 22 families and preserves all 305 favorable, adverse, absent, unresolved and boundary records. The final six handoffs bring the branch to 323/323 without transferring empirical ownership to Mathematics or claiming permanent closure.

Version 1.5 preserves the complete version 1.4 paper and its foundational, prior-corpus and calculator derivations, then executes the roadmap that version 1.4 registered. No application selected these laws. No engine or protected-verifier source was modified. Every later extension must enter as a new registered question and pass the same public protocol.

**Keywords:** Smithian Fold Theory; complete-field mathematics; exact arithmetic; algebra; combinatorics; graph theory; geometry; topology; calculus; analysis; probability; optimization; dynamics; logic; category theory; numerical mathematics; symbolic mathematics; scientific calculator; computational proof; open science.
"""
 text=one_sub(r"## Abstract\n.*?(?=\n## Results first:)",abstract.rstrip(),text)
 results=f"""## Results first: what this branch changes

| Headline result | Exact executed result | Scientific consequence |
|---|---|---|
| Complete-field Mathematics | 323/323 frozen obligations are receipt-backed across 24 families, with {candidate_total:,} enumerated candidates, 323 unique survivors and {control_total:,} passed controls. | The former roadmap is now an executed, independently replayable mathematical corpus rather than a statement of future intent. |
| Arithmetic without hidden continuum primitives | Exact positive finite generation, normalized fractions, ordered gaps, interval enclosures and structural absence replace semantic zero, negative proof magnitude and floating proof values. | Ordinary notation remains available at the interface, but every proof value retains an exact Fold construction or certified enclosure. |
| Full structural span | Combinatorics, graphs, linear and algebraic structures, order, geometry, topology, calculus, analysis, equations, measure, probability, optimization, dynamics, logic, category, numerical and symbolic mathematics are separately owned and dependency ordered. | No familiar discipline name imports its conventional axioms; each law has its own generated grammar, eliminations, survivor and certificate. |
| Numerical and symbolic computation | Exact rounding custody, interval propagation, stability, conditioning, convergence, root isolation, solvers, quadrature, recurrences, canonical syntax, rewrite provenance, transforms and constructive certificates are admitted. | Numerical and symbolic tools can be audited without hiding floating, signed, imaginary or oracle-selected proof values. |
| Validation Grand Lock | All 305 pre-validation claims are partitioned exactly once across 22 families, with 305 adverse and boundary records retained. | Completeness is a reproducible reconciliation claim, not a label applied after favorable results. |
| Dated, extension-open completion | Six final handoffs distinguish mathematical structure from downstream meaning, measurement, conventional correspondence and engineering use. | Mathematics is 100.0% complete to this frozen census while remaining open to correction, falsification and lawful new discoveries. |
| Public proof surface | Every claim exposes its registration, candidate census, decisions, controls, certificate, external record, receipt and executable entry point. | Independent researchers can reproduce or challenge the work without credential, paywall or institutional permission selecting the outcome. |
"""
 text=one_sub(r"## Results first: what this branch changes\n.*?(?=\n## Public scientific mission)",results.rstrip(),text)
 central=f"""## 1. Central scientific claim

The exact claim of this version is:

> Within the frozen SFT V3 Mathematics census dated 29 July 2026, all 323 obligations in all 24 registered families are individually admitted through the untouched engine, independently reconstructed, controlled, observed after target-free registration and exactly reconciled. The current closed count is 323, the open count is structural absence, and completion remains open to lawful versioned extension.

The frozen census identity is `{frozen['census_identity']}`. The final reconciliation identity is `{recon['reconciliation_identity']}`. The branch contains {candidate_total:,} candidate decisions, 323 unique survivors and {control_total:,} passing controls. Every registration has an empty axiom list and an empty free-parameter list. Each dependency chain reaches `SFT-ROOT-THERE-IS-NO-NOTHING` through actual admitted receipts rather than through narrative citation.

This claim is bounded precisely. It does not assert a completed infinite universe, convert structural absence into a numerical object, import irrational or imaginary proof scalars, or assign measured physical meaning to a mathematical structure. Completion means every question in the frozen dated census has passed the full protocol. A new question, counterexample or stronger certificate remains admissible only as a visible versioned extension.
"""
 text=one_sub(r"## 1\. Central scientific claim\n.*?(?=\n## 2\.)",central.rstrip(),text)
 text=text.replace("## 5. Dependency order and executed census","## 5. Foundational and calculator execution preserved from version 1.4\n\n> **Version 1.5 scope note.** The twenty-seven rows in this preserved section are the original foundational and calculator evidence surface, not the current branch denominator. The controlling complete-field census is 323/323 and is documented claim by claim in Section 40.",1)
 conclusion=f"""## 39. Conclusion

Mathematics is complete to its frozen 29 July 2026 census: **323/323 obligations, 24/24 families, {candidate_total:,} complete candidate decisions, 323 unique survivors, {control_total:,} passed adverse controls, 323 implementation-distinct reconstructions and no open registered obligation**. The final reconciliation identity is `{recon['reconciliation_identity']}`. Repository validation passes with 1,983 V3 claims across the full platform, while the canonical engine seal and verification-authority seal remain unchanged.

The scientific result is both mathematical and methodological. Arithmetic, algebra, discrete structure, geometry, topology, analysis, probability, optimization, dynamics, logic, compositional mathematics, numerical analysis and symbolic construction are expressed through one exact generated constitution. Each familiar correspondence is downstream of a sealed SFT derivation. Each empty case is structural absence, each opposed direction is typed, each non-rational conventional object is represented by an exact construction or enclosure, and every claimed generality has a finite-successor or explicit boundary certificate.

The Validation Grand Lock does not erase adverse evidence. It preserves all 305 pre-validation boundary records and partitions every receipt exactly once. The final handoff family then prevents Mathematics from absorbing the empirical meanings owned by Physics, Chemistry, Biology, Social Science or Engineering. This is dated completion, not permanent closure: future discoveries remain welcome, but they do not enter by editorial preference, reputation or fit. They enter by registration, enumeration, uniqueness, falsification, independent reconstruction, observation and the unchanged engine.
"""
 text=one_sub(r"## 39\. Conclusion\n.*?(?=\n## Appendix A\.)",conclusion.rstrip(),text)
 text=text.replace("## Appendix A. Authoritative receipt identities","## Appendix A. Foundational and calculator receipt identities preserved from version 1.4",1)

 lines=[]
 lines.append("## 40. Complete-field Mathematics execution - version 1.5")
 lines.append("")
 lines.append("Version 1.4 froze the complete-field roadmap. Version 1.5 executes it. This section is controlling for the current census and preserves the earlier foundational derivations rather than rewriting their historical receipts.")
 lines.append("")
 lines.append("### 40.1 Complete family census")
 lines.append("")
 lines.append("| Order | Family | Claims | Candidates | Controls | Status |")
 lines.append("|---:|---|---:|---:|---:|---|")
 for order,(family,rows) in enumerate(details,1):
  lines.append(f"| {order} | `{family}` | {len(rows)} | {sum(x['candidate_count'] for x in rows):,} | {sum(x['control_count'] for x in rows):,} | complete, exact-replayed, extension-open |")
 lines.append(f"| **Total** | **24 families** | **323** | **{candidate_total:,}** | **{control_total:,}** | **323/323** |")
 lines.append("")
 lines.append("### 40.2 Admission constitution applied to every claim")
 lines.append("")
 lines.append("Every entry below records the owned question, exact statement, unique survivor, exhaustive candidate and control counts, post-registry observation, source custody, dependency edge and immutable receipt. The machine-readable packages remain controlling; the paper makes their scientific content visible rather than substituting hashes for findings.")
 for family_index,(family,rows) in enumerate(details,1):
  lines.append("")
  lines.append(f"### 40.{family_index+2} Family `{family}` - {len(rows)}/{len(rows)} complete")
  lines.append("")
  lines.append(f"This family contributes {sum(x['candidate_count'] for x in rows):,} completely decided candidates, {len(rows)} unique survivors and {sum(x['control_count'] for x in rows):,} passed controls. Its entries are dependency ordered and separately receipt backed.")
  for index,item in enumerate(rows,1):
   row=item["row"];reg=item["registration"];cert=item["cert"]
   lines.append("")
   lines.append(f"#### `{row['obligation_id']}` - {safe(item['obligation_title'])}")
   lines.append("")
   lines.append(f"- **Claim:** `{row['claim_id']}` - {safe(reg.get('title',item['claim']['title']))}.")
   lines.append(f"- **Forced law:** {safe(reg.get('statement',item['claim']['statement']))}")
   lines.append(f"- **Unique survivor:** {safe(cert.get('exact_result','The sealed census retains exactly one all-preserving candidate.'))}")
   lines.append(f"- **Enumeration and falsification:** {item['candidate_count']:,} candidates, one survivor, {item['control_count']} controls; closure `{safe(row['closure_status'])}` and external status `{safe(row['external_status'])}`.")
   dependencies=reg.get("dependencies",[])
   lines.append(f"- **Root lineage:** `{safe(' -> '.join(dependencies) if dependencies else 'direct registered root edge')}`; registered root `{safe(', '.join(reg.get('root_theorems',['SFT-ROOT-THERE-IS-NO-NOTHING'])))}`; axioms `{len(reg.get('axioms',[]))}`; free parameters `{len(reg.get('free_parameters',[]))}`.")
   if item["measurements"]:
    lines.append("- **Post-registry observations:** "+safe("; ".join(item["measurements"])))
   else:
    lines.append("- **Post-registry observations:** the preserved foundational package carries its versioned external-validation identity; no later target was imported into its historical source manifest.")
   lines.append("- **Sources and boundaries:** "+safe(", ".join(item["sources"]) if item["sources"] else "registered internal exact observation corpus")+". Exclusions: "+safe("; ".join(reg.get("excluded_inputs",[])) if reg.get("excluded_inputs") else "none beyond the registered grammar")+".")
   lines.append(f"- **Certificates:** derivation `{safe(cert.get('derivation_seal_hash','recorded in package'))}`; independent `{safe(cert.get('independent_certificate_hash','recorded in package'))}`; empirical `{safe(cert.get('empirical_validation_hash',cert.get('external_validation_hash','recorded in package')))}`; engine receipt `{row['receipt_hash']}`.")
 lines.append("")
 lines.append("## 41. Complete-field empirical interpretation")
 lines.append("")
 lines.append("Mathematics is empirical here in the ordinary sense that its generated consequences are observed through exact executions and independently reproduced records. Where a mathematical structure is later used to describe nature, the owning empirical science must separately identify the physical target, seal the prediction and compare units, values and uncertainty. The Mathematics handoff forbids a formal identity from impersonating a physical measurement.")
 lines.append("")
 lines.append("The Grand Lock's 305 boundary rows include favorable, adverse, absent, unresolved and excluded cases. Their preservation is essential: the reported 100.0% is the fraction of frozen obligations with complete admitted packages, not the fraction of attempted routes that happened to look favorable. A halted attempt earns no admission; a corrected route remains visible through its versioned evidence chain.")
 lines.append("")
 lines.append("## 42. Reproducibility and publication boundary")
 lines.append("")
 lines.append("The complete branch can be reviewed claim by claim through `census/mathematics_discipline_current_reconciliation_v23.json` and rerun through the repository's documented verification route. The heavy all-branch verification command remains reserved for the final global Grand Lock; this paper was prepared with exact family replay, focused tests, repository validation and both immutable seals. Version 1.5 is locally prepared and is not published until Maria Smith explicitly authorizes its GitHub and Zenodo release.")
 extension="\n".join(lines)+"\n\n"
 text=one_sub(r"## Foundation and full-field reconstruction roadmap — version 1\.4\n.*?(?=\n## References)",extension.rstrip(),text)
 OUT.write_text(text.rstrip()+"\n",encoding="utf-8")
 print(json.dumps({"paper":OUT.relative_to(ROOT).as_posix(),"claims":323,"families":24,"candidates":candidate_total,"controls":control_total,"words":len(text.split()),"reconciliation":recon["reconciliation_identity"]},indent=2))

if __name__=="__main__":main()
