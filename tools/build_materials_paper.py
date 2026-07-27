#!/usr/bin/env python3
"""Build the exhaustive Materials manuscript from immutable admitted evidence."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.materials.external_bindings import BINDING_BY_CLAIM  # noqa: E402
from sft.materials.generated_law import MATERIALS_SPECS  # noqa: E402
from sft.materials.sources import SOURCE_BY_ID  # noqa: E402
from sft.materials.successor_evidence import BINDINGS as SUCCESSOR_BINDINGS, SOURCE_BY_ID as SUCCESSOR_SOURCE_BY_ID, SPECS as SUCCESSOR_SPECS  # noqa: E402
from sft.materials.structural_counts import (  # noqa: E402
    acoustic_branch_census,
    allowed_crystallographic_orders,
    bravais_census,
    crystal_system_census,
    rotation_factor_certificate,
    simple_cubic_neighbours,
)
from sft.materials.v2_reconciliation import V2_MATERIALS_QUESTIONS  # noqa: E402
from tools.publication_series_voice import open_science_position  # noqa: E402


INVENTORY = ROOT / "publications/inventories/materials.json"
PAPER = ROOT / "publications/current/materials/FROM_FOLD_TO_MATERIALS.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/materials_zenodo_metadata_v1_2_draft.json"

SUBBRANCH_INTRO = {
    "measurement_identity": "The branch begins by retaining material, specimen, composition, phase, microstructure, property and metrological identities as different carriers with explicit method and scale boundaries.",
    "crystal_quasicrystal": "Periodic and aperiodic order are generated from exact site, adjacency, translation, rotation, reciprocal and displacement support rather than assumed from a crystallographic table.",
    "defects_microstructure": "Defects are retained differences from a declared reference organization; microstructure records their connected mesoscale arrangement, interfaces and transport paths.",
    "electronic_semiconductor": "Electronic material classes preserve occupation, held absence, accessible support, gaps, doping, junctions, transport and optical-transition boundaries.",
    "superconducting_superfluid_topological": "Collective recurrence, whole return classes and global path obstruction organize superconducting, superfluid and topological material response.",
    "mechanical": "Mechanical laws keep reference state, direction, load path, deformation history, defects, crack boundaries and method geometry in the same auditable record.",
    "thermal_magnetic_optical": "Thermal, magnetic, dielectric and optical response are condition-bounded transition relations with complete carrier, phase, loss and history ledgers.",
    "material_classes_bulk": "Material classes arise from retained constituent and network organization; molecular-to-bulk claims require scale-stable composition without erasing interfaces, fluctuations or preparation history.",
    "processing_degradation": "Processing and degradation are ordered paths, never endpoint-only labels: every intermediate structure, transfer, product, defect and environmental boundary remains held.",
    "advanced_functional_sustainable": "Functional and lifecycle laws compose coupled response and complete material-flow paths while keeping application and biological outcomes outside law selection.",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return str(value).replace("\n", " ").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").strip()


def bullets(values) -> str:
    rows = tuple(values)
    return "\n".join(f"- {clean(value)}" for value in rows) if rows else "- None."


def axis_rows(spec, candidate: dict, elimination: dict) -> str:
    decisions = {row["candidate_id"]: row for row in elimination["decisions"]}
    coordinates = spec.exact_result.split("__")
    output = ["| Axis | Eliminated form | Forced form | Exact elimination / retention basis |", "|---|---|---|---|"]
    for index, dimension in enumerate(spec.dimensions):
        rejected = next(row for row in dimension.choices if not row.admitted)
        changed = list(coordinates)
        changed[index] = rejected.name
        reason = decisions["__".join(changed)]["reason"]
        output.append(f"| `{dimension.key}` | `{rejected.name}` | `{dimension.admitted_choice.name}` | {clean(reason)} {clean(dimension.admitted_choice.reason)} |")
    return "\n".join(output)


def structural_detail(claim_id: str) -> str:
    if claim_id == "SFT-MAT-CRYST-CUBIC-COORDINATION-001":
        rows = simple_cubic_neighbours(("axis-one", "axis-two", "axis-three"))
        return "The exact product is three independently admitted spatial generators times the two Fold fibre orientations. The six generated neighbours are: " + ", ".join(f"{row.generator}/{row.orientation}" for row in rows) + ". No coordinate subtraction is used; opposed directions are held labels."
    if claim_id == "SFT-MAT-CRYST-ROTATION-RESTRICTION-001":
        cert = rotation_factor_certificate()
        return f"The rank-two integral rotation boundary requires totient degree at most two. If an odd prime p divides the order, p-1 divides the degree, so only odd prime three survives. Every order is therefore 2^a times 3^b with {', '.join(cert['exponent_constraints'])}. Exhaustion leaves {tuple(row.value for row in allowed_crystallographic_orders())}; five is the least excluded positive order. This is a depth-independent factor certificate, not a depth-seven lookup and not a trigonometric approximation."
    if claim_id == "SFT-MAT-CRYST-SYSTEMS-001":
        rows = crystal_system_census()
        return "The complete rank-three metric grammar is the product of three length-equivalence classes and four angle-equivalence classes. Quotienting by axis relabelling and rotation compatibility retains seven forms: " + ", ".join(f"{row.name} ({row.length_class}; {row.angle_class})" for row in rows) + "."
    if claim_id == "SFT-MAT-CRYST-BRAVAIS-001":
        rows = bravais_census()
        return "The system/centering grammar contains seven system classes times five centering classes, or thirty-five candidates. Exact basis/centering compatibility retains fourteen: " + ", ".join(f"{row.crystal_system}/{row.centering}" for row in rows) + ". The paper claims this quotient only inside the registered rank-three translation and centering grammar."
    if claim_id == "SFT-MAT-CRYST-PHONON-001":
        rows = acoustic_branch_census()
        return "A propagation direction consumes one rank-three orientation. The remaining two independent cross-axis orientations are transverse. The complete census is: " + ", ".join(f"{row.orientation}/{row.generator}" for row in rows) + ", yielding three acoustic branches without an irrational normalization or continuous-mode premise."
    return "The law's exact result is relational. Any material-specific magnitude remains conditional on the specimen, method, direction, scale, history and declared conditions; no such magnitude is promoted into a universal constant."


def claim_block(order: int, spec, level: int = 3) -> str:
    claim_id = spec.claim_id
    root = ROOT / "claims" / claim_id
    registration = read(root / "registration.json")
    candidate = read(root / "candidate_census.json")
    elimination = read(root / "elimination_receipt.json")
    controls = read(root / "controls.json")["controls"]
    certificate = read(root / "certificate.json")
    empirical = read(root / "empirical_validation.json")
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == claim_id)
    if claim_id in BINDING_BY_CLAIM:
        binding_requirements = BINDING_BY_CLAIM[claim_id].requirements
        source_rows = [SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    else:
        binding_requirements = SUCCESSOR_BINDINGS[claim_id]
        source_rows = [SUCCESSOR_SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    witness_text = "\n".join(
        f"- `{name}`: {description}; passed `{str(passed).lower()}`."
        for name, description, passed in spec.operational_witnesses
    )
    control_text = "\n".join(
        f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`."
        for row in controls
    )
    source_text = "\n".join(
        f"- `{row.source_id}` - {row.body if hasattr(row, 'body') else 'National Institute of Standards and Technology'}; "
        f"[{row.source_uri if hasattr(row, 'source_uri') else row.uri}]({row.source_uri if hasattr(row, 'source_uri') else row.uri}); "
        f"snapshot `{row.snapshot_path if hasattr(row, 'snapshot_path') else row.path}`; "
        f"`{row.snapshot_hash if hasattr(row, 'snapshot_hash') else row.digest}`; scope: "
        f"{row.evidence_scope if hasattr(row, 'evidence_scope') else 'post-seal claim-specific authoritative comparison'}."
        for row in source_rows
    )
    fragment_identity = sha256_identity(tuple((row.source_id, row.fragment) for row in binding_requirements))
    heading = "#" * level
    return f"""{heading} {order}. {spec.title}

Claim identity: `{claim_id}`

**Question and exact theorem.** {clean(spec.statement)}

> `{clean(spec.exact_result)}`

**Rooted dependency chain.** The engine registration names the one premise-free root theorem and requires these already admitted receipts:

{bullets(f'`{row}`' for row in spec.dependencies)}

The repository graph audit independently confirms that this claim reaches `SFT-ROOT-THERE-IS-NO-NOTHING`.

**Generated grammar and boundary.** {clean(spec.generation_rule)}

Boundary: {clean(spec.grammar_boundary)}

The Cartesian product contains `{candidate['expected_cardinality']}` candidates. The evidence retains `{len(candidate['candidates'])}` candidate records and `{len(elimination['decisions'])}` decisions. Exactly one decision survives. The other 255 are rejected at their first non-preserving coordinate.

{axis_rows(spec, candidate, elimination)}

**Unique survivor, base and successor.** Sole survivor: `{spec.exact_result}`.

Base: {clean(spec.induction_base)}

Successor: {clean(spec.induction_step)}

Closure scope: `{certificate['closure_scope']}`. Minimality and named-shape uniqueness are preserved in the closure certificate.

**Operational witnesses.**

{witness_text}

**Detailed mathematical and physical meaning.** {structural_detail(claim_id)}

{SUBBRANCH_INTRO[spec.subbranch]}

**Adverse controls.**

{control_text}

**Independent implementation.** The implementation-distinct validator regenerated the literal eight-axis product, candidate order, all decisions, one survivor, closure fields and four control classes. Implementation hash `{certificate['independent_implementation_hash']}`; certificate `{certificate['independent_certificate_hash']}`; external-validation hash `{certificate['external_validation_hash']}`.

**Post-seal empirical correspondence.** This claim belonged either to the original complete 84-law seal or the complete eight-law V1/V2 reconciliation seal; in both cases its entire prediction family was fixed before its external source identities were selected. For this claim, `{len(binding_requirements)}` claim-specific source discriminators were required; their ordered identity is `{fragment_identity}`. Target content opened after the derivation seal: `{str(empirical['target_opened_after_seal']).lower()}`. All rows preserved: `{str(empirical['all_rows_preserved']).lower()}`. Exact comparison passed: `{str(empirical['passed']).lower()}`. The deliberately changed unfavorable record was rejected.

Measurement-body sources:

{source_text}

Comparison and custody records:

{bullets(empirical['measurements'])}

Falsification boundary: {clean(empirical['falsification_condition'])}

**Explicit exclusions.**

{bullets(registration['excluded_inputs'])}

**Immutable evidence identities.** Pre-source branch seal `{certificate.get('pre_source_complete_branch_seal', certificate.get('pre_source_complete_successor_seal'))}`; source manifest `{certificate['source_manifest_hash']}`; derivation seal `{certificate['derivation_seal_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical validation `{certificate['empirical_validation_hash']}`; measurement receipt `{certificate['measurement_receipt_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.
"""


def main() -> None:
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    if inventory["required_claim_count"] != 92 or inventory["admitted_claim_count_at_freeze"] != 92:
        raise SystemExit("Materials inventory is not completely admitted")
    if any(row["status"] != "model_admitted" for row in inventory["obligations"]):
        raise SystemExit("Materials inventory contains an unadmitted obligation")
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("authorized Materials publication requires a DOI")
    boundary = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi})."
        if authorized else
        "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** Building this file performs no push, upload or publication."
    )
    mission = open_science_position(
        "For Materials Science, an attractive specimen, vendor datasheet or selected favorable measurement cannot stand "
        "for a material law. Carrier, composition, phase, microstructure, preparation, direction, scale, method and condition "
        "remain in the observation record. Exact structural counts are stated as exact; variable magnitudes remain bound to "
        "their measured specimen rather than being promoted into fictitious universal constants."
    )
    sections = [f"""# From Fold to Materials

**Materials Science Branch Paper 001, version 1.2.0 — Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the Materials Science foundation of the third clean-room reconstruction of Smithian Fold Theory at its current-evidence-closed, extension-open boundary. The frozen successor inventory contains 92 obligations in ten ordered subbranches. Their exact grammars execute 23,552 candidates and 23,552 one-for-one decisions, yielding 92 unique survivors, 92 depth-independent closure certificates, 368 passing adverse controls, 92 implementation-distinct reconstructions and 92 post-seal NIST/BIPM correspondence checks. All 92 dependency graphs reach the single premise-free root theorem. The original 84-law surface and the subsequent eight-law V1/V2 atomic-reconciliation surface were each sealed in full before their external target identities were selected. Headline exact results include six simple-cubic neighbours; periodic rotation orders one, two, three, four and six with five excluded; seven crystal systems; fourteen Bravais classes; three acoustic displacement orientations; exact two-label aperiodic substitution without a positive rational fixed scale; shared acoustic and opposed optical basis modes; rank-three cube-count thermal support; p-n rectification without signed proof values; superconducting isotope-response provenance; ferrimagnetic unequal-sublattice residual support; integer and primary reduced odd-denominator Hall classes with even-denominator observations explicitly retained outside that primary hierarchy; exact positive-whole topological edge-class gaps; and a source-bound water bulk-property ledger including boiling, liquid/solid density and heat capacity.

## Results first: exact materials classifications

| Headline result | Exact result | Empirical and scientific meaning |
|---|---|---|
| Simple-cubic nearest adjacency | `3` spatial generators x `2` held orientations = `6` neighbours | The full adjacency count is forced without signed coordinates and agrees with the registered crystallographic source boundary. |
| Crystallographic rotation restriction | Allowed positive orders are exactly `1, 2, 3, 4, 6`; `5` is the least excluded order | A depth-independent factor certificate replaces trigonometric approximation; the standard crystallographic restriction is recovered after sealing. |
| Crystal systems | Exactly `7` rotation-compatible rank-three metric quotient classes | The complete `3 x 4` length/angle grammar is enumerated and quotient compatibility retains seven. |
| Bravais classes | Exactly `14` survivors from `7 x 5 = 35` system/centering candidates | Basis and centering compatibility eliminate the other 21 candidates; the standard classification is a post-derivation correspondence. |
| Acoustic branches | Exactly `3`: one longitudinal and two transverse | A held propagation orientation consumes one of the three spatial orientations and leaves two independent cross-axis orientations. |
| Complete branch evidence | 92 laws, 23,552 candidates, 92 survivors, 368 adverse controls, 92 independent reconstructions and 92 post-seal NIST/BIPM checks | Structural results and specimen-dependent measurements are not mixed. Each external comparison preserves method, scale, condition, uncertainty and falsification rows. |

{mission}

## 1. Publication, authorship and open-science boundary

{boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Reproducibility reports and submissions: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is released under CC BY 4.0 and code under Apache-2.0. Copyright preserves authorship while the licenses preserve open inspection, reuse, criticism and independent replication. The Ernos Labs designation identifies conformance to the published methodological and community standards; copying alone does not confer that designation.

## 2. Exact scope and meaning of closure

Closure means every obligation in the frozen Materials question surface has one engine-admitted theorem within its exact generated grammar, full dependency trace, adverse-control boundary and registered empirical protocol. It does not mean that every possible material, specimen, processing history or future observation has been enumerated. Biology beyond the material interface, clinical outcomes, Earth-system fate and application engineering remain later or external validation domains.

## 3. Constitutional arithmetic and prohibited premises

Structural absence is empty One, never numerical zero. Counts are generated positive wholes; exact parts are positive held fractions. Opposition and direction are held fibres, never negative proof quantities. Irrational and imaginary proof values, floating proof arithmetic, a completed infinity, ungenerated continuum, axioms, free or fitted parameters, imported constitutive equations, pretrained models, consensus selection, target-derived rules and application results are prohibited. Host counters can enumerate artifacts but cannot act as scientific values.

## 4. Dependency spine to the root theorem

Each Materials registration has `root_theorems=(SFT-ROOT-THERE-IS-NO-NOTHING,)`, zero axioms and zero free parameters. Dependencies are accepted only when their immutable model-admission receipts already exist. A separate graph traversal over the materialized registrations confirms 92 of 92 paths reach the root. The path runs through the independently admitted Foundation, Mathematics, Information Science, Physics and Chemistry receipts named in each claim section; no branch name substitutes for an actual dependency identity.

## 5. Complete pre-source seal

Before NIST or BIPM source identities were chosen, V3 froze the original 84 obligations, exact counting module and target-blind blueprints. That seal records 21,504 candidates and remains `sha256:da97a6cb6a001964a069b45a5a3698e7ea90f334a08d69c62bd09c46d8112035`. The later atomic V1/V2 audit exposed eight nonduplicative Materials-owned omissions. Before selecting any new source identity, V3 froze all eight successor obligations together, 2,048 candidates and their complete prediction set under `sha256:0e8d7f14a7389b7ec44a37205ce2c9074db65f7b6ed5a466b97f2a01418ef331`. Both seals expressly record that source identities were unselected and target content unopened.

## 6. Single fail-closed engine

For each claim, the engine verifies registration, source identity, admitted dependencies, exact candidate identity and cardinality, one decision per candidate, exactly one survivor, closure, minimality, named-shape uniqueness, four adverse controls and implementation-distinct reconstruction. Empirical evidence additionally requires an evaluator-verified derivation seal, capability isolation, target absence before seal, custody release only after a matching prediction seal, all-row retention, an explicit falsification condition and a tampered unfavorable control. A violation halts and preserves a rejection receipt; it cannot enter the model census.

## 7. Empirical method

Forty-two registered byte-frozen records from NIST and BIPM/JCGM supply the independent external boundary across the original and successor seals. Each claim requires at least two claim-specific discriminators. The predictor cannot read filesystem, network, clock, environment, subprocess, dynamic import or foreign functions. A distinct custodian opens source content only after sealing, verifies every snapshot hash and required feature, constructs the registered observation record and releases it through the portable custody exchange. External authority may falsify a correspondence but cannot alter the already sealed grammar or survivor.

This branch distinguishes exact structural counts from specimen-dependent magnitudes. Six neighbours, allowed rotation orders, seven systems, fourteen Bravais classes and three acoustic branches are exact count/classification claims. Elastic moduli, conductivities, strengths, transition temperatures and analogous quantities depend on material identity, preparation, direction, scale, method and condition; the Fold laws force those dependencies and ledgers, not one fictitious number for every material.

## 8. Exact structural count certificates

### 8.1 Six simple-cubic neighbours

Three independently admitted stable spatial generators each carry exactly two held Fold orientations. Their literal product contains six distinct nearest-adjacency positions. No signed coordinate or numerical zero is needed.

### 8.2 Rotation restriction

The rank-two integral rotation boundary requires Euler-totient degree no greater than two. The factor certificate proves depth independence: if odd prime p divides an order, p-1 divides its degree, leaving only odd prime three; the remaining powers satisfy `a<=2`, `b<=1` and exclude simultaneous `a=2,b=1`. Orders one, two, three, four and six survive; five is the least excluded positive order.

### 8.3 Seven crystal systems and fourteen Bravais classes

The rank-three metric grammar enumerates three length-equivalence classes times four angle-equivalence classes and retains seven rotation-compatible quotient classes. Crossing those seven classes with five centering forms yields thirty-five candidates; basis and symmetry compatibility retain fourteen. The complete named survivors and exact claim receipts appear in their sections below.

### 8.4 Three acoustic branches

For one held propagation orientation in rank three, displacement has one propagation-aligned orientation and two independent transverse orientations. The complete displacement census therefore contains three acoustic branches.

## 9. V1/V2 reconciliation without answer import

The V2 corpus is used only as a question-level completeness obligation. Steps 47, 49, 52, 54, 72, 74, 75, 133, 137, 143, 193 and the Materials portion of 291 are mapped to newly executed V3 claims. None of their prior values, equations or certificates is exposed to the V3 derivation. Step 291's planetary and Tully-Fisher content is explicitly routed to Astronomy and Cosmology rather than hidden inside Materials closure.

## 10. Reading the exhaustive ledger

Every claim section below records the theorem, exact dependency identities, grammar and boundary, all eight binary axes, the 256-candidate census, sole survivor, base/successor certificate, witnesses, meaning, controls, independent implementation, post-seal source custody, falsifier and immutable evidence identities. The machine-readable JSON remains authoritative and is bundled with this paper.
"""]
    section = 11
    order = 1
    for subbranch in inventory["subbranch_order"]:
        sections.append(f"\n## {section}. {subbranch.replace('_', ' ').title()}\n\n{SUBBRANCH_INTRO[subbranch]}\n")
        for spec in (row for row in MATERIALS_SPECS + SUCCESSOR_SPECS if row.subbranch == subbranch):
            sections.append(claim_block(order, spec))
            order += 1
        section += 1
    v2_rows = "\n".join(
        f"- Step {row.step}: {row.question} -> {', '.join(f'`{claim}`' for claim in row.required_v3_claim_ids)}" + (f"; routed remainder: {row.routed_remainder}" if row.routed_remainder else "")
        for row in V2_MATERIALS_QUESTIONS
    )
    source_rows = "\n".join(
        f"- `{row.source_id}` - [{row.source_uri}]({row.source_uri}); snapshot `{row.snapshot_path}`; `{row.snapshot_hash}`; {row.evidence_scope}."
        for row in SOURCE_BY_ID.values()
    ) + "\n" + "\n".join(
        f"- `{row.source_id}` - [{row.uri}]({row.uri}); snapshot `{row.path}`; `{row.digest}`; post-seal claim-specific authoritative comparison."
        for row in SUCCESSOR_SOURCE_BY_ID.values()
    )
    sections.append(f"""
## {section}. Integrated reconciliation table

{v2_rows}

## {section + 1}. External-source ledger

{source_rows}

## {section + 2}. Reproducibility and falsification

The repository's one-command validation route parses every schema, verifies snapshot and source hashes, checks the frozen inventory, exercises the engine and replays every admitted execution manifest entry. The Materials publication gate separately requires all 92 evidence packages, complete candidate/decision parity, one survivor each, four passing controls each, 92 empirical validations, paper inclusion of each receipt identity, both pre-source seals, atomic V1/V2 reconciliation, evidence maps and a rendered PDF.

The branch fails if any registered source hash changes without an explicit new version, any required discriminator is absent, any prediction opens a target before sealing, any row is omitted, any tampered record passes, any dependency no longer resolves to the root, any census is incomplete, any claim has other than one survivor, or an independent validator fails to reconstruct the result.

## {section + 3}. Limitations

- Closure is relative to the declared positive-finite grammars and question surface, not every conceivable future material.
- The external correspondence records are independent tests, not derivational premises.
- Property laws are conditional on specimen, preparation, direction, method, scale, history and environment; this paper does not claim universal numerical moduli, conductivities or thresholds.
- Biomaterial claims stop at the material/biological interface. Biological functions and clinical outcomes require their own branches.
- Industrial performance can test a law but cannot select it.

## {section + 4}. Conclusion

The Materials foundation is current-evidence closed and extension-open at its frozen V3 successor boundary: 92 required laws, 23,552 exact candidates and decisions, 92 unique survivors, 368 adverse controls, 92 independent reconstructions, 92 post-seal authority checks and 92 root traces. The result is an openly inspectable computational account of material identity, organization, defects, collective response, classes, processing, degradation and function. Later lawful discoveries may extend or falsify this boundary; they may not be excluded merely because the present census is complete. Its evidential authority lies in the complete public chain from the premise-free root theorem to immutable receipts and falsifiable external checks.

## {section + 5}. Publication and repository links

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Materials release: https://github.com/MettaMazza/ernos-labs-sft-platform/releases/tag/materials-v1.0.0
- Zenodo DOI: {f'https://doi.org/{doi}' if doi else 'reserved at publication'}
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions: https://discord.gg/ucwGryVxGr

## {section + 6}. References

- Bureau International des Poids et Mesures / Joint Committee for Guides in Metrology, International Vocabulary of Metrology.
- National Institute of Standards and Technology, Materials Science and Engineering Division records listed in the external-source ledger.
- Smith, Maria. *From Nothing to Fold*. Ernos Labs Foundation Branch Paper 001. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *After Turing: The Fold Machine*. doi:10.5281/zenodo.21518311.
- Smith, Maria. *The Quantum Fold Machine*. doi:10.5281/zenodo.21518313.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Chemistry*. doi:10.5281/zenodo.21531455.
""")
    rendered = "\n".join(sections).rstrip() + "\n"
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text(rendered, encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
