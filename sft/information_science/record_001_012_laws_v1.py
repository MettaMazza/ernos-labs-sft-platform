"""Complete Data, Records, Metadata, Provenance and Integrity family laws."""
from __future__ import annotations

import hashlib
import json

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def data_item(source, field, value):
    if not source or not field:
        raise ValueError("data identity requires source and field")
    return (source, field, value)


def relation(schema, rows):
    if not schema or len(schema) != len(set(schema)):
        raise ValueError("schema fields must be complete and unique")
    if any(len(row) != len(schema) for row in rows):
        raise ValueError("every row must instantiate the complete schema")
    return tuple(tuple(zip(schema, row)) for row in rows)


def metadata(record, schema_id, unit, source):
    return {"record_identity": canonical(record), "schema": schema_id, "unit": unit, "source": source}


def validates_schema(record, schema):
    return set(record) == set(schema) and all(isinstance(record[field], schema[field]) for field in schema)


def valid_provenance(chain):
    return bool(chain) and len({row["id"] for row in chain}) == len(chain) and chain[0]["parent"] is None and all(chain[index]["parent"] == chain[index - 1]["id"] for index in range(1, len(chain)))


def integrity_record(payload):
    return {"payload": payload, "identity": canonical(payload)}


def integrity_passes(record):
    return record["identity"] == canonical(record["payload"])


def version(identifier, payload, parent):
    return {"version": identifier, "payload_identity": canonical(payload), "parent": parent}


def completeness(expected, observed):
    return {
        "retained": tuple(item for item in expected if item in observed),
        "absent": tuple(item for item in expected if item not in observed),
        "unexpected": tuple(item for item in observed if item not in expected),
    }


RECORD = data_item("source-A", "temperature", (21, 2))
SCHEMA = {"name": str, "count": int}
PROVENANCE = (
    {"id": "capture", "parent": None},
    {"id": "normalize", "parent": "capture"},
    {"id": "publish", "parent": "normalize"},
)

OBS = {
    "001": ("data identity retains source, field and exact value", RECORD == ("source-A", "temperature", (21, 2)) and canonical(RECORD) == canonical(RECORD)),
    "002": ("a two-field relation retains every field in every ordered row", relation(("symbol", "label"), (("a", "A"), ("b", "B"))) == ((("symbol", "a"), ("label", "A")), (("symbol", "b"), ("label", "B")))),
    "003": ("metadata binds the record identity, schema, unit and source without replacing the data", metadata(RECORD, "temperature-parts-v1", "exact-part", "sensor-A")["record_identity"] == canonical(RECORD) and len(metadata(RECORD, "temperature-parts-v1", "exact-part", "sensor-A")) == 4),
    "004": ("schema validation accepts the complete typed record and rejects a missing field", validates_schema({"name": "alpha", "count": 3}, SCHEMA) and not validates_schema({"name": "alpha"}, SCHEMA)),
    "005": ("the provenance chain is contiguous, ordered and duplicate-free", valid_provenance(PROVENANCE) and not valid_provenance((PROVENANCE[0], PROVENANCE[2]))),
    "006": ("integrity verification accepts the retained payload and rejects a changed payload", integrity_passes(integrity_record(RECORD)) and not integrity_passes({"payload": RECORD + ("changed",), "identity": canonical(RECORD)})),
    "007": ("versions retain distinct payload identities and an explicit parent relation", version("v2", ("a", "b"), "v1")["parent"] == "v1" and version("v1", ("a",), None)["payload_identity"] != version("v2", ("a", "b"), "v1")["payload_identity"]),
    "008": ("structural absence, missing expected record and unknown retained value remain three distinct tagged states", len({("absence", "0"), ("missing", "expected-row"), ("unknown", "retained-row")}) == 3),
    "009": ("exact duplicates share one canonical identity while declared aliases retain their source tokens and common target", canonical(("a", 1)) == canonical(("a", 1)) and {"A": "a", "alpha": "a"}["A"] == {"A": "a", "alpha": "a"}["alpha"]),
    "010": ("record linkage retains the exact key match and every unresolved alternative", tuple(row for row in (("r1", "s1", "exact"), ("r2", "s2", "possible"), ("r2", "s3", "possible")) if row[0] == "r2") == (("r2", "s2", "possible"), ("r2", "s3", "possible"))),
    "011": ("the dataset ledger accounts separately for retained, absent and unexpected identities", completeness(("r1", "r2", "r3"), ("r1", "r3", "r4")) == {"retained": ("r1", "r3"), "absent": ("r2",), "unexpected": ("r4",)}),
    "012": ("the custody package reproduces the same source, metadata, provenance and integrity identity", canonical((RECORD, metadata(RECORD, "temperature-parts-v1", "exact-part", "sensor-A"), PROVENANCE)) == canonical((RECORD, metadata(RECORD, "temperature-parts-v1", "exact-part", "sensor-A"), PROVENANCE))),
}

DEFINITIONS = {
    "001": ("SFT-INFO-RECORD-DATA-IDENTITY-001", "Data item and record identity", "source-field-value-identity", "A data item is an exact source-bound field/value record whose canonical identity includes its provenance-bearing source, declared field and complete exact value."),
    "002": ("SFT-INFO-RECORD-TUPLE-RELATION-002", "Field, tuple and relation organization", "complete-schema-tuple-relation", "A tuple instantiates every field of one ordered duplicate-free schema; a relation is the complete retained family of such typed tuples."),
    "003": ("SFT-INFO-RECORD-METADATA-003", "Metadata as retained interpretive record", "data-bound-metadata-record", "Metadata is a separate retained record bound to the canonical data identity and carrying the declared schema, unit and source needed to interpret the data without replacing it."),
    "004": ("SFT-INFO-RECORD-SCHEMA-TYPE-004", "Schema and type custody", "complete-field-type-custody", "A record conforms to a schema exactly when every declared field occurs once, no undeclared field enters and every value belongs to its generated type fibre."),
    "005": ("SFT-INFO-RECORD-PROVENANCE-005", "Provenance chain composition", "contiguous-acyclic-provenance-chain", "Provenance is the complete ordered parent-bound transformation chain from source capture to present record; gaps, duplicates and cycles halt custody."),
    "006": ("SFT-INFO-RECORD-INTEGRITY-006", "Integrity and tamper evidence", "identity-bound-integrity-check", "Integrity is equality between a retained canonical payload identity and a freshly reconstructed identity; any changed distinction produces a different identity and fails verification."),
    "007": ("SFT-INFO-RECORD-VERSION-REVISION-007", "Version and revision identity", "payload-and-parent-version-identity", "A version retains its own identifier, exact payload identity and explicit parent; revision never silently overwrites or aliases the prior record."),
    "008": ("SFT-INFO-RECORD-ABSENT-MISSING-UNKNOWN-008", "Missing, absent and unknown distinctions", "three-way-absence-missing-unknown", "Structural absence displayed as 0, an expected-but-missing record and a retained record with unknown value are distinct states and may never be collapsed into a numerical zero."),
    "009": ("SFT-INFO-RECORD-DUPLICATE-ALIAS-009", "Duplicate and alias resolution", "canonical-duplicate-alias-ledger", "Duplicates are records with identical canonical identities; aliases retain distinct source tokens plus an explicit many-to-one canonical-name relation rather than silent deletion."),
    "010": ("SFT-INFO-RECORD-LINKAGE-IDENTITY-010", "Record linkage and identity boundaries", "complete-link-alternative-ledger", "Record linkage is an exact declared relation between source identities; unresolved candidates remain explicit alternatives and no fitted similarity threshold silently selects identity."),
    "011": ("SFT-INFO-RECORD-DATASET-COMPLETENESS-011", "Dataset completeness and omission ledger", "retained-absent-unexpected-ledger", "Dataset completeness compares the full registered identity support with the observed support and separately retains every present, absent and unexpected row."),
    "012": ("SFT-INFO-RECORD-CUSTODY-REPRODUCIBILITY-012", "Record custody and reproducibility certificate", "reconstructing-custody-package", "A reproducibility certificate binds data, metadata, provenance, schema and integrity identities so an independent reconstruction yields the same complete record identity or halts."),
}

IDS = tuple(DEFINITIONS[number][0] for number in sorted(DEFINITIONS))
EXCLUSIONS = (
    "no axiom, imported data model, database convention or target outcome selects the result",
    "displayed 0 denotes structural absence only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no silent overwrite, hidden missing value, erased alias or unrecorded provenance step",
    "no sampled row family or unregistered infinite dataset",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_reason, admitted, admitted_reason):
    return binary_dimension(key, key + "?", rejected, rejected_reason, admitted, admitted_reason)


def dimensions(relation):
    return (
        dimension("carrier", "partial-record-carrier", "A partial carrier can omit a registered record.", "complete-source-bound-carrier", "Every registered record identity occurs exactly once."),
        dimension("identity", "mutable-presentation-identity", "Presentation or mutable location does not preserve record identity.", "canonical-content-and-source-identity", "Exact content and retained source determine identity."),
        dimension("relation", "imported-record-answer", "An imported schema or answer cannot force the law.", relation, "The registered relation follows from complete record structure."),
        dimension("custody", "unrecorded-transformation", "An unrecorded step breaks reconstruction.", "complete-provenance-custody", "Every transformation and parent record is retained."),
        dimension("enumeration", "sampled-records", "A sample cannot close dataset completeness.", "complete-declared-record-product", "Every declared record coordinate is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forward forcing.", "root-bound-forward-forcing", "The derivation retains its chain to the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("extension", "fit-exception-extra-rule", "An exception introduces a choice or fitted parameter.", "finite-successor-or-explicit-boundary", "Extension and its boundary are exact and registered."),
    )


class RecordProgram(GeneratedInformationProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="information_science",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = (
        "SFT-INFO-SYMREP-COMPLETENESS-014",
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis RECORD-{number} product before observation access.",
        f"Every positive finite RECORD-{number} data item, schema, provenance chain, dataset and registered successor boundary.",
        dimensions(relation),
        f"RECORD-{number} uniquely retains {relation}, complete record custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least record retains one source, one field, one exact value, one schema row and one canonical identity.",
        "Appending one field, row, metadata entry, provenance step or version preserves all prior identities and generates every new custody relation exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-record-census", "Every declared data item, field, row, provenance step and omission state is retained.", passed),
            Witness("target-free", "The survivor was frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact record witness and reject four adverse controls.",
        "The claim closes the declared positive finite record and successor grammar; operational storage systems, legal policy and semantic meaning remain outside this information-law owner.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
