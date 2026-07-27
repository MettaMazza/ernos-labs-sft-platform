"""Claim-specific post-seal Biology authority bindings."""

from __future__ import annotations

from dataclasses import dataclass

from sft.biology.obligations import BIOLOGY_OBLIGATIONS


@dataclass(frozen=True)
class SourceRequirement:
    source_id: str
    fragment: str


@dataclass(frozen=True)
class BiologyBinding:
    claim_id: str
    requirements: tuple[SourceRequirement, ...]


def req(source_id: str, fragment: str) -> SourceRequirement:
    return SourceRequirement(source_id, fragment)


FAMILY_REQUIREMENTS = {
    "life_boundary": (req("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "cell is the smallest independent unit of life"), req("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "metabolic energy")),
    "compartment_identity": (req("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "membrane-enclosed organelles"), req("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "cellular component")),
    "metabolism_resource": (req("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "generation and controlled utilization of metabolic energy"), req("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "biological process")),
    "inheritance_replication": (req("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "DNA is the chemical of inheritance"), req("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "replication")),
    "variation_evolution": (req("SFT-BIO-SRC-NCBI-EVOLUTION-GENETICS-V1", "heritable variation"), req("SFT-BIO-SRC-NCBI-EVOLUTION-GENETICS-V1", "genetic drift")),
    "gene_genome_regulation": (req("SFT-BIO-SRC-SEQUENCE-ONTOLOGY-OBO-RELEASE-V1", "name: gene"), req("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "genome expression")),
    "protein_structure_function": (req("SFT-BIO-SRC-NCBI-PROTEIN-FOLDING-V1", "protein folding"), req("SFT-BIO-SRC-SEQUENCE-ONTOLOGY-OBO-RELEASE-V1", "name: polypeptide")),
    "cell_process": (req("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "plasma membrane"), req("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "signal transduction")),
    "multicellular_development": (req("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "differentiation"), req("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "multicellular organisms")),
    "organism_physiology": (req("SFT-BIO-SRC-NCBI-HOMEOSTASIS-V1", "homeostasis"), req("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "organisms function within interdependent communities")),
    "population_ecology": (req("SFT-BIO-SRC-GBIF-DARWIN-CORE-ARCHIVE", "sampling event"), req("SFT-BIO-SRC-GBIF-SURVEY-GUIDE-V1", "sampling effort")),
    "observation_handoffs": (req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "evidence code"), req("SFT-BIO-SRC-GBIF-DARWIN-CORE-ARCHIVE", "protocols")),
}


SPECIAL_REQUIREMENTS = {
    "SFT-BIO-NUCLEOTIDE-ALPHABET-001": (req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Standard Code"), req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Base1")),
    "SFT-BIO-CODON-001": (req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Base1"), req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Base2"), req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Base3")),
    "SFT-BIO-CODON-BOX-001": (req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "AAs"), req("SFT-BIO-SRC-NCBI-GENETIC-CODE", "Base3")),
    "SFT-BIO-GENE-001": (req("SFT-BIO-SRC-SEQUENCE-ONTOLOGY-OBO-RELEASE-V1", "name: gene"), req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "reference")),
    "SFT-BIO-GENOME-001": (req("SFT-BIO-SRC-SEQUENCE-ONTOLOGY-OBO-RELEASE-V1", "name: genome"), req("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "genome expression")),
    "SFT-BIO-EXPRESSION-REGULATION-001": (req("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "extracellular signaling"), req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "biological context")),
    "SFT-BIO-PROTEIN-QUATERNARY-001": (req("SFT-BIO-SRC-RCSB-1COP-CIF", "CRO REPRESSOR"), req("SFT-BIO-SRC-RCSB-1COP-CIF", "SOLUTION NMR"), req("SFT-BIO-SRC-NCBI-PROTEIN-FOLDING-V1", "polypeptide chains must assemble")),
    "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001": (req("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "L-amino acids"), req("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "D-sugars")),
    "SFT-BIO-DYSREGULATED-DIVISION-001": (req("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "cancer"), req("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "cell cycle")),
    "SFT-BIO-REGENERATION-001": (req("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "regeneration"), req("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "differentiation")),
    "SFT-BIO-HOMEOSTASIS-001": (req("SFT-BIO-SRC-NCBI-HOMEOSTASIS-V1", "setpoint"), req("SFT-BIO-SRC-NCBI-HOMEOSTASIS-V1", "controller")),
    "SFT-BIO-SENESCENCE-001": (req("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "life span"), req("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "survival and reproduction")),
    "SFT-BIO-ECOLOGICAL-NETWORK-001": (req("SFT-BIO-SRC-EUROPEPMC-SCALE-FREE-RARE-6399239-XML-V1", "scale-free networks are not ubiquitous"), req("SFT-BIO-SRC-EUROPEPMC-SCALE-FREE-RARE-6399239-XML-V1", "log-normal distributions fit")),
    "SFT-BIO-BIOLOGICAL-ALLOMETRY-001": (req("SFT-BIO-SRC-EUROPEPMC-ALLOMETRY-11782306-XML-V1", "universal allometric exponent"), req("SFT-BIO-SRC-EUROPEPMC-ALLOMETRY-11782306-XML-V1", "3/4"), req("SFT-BIO-SRC-EUROPEPMC-ALLOMETRY-11782306-XML-V1", "2/3")),
    "SFT-BIO-BIO-UNCERTAINTY-001": (req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "Missing annotations do not imply"), req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "NOT statement")),
    "SFT-BIO-BIO-CAUSALITY-001": (req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "causal relations"), req("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "biological context")),
}


BIOLOGY_BINDINGS = tuple(BiologyBinding(row.claim_id, SPECIAL_REQUIREMENTS.get(row.claim_id, FAMILY_REQUIREMENTS[row.subbranch])) for row in BIOLOGY_OBLIGATIONS)
BINDING_BY_CLAIM = {row.claim_id: row for row in BIOLOGY_BINDINGS}


def validate_bindings() -> None:
    if len(BINDING_BY_CLAIM) != len(BIOLOGY_OBLIGATIONS):
        raise ValueError("Biology bindings do not cover the frozen inventory exactly")
    if any(not row.requirements for row in BIOLOGY_BINDINGS):
        raise ValueError("Biology claim lacks a purpose-matched source requirement")


validate_bindings()

__all__ = ("SourceRequirement", "BiologyBinding", "BIOLOGY_BINDINGS", "BINDING_BY_CLAIM", "validate_bindings")
