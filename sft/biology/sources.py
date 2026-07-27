"""Post-seal authoritative source identities for foundational Biology."""

from __future__ import annotations

from dataclasses import dataclass
import html
from pathlib import Path
import re

from sft.engine.source import hash_file


@dataclass(frozen=True)
class BiologySource:
    source_id: str
    body: str
    source_uri: str
    snapshot_path: str
    snapshot_hash: str
    evidence_scope: str


def source(source_id: str, body: str, uri: str, path: str, digest: str, scope: str) -> BiologySource:
    return BiologySource(source_id, body, uri, path, digest, scope)


BIOLOGY_AUTHORITY_SOURCES = (
    source("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "US National Academies / NCBI Bookshelf", "https://www.ncbi.nlm.nih.gov/books/NBK32506/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-nasem-unity-biology-2010.html", "sha256:62b53a959de8aa5b377997063a3a2719a87ff029a99f36225a383c7a4cfad9e6", "DNA inheritance; cell; multicellularity; organism; community; ecosystem; biological energy"),
    source("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "NCBI Bookshelf, The Cell", "https://www.ncbi.nlm.nih.gov/books/NBK9841/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-cell-origin-metabolism.html", "sha256:ce64ef3e815f9a4f14dc6938e708f449bfd3a39de108c317aac8a941bff68b6b", "cells; membranes; compartments; metabolism; replication"),
    source("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "Gene Ontology Consortium", "https://geneontology.org/docs/ontology-documentation/", "experiments/external_sources/biology/snapshots/sft-bio-src-go-ontology-documentation.html", "sha256:a55c5b5fc204dae486fa1bdfa85d50035f70bf2286fc089783d1a961fa8fcf26", "molecular function; cellular component; biological process and relations"),
    source("SFT-BIO-SRC-GO-ANNOTATION-EVIDENCE", "Gene Ontology Consortium", "https://geneontology.org/docs/go-annotations/", "experiments/external_sources/biology/snapshots/sft-bio-src-go-annotation-evidence.html", "sha256:b16235ab261f6b02afa71826546aad87823680ff267e0bd1c433d54c838b7ebd", "evidence codes; context; negation; missingness; causal activity models"),
    source("SFT-BIO-SRC-NCBI-GENETIC-CODE", "NCBI Taxonomy", "https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-genetic-code.html", "sha256:c329091f012ae379949dc3a39f1961d2338a7b38ddad60245f9c12d8a31db514", "complete genetic-code tables and ordered base positions"),
    source("SFT-BIO-SRC-RCSB-1COP-CIF", "Worldwide Protein Data Bank / RCSB PDB", "https://files.rcsb.org/download/1COP.cif", "experiments/external_sources/biology/snapshots/sft-bio-src-rcsb-1cop-cif.cif", "sha256:6eddefaa66f6191a3080ca3b0dd333c9e7859448d6aaf17b79b60a3e32ad9a3c", "primary Lambda Cro NMR ensemble and homodimer assembly"),
    source("SFT-BIO-SRC-GBIF-DARWIN-CORE-ARCHIVE", "Global Biodiversity Information Facility", "https://ipt.gbif.org/manual/en/ipt/latest/dwca-guide", "experiments/external_sources/biology/snapshots/sft-bio-src-gbif-darwin-core-archive.html", "sha256:89adbe8ba230fd51495154e86843e624d2805d632bc17e55136e88f85c7cad1f", "taxon, occurrence and sampling-event data structures"),
    source("SFT-BIO-SRC-SEQUENCE-ONTOLOGY-OBO-RELEASE-V1", "Sequence Ontology Consortium", "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.obo", "experiments/external_sources/biology/snapshots/sft-bio-src-sequence-ontology-obo-release-v1.obo", "sha256:dde032d4c7cfb89a7013f2f8ab7420a8ef7dc469fbc2b0ffb38bef2a064a1d1f", "sequence features, gene, genome, transcript, polypeptide and mutation classes"),
    source("SFT-BIO-SRC-GBIF-SURVEY-GUIDE-V1", "Global Biodiversity Information Facility", "https://docs.gbif.org/guide-publishing-survey-data/en/", "experiments/external_sources/biology/snapshots/sft-bio-src-gbif-survey-guide-v1.html", "sha256:58b745acf0df0e8235a5c50e9ff86a128593f26fb6982fd92834ca544bf31be8", "ecological survey protocol, effort, occurrence, absence and monitoring"),
    source("SFT-BIO-SRC-NCBI-EVOLUTION-GENETICS-V1", "NCBI Bookshelf", "https://www.ncbi.nlm.nih.gov/books/NBK595925/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-evolution-genetics-v1.html", "sha256:49fd44aa874381d681845301eb337b361ed763fb4272118befc61af4a07eaceb", "heritable variation, mutation, selection, population size and drift"),
    source("SFT-BIO-SRC-NCBI-PROTEIN-FOLDING-V1", "NCBI Bookshelf, The Cell", "https://www.ncbi.nlm.nih.gov/books/NBK9843/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-protein-folding-v1.html", "sha256:ba95b96559c7a21af68f3dc044011bb842b1d641ef86beeb2713a8b360e14313", "sequence, folding, intermediates, chaperones, function and assembly"),
    source("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "NCBI Bookshelf, Genomes", "https://www.ncbi.nlm.nih.gov/books/NBK21127/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-genome-regulation-development-v1.html", "sha256:e1d430fae9b5cee3fdd0778c89ccb4a578be472db6a81f5ba802191d94e909ce", "genome expression, signalling, differentiation and development"),
    source("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "NCBI Bookshelf, Developmental Biology", "https://www.ncbi.nlm.nih.gov/books/NBK10041/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-aging-senescence-v1.html", "sha256:920f58581ed5a30448598733f38a1b2eb85682fb9901cf5c1a5606513f6adb4c", "aging, lifespan, regeneration and cancer distinction"),
    source("SFT-BIO-SRC-NCBI-HOMEOSTASIS-V1", "NCBI Bookshelf", "https://www.ncbi.nlm.nih.gov/books/NBK559138/?report=printable", "experiments/external_sources/biology/snapshots/sft-bio-src-ncbi-homeostasis-v1.html", "sha256:687e91d0923fa79516112a8c3bd99df2a4b911d3fc79d0c488954caaee4c7c24", "physiology and homeostatic control loops"),
    source("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "US National Library of Medicine / PubMed", "https://pubmed.ncbi.nlm.nih.gov/35969306/?format=pubmed", "experiments/external_sources/biology/snapshots/sft-bio-src-pubmed-homochirality-35969306-v1.html", "sha256:8980303d43e13f638eccaf22e24edc141fc51b26037c5e9336facdea4f5c9bca", "observed L-amino-acid and D-sugar predominance with mechanism unresolved"),
    source("SFT-BIO-SRC-EUROPEPMC-SCALE-FREE-RARE-6399239-XML-V1", "Europe PMC", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6399239/fullTextXML", "experiments/external_sources/biology/snapshots/sft-bio-src-europepmc-scale-free-rare-6399239-xml-v1.xml", "sha256:3896db77ef007b8da965fb21a7f87d63790222cb566889ec89d978392ded21a8", "severe empirical scale-free test and alternative distributions"),
    source("SFT-BIO-SRC-EUROPEPMC-ALLOMETRY-11782306-XML-V1", "Europe PMC", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11782306/fullTextXML", "experiments/external_sources/biology/snapshots/sft-bio-src-europepmc-allometry-11782306-xml-v1.xml", "sha256:214f06e309b9505e2ec0852d9b30cb02b6c4863c7e17f16d16ceb17378462e99", "three-quarter, two-thirds, unity and nonuniversal allometric evidence"),
)


SOURCE_BY_ID = {row.source_id: row for row in BIOLOGY_AUTHORITY_SOURCES}


def source_corpus(root: Path, source_id: str) -> str:
    source_row = SOURCE_BY_ID[source_id]
    raw = (root / source_row.snapshot_path).read_text(encoding="utf-8", errors="replace")
    without_tags = re.sub(r"<[^>]+>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", without_tags)).casefold()


def validate_sources(root: Path) -> None:
    if len(SOURCE_BY_ID) != len(BIOLOGY_AUTHORITY_SOURCES) == 17:
        raise ValueError("Biology source identities repeat or are incomplete")
    for row in BIOLOGY_AUTHORITY_SOURCES:
        if hash_file(root / row.snapshot_path) != row.snapshot_hash:
            raise ValueError(f"Biology snapshot changed: {row.source_id}")


__all__ = ("BiologySource", "BIOLOGY_AUTHORITY_SOURCES", "SOURCE_BY_ID", "source_corpus", "validate_sources")
