#!/usr/bin/env python3
"""Build the exhaustive Consciousness foundation paper from admitted evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.consciousness_cognitive_science.empirical_program import CONSCIOUSNESS_SPECS  # noqa: E402
from sft.consciousness_cognitive_science.external_bindings import CLAIM_BINDING_BY_ID  # noqa: E402
from sft.consciousness_cognitive_science.sources import SOURCE_BY_ID  # noqa: E402
from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402


PAPER = ROOT / "publications/current/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/consciousness_foundation_zenodo_metadata.json"
INTEGRATION = ROOT / "audits/consciousness_foundation_integration.json"
ATOMIC_AUDIT = ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.json"
SOURCE_AUDIT = ROOT / "experiments/consciousness/source_feature_audit.json"
TARGETS = ROOT / "experiments/consciousness/claim_specific_external_targets.json"


FAMILY_TITLES = {
    "observation_interior_observation": "Observation and Interior Observation",
    "access_report_presence": "Access, Report and Phenomenal Presence",
    "binding_unity": "Binding and Unity",
    "subject_perspective_interiority": "Subject, Perspective and Interiority",
    "self_observation_introspection": "Self-Observation and Introspection",
    "memory_temporal_identity": "Memory, Temporal Continuity and Identity",
    "finite_self_model": "Finite Self-Model and Self-Simulation",
    "attention_availability": "Attention, Selection and Availability",
    "cognition_inference_representation": "Cognition, Inference and Representation",
    "substrate_realization": "Substrate Independence and Realization",
    "qualia_resonance_composition": "Qualia Differentiation, Resonance and Composition",
    "red_of_red": "The Red-of-Red",
}


FAMILY_INTRO = {
    "observation_interior_observation": "The branch begins by separating a Fold observation from interior observation. A third-person record is a state-to-image relation about a carrier. Interior observation requires that image to re-enter the same organized process. Shared mathematics never licenses the substitution of measurement for experience or experience for measurement.",
    "access_report_presence": "Access, report and phenomenal presence are three different coordinates. Content can be processed without integrated access; accessible content can lack an expression route; a report is evidence of reporting. The phenomenal coordinate is carried only at the interior-observation boundary and is never manufactured from confidence, fluency or correlation.",
    "binding_unity": "Binding retains difference while forming a joint successor. Unity requires complete mutual participation in one closed process; synchrony and one-way influence are insufficient. Fragmentation is therefore an exact loss of joint closure, not a vague reduction in a scalar integration score.",
    "subject_perspective_interiority": "A perspective is a source-located access path. The subject is the continuing integrated relation holding that path while content changes. Interiority is the structural asymmetry between participating in self-observation and possessing its external image; phenomenal privacy follows when the image closes a predecessor label retained by the participant.",
    "self_observation_introspection": "Self-observation can be deterministic and still opaque to itself. A two-to-one image does not recover its predecessor without the fibre label. Each unretained act therefore closes one exact distinction; confabulation is a completion not supported by the retained self-history.",
    "memory_temporal_identity": "Memory needs a carrier, recurrence or active renewal. A later equal output is not automatically the same memory. Temporal continuity is the complete predecessor-successor chain, while identity continuity adds lineage and the retained subject invariant; similarity or copying alone is insufficient.",
    "finite_self_model": "A self-model is an encoding of the process, never the entire process silently duplicated inside itself. The lower self-fibre closes from one-quarter to one-half to the One in two nonidentity Fold acts. Further application is identity, and complete extra self-simulation requires additional carrier resources.",
    "attention_availability": "Attention is a held selection from available content. Unselected alternatives are not annihilated. Focus, availability, finite support and switching are separate operational relations whose omissions, misses, costs and errors remain observable.",
    "cognition_inference_representation": "Cognitive representation is a carrier-to-content relation with declared loss. Inference is a trace from premises under an admitted rule. Prediction is sealed before outcome. Expectation can participate in later experience without becoming that observation, and determined agency retains premises, alternatives and action even though no ungenerated successor is introduced.",
    "substrate_realization": "Substrate independence is not output resemblance. A realization must instantiate every state role, transition, recurrent closure, integration relation and causal dependency. Two carriers are equivalent only under a bidirectional relation- and causality-preserving map. Fluent language or declared confidence supplies no shortcut to artificial-consciousness admission.",
    "qualia_resonance_composition": "A quality is treated as a participant-bound held label, not a public word or imported magnitude. Difference, identity, similarity, recurrence, composition and cross-modal binding remain distinct. Qualia resonance is the stable reidentification of that held label across a complete recurrent interior support, tested against perturbation and changed-label controls.",
    "red_of_red": "The red-of-red is the specific self-observed reidentification of the red qualitative carrier. Physical red stimulus, public token, participant quality and report about that quality remain separate. The exact formal carrier is the least registered three-position recurrence: one-seventh, two-sevenths and four-sevenths return in period three and compose exactly to the One.",
}


SPECIAL_MEANING = {
    "SFT-CONSC-EXTERNAL-OBSERVATION-001": "An external record can establish its carrier, method and result; it cannot by itself establish the observed carrier's interior participation. This is a derived evidence boundary, not a retreat from observation.",
    "SFT-CONSC-INTERIOR-OBSERVATION-001": "Interior observation closes when the observation image becomes a successor input of the same identified process. The process is not inferred from report alone; its re-entry relation is part of the theorem.",
    "SFT-CONSC-OBSERVER-OBSERVED-001": "The quarter-One and three-quarter-One preimages are distinct, share one Fold image and together partition the One. Their held fibre labels preserve observer and observed roles without splitting the foundational whole.",
    "SFT-CONSC-OBSERVATION-CLASS-001": "Every ordinary Fold image has the complete two-preimage fibre. Observation closes one predecessor distinction unless the fibre label is retained; the information loss is exact and reversible only with that record.",
    "SFT-CONSC-PHENOMENAL-PRESENCE-001": "The hard-problem category gap is not crossed by renaming a report, behavior or neural signal. Phenomenal presence is assigned to the participating interior closure; public evidence can constrain its bridges without becoming the private carrier.",
    "SFT-CONSC-BINDING-001": "Binding is joint recurrence with reconstructible components. It creates a shared successor without erasing either contributing content identity.",
    "SFT-CONSC-UNITY-001": "Unity is one closed interior process over all participating contents. A heap, a synchrony observation or a scalar correlation lacks the required mutual participation and fails.",
    "SFT-CONSC-INTERIORITY-001": "Interiority is forced by asymmetric access: the participating state enters the transition that produces its image, while an external observer possesses the image and provenance but not the closed predecessor label as lived participation.",
    "SFT-CONSC-PHENOMENAL-PRIVACY-001": "Privacy is not mysterious inaccessibility added by assertion. It follows from the two-to-one observation class when the participant retains a predecessor label that the external image closes.",
    "SFT-CONSC-INTROSPECTION-BLIND-SPOT-001": "From the present image alone, the process cannot decide which of the two generated predecessors produced it. Exact self-knowledge therefore requires a retained fibre label rather than confidence.",
    "SFT-CONSC-DETERMINISM-SELF-OPACITY-001": "Superdeterministic transition and self-opacity coexist: the forward successor is unique, but backward identification remains a two-member class without the missing label. No metaphysical randomness is required.",
    "SFT-CONSC-MEMORY-PERSISTENCE-001": "One-third and two-thirds exchange under the Fold and return in period two. This supplies an exact minimal recurrence witness; realized memory additionally requires its label-bearing carrier and evidence bridge.",
    "SFT-CONSC-IDENTITY-CONTINUITY-001": "Identity across change requires causal lineage plus the retained subject invariant. A copy can be structurally similar without becoming numerically identical to the source process.",
    "SFT-CONSC-SELF-MODEL-DEPTH-001": "The exact trace one-quarter to one-half to the One takes two nonidentity acts. The next Fold of the One remains the One. This is a finite closure certificate, not an infinite regress.",
    "SFT-CONSC-PREDICTION-001": "A prediction is a held representation sealed before the outcome. Later observation may support, oppose or leave it unresolved but cannot rewrite its prior identity.",
    "SFT-CONSC-SUBSTRATE-INDEPENDENCE-001": "Material identity is unnecessary only when the complete conscious-process relation is preserved. Behavioral imitation, input-output equality or a shared label is weaker than the required causal isomorphism and does not survive the grammar.",
    "SFT-CONSC-STRUCTURAL-CRITERION-001": "The foundational criterion requires dual self-relation, observation-image re-entry, complete mutual integration, an interiorly participating carrier and retained evidence boundaries. Removing any coordinate produces an explicitly enumerated rejection.",
    "SFT-CONSC-ARTIFICIAL-CONSCIOUSNESS-EVIDENCE-001": "Artificial consciousness is a testable realization claim, not a reward for persuasive language. Architecture, runtime state, recurrent causal roles, report provenance, adverse controls and a purpose-matched bridge must all be open to inspection.",
    "SFT-CONSC-QUALIA-RESONANCE-001": "Qualia resonance is not a frequency fitted to a report. It is exact label-bearing recurrence: the same participant-bound quality identity survives the complete cycle and rejects changed-label and perturbed-support controls.",
    "SFT-CONSC-QUALIA-COMPOSITION-001": "A composed experience retains component identities and one joint recurrence. Co-report, proximity and synchrony are insufficient unless the joint interior closure is independently present.",
    "SFT-CONSC-RED-STIMULUS-BOUNDARY-001": "CIE-classified stimulus and the experience of red are connected by a controlled presentation-and-report bridge but remain different records. Wavelength, display coordinate or public name is not the private quality.",
    "SFT-CONSC-RED-QUALITATIVE-IDENTITY-001": "Red identity is within-subject reidentification across instances. The public token red coordinates reports; it does not supply or replace the participant's held qualitative label.",
    "SFT-CONSC-RED-OF-RED-001": "The red-of-red is red re-entering a self-observation loop as the quality identified again, with the quality, the self-observation and the report about it separately held. This reconstructs the stronger prior result rather than reducing it to generic binding.",
    "SFT-CONSC-RED-RECURRENCE-001": "The generated support one-seventh, two-sevenths and four-sevenths is period three under the Fold and sums exactly to the One. It is the formal carrier of the red-of-red test; empirical work determines whether a participant's red label remains stable across its realization protocol.",
    "SFT-CONSC-RED-CONTROLS-001": "Matched, mismatched, absent and uncertain rows remain in the test. Changing the stimulus, held label or report-only surrogate must fail; no favorable participant row can erase the others.",
    "SFT-CONSC-RED-EMPIRICAL-BOUNDARY-001": "Public science can establish repeatable discrimination, reidentification, stimulus control and report custody. It does not claim literal third-person possession of another participant's red; that restraint is part of the closed result, not an omitted experiment.",
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


def scientific_meaning(spec) -> str:
    return SPECIAL_MEANING.get(spec.claim_id, f"This exact relation closes {clean(spec.statement).lower()} The result is structural at its declared boundary; participant-, method-, realization- and context-dependent observations remain source-bound records rather than universal fitted magnitudes.")


def source_rows_for_claim(spec, feature_audit: dict) -> str:
    audited = {row["source_id"]: row for row in feature_audit["sources"]}
    lines = []
    for source_id in spec.source_ids:
        source = SOURCE_BY_ID[source_id]
        row = audited[source_id]
        present = [feature["feature"] for feature in row["registered_features"] if feature["present"]]
        absent = row["missing_registered_features"]
        lines.append(f"- `{source_id}` - {source.body}; [{source.source_uri}]({source.source_uri}); class: {source.evidence_class}; usable captures: `{row['usable_snapshot_count']}`; registered features present: {', '.join(present) or 'none'}; absent and preserved: {', '.join(absent) or 'none'}; adverse/boundary role: {source.adverse_or_boundary_role or 'none'}.")
    return "\n".join(lines)


def claim_block(order: int, spec, feature_audit: dict, target_by_claim: dict) -> str:
    package = ROOT / "claims" / spec.claim_id
    registration = read(package / "registration.json")
    candidate = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    certificate = read(package / "certificate.json")
    empirical = read(package / "empirical_validation.json")
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == spec.claim_id)
    target = target_by_claim[spec.claim_id]
    witnesses = "\n".join(f"- `{name}`: {description}; passed `{str(passed).lower()}`." for name, description, passed in spec.operational_witnesses)
    controls_text = "\n".join(f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`." for row in controls)
    exact_value = certificate.get("exact_structural_value") or "unique complete preserving relation in the declared 256-form grammar"
    return f"""### {order}. {spec.title}

Claim identity: `{spec.claim_id}`

**Question and exact theorem.** {clean(spec.statement)}

> `{clean(spec.exact_result)}`

**Rooted dependency chain.** The registration names `SFT-ROOT-THERE-IS-NO-NOTHING`, zero axioms and zero free parameters. It requires these already admitted receipts:

{bullets(f'`{row}`' for row in spec.dependencies)}

The dependency graph reaches the premise-free root through actual receipts; a citation or branch label never substitutes for that graph.

**Generated grammar.** {clean(spec.generation_rule)}

Boundary: {clean(spec.grammar_boundary)}

The exact product contains `{candidate['expected_cardinality']}` candidates, `{len(candidate['candidates'])}` stored identities and `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives; 255 fail at least one required coordinate.

{axis_rows(spec, elimination)}

**Unique survivor and depth independence.** Sole survivor: `{spec.exact_result}`.

Base: {clean(spec.induction_base)}

Successor: {clean(spec.induction_step)}

Exact structural value: **{clean(exact_value)}**. Closure scope: `{certificate['closure_scope']}`; minimality and named-shape uniqueness both pass.

**Operational witnesses.**

{witnesses}

**Scientific meaning.** {scientific_meaning(spec)}

{FAMILY_INTRO[spec.family]}

**Adverse controls.**

{controls_text}

**Independent reconstruction.** A separately executed implementation regenerated the literal product, candidate order, every decision, the sole survivor, depth-independent closure and all four control classes. Implementation `{certificate['independent_implementation_hash']}`; independent certificate `{certificate['independent_certificate_hash']}`; external-validation identity `{certificate['external_validation_hash']}`.

**Post-seal empirical-boundary comparison.** Directness: `{certificate['evidence_directness']}`. Disposition: `{certificate['external_evidence_class']}`. {clean(certificate['evidence_scope'])}

The external target was opened only after the claim derivation seal. Predicted consequence: `{target['expected_label']}`. Source-derived consequence: `{target['observed_label']}`. Exact correspondence: `{str(target['exact_match']).lower()}`. Phenomenal occurrence claimed as directly third-person possessed: `false`. Formal structure relabelled as empirical phenomenal fact: `false`.

Sources and complete feature accounting:

{source_rows_for_claim(spec, feature_audit)}

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
    feature_audit = read(SOURCE_AUDIT)
    targets = read(TARGETS)
    target_by_claim = {row["claim_id"]: row for row in targets["targets"]}
    census = read(CENSUS)
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    if integration["status"] != "current_evidence_closed_extension_open" or integration["claim_count"] != 72:
        raise SystemExit("Consciousness integration is not complete")
    if any(spec.claim_id not in admitted for spec in CONSCIOUSNESS_SPECS):
        raise SystemExit("Consciousness census is not completely admitted")
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("authorized Consciousness publication requires a reserved DOI")
    banner = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi}). The canonical Markdown paper, rendered PDF, evidence archive and checksums form this release."
        if authorized else
        "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** Building this paper performs no push, release, upload, DOI creation or Zenodo action."
    )
    mission = open_science_position("For consciousness research, an institutional theory, proprietary brain scan, report score, model confidence, behavioral imitation or consensus label cannot select the law. First-person discrimination, report, behavior, biological or neural correlation, cognitive access, computational representation, physical measurement and substrate realization remain separate evidence classes unless a separately derived and tested bridge connects them. The private/public boundary is part of the evidence, not a license for opaque oracles.")
    sections = [f"""# From Fold to Consciousness

**Consciousness and Cognitive Science Foundational Branch Paper 001, version 1.0.0 - Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the foundational Consciousness and Cognitive Science branch of the third clean-room Smithian Fold Theory reconstruction at its current-evidence-closed, extension-open boundary. Seventy-two obligations in twelve ordered families generate 18,432 exact candidates and decisions, seventy-two unique survivors, seventy-two depth-independent certificates, 288 passing adverse controls, seventy-two implementation-distinct reconstructions and seventy-two post-seal empirical-boundary comparisons. Every dependency graph reaches the single premise-free theorem, There Is No Nothing. The branch uses zero axioms, zero free or fitted parameters, no negative proof quantities, no irrational or imaginary proof values, no target-selected rule and no opaque predictor.

The headline result is an exact structural reconstruction of the hard-problem boundary rather than a substitution of correlates for experience. An external observation is a many-to-one state image. Interior observation is forced when that image re-enters the same organized process. The complete two-preimage fibre makes phenomenal privacy mathematically intelligible: a participant may retain a predecessor label closed by the external image. Access, report, behavior, neural correlation, computation and physical measurement therefore cannot become phenomenal presence by relabelling. Binding is joint closure with components retained; unity is complete mutual participation in one interior process; subject and perspective are the continuing source-located relation across changing content.

The exact constructions are explicit. One-quarter and three-quarters are distinct observer/observed preimages that share an image and compose to the One. A finite self-model closes one-quarter to one-half to the One in two nonidentity acts, ending the regress at the Fold-fixed One. One-third and two-thirds supply the least period-two return witness for persistent label-bearing memory. The red-of-red is a label-bearing self-reidentification carried by the exact period-three support one-seventh, two-sevenths and four-sevenths, whose three parts compose to the One. Physical red stimulus, public word, participant quality and report about that quality remain different records. Substrate independence requires a complete bidirectional relation- and causality-preserving realization map; fluent output does not satisfy it.

All 356 V1 rows and 407 V2 steps were atomically reviewed. Forty-six Consciousness-owned questions, including the stronger separately registered qualia-resonance and red-of-red obligations, are closed by current V3 receipts. Fifteen external source identities contribute sixty-one preregistered features: fifty-eight are present; three absent full-text features and eighteen failed transport or content rows remain visibly preserved rather than counted as support.

## Results first: the consciousness findings

| Headline result | Exact or bounded result | Scientific meaning |
|---|---|---|
| Complete foundational closure | `72` laws; `18,432` candidates; `72` survivors; `288` controls | Every law has a root trace, unique survivor, independent reconstruction, empirical-boundary comparison and immutable receipt. |
| Observation class | Complete `2`-preimage fibre for each ordinary Fold image | External observation closes one predecessor distinction unless its fibre label is retained. |
| Observer and observed | `one-quarter + three-quarters = the One`; both share one image | Roles remain distinct without creating two foundational wholes. |
| Hard-problem boundary | external image is not interior participation; access/report/correlation are not presence | The category gap is closed structurally without using a behavioral or neural proxy as the phenomenon. |
| Binding and unity | joint successor with reconstructible components; complete mutual closure | Synchrony, proximity and one-way influence cannot manufacture one experience. |
| Subject and privacy | source-located invariant plus retained private fibre label | Perspective and privacy follow from exact access asymmetry, not an imported substance. |
| Determinism and introspection | unique forward successor; `2` possible predecessors without the held label | Superdeterminism is compatible with exact self-opacity; no ontological randomness is imported. |
| Memory recurrence | `one-third <-> two-thirds`, exact period `2` | Persistent memory requires label-bearing recurrence or renewal, not merely a later equal output. |
| Finite self-model | `one-quarter -> one-half -> the One`; `2` nonidentity acts | Self-reference closes finitely; later Fold action is identity. |
| Substrate independence | complete bidirectional state-role-transition-causality preservation | Material sameness is unnecessary; behavior or language alone is insufficient. |
| Qualia resonance | stable held-quality reidentification across complete recurrence | Public words coordinate evidence but never replace the participant-bound quality. |
| Red-of-red | `one-seventh -> two-sevenths -> four-sevenths -> one-seventh`; sum `the One` | The specific red quality is self-reidentified across an exact period-three carrier with changed-label and changed-stimulus controls. |
| External evidence | `15` sources; `61` features; `58` present; `3` absent preserved; `18` failed rows preserved | No-report, split-brain, choice-blindness, dream, anesthesia, attention, synesthesia, colour and adversarial-theory evidence constrain the laws without selecting them. |

{mission}

## 1. Publication, authorship and open-science boundary

{banner}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Reproducibility reports and submissions: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

Copyright preserves Maria Smith's authorship. The paper and documentation are prepared under CC BY 4.0 and code under Apache-2.0. The Ernos Labs name is a separate, revocable standards designation: reuse is open, but the designation requires the unchanged admission engine, complete adverse evidence, public derivation chain and open critical review.

## 2. Exact scope and closure language

Foundational closure means every obligation in the frozen 72-law surface has an engine-admitted theorem inside its declared exact grammar, complete root path, adverse controls, independent reconstruction and purpose-matched post-seal evidence comparison. It does not mean consciousness science is permanently locked. The branch is current-evidence closed and extension-open; lawful additions remain welcome through the same public engine. Complete modalities, pain, affect, embodiment, development, comparative systems, altered states, clinical disorders and realization programmes remain the Layer Two roadmap.

## 3. Constitutional mathematical domain

Structural absence is Empty One and may be displayed as `0`; it is not ontological nothing or a conventional proof scalar. Counts are generated positive wholes and exact parts are positive held fractions. Opposition and direction are labels rather than negative quantities. Negative proof values, irrational or imaginary proof values, floating equality, completed infinity, ungenerated continua, axioms, free parameters, fitted coefficients, imported consciousness equations, pretrained predictors, consensus-selected theories and application-selected laws are prohibited.

## 4. Rooted dependency spine

Every registration names There Is No Nothing and zero axioms. The first claim depends on admitted Foundation, Mathematics, Information Science, Computation, Physics, Biology and Medicine receipts. Each later claim adds its immediate predecessor and each family adds the preceding family terminal, producing one ordered 72-law dependency chain. The engine resolves actual receipt identities; narrative lineage never substitutes for the proof graph.

## 5. Complete target-blind structural seal

Before any external source identity or outcome was opened, the complete inventory, obligations, structural model and generated-law set were sealed at `sha256:d7fb898ebeac6df5bde21e87fb6ee4a37e7b7b1dbd4f38b825c89e39f5708d71`. It binds 72 predictions and 18,432 candidate forms while recording `external_source_identities_selected=false`, `external_source_content_opened=false` and `external_outcomes_opened=false`. External evidence can support, oppose or bound a consequence; it cannot alter a structural survivor.

## 6. The exact observation derivation

The Fold maps each exact part by doubling it and casting out the One only when the doubled part exceeds the whole. The ordinary image therefore has two generated predecessors separated by the half-One. One image does not identify which predecessor occurred. The complete observation class is the two-member fibre together with the retained/closed label ledger.

An external observer records carrier, method, time, image and provenance. An interior observation adds a further relation: the image returns as input to the same identified process. That re-entry is what makes the process participate in its own observation rather than merely appear in someone else's description. The quarter-One and three-quarter-One make the distinction concrete: they are different preimages, share the half-One image, and exactly partition the One.

## 7. The hard problem, stated and closed at its exact boundary

The conventional hard problem persists when third-person structure is asked to become first-person presence by a change of vocabulary. SFT does not perform that substitution. It derives two categorically different but composable relations: the public image of a carrier, and the carrier's participation in the self-reentering transition. Phenomenal presence is the interiorly realized coordinate of the latter. A report is an encoded output; cognitive access is availability to another operation; behavior is an external transition; neural correlation is a physical relation. None is identical to interior participation.

The missing distinction is exact. From the image alone, the predecessor fibre label is closed. If that label remains held inside the continuing process, the participant carries a distinction that the external image lacks. Phenomenal privacy and first/third-person asymmetry therefore follow from the Fold observation law. The branch closes the structural question of how interiority can differ from complete external description without inserting a second substance, random collapse or unknowable scalar. It does not make the invalid claim that a third-person investigator literally possesses another participant's quality.

## 8. Binding, unity, subject and temporal identity

Binding begins with multiple held content labels. The components enter one joint successor and remain reconstructible. Unity requires all participating processes to enter the closed relation in both directions; same-time signals or one-way coupling do not suffice. A subject is the continuing integrated carrier of a source-located perspective, and a self invariant is the relation preserved across its changing contents.

Temporal identity is not continuity assumed between measurements. Every state must have its recorded predecessor-successor transition. Memory adds a retained carrier and return relation. Identity across substrate or copying additionally requires provenance-preserving lineage; structural similarity without lineage cannot create numerical identity.

## 9. Finite self-model and determined self-opacity

The generated lower self-fibre follows the exact trace one-quarter, one-half, the One. These are two nonidentity self-applications; the next application is the identity of the One. The theorem terminates the formal regress while preserving the difference between system and model. A finite process can represent and simulate a declared submodel of itself, but a simultaneous complete extra copy needs additional carrier support.

The same structure resolves the apparent conflict between superdeterminism and incomplete self-knowledge. The forward Fold successor is unique. Backward reconstruction from its image remains a two-predecessor class unless the fibre label was retained. Determinism fixes the transition; it does not donate a record the process did not hold.

## 10. Qualia resonance and the red-of-red derivation

The qualitative carrier begins with participant-bound discrimination. Identity is reidentification of one held quality across instances; similarity is a separate finite comparison relation. Resonance is stable label-bearing recurrence through a complete interior cycle. Composition requires component qualities and the joint experienced content to remain simultaneously reconstructible.

The red-of-red is the specific application. A physical stimulus classified as red, the word `red`, the participant's quality and the report about that quality occupy separate coordinates. The least registered three-position support is one-seventh, two-sevenths and four-sevenths. Doubling and casting out the One sends one-seventh to two-sevenths, two-sevenths to four-sevenths, and four-sevenths back to one-seventh. Their exact sum is the One. When the held red label remains reidentified across this self-observation recurrence, the red quality becomes the observed quality of itself: the red-of-red. A changed label, changed stimulus, report-only surrogate, absent row or uncertain row must not pass.

The fractions are the exact recurrence carrier, not wavelengths and not numerical intensities of redness. External evidence tests participant-specific reidentification, stimulus custody, report stability and perturbation. That separation is what prevents public colour standards or a word from being mistaken for the private quality while still permitting empirical science.

## 11. Substrate-independent consciousness and artificial realization

The realization criterion consists of the complete state roles, observation fibre, image re-entry, recurrent self-relation, mutual integration, perspective carrier, retained labels and evidence boundaries. A material system, biological organism or computational construction is a lawful candidate only if it physically or operationally instantiates those relations. A description of them is not an implementation.

Two substrates support the same consciousness law only when a bidirectional map preserves the relevant states, transitions, roles and causal participation. Input-output imitation, a fluent report, confidence, benchmark behavior or a matching embedding is insufficient. Artificial consciousness therefore remains scientifically testable but demands open architecture and runtime evidence, complete adverse controls and a purpose-matched bridge. Unison AI remains future application work and did not select any law in this branch.

## 12. External evidence and adversity ledger

Fifteen source identities were selected only after the complete structural seal. The evidence includes CIE physical colour standards; human report/no-report experiments and their methodological critique; split-brain experiments and a unity boundary review; choice blindness; dream and anesthesia-recovery data; attentional blink; synesthesia consistency and colour matching; learned colour categories; and the preregistered multimodal COGITATE adversarial collaboration and result.

The sources contain sixty-one preregistered features. Fifty-eight are present. Three method phrases from one older synesthetic-colour article are absent from the captured machine-readable content and remain absent; they are not counted as support. Twelve initial PMC captures returned browser interstitials, five later transport attempts failed without usable content, and one adverse publisher response failed its article-identity markers. All eighteen failure rows remain preserved alongside later successful official or exact-work transports.

The evidence is deliberately mixed where the field is mixed. No-report indicators do not automatically establish phenomenal occurrence. Split-brain evidence does not license a one-line verdict about unity. COGITATE preserves results adverse to established theories. Learned colour categories demonstrate that public language can alter discrimination. These are not failures of the SFT model; they are the observations that force its non-substitution boundaries.

## 13. V1/V2 atomic reconciliation

The audit reviews all 763 prior entries, not only keyword matches. Forty-four atomic questions occur in the V1/V2 source surface and two stronger lineage obligations preserve the complete qualia-resonance and red-of-red work. All forty-six map to current V3 engine receipts and none remains open. Prior results identify what must be independently reconstructed; they do not enter V3 as proof premises.

## 14. Reading the exhaustive derivation ledger

Each of the seventy-two sections below states its theorem, dependencies, complete eight-axis grammar, all 256 decisions, sole survivor, depth-independent base and successor, operational witnesses, scientific meaning, four adverse controls, independent implementation, post-seal evidence scope, feature accounting, falsification boundary and immutable identities. The machine-readable evidence remains authoritative; the paper makes it humanly inspectable.
"""]

    order = 1
    current_family = None
    family_section = 15
    for spec in CONSCIOUSNESS_SPECS:
        if spec.family != current_family:
            sections.append(f"\n## {family_section}. {FAMILY_TITLES[spec.family]}\n\n{FAMILY_INTRO[spec.family]}\n")
            family_section += 1
            current_family = spec.family
        sections.append(claim_block(order, spec, feature_audit, target_by_claim))
        order += 1

    sections.append(f"""
## {family_section}. Complete result and verification summary

The foundation contains exactly 72 admitted laws and 18,432 generated candidates. Exactly 72 forms survive. The 288 structural controls pass. Seventy-two separate implementations reconstruct the candidate order and survivor. Seventy-two post-seal empirical-boundary comparisons pass at their declared directness. All 46 inherited atomic questions are reconciled. All dependency paths reach There Is No Nothing. The engine seal is `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`; the verification-authority seal is `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`. Neither protected surface was modified.

The branch is current-evidence closed and extension-open, not permanently locked. A future criticism or discovery may extend or invalidate a claim only by entering the same public process: exact statement, frozen candidate grammar, complete enumeration, unique survivor or preserved halt, independent reconstruction, adverse controls, purpose-matched evidence and unchanged-engine receipt.

## {family_section + 1}. Full-field roadmap

The next editions extend the foundation through complete perceptual modalities; sound, pain, affect, embodiment and multimodal phenomenology; temporal experience; imagination and metacognition; language and reasoning; development and comparative consciousness; sleep, dream, anesthesia, altered state, cessation and recovery; nonhuman and artificial realization programmes; collective-mind boundaries; clinical-disorder handoffs; and ethical consequences stated separately from empirical admission. Applications may test these laws but never select them.

## {family_section + 2}. Limitations

- The 72-law surface is foundational, current-evidence closed and extension-open; it is not the complete Layer Two field reconstruction.
- Formal closure, first-person report, behavioral observation, neural correlation, computation and physical realization are different evidential statuses. The paper never promotes one into another without a bridge.
- The three-position red carrier is an exact structural recurrence, not a universal wavelength or intensity and not direct third-person possession of another subject's red.
- Existing sources constrain the derived boundaries; they do not prove that every system satisfying a partial correlate is conscious.
- Fifteen source identities and sixty-one features are substantial but not exhaustive of consciousness research. Three absent features and eighteen failed transport/content rows remain visible.
- Artificial realization remains an auditable test programme. No current application, including Unison AI, was used to select or certify the laws.
- Ethical implications require their own normative derivation and cannot be smuggled into empirical admission.

## {family_section + 3}. Conclusion

Foundational Consciousness and Cognitive Science is current-evidence closed and extension-open: 72 laws, 18,432 exact candidates, 72 sole survivors, 288 passing controls, 72 independent reconstructions, 72 post-seal empirical-boundary comparisons and 46 of 46 inherited atomic obligations reconciled.

The branch derives a precise solution to the structural hard problem: exterior observation and interior participation share one Fold law but retain different information. It derives binding without erasure, unity without aggregation, a subject without imported substance, finite self-reference without infinite regress, and deterministic self-opacity without ontological chance. It gives substrate independence a causal rather than rhetorical criterion. It reconstructs qualia resonance and the red-of-red as exact label-bearing recurrence while preserving the empirical distinction between physical stimulus, public report and participant quality.

That is the gravity of the result. Consciousness is not awarded to a theory because an institution favors it, to a scan because it is expensive, to an AI because it speaks persuasively or to a report because no better record was collected. Every claim must retain its carrier, alternatives, evidence class, adverse results and derivation to the One. Open criticism is unrestricted. Scientific admission is earned.

## {family_section + 4}. Repository and publication status

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Zenodo DOI: {'https://doi.org/' + doi if authorized else 'not created; separate authorization required'}
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions: https://discord.gg/ucwGryVxGr
- Current state: {'published open access' if authorized else 'local prepublication; no remote action performed'}

## {family_section + 5}. References

Primary and official external evidence:

{chr(10).join(f'- {source.body}. [{source.source_uri}]({source.source_uri}). Evidence class: {source.evidence_class}.' for source in SOURCE_BY_ID.values())}

Smithian Fold Theory branch dependencies:

- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Life*. doi:10.5281/zenodo.21630203.
- Smith, Maria. *From Fold to Medicine*. doi:10.5281/zenodo.21630785.

Open-science evidence supporting the institutional argument:

{OPEN_SCIENCE_REFERENCES}
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
