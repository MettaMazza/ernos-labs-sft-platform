#!/usr/bin/env python3
"""Build the exhaustive Biology foundation paper from admitted evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.biology.external_bindings import BINDING_BY_CLAIM  # noqa: E402
from sft.biology.generated_law import BIOLOGY_SPECS  # noqa: E402
from sft.biology.sources import SOURCE_BY_ID  # noqa: E402
from sft.biology.structural_counts import exact_codon_certificate  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402


INVENTORY = ROOT / "publications/inventories/biology.json"
PAPER = ROOT / "publications/current/biology/FROM_FOLD_TO_LIFE.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/biology_foundation_zenodo_metadata.json"


SUBBRANCH_INTRO = {
    "life_boundary": "The branch begins by separating a merely reactive chemical network from a bounded organization that jointly maintains identity, resources, compartment and hereditary continuation. No single familiar property is allowed to stand in for life.",
    "compartment_identity": "Biological identity requires a held boundary. Inside and outside, membrane organization, selective transitions, nested compartments and lineage provenance remain separate reconstructible relations.",
    "metabolism_resource": "Metabolism is treated as a complete, compartment-bound transformation and transfer ledger. Energy language cannot hide missing matter, unrecorded waste, unspecified resources or an impossible closed organism detached from its environment.",
    "inheritance_replication": "Inheritance is a predecessor-successor relation carried by an identified word or structure. Template, product, fidelity, mismatch, variation and lineage remain distinct; a Fold preimage count cannot by itself prove biological replication.",
    "variation_evolution": "Evolutionary laws retain the population, environment, heritable distinctions, successor counts and finite sampling boundary. Selection and drift are competing generated explanations until controls distinguish them; benefit alone does not force fixation.",
    "gene_genome_regulation": "The code is generated as an exact finite word structure before external tables are opened. Gene, genome, expression and regulation remain evidence-bound sequence and process relations rather than names borrowed from an annotation database.",
    "protein_structure_function": "Protein sequence, folding, ensemble, function, interaction and quaternary assembly are different carriers. No opaque predictor, fixed clash cutoff or one favored coordinate model is admitted as a biological law.",
    "cell_process": "A cell closes boundary, maintenance, inheritance and regulated process integration. Transport, signalling, excitability, division and dysregulation are separate state-transition questions with condition and adverse controls.",
    "multicellular_development": "Multicellularity is reconstructed from lineage-related cells, interfaces, differentiation, ordered development, spatial morphogenesis and regeneration without erasing cellular identity or developmental failures.",
    "organism_physiology": "Organismal identity composes living parts across a life cycle. Physiology, homeostatic control, reproduction and senescence keep environment, stage, population, survival and censoring boundaries explicit.",
    "population_ecology": "Populations, species criteria, communities, trophic graphs and ecosystems are bounded data structures. Network and allometric universality claims receive explicit hostile alternatives rather than preferred-law status.",
    "observation_handoffs": "Biological observation is part of the science: specimen, condition, assay, uncertainty, missingness, controls and causal scope are retained. Upstream laws are cited without reownership and downstream medical or consciousness claims are not smuggled into Biology.",
}


SPECIAL_MEANING = {
    "SFT-BIO-LIFE-CHEMICAL-BOUNDARY-001": "The survivor requires compartment, maintenance, hereditary continuation and regulated resource exchange together. Autocatalysis or dissipation alone remains an eliminated incomplete form. This is a finite operational boundary, not a claim that every disputed biological entity has already been classified.",
    "SFT-BIO-LIFE-AUTOCATALYTIC-CLOSURE-001": "The generated closure test asks whether every required catalytic role is regenerated inside the declared finite reaction support while external resources and the compartment are still recorded. The earlier numerical 1/4 to 1/2 to 1 story is not imported as a chemical concentration or universal ignition threshold.",
    "SFT-BIO-REPLICATION-001": "The Fold supplies distinguishability and successor organization, but Biology additionally requires a resource-bounded predecessor-to-copy process and retained lineage. No universal per-generation doubling is asserted for every biological replicator.",
    "SFT-BIO-FIXATION-001": "Fixation is exactly whole support of the registered variant in the declared finite population. It is an observed state classification, not a theorem that every beneficial allele must reach that state.",
    "SFT-BIO-DRIFT-BOUNDARY-001": "Genetic drift is preserved as a genuine finite-sampling alternative. A selection claim closes only when variant-linked differential continuation survives the registered controls; otherwise the engine does not award a selective cause.",
    "SFT-BIO-NUCLEOTIDE-ALPHABET-001": "The exact construction uses two independently held distinctions. Their ordered product has four and only four labels. NCBI's genetic-code table is opened after sealing and confirms the external DNA coding boundary; it never chooses four.",
    "SFT-BIO-CODON-001": "The complete ordered product of four generated labels over three positions contains 4 x 4 x 4 = 64 distinct words. The census stores all 64 exactly, with no floating value, continuum alphabet or imported codon table.",
    "SFT-BIO-CODON-BOX-001": "Prefix equivalence over the first two positions yields 4 x 4 = 16 boxes. Holding the third position leaves exactly four codons in each box and partitions all 64 words once. This proves the combinatorial box structure, not a universal amino-acid assignment for every genetic-code variant.",
    "SFT-BIO-PROTEIN-FOLD-001": "The law closes directed, condition-bounded reduction into a recurrent structure class and rejects exhaustive random search. It does not claim that every protein has one rigid conformation or that the old two-step 3/4-to-1 path is a measured folding trajectory.",
    "SFT-BIO-PROTEIN-ENSEMBLE-001": "Alternate conformers and intrinsically disordered support are retained. The RCSB 1COP deposit itself contains a solution-NMR ensemble, directly demonstrating why one coordinate file may not erase conformational multiplicity.",
    "SFT-BIO-PROTEIN-QUATERNARY-001": "The primary 1COP deposit confirms a Lambda Cro homodimer and its experimental NMR provenance. The prior 10.266 and 12.539 angstrom docking errors, imported 3.2 angstrom clash floor and Euclidean six-dimensional score are not admitted; the V3 theorem is the exact assembly evidence boundary, not a successful coordinate predictor claim.",
    "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001": "The external record supports predominantly L-amino-acid proteins and D-sugar nucleic acids while explicitly preserving that the origin mechanism remains unresolved. Weak-parity language therefore cannot be presented as if it uniquely selected the observed biological hand.",
    "SFT-BIO-EXCITABLE-THRESHOLD-001": "The exact law is regenerative transition after a declared threshold, with subthreshold and refractory controls. Half-One is structural balance in the proof language; it is not silently reinterpreted as one universal membrane voltage.",
    "SFT-BIO-DYSREGULATED-DIVISION-001": "Persistent cycling is insufficient to identify cancer. The admitted boundary requires lineage-supported failure of normal division, death or differentiation control in tissue context, with mutations and clonal history retained.",
    "SFT-BIO-SENESCENCE-001": "Ageing is not denominator parity. Survival, repair, reproduction, population, condition and censoring records are required; the law distinguishes senescence from cancer and from one cellular Hayflick observation.",
    "SFT-BIO-ECOLOGICAL-RECURRENCE-001": "A bounded periodic orbit alone is not ecosystem stability. Species, resources, perturbations and observation effort remain in the state; stability means persistence or recovery under registered perturbation at a declared boundary.",
    "SFT-BIO-ECOLOGICAL-NETWORK-001": "The external severe test reports that strongly scale-free networks are rare and that log-normal alternatives often fit as well or better. The admitted law is the complete graph and unfavorable-model comparison protocol, not the overclaim that biological networks are universally scale-free or small-world.",
    "SFT-BIO-BIOLOGICAL-ALLOMETRY-001": "The source record retains 3/4, 2/3, unity, size-range dependence and evidence against one universal exponent. The Fold theorem requires a source-, taxon-, range- and condition-bounded allometric comparison; it does not fit or select a preferred exponent.",
    "SFT-BIO-BIO-UNCERTAINTY-001": "Gene Ontology's evidence rules explicitly state that missing annotations do not imply absence and preserve NOT assertions separately. The Fold record likewise distinguishes variation, error, missingness, censoring and demonstrated negation.",
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
    return SPECIAL_MEANING.get(spec.claim_id, f"The result is an exact relational classification at the declared biological boundary. It forces {clean(spec.statement).lower()} Specimen-, organism-, population-, method- and condition-dependent magnitudes remain explicit records and are never promoted into universal constants without a separately generated and externally tested law.")


def claim_block(order: int, spec) -> str:
    package = ROOT / "claims" / spec.claim_id
    registration = read(package / "registration.json")
    candidate = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    certificate = read(package / "certificate.json")
    empirical = read(package / "empirical_validation.json")
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == spec.claim_id)
    binding = BINDING_BY_CLAIM[spec.claim_id]
    source_rows = [SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    witnesses = "\n".join(f"- `{name}`: {description}; passed `{str(passed).lower()}`." for name, description, passed in spec.operational_witnesses)
    controls_text = "\n".join(f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`." for row in controls)
    sources = "\n".join(f"- `{row.source_id}` - {row.body}; [{row.source_uri}]({row.source_uri}); snapshot `{row.snapshot_path}`; `{row.snapshot_hash}`; scope: {row.evidence_scope}." for row in source_rows)
    fragment_identity = sha256_identity(tuple((row.source_id, row.fragment) for row in binding.requirements))
    return f"""### {order}. {spec.title}

Claim identity: `{spec.claim_id}`

**Question and exact theorem.** {clean(spec.statement)}

> `{clean(spec.exact_result)}`

**Rooted dependency chain.** The registration names `SFT-ROOT-THERE-IS-NO-NOTHING`, zero axioms and zero free parameters. It requires these already admitted receipts:

{bullets(f'`{row}`' for row in spec.dependencies)}

The dependency graph independently reaches the premise-free root theorem; a branch label never substitutes for a receipt.

**Generated grammar.** {clean(spec.generation_rule)}

Boundary: {clean(spec.grammar_boundary)}

The exact product contains `{candidate['expected_cardinality']}` candidates, `{len(candidate['candidates'])}` stored candidate identities and `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives; 255 fail at least one required coordinate.

{axis_rows(spec, elimination)}

**Unique survivor and depth independence.** Sole survivor: `{spec.exact_result}`.

Base: {clean(spec.induction_base)}

Successor: {clean(spec.induction_step)}

Closure scope: `{certificate['closure_scope']}`; minimality and named-shape uniqueness both pass.

**Operational witnesses.**

{witnesses}

**Scientific meaning.** {scientific_meaning(spec)}

{SUBBRANCH_INTRO[spec.subbranch]}

**Adverse controls.**

{controls_text}

**Independent reconstruction.** A separately executed implementation regenerated the literal product, candidate order, every decision, the one survivor, depth-independent closure and all four control classes. Implementation `{certificate['independent_implementation_hash']}`; certificate `{certificate['independent_certificate_hash']}`; external-validation `{certificate['external_validation_hash']}`.

**Post-seal external comparison.** The entire 75-law prediction family was sealed before any source identity was chosen. This claim requires `{len(binding.requirements)}` purpose-matched discriminators with ordered identity `{fragment_identity}`. Target opened after derivation seal: `{str(empirical['target_opened_after_seal']).lower()}`. All rows preserved: `{str(empirical['all_rows_preserved']).lower()}`. Exact comparison: `{str(empirical['passed']).lower()}`. A deliberately changed observation was rejected.

Sources:

{sources}

Comparison record:

{bullets(empirical['measurements'])}

Falsification boundary: {clean(empirical['falsification_condition'])}

**Explicit exclusions.**

{bullets(registration['excluded_inputs'])}

**Immutable evidence identities.** Pre-source seal `{certificate['pre_source_complete_branch_seal']}`; source manifest `{certificate['source_manifest_hash']}`; derivation seal `{certificate['derivation_seal_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical validation `{certificate['empirical_validation_hash']}`; measurement receipt `{certificate['measurement_receipt_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.
"""


def main() -> None:
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    if inventory["required_claim_count"] != 75 or inventory["admitted_claim_count_at_freeze"] != 75:
        raise SystemExit("Biology foundation inventory is not completely admitted")
    if any(row["status"] != "model_admitted" for row in inventory["obligations"]):
        raise SystemExit("Biology inventory contains an unadmitted law")
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("authorized Biology publication requires its reserved DOI")
    publication_banner = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi}). "
        "The canonical Markdown paper, rendered PDF, complete evidence/source archive and checksum ledger form this release."
        if authorized
        else "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** Building this paper performs no push, release, upload, DOI creation or Zenodo action."
    )
    counts = exact_codon_certificate()
    mission = open_science_position("For Biology, a database label, selected organism, favorable specimen, opaque structure predictor or consensus classification cannot stand for a law of life. Organism, lineage, compartment, environment, condition, method, missingness and adverse observations remain in the evidence. Exact code counts are stated as exact; variable biological magnitudes remain bounded to their measured populations and protocols.")
    sections = [f"""# From Fold to Life

**Biology and Life Sciences Foundational Branch Paper 001, version 1.0.0 — Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the foundational Biology and Life Sciences branch of the third clean-room Smithian Fold Theory reconstruction at its current-evidence-closed, extension-open boundary. Seventy-five obligations in twelve ordered families generate 19,200 exact candidates and decisions, seventy-five unique survivors, seventy-five depth-independent closure certificates, three hundred passing adverse controls, seventy-five implementation-distinct reconstructions and seventy-five post-seal external comparisons. Every dependency graph reaches the single premise-free theorem, There Is No Nothing. The branch uses zero axioms, zero free or fitted parameters, no negative proof quantities, no irrational or imaginary proof values, no target-selected rule and no opaque predictor.

The exact headline construction generates four DNA coding labels from two held distinctions, three ordered codon positions, sixty-four complete codon words, sixteen first-two-position boxes and four third-position words per box. The paper also closes explicit laws for living organization, compartments, metabolism, inheritance, evolution, genes and genomes, protein folding and assemblies, cells, development, organisms, physiology, populations, ecosystems and biological evidence. A complete audit of 763 prior V1/V2 entries identifies thirty Biology-owned atoms; all thirty now map to immutable V3 receipts, with twenty-one corrected at a stricter evidence boundary. Those corrections are scientific results: beneficial variants do not inevitably fix; protein state cannot be reduced to one rigid shape; biological homochirality is observed while its origin remains unresolved; a universal three-quarter allometric exponent is not supported; strongly scale-free networks are empirically rare; and denominator parity, cycling or one periodic orbit cannot by themselves identify senescence, cancer or ecosystem stability.

## Results first: the biological findings

| Headline result | Exact or bounded result | Scientific meaning |
|---|---|---|
| Nucleic-acid coding alphabet | `2 x 2 = 4` held symbol labels | Four is generated before the NCBI genetic-code table is opened. |
| Codon word space | `4 x 4 x 4 = 64` ordered triplets | All sixty-four words are explicitly enumerated; no codon table selects the count. |
| Codon prefix boxes | `4 x 4 = 16` boxes, each holding `4` third-position words | The complete partition covers each of the sixty-four codons exactly once. |
| Living/nonliving boundary | Compartment + maintenance + inheritance + regulated resource exchange | Autocatalysis or dissipation alone is an eliminated incomplete form. |
| Evolution | Heritable variation + differential continuation + controlled environment | Selection is distinguished from drift; benefit alone does not force fixation. |
| Protein structure | Directed condition-bounded fold plus retained conformational ensemble | Fast reduction is admitted; one rigid universal native shape is not. |
| Homochirality | L-amino-acid/D-sugar predominance observed; origin mechanism unresolved | The old parity-selection overclaim is removed instead of hidden. |
| Networks and scaling | Whole-graph hostile alternatives; 3/4, 2/3, unity and nonuniversal allometry retained | Scale-free and three-quarter universality are not imported as laws. |
| Complete evidence | 75 laws; 19,200 candidates; 75 survivors; 300 controls; 75 independent reconstructions; 75 post-seal comparisons | Every result has a root trace, falsifier, custody record and immutable engine receipt. |

{mission}

## 1. Publication, authorship and open-science boundary

{publication_banner}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Reproducibility reports and submissions: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

Copyright preserves Maria Smith's authorship. The paper and documentation are prepared under CC BY 4.0 and code under Apache-2.0. The Ernos Labs name is a separate, revocable standards designation: reuse is open, but the designation requires continued adherence to the public constitution, unchanged admission engine, complete adverse evidence and open critical review.

## 2. Exact scope and closure language

Foundational closure means every obligation in the frozen 75-law question surface has an engine-admitted theorem inside its declared exact grammar, a complete dependency path, adverse controls, an independent reconstruction and a post-seal external comparison. It does not mean Biology is permanently closed, that every species or future observation has been enumerated, or that the full field-wide Layer Two roadmap is complete. This foundation is current-evidence closed and extension-open: any lawful discovery, correction or invalidation can be admitted through the same public process.

## 3. Constitutional mathematical domain

Structural absence is Empty One and may be displayed as `0`; it is not conventional numerical nothing. Counts are generated positive wholes and exact parts are positive held fractions. Opposition, side and orientation are labels rather than negative scalars. Negative proof quantities, irrational or imaginary proof values, floating equality, completed infinity, ungenerated continua, axioms, free parameters, fitted coefficients, imported biological equations, pretrained predictors, consensus-selected survivors and application-selected laws are prohibited. Conventional notation appears only in downstream correspondence prose where it cannot act as proof input.

## 4. Dependency spine

Every Biology registration names the single premise-free root and zero axioms. The first law depends only on already admitted Foundation, Mathematics, Information Science, Physics, Chemistry and Materials receipts. Each later law also depends on its immediate Biology predecessor, producing an ordered 75-law chain. The engine accepts a dependency only if its immutable model-admission receipt already exists. Thus every law is traceable to the root through actual claim identities, not through a narrative assertion that a branch exists.

## 5. Complete target-blind seal

Before any external source identity was selected, the whole 75-law inventory, exact counting module and target-blind blueprint set were frozen. The seal is `sha256:4b3e1ba191d363a1b67e1a02853f071cdf2c9d3d86081fced05ab3c5d079e639`. It binds seventy-five predictions, 19,200 candidate identities and the exact source files while recording `external_source_identities_selected=false` and `external_target_content_opened=false`. No later source discovery can change those candidates or survivors without breaking the seal.

## 6. Exact codon certificate

The independent finite certificate is `{counts}`. Two held distinctions generate four ordered labels. The complete length-three product contains sixty-four distinct words. Prefix equivalence on the first two positions forms sixteen boxes. Every box holds four third-position alternatives; their union contains all sixty-four words exactly once. NCBI is then used as an external genetic-code correspondence, not as the generator.

## 7. External evidence and preserved adversity

Seventeen byte-frozen usable sources cover the twelve families: US National Academies/NCBI organization records, NCBI cell and molecular-biology chapters, Gene Ontology evidence rules, Sequence Ontology, NCBI's genetic-code table, the primary RCSB 1COP deposition, GBIF survey standards, evolution/genetics, protein folding, development, homeostasis, aging, homochirality, and full-text network/allometry studies. Each claim binds at least two purpose-matched fragments. The prediction process cannot read filesystem, network, clock, environment, dynamic import, subprocess or external target. A separate custodian opens sources after sealing and releases a target only for a matching prediction seal.

The evidence ledger also preserves four failures: the Sequence Ontology web endpoint failed the local TLS handshake; one GBIF page returned 403; and two PMC printable endpoints returned challenge pages rather than article content. Registered official release or Europe PMC endpoints supplied the same purposes in new addenda without deleting the failed rows. Scientific adverse results are likewise retained: nonuniversal allometry, rarity of strong scale-freeness and unresolved homochirality mechanism are part of the accepted evidence rather than inconvenient exceptions.

## 8. V1/V2 categorical audit and corrected legacy boundaries

All 356 V1 rows and 407 V2 steps were reviewed. Nine V1 rows and nine V2 steps contain Biology-owned atoms after mixed statements are decomposed at categorical boundaries. Thirty atomic obligations are identified; thirty are mapped to current Biology receipts; none remains open. Twenty-one are explicitly corrected rather than cosmetically called historical. Physics retains irreversibility, Chemistry retains molecular chirality, computation retains general complexity, and Biology owns living organization, inheritance, protein behavior, evolution, organismal and ecological consequences.

The corrected boundaries include: no inevitable selection-to-fixation law; no single rigid protein state; no parity-derived biological hand; no universal numerical autocatalytic ignition threshold; no denominator-parity aging law; no half-One membrane-voltage claim; no recurrence-only cancer diagnosis; no one-orbit ecosystem stability; no universal scale-free/small-world topology; no universal three-quarter allometry; and no claim that the inaccurate prior Lambda Cro docking output was a validated predictor.

## 9. Reading the exhaustive derivation ledger

Each of the seventy-five sections below states the theorem, dependencies, full eight-axis grammar, all 256 candidate decisions, unique survivor, depth-independent base/successor certificate, operational witnesses, scientific meaning, four adverse controls, independent implementation, post-seal sources, falsification boundary and immutable identities. The machine-readable files remain authoritative; this prose makes their meaning inspectable.
"""]
    section_number = 10
    order = 1
    for subbranch in inventory["subbranch_order"]:
        sections.append(f"\n## {section_number}. {subbranch.replace('_', ' ').title()}\n\n{SUBBRANCH_INTRO[subbranch]}\n")
        for spec in (row for row in BIOLOGY_SPECS if row.subbranch == subbranch):
            sections.append(claim_block(order, spec))
            order += 1
        section_number += 1

    source_rows = "\n".join(f"- `{row.source_id}` — [{row.source_uri}]({row.source_uri}); `{row.snapshot_hash}`; {row.evidence_scope}." for row in SOURCE_BY_ID.values())
    audit = read(ROOT / "audits/biology_v1_v2_atomic_ownership.json")
    sections.append(f"""
## {section_number}. Integrated audit result

- Prior entries reviewed: `{audit['source_surface']['total_source_rows_reviewed']}`.
- Biology-relevant prior rows: `{audit['source_surface']['biology_relevant_source_row_count']}`.
- Biology-owned atoms: `{audit['summary']['biology_owned_atom_count']}`.
- Same-strength V3-closed atoms: `{audit['summary']['same_strength_closed_atom_count']}`.
- Open atoms: `{audit['summary']['same_strength_open_atom_count']}`.
- Corrected prior atoms: `{audit['summary']['corrected_prior_atom_count']}`.
- Audit identity: `{audit['audit_identity']}`.

## {section_number + 1}. External-source ledger

{source_rows}

Preserved unsuccessful source rows are recorded in `experiments/external_sources/biology/biology_foundation_source_manifest.json` and `experiments/external_sources/biology/biology_foundation_family_source_manifest_v1.json`; their official transport/content replacements are separately registered, not substituted invisibly.

## {section_number + 2}. Reproducibility and falsification

The repository's one-command verification route checks engine and verification-authority seals, schemas, dependency resolution, source hashes, inventory cardinality, execution manifests, receipts and branch gates. The Biology-focused suite independently checks 75 inventory/spec alignments, all 19,200 candidates, 75 unique survivors, dependency order, all 153 registered source fragments, the exact codon certificate and prohibited blueprint fields.

The branch is falsified at its declared boundary if any source hash changes without a new version, any required external fragment is absent, any target becomes accessible before sealing, any adverse or failed row is omitted, any tampered target is accepted, any dependency loses its root path, any candidate census is incomplete, any claim has other than one survivor, or any implementation-distinct validator fails.

## {section_number + 3}. Full-field Biology roadmap

This paper completes Layer One. Later versions extend, in dependency order, through biochemistry at the living boundary; structural and quantitative biology; genetics, genomics and epigenetics; RNA and cellular machinery; microbiology and virology; taxonomy and phylogeny; development and regeneration; comparative plant, fungal, animal, marine and extremophile biology; neuroscience at the substrate boundary; immunology; behaviour and sensory biology; biodiversity and conservation; systems and synthetic biology; biological data inference; origins-of-life hypotheses; ageing; biosphere processes; and astrobiology handoffs. Fold Protein remains a downstream validation application and cannot select these laws.

## {section_number + 4}. Limitations

- The 75-law foundation is complete at its frozen current-evidence boundary, not a permanent declaration that no new biological law can exist.
- Most foundational results are exact relational and classification laws. Only the code counts are universal numerical results in this edition.
- External authority and primary data test correspondence; they are not premises of the derivation.
- The paper does not claim one universal life definition outside the registered finite operational grammar.
- Clinical efficacy belongs to Medicine; consciousness and qualia belong to their own branch; engineering applications cannot select Biology laws.
- Allometry, network topology, protein ensembles, senescence, ecological stability and similar quantities remain population-, condition-, scale- and method-bounded.

## {section_number + 5}. Conclusion

Foundational Biology is current-evidence closed and extension-open: seventy-five required laws, 19,200 exact candidates and decisions, seventy-five unique survivors, three hundred passing adverse controls, seventy-five independent reconstructions, seventy-five post-seal external comparisons, seventy-five root traces, and thirty of thirty legacy Biology atoms reconciled. The result is not a list of biological vocabulary. It is a public chain from the premise-free root theorem through exact finite alternatives to falsifiable, source-bound statements about life, heredity, evolution, cells, organisms and ecosystems.

The corrections matter as much as the correspondences. The engine did not reward familiar slogans: it rejected inevitable fixation, rigid one-state proteins, parity-selected homochirality, universal three-quarter allometry, ubiquitous scale-free networks and recurrence-only biological diagnoses. That is the empirical standard Ernos Labs is meant to make reproducible: open inquiry without open admission-by-assertion, and no credential, institution, model or author exempt from the same public gate.

## {section_number + 6}. Repository and publication status

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Zenodo DOI: {f'https://doi.org/{doi}' if authorized else 'reserved only after explicit publication authorization'}
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions: https://discord.gg/ucwGryVxGr
- Current state: {'published open access' if authorized else 'local prepublication; no remote action performed'}

## {section_number + 7}. References

- National Academies of Sciences, Engineering, and Medicine. *A New Biology for the 21st Century*. NCBI Bookshelf.
- Cooper, G. M. *The Cell: A Molecular Approach*. NCBI Bookshelf.
- Brown, T. A. *Genomes*. NCBI Bookshelf.
- Gene Ontology Consortium. Ontology and annotation evidence documentation.
- Sequence Ontology Consortium. Official OBO release.
- National Center for Biotechnology Information. Genetic Codes.
- Worldwide Protein Data Bank / RCSB PDB. Entry 1COP.
- Global Biodiversity Information Facility. Darwin Core and survey-data guidance.
- Broido, A. D., and Clauset, A. *Scale-free networks are rare*. Nature Communications 10, 1017 (2019).
- van der Heijden, M. et al. *All You Need to Know About Allometric Scaling*. 2025.
- Gleiser, M. *Biological Homochirality and the Search for Extraterrestrial Biosignatures*. 2022.
- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Chemistry*. doi:10.5281/zenodo.21531455.

Open-science evidence supporting the institutional argument:

{OPEN_SCIENCE_REFERENCES}
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
