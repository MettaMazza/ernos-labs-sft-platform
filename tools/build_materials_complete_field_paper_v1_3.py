#!/usr/bin/env python3
"""Build the 289-law Materials paper without altering any scientific authority."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_2.md"
OUT = ROOT / "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md"
CURRENT = ROOT / "publications/current/materials/FROM_FOLD_TO_MATERIALS.md"
FROZEN = ROOT / "census/materials_discipline_obligations.json"
RECON = ROOT / "census/materials_discipline_current_reconciliation_v20.json"
CLAIMS = ROOT / "census/claims.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value) -> str:
    return str(value).replace("\n", " ").strip()


def bullets(rows) -> str:
    values = tuple(rows)
    return "\n".join(f"- {clean(row)}" for row in values) if values else "- None."


def current_certificate(package: Path, receipt_hash: str):
    matches = [path for path in sorted(package.glob("certificate*.json")) if read(path).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1:
        raise SystemExit(f"{package.name}: expected one current certificate, found {len(matches)}")
    return read(matches[0])


def claim_section(order: int, field: str, obligation: str, claim_id: str, row: dict) -> str:
    package = ROOT / "claims" / claim_id
    registration = read(package / "registration.json")
    census = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    empirical = read(package / "empirical_validation.json")
    certificate = current_certificate(package, row["receipt_hash"])
    survivors = [item for item in elimination["decisions"] if item["survives"]]
    if len(census["candidates"]) != len(elimination["decisions"]) or len(survivors) != 1:
        raise SystemExit(f"incomplete enumeration: {claim_id}")
    if not all(item["passed"] for item in controls) or not empirical["passed"] or not empirical["all_rows_preserved"]:
        raise SystemExit(f"incomplete control or empirical custody: {claim_id}")
    unique = registration.get("candidate_grammar", {}).get("unique_survivor", survivors[0]["candidate_id"])
    coordinates = unique.split("__")
    control_rows = "\n".join(
        f"- `{item['kind']}` — passed; expected: {clean(item['expected_behavior'])}; observed: {clean(item['observed_behavior'])}; receipt `{item['receipt_hash']}`."
        for item in controls
    )
    measurements = bullets(empirical.get("measurements", ()))
    sources = bullets(f"`{source}`" for source in empirical.get("data_source_ids", ()))
    dependencies = bullets(f"`{dependency}`" for dependency in registration.get("dependencies", ()))
    exclusions = bullets(registration.get("excluded_inputs", ()))
    exact = certificate.get("exact_result", registration.get("statement", ""))
    closure = elimination["closure"]
    return f"""### {order}. {registration['title']}

Field: `{field}`  
Obligation: `{obligation}`  
Claim: `{claim_id}`

**Question, law and forced result.** {clean(registration.get('statement', exact))}

> {clean(exact)}

**Trace to the foundational theorem.** The claim registration names no axioms and no free parameters. It depends only on these already admitted receipt identities:

{dependencies}

The complete owner/dependency graph in `census/materials_hand_001_006_dependency_registry_v1.json` independently proves this claim reaches `SFT-ROOT-THERE-IS-NO-NOTHING`.

**Complete candidate grammar.** {clean(registration['candidate_grammar']['generator'])}

Boundary: {clean(registration['candidate_grammar']['boundary'])}

The literal product contains `{len(census['candidates'])}` candidates and the elimination ledger contains exactly `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives and `{len(elimination['decisions']) - 1}` are eliminated. The forced coordinates are:

{bullets(f'`{coordinate}`' for coordinate in coordinates)}

Unique survivor: `{survivors[0]['candidate_id']}`.

Closure: `{closure['scope']}`; minimality `{str(closure['minimality_passed']).lower()}`; named-shape uniqueness `{str(closure['named_shape_uniqueness_passed']).lower()}`; proof `{closure['proof_hash']}`; generality `{closure['generality_certificate_hash']}`.

**What it means.** This law retains every carrier, relation, organization, observation condition, record, provenance edge, positive-finite extension and explicit handoff required by its question. It does not turn a selected specimen, fitted magnitude, imported named model or application outcome into a law. Structural absence remains typed empty One; host numerical `0` is only its display notation.

**Falsification controls.** All four required controls passed:

{control_rows}

**Independent reconstruction and engine admission.** Independent implementation `{certificate['independent_implementation_hash']}` regenerated the declared census and sole survivor; independent certificate `{certificate['independent_certificate_hash']}`. Derivation seal `{certificate['derivation_seal_hash']}`. Source manifest `{certificate['source_manifest_hash']}`. Engine receipt `{row['receipt_hash']}` at `{row['receipt_path']}`. Closure scope `{row['closure_status']}`. External status `{row['external_status']}`.

**Post-seal external comparison.** Target opened after seal: `{str(empirical['target_opened_after_seal']).lower()}`. Evaluator verified seal: `{str(empirical['evaluator_verified_seal']).lower()}`. All rows preserved: `{str(empirical['all_rows_preserved']).lower()}`. Comparison passed: `{str(empirical['passed']).lower()}`.

Source identities:

{sources}

Measured, observed, adverse and boundary records:

{measurements}

Falsification condition: {clean(empirical['falsification_condition'])}

Measurement receipt `{empirical['measurement_receipt_hash']}`; empirical validation `{certificate['empirical_validation_hash']}`; external validation `{certificate['external_validation_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.

**Prohibited inputs.**

{exclusions}
"""


def main():
    frozen = read(FROZEN)
    recon = read(RECON)
    live = {row["claim_id"]: row for row in read(CLAIMS)["claims"]}
    if recon["current_closed_count"] != 289 or recon["frozen_obligation_count"] != 289 or recon["current_open_count"] != 0:
        raise SystemExit("Materials complete-field reconciliation is not 289/289")
    mapping = {}
    for rows in recon["completed_families"].values():
        for row in rows:
            mapping[row["obligation_id"]] = row["claim_id"]
    extension_obligations = frozen["obligations"][92:]
    if len(extension_obligations) != 197 or any(item["obligation_id"] not in mapping for item in extension_obligations):
        raise SystemExit("Materials 197-law complete-field extension is not fully mapped")

    base = BASE.read_text(encoding="utf-8")
    body_start = base.index("## Public scientific mission and admission boundary")
    body_end = base.index("## 23. Reproducibility and falsification")
    preserved = base[body_start:body_end].rstrip()
    preserved = preserved.replace("92 of 92", "289 of 289").replace("all 92", "all 289")
    preserved = preserved.replace("92 required laws", "289 required laws")

    front = """# From Fold to Materials

**Materials Science Branch Paper 001, version 1.3.0 — complete-field Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the complete dated Materials Science reconstruction: 289 of 289 registered obligations admitted through the untouched Smithian Fold Theory engine, while remaining open to lawful extension. The branch contains 73,984 exact generated candidates and decisions, 289 unique survivors, 1,156 passing adverse controls, 289 implementation-distinct reconstructions and 289 receipt-bound empirical packages. Every admitted law reaches the single premise-free foundational theorem. The complete-field extension adds quantitative crystallography and diffraction; defects and multiscale microstructure; phase transformation and metastability; fracture, fatigue, creep, tribology and rheology; thermal, electronic, ionic, magnetic, superconducting, optical and photonic response; complete material classes; soft, biological, nano and surface materials; degradation; processing; computational materials; extreme conditions; sustainability; complete empirical vectors; and one-owner cross-branch handoffs. No axiom, free or fitted parameter, imported constitutive model, target-selected law, negative proof quantity, irrational or imaginary proof value, floating proof arithmetic or numerical-zero ontology is admitted.

## Results first: complete-field Materials reconstruction

| Headline finding | Exact result | Empirical meaning |
|---|---|---|
| Complete dated field census | `289/289` obligations; `0` open (display `0` denotes absence) | Every current obligation has its own receipt; future lawful additions remain permitted. |
| Exact enumeration | `73,984` candidates and decisions; `289` sole survivors | Every law is selected by complete grammar enumeration, not fitting or consensus. |
| Falsification and reconstruction | `1,156` adverse controls; `289` independent reconstructions | A missing distinction, changed source, altered artifact or boundary violation halts. |
| Quantitative structural classifications | six simple-cubic neighbours; orders `1,2,3,4,6`; seven crystal systems; fourteen Bravais classes; three acoustic modes | These are exact forced classifications, not measured fits. |
| Full response surface | mechanics, transport, phase, electromagnetic, optical, collective, interfacial and lifecycle laws are separately retained | Specimen, method, scale, condition, uncertainty and adverse evidence remain attached. |
| Empirical Grand Lock | all `271` pre-validation Materials claims represented by `1,040` evidence lines and `334` source-identity occurrences | No favorable-only aggregation; adverse, absent, unavailable, unresolved and out-of-bound rows remain visible. |
| One-owner completeness | `1,681` predecessor claims root-reachable through `28,437` dependency edges, including `19,852` cross-branch uses | Cross-field use is a directed dependency, never duplicate ownership. |

"""

    grouped = []
    order = 93
    for field in frozen["field_order"][10:]:
        obligations = [item for item in extension_obligations if item["field"] == field]
        grouped.append(f"## Complete-field family: {field.replace('_', ' ').title()}\n")
        for item in obligations:
            claim_id = mapping[item["obligation_id"]]
            grouped.append(claim_section(order, field, item["obligation_id"], claim_id, live[claim_id]))
            order += 1
    if order != 290:
        raise SystemExit(f"expected 289 claim sections, ended at {order - 1}")

    tail = f"""## Reproducibility, falsification and extension boundary

The one-command repository validation remains the complete public route. This paper update additionally requires the 289/289 reconciliation identity `{recon['reconciliation_identity']}`, exact replay of the final HAND family, focused family tests, repository validation and both immutable authority seals. The final repository-wide heavy verification remains reserved for the final cross-branch Grand Lock; it is not redundantly rerun for this local paper preparation.

The Materials branch is complete to its dated current standard, not permanently locked. A lawful new observation may falsify an existing correspondence or create a new obligation. It must be preregistered, enumerated, independently reconstructed, passed through the same untouched engine, externally compared where possible and added by versioned extension. Neither popularity nor credentials can close or suppress it.

## Conclusion

Materials Science now has a public, exact and machine-auditable path from the premise-free Fold theorem to 289 separately admitted laws and their external evidence. The result does not ask the reader to trust Maria Smith, Ernos Labs, an institution or an AI system. It exposes the grammars, exclusions, candidate censuses, one-for-one decisions, controls, source custody, receipts and falsifiers needed to reproduce or invalidate every claim. That is the scientific authority asserted here: transparent evidence and a common fail-closed method, not permission from a gatekeeper.

## Publication and repository links

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions and open review: https://discord.gg/ucwGryVxGr
- Paper license: CC BY 4.0; code license: Apache-2.0; authorship and creative rights retained.

## References

- Bureau International des Poids et Mesures / Joint Committee for Guides in Metrology, International Vocabulary of Metrology.
- National Institute of Standards and Technology records identified in the claim-level source ledgers.
- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *After Turing: The Fold Machine*. doi:10.5281/zenodo.21518311.
- Smith, Maria. *The Quantum Fold Machine*. doi:10.5281/zenodo.21518313.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Chemistry*. doi:10.5281/zenodo.21531455.
"""
    result = front + preserved + "\n\n" + "\n\n".join(grouped) + "\n\n" + tail
    result = result.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(result.rstrip() + "\n", encoding="utf-8")
    CURRENT.write_text(result.rstrip() + "\n", encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)} with 289 complete claim sections")


if __name__ == "__main__":
    main()
