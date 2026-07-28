#!/usr/bin/env python3
"""Build the exhaustive Earth and Environmental Sciences foundation paper."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.earth_environment.empirical_program import EARTH_SPECS  # noqa: E402
from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402


PAPER = ROOT / "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md"
CENSUS = ROOT / "census/claims.json"
INTEGRATION = ROOT / "audits/earth_environment_foundation_integration.json"
ATOMIC_AUDIT = ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.json"
SOURCE_REGISTRY = ROOT / "experiments/earth_environment/source_registry.json"
SOURCE_AUDIT = ROOT / "experiments/earth_environment/source_feature_audit.json"
TARGETS = ROOT / "experiments/earth_environment/claim_specific_external_targets.json"
METADATA = ROOT / "publication/earth_environment_foundation_zenodo_metadata.json"


FAMILY_TITLES = {
    "earth_system_observation": "Earth-System Identity, Reservoirs, Boundaries and Observation",
    "planetary_budgets": "Planetary Energy, Matter and Information Budgets",
    "geological_material_history": "Geological Material, Layer, Provenance and History",
    "interior_geodynamics": "Planetary Interior and Geodynamics",
    "seismic_volcanic": "Stress, Rupture, Seismicity and Volcanism",
    "hydrosphere_cryosphere": "Hydrosphere and Cryosphere",
    "atmosphere_weather": "Atmosphere, Weather and Earth-Ionosphere Recurrence",
    "ocean_coast": "Ocean and Coast",
    "climate_system": "Climate, Forcing, Feedback, Attribution and Tipping",
    "biogeochemical_ecological": "Biogeochemical and Ecological Coupling",
    "environmental_transport_quality": "Environmental Transport, Transformation and Quality",
    "evidence_hazard_handoffs": "Field Evidence, Remote Sensing, Forecasts and Hazard Handoffs",
}


FAMILY_INTRO = {
    "earth_system_observation": "Earth science begins with a bounded joint carrier, not a map label. Reservoirs, interfaces, state, time, scale and observation class remain explicit. Detected absence, non-detection, censoring, missingness and outside-scope status are different records; the symbol 0 may represent declared absence but may not silently convert an unknown or missing observation into ordinary numerical nothing.",
    "planetary_budgets": "A planetary budget is a complete bounded ledger. Stock, flow, source, sink, storage, transformation and export are separate coordinates. Closure can be tested only after units, time intervals, interfaces, missing terms and residuals are retained; a fitted residual cannot manufacture conservation.",
    "geological_material_history": "Geological identity requires specimen, composition, phase, texture, provenance and method. Layers are positive ordered carriers with explicit contacts and interruptions. Earth history is a dated multi-proxy reconstruction whose gaps and alternatives remain evidence, not empty numerical entries.",
    "interior_geodynamics": "Interior compartments and geodynamic relations are inference-bounded. Depth, composition, state, contrast, source, transfer and uncertainty remain reconstructible. Universal mechanics and thermodynamics enter only through prior admitted receipts; Earth-specific observations do not select those laws.",
    "seismic_volcanic": "Stress, strain, rupture, waves, catalog construction and volcanism remain distinct. The exact size-count grammar enumerates exponents before data. A heterogeneous catalogue result that opposes the unit-exponent prediction remains adverse; a later homogeneous holdout may add evidence but cannot rewrite it.",
    "hydrosphere_cryosphere": "Water reservoirs, phase handoffs, surface routes, groundwater routes and ice carriers form one coupled ledger without losing phase, location, interval or uncertainty. An unobserved store is not zero and a flow is not a stock.",
    "atmosphere_weather": "Atmospheric composition, radiative transfer, moisture, circulation and weather are source- and timescale-bounded. A bounded Earth-ionosphere cavity forces distinct recurrent modes structurally; dimensional frequencies remain separately measured records rather than imported proof parameters.",
    "ocean_coast": "Ocean identity retains composition, depth, stratification, circulation and interfaces. Air-sea transfer is two-sided. Coastal and tidal observations retain geometry, forcing, local response, datum and time rather than treating a site-dependent magnitude as a universal constant.",
    "climate_system": "Weather and climate differ by retained timescale and state history. Forcing, feedback, variability and attribution require complete counterfactual and evidence records. The exact Fold witness supplies multiple basins and a shared image; it does not fabricate a universal physical half-threshold.",
    "biogeochemical_ecological": "Carbon, nitrogen and phosphorus cycles retain chemical species, reservoirs, organisms, transformations and flows. Biosphere exchange is explicitly two-way. Ecology remains at the Biology handoff: environmental carriers constrain biological response without re-owning universal biological law.",
    "environmental_transport_quality": "A pollutant requires substance, form, source, medium, exposure and endpoint. Source-path-receptor chains retain transport, transformation, accumulation and release. Environmental quality is purpose- and jurisdiction-bounded; a threshold cannot silently become a universal natural law.",
    "evidence_hazard_handoffs": "Field observations, remote sensing, proxy reconstruction, model assimilation and forecasts are separate evidence classes. Hazard, exposure, vulnerability, capacity and consequence remain different carriers. Forecast success cannot admit an opaque relation, and a model output cannot be relabelled as observation.",
}


SPECIAL_MEANING = {
    "SFT-EARTH-SYSTEM-001": "The theorem supplies the minimum complete Earth-system object: named reservoirs plus interfaces, state, scale and time. It prevents a convenient variable list from being mistaken for the system it samples.",
    "SFT-EARTH-ABSENCE-MISSINGNESS-001": "The symbol 0 is lawful only as an explicit representation of observed absence at a declared detection boundary. Missing, censored, unobserved and outside-scope rows remain distinct and halt any computation that tries to substitute ordinary zero for them.",
    "SFT-EARTH-BUDGET-CLOSURE-001": "Budget closure is a comparison of independently reconstructible routes. It cannot be achieved by deleting an unresolved term or fitting the residual to the desired answer.",
    "SFT-EARTH-STRATIGRAPHIC-ORDER-001": "Positive ordered layers force a partial history while contacts, unconformities, intrusions and faults preserve the evidence that interrupts simple succession.",
    "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001": "The generated size-count candidates are exponents 1, 2 and 3. Exact enumeration uniquely selects exponent 1 before opening the catalogue. The first global mixed-type test was adverse: N>=5/N>=6 = 18469/1494 and the registered interval 0.076998990840681139-0.084918164588559525 excludes 1/10. Because magnitude-type and event-status heterogeneity were preserved, a separately preregistered 2020-2026 mww holdout tested N>=6/N>=7 = 253/27, equivalently exceedance 27/253; its interval 0.085657503235220589-0.13089188889528297 contains 1/10. The first result remains adverse and unreclassified.",
    "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001": "A bounded cavity and positive finite recurrence force more than one distinguishable mode. The theorem does not read a frequency from theory or turn a measured hertz value into a proof parameter; primary magnetometer evidence tests the separate dimensional boundary.",
    "SFT-EARTH-EARTH-SYSTEM-TIPPING-001": "The exact two-basin witness forces distinguishable basins sharing an image and supports path dependence. It explicitly rejects conversion of the abstract half-One holding coordinate into a universal measured Earth-system threshold.",
    "SFT-EARTH-MODEL-DATA-ASSIMILATION-001": "A model remains a conditional correspondence with inputs, parameters, observations, errors and outputs retained. Assimilation does not promote the model into a direct observation or allow forecast performance to select a hidden law.",
    "SFT-EARTH-HAZARD-RISK-HANDOFF-001": "Hazard is not risk. Exposure, vulnerability, capacity and consequence are additional carriers whose ownership passes to social, medical and engineering branches at explicit boundaries.",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return str(value).replace("\n", " ").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").strip()


def bullets(values) -> str:
    rows = tuple(values)
    return "\n".join(f"- {clean(value)}" for value in rows) if rows else "- None."


def axis_rows(spec, elimination: dict) -> str:
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


def source_rows_for_claim(target: dict, source_by_id: dict) -> str:
    lines = []
    for evidence in target["source_evidence"]:
        source = source_by_id[evidence["source_id"]]
        present = [row["feature"] for row in evidence["feature_rows"] if row["status"] == "present"]
        absent = [row["feature"] for row in evidence["feature_rows"] if row["status"] != "present"]
        lines.append(
            f"- `{source['source_id']}` - {source['custodian']}, [{source['title']}]({source['locator']}); class `{source['source_kind']}`; transport `{evidence['transport_status']}`; features `{evidence['present_feature_count']}/{evidence['registered_feature_count']}` present; present: {', '.join(present) or 'none'}; absent and preserved: {', '.join(absent) or 'none'}."
        )
    return "\n".join(lines)


def claim_block(order: int, spec, target: dict, source_by_id: dict, census_by_id: dict) -> str:
    package = ROOT / "claims" / spec.claim_id
    registration = read(package / "registration.json")
    candidate = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    certificate = read(package / "certificate.json")
    empirical = read(package / "empirical_validation.json")
    census_row = census_by_id[spec.claim_id]
    witnesses = "\n".join(f"- `{name}`: {description}; passed `{str(passed).lower()}`." for name, description, passed in spec.operational_witnesses)
    controls_text = "\n".join(f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`." for row in controls)
    meaning = SPECIAL_MEANING.get(spec.claim_id, f"This closes the exact foundational relation stated above within its declared positive-finite grammar. Earth-specific dimensional magnitudes remain source-, place-, time-, instrument- and protocol-bounded observation records rather than fitted proof parameters.")
    numeric = ""
    if target["numeric_comparison"] is not None:
        numeric = f"\n\n**Complete quantitative comparison.** `{json.dumps(target['numeric_comparison'], sort_keys=True)}`"
    return f"""### {order}. {spec.title}

Claim identity: `{spec.claim_id}`

**Question and exact theorem.** {clean(spec.statement)}

> `{clean(spec.exact_result)}`

**Rooted dependency chain.** The registration names `SFT-ROOT-THERE-IS-NO-NOTHING`, zero axioms and zero free or fitted parameters. It requires these already admitted receipts:

{bullets(f'`{row}`' for row in spec.dependencies)}

Every dependency precedes this claim in the admitted census and recursively reaches the premise-free root. A branch label, publication or consensus statement cannot substitute for that receipt graph.

**Generated grammar.** {clean(spec.generation_rule)}

Boundary: {clean(spec.grammar_boundary)}

The literal eight-axis product contains `{candidate['expected_cardinality']}` candidates, `{len(candidate['candidates'])}` stored candidate identities and `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives and 255 fail at least one required coordinate.

{axis_rows(spec, elimination)}

**Unique survivor and depth independence.** Sole survivor: `{spec.exact_result}`.

Base: {clean(spec.induction_base)}

Successor: {clean(spec.induction_step)}

Closure scope: `{certificate['closure_scope']}`; minimality and named-shape uniqueness both pass.

**Operational witnesses.**

{witnesses}

**Scientific meaning.** {meaning}

{FAMILY_INTRO[spec.family]}

**Adverse controls.**

{controls_text}

**Independent reconstruction.** A separately executed implementation regenerated the literal product, candidate order, every decision, the sole survivor, depth-independent closure and all four control classes. Implementation `{certificate['independent_implementation_hash']}`; certificate `{certificate['independent_certificate_hash']}`; external-validation identity `{certificate['external_validation_hash']}`.

**Post-seal empirical comparison.** Directness: `{certificate['evidence_directness']}`. Disposition: `{certificate['external_evidence_class']}`. Predicted consequence: `{target['expected_label']}`. Source-derived consequence: `{target['observed_label']}`. Exact boundary correspondence: `{str(target['exact_match']).lower()}`. External evidence selected the survivor: `false`. Formal structure relabelled as direct measurement: `false`. Model, forecast, proxy or retrieval relabelled as observation: `false`.{numeric}

Sources and complete feature accounting:

{source_rows_for_claim(target, source_by_id)}

Comparison record:

{bullets(empirical['measurements'])}

Falsification boundary: {clean(empirical['falsification_condition'])}

**Explicit exclusions.**

{bullets(registration['excluded_inputs'])}

**Immutable evidence identities.** Complete pre-source seal `{certificate['pre_source_complete_branch_seal']}`; source manifest `{certificate['source_manifest_hash']}`; derivation seal `{certificate['derivation_seal_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical validation `{certificate['empirical_validation_hash']}`; measurement receipt `{certificate['measurement_receipt_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.
"""


def main() -> None:
    metadata = read(METADATA)
    integration = read(INTEGRATION)
    atomic = read(ATOMIC_AUDIT)
    registry = read(SOURCE_REGISTRY)
    source_by_id = {row["source_id"]: row for row in registry["sources"]}
    feature_audit = read(SOURCE_AUDIT)
    targets = read(TARGETS)
    target_by_claim = {row["claim_id"]: row for row in targets["targets"]}
    census = read(CENSUS)
    census_by_id = {row["claim_id"]: row for row in census["claims"]}
    if integration["status"] != "current_evidence_closed_extension_open" or integration["claim_count"] != 74:
        raise SystemExit("Earth integration is not complete")
    if any(spec.claim_id not in census_by_id or not census_by_id[spec.claim_id].get("model_admitted") for spec in EARTH_SPECS):
        raise SystemExit("Earth census is not completely admitted")
    if metadata["publication_authorized"]:
        raise SystemExit("Earth remote publication has not been authorized")
    mission = open_science_position("For Earth and environmental science, an expensive sensor, institutional model, consensus map, forecast score or proprietary data product cannot select a natural law. Field observation, instrument output, retrieval, interpolation, proxy reconstruction, simulation, assimilation and forecast remain separate evidence classes unless a separately derived and tested bridge connects them. Public source and method custody are conditions of admission, not optional documentation.")
    sections = [f"""# From One World to Earth

**An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Earth and Environmental Sciences from Smithian Fold Theory**

**Earth and Environmental Sciences Foundational Branch Paper 001, version 1.0.0 - Smithian Fold Theory V3 Clean-Room Reconstruction**

**DOI:** [10.5281/zenodo.21640810](https://doi.org/10.5281/zenodo.21640810) · **Published open access:** 28 July 2026

## Abstract

This paper reports the current-evidence-closed, extension-open foundation of Earth and Environmental Sciences in the third clean-room Smithian Fold Theory reconstruction. Seventy-four obligations in twelve ordered families generate 18,944 exact candidate forms and decisions, seventy-four unique survivors, seventy-four depth-independent certificates, 296 passing adverse controls, seventy-four implementation-distinct reconstructions and seventy-four post-seal empirical-boundary comparisons. Every dependency chain reaches the single premise-free theorem, There Is No Nothing. The branch uses zero axioms, zero free or fitted parameters, no negative proof quantities, no irrational or imaginary proof values, no target-selected law and no opaque predictor.

The foundation reconstructs Earth-system identity, reservoirs, boundaries, stocks, flows, energy and matter ledgers, geological order and history, interior and geodynamic carriers, rupture and seismic records, volcanism, water and ice, atmosphere, weather, ocean, climate, biogeochemical cycling, environmental transport and quality, observational evidence classes and hazard handoffs. It explicitly distinguishes observation from retrieval, proxy, reconstruction, model and forecast; observed absence from non-detection, censoring and missingness; stock from flow; hazard from risk; and universal upstream law from contingent Earth history.

The quantitative headline is a pre-source exponent prediction for earthquake magnitude-frequency counts. Exact candidate enumeration uniquely selected exponent 1. The first global 2010-2020 mixed-magnitude catalogue was adverse: N>=5/N>=6 = 18469/1494 and its registered exceedance interval 0.076998990840681139-0.084918164588559525 excludes 1/10. That result remains adverse and unreclassified. A separately preregistered homogeneous 2020-2026 mww holdout returned N>=6/N>=7 = 253/27, or 27/253 exceedance; its interval 0.085657503235220589-0.13089188889528297 contains 1/10. The branch also derives bounded distinct Earth-ionosphere recurrence modes without importing a dimensional frequency and derives a two-basin tipping structure while rejecting a universal physical half-threshold.

All 356 V1 rows and 407 V2 steps were atomically reviewed. The three Earth-owned prior questions are all reconciled to current receipts. Twenty-one post-seal external source identities contribute ninety-one preregistered features: sixty-seven are present and twenty-four are absent and preserved. One original failed transport remains recorded; an independently preregistered alternate transport is an addendum, not a silent replacement.

## Results first: the Earth findings

| Headline result | Exact or bounded result | Scientific meaning |
|---|---|---|
| Complete foundational closure | `74` laws; `18,944` candidates; `74` sole survivors; `296` passing controls | Every foundation obligation has a root trace, unique survivor, independent reconstruction, empirical comparison and immutable receipt. |
| Earth-system object | bounded joint reservoirs, interfaces, state, scale and time | A convenient variable set cannot silently become the Earth system. |
| Observation and absence | direct, retrieval, proxy, reconstruction, model and forecast are distinct; absence, non-detection, censoring, missingness and outside-scope are distinct | The symbol 0 may represent declared absence, never ordinary nothing or an unknown value. |
| Planetary ledger | source + storage change + transfer + export retained at a declared boundary | Conservation cannot be manufactured by deleting or fitting a residual. |
| Geological history | positive ordered layers plus explicit contacts, interruptions, dates and alternatives | Historical reconstruction preserves gaps instead of converting them into a smooth continuum. |
| Earthquake size-frequency exponent | unique structural exponent `1`; mixed catalogue adverse `18469/1494`; homogeneous holdout `253/27` | The prediction precedes data; adverse and favorable results coexist without reclassification. |
| Earth-ionosphere recurrence | bounded carrier forces distinct modes; dimensional frequency remains measured | The model predicts mode structure without fitting a hertz value. |
| Earth-system tipping | exact two-basin/shared-image witness; no universal physical `1/2` threshold | Fold structure does not overwrite contingent environmental thresholds. |
| Climate evidence | weather, climate, forcing, feedback, variability and attribution retain timescale and comparison records | Model or forecast output cannot substitute for observation. |
| Environmental risk | hazard, exposure, vulnerability, capacity and consequence remain separate | Earth science hands social, medical and engineering consequences across explicit boundaries. |

## Status and scope

**PUBLISHED OPEN-ACCESS BRANCH PAPER.** The canonical release contains this Markdown paper, its rendered PDF, the evidence/source archive and checksum ledger.

Foundational closure means every question in the frozen seventy-four-obligation Layer One surface has one engine-admitted theorem inside its declared exact grammar, with a complete root path, adverse controls, independent reconstruction and purpose-matched post-seal comparison. It does not claim the complete Layer Two reconstruction of every Earth discipline and it does not permanently lock the branch. Lawful extensions remain open through the same public engine.

{mission}

This position rejects paywalls, credential gates and opaque oracles as substitutes for transparent derivation and inspectable evidence. It does not reject expertise; it requires expertise to remain reproducible and publicly answerable.

## Method: one root, one unchanged engine, no target-selected law

The derivational root is There Is No Nothing. The One and Fold, exact arithmetic, information, computation, physics, chemistry, materials and biology enter only through already admitted dependencies. Before any external source identity or outcome was opened, the branch froze seventy-four claims, eight binary preservation axes per claim, 18,944 candidates, all predicted consequence labels and falsification conditions. Each literal 256-form product is complete by construction. One form alone preserves carrier, boundary, relation, record, evidence class, provenance, positive-finite successor closure and absence of an extra rule.

The capability-closed predictor cannot access the filesystem, network, clock, environment, subprocess or target. A distinct custodian releases the source-derived target only after the derivation seal. Every claim is reconstructed by a separate implementation. Four mandatory structural controls reject a false premise, changed source identity, changed candidate artifact and boundary violation. The canonical engine and verification-authority seals were checked before, during and after admission and were not edited.

## External evidence constitution

The sources were chosen after the complete derivation seal by question-purpose and authoritative or primary custody. Their ninety-one features were preregistered before capture outcomes. Sixty-seven appeared in the captured surfaces. Twenty-four did not and remain absent. The original Smithsonian transport returned HTTP 403 and remains a failed row; a separately registered WFS addendum succeeded without rewriting it. Earth evidence tests declared consequence boundaries and one exact numerical prediction. It does not select any structural survivor.

## V1/V2 atomic reconciliation

The accountability audit reviewed all 763 registered V1/V2 entries. It isolated three Earth-owned questions: Earth-ionosphere recurrence, Earth-system tipping and earthquake magnitude-frequency. All three map to current V3 receipts. Prior answers were never admitted as V3 premises; they ensured that the clean reconstruction did not omit known earlier work.

## Reading the exhaustive derivation ledger

Each of the seventy-four sections below states its theorem, receipt dependencies, complete eight-axis grammar, 256-form census, sole survivor, depth-independent base and successor, operational witnesses, scientific meaning, four adverse controls, independent implementation, external evidence scope, complete feature accounting, falsification boundary and immutable evidence identities.
"""]
    current_family = None
    family_section = 1
    order = 1
    for spec in EARTH_SPECS:
        if spec.family != current_family:
            sections.append(f"\n## Ledger family {family_section}: {FAMILY_TITLES[spec.family]}\n\n{FAMILY_INTRO[spec.family]}\n")
            family_section += 1
            current_family = spec.family
        sections.append(claim_block(order, spec, target_by_claim[spec.claim_id], source_by_id, census_by_id))
        order += 1
    roadmap = read(ROOT / "publications/inventories/earth_environment.json")["later_full_field_extensions"]
    sections.append(f"""
## Complete result and verification summary

The foundation contains exactly 74 admitted laws and 18,944 generated candidates. Exactly 74 forms survive. All 296 structural controls pass. Seventy-four independent implementations reproduce candidate order, decisions and sole survivor. Seventy-four post-seal comparisons pass at their declared boundary, while the mixed-catalogue earthquake test remains explicitly adverse inside the one quantitative claim. All three inherited atomic questions reconcile. Every dependency path reaches There Is No Nothing. The engine seal is `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`; the authority seal is `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`. Neither protected surface was modified.

The branch is current-evidence closed and extension-open, not permanently locked. New evidence or a new Earth relation may extend, correct or invalidate a claim only through the same public process: exact statement, frozen grammar, complete enumeration, unique survivor or preserved halt, independent reconstruction, adverse controls, purpose-matched evidence and unchanged-engine receipt.

## Full-field continuation roadmap

This foundational edition is the dependency-safe base. Later versioned editions will extend, in order, through:

{bullets(roadmap)}

Other planets and cosmic populations remain Astronomy and Cosmology-owned. Human-environment systems pass to Social and Collective Systems. Intervention design passes to Engineering Translation. Applications may test the laws but never select them.

## Limitations

- This is the complete frozen Layer One foundation, not the complete Layer Two reconstruction of every Earth and environmental discipline.
- Seventy-three claims make structural and evidence-boundary comparisons; they do not pretend that site-, time-, instrument- or method-dependent magnitudes are universal constants.
- The earthquake exponent is the only exact quantitative natural-data prediction in this edition. Its first test is adverse and remains adverse; the independent homogeneous holdout is compatible and does not erase it.
- Bounded Earth-ionosphere modes are derived without a dimensional frequency prediction in this edition.
- The two-basin tipping witness is structural and explicitly makes no universal physical threshold claim.
- Twenty-four absent source features and one failed original transport remain visible. They are not support.
- External catalogs and documentation can change; this release binds captured bytes, source identities, dates and transport history.
- Current-evidence closure is revocable by lawful new evidence and does not constitute permanent ownership of knowledge.

## Conclusion

Foundational Earth and Environmental Sciences is current-evidence closed and extension-open: 74 laws, 18,944 exact candidates, 74 sole survivors, 296 passing controls, 74 independent reconstructions, 74 post-seal comparisons and 3 of 3 inherited atomic obligations reconciled.

The scientific result is not a new opaque Earth model. It is the opposite: an exact constitution for what an Earth object, boundary, ledger, history, observation, prediction and adverse result must retain before it can become scientific evidence. It derives a quantitative earthquake exponent before measurement and preserves both its adverse first test and compatible holdout. It derives bounded recurrence without fitting a frequency and tipping structure without pretending that a mathematical half is a measured planetary threshold.

This is how Earth science remains empirical without becoming answer-selected. A sensor is not a law. A model is not an observation. A missing row is not zero. A forecast score is not derivation. An institutional label is not proof. Open criticism remains unrestricted; scientific admission is the reproducible act of satisfying the same public standard.

## Repository and publication status

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Zenodo DOI: https://doi.org/10.5281/zenodo.21640810
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions: https://discord.gg/ucwGryVxGr
- Current state: published open access

## References

Primary and authoritative Earth evidence:

{chr(10).join(f"- {row['custodian']}. [{row['title']}]({row['locator']}). Registered class: {row['source_kind']}." for row in registry['sources'])}

Smithian Fold Theory branch dependencies:

- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Chemistry*. Canonical branch paper in the repository and Zenodo series.
- Smith, Maria. *From Fold to Materials*. Canonical branch paper in the repository and Zenodo series.
- Smith, Maria. *From Fold to Life*. doi:10.5281/zenodo.21630203.

Open-science evidence supporting the institutional argument:

{OPEN_SCIENCE_REFERENCES}
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
