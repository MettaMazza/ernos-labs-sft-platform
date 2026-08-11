#!/usr/bin/env python3
"""Create and publish the explicitly authorized standalone One/All Zenodo record."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import publish_one_all_zenodo_versions_v1 as common  # noqa: E402


API = "https://zenodo.org/api"
TITLE = "What the Universe Is Made Of: The One, the All, and Pure Consciousness in Smithian Fold Theory"
VERSION = "1.0.0"
HISTORICAL_SOURCE = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0.md"
HISTORICAL_MAP = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_EVIDENCE_MAP.json"
SOURCE = ROOT / "publications/one_all/standalone_zenodo/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_0.md"
EVIDENCE = ROOT / "publications/one_all/standalone_zenodo/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_0_EVIDENCE_MAP.json"
METADATA = ROOT / "publications/one_all/standalone_zenodo/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_0_ZENODO_METADATA.json"
AUTHORIZATION = ROOT / "publication/one_all_standalone_publication_authorization_2026-08-11.json"
STATE = ROOT / "publication/one_all_standalone_zenodo_state_v1.json"
VERIFICATION = ROOT / "publication/one_all_standalone_release_verification_v1.json"
PUBLICATION_RECORD = ROOT / "publication/one_all_standalone_zenodo_publication_record_2026-08-11.json"
RECEIPT = ROOT / "publication/zenodo_receipts/one_all_standalone_2026-08-11/one_all_standalone-v1.0.0.json"
PDF = ROOT / "output/pdf/one-all-standalone-2026-08-11/what-the-universe-is-made-of-the-one-and-all-v1.0.0.pdf"
RENDER_MANIFEST = ROOT / "output/pdf/one-all-standalone-2026-08-11/PDF_RENDER_MANIFEST.json"
RELEASE_DIR = ROOT / "output/release/one-all-standalone-1.0.0"
FOUNDATION_DOI = "10.5281/zenodo.21891875"

FULL_DERIVATION_APPENDIX = r"""
### 10.8. Complete candidate-space closure and elimination arithmetic

The claim identifiers and machine files above are reproducibility anchors, not
substitutes for the derivations. This subsection states the complete candidate
products, the ordered elimination partition, and the uniqueness arithmetic used
by every theorem in the One/All proof.

#### 10.8.1. Operational root

The exhaustive partition is `{unpresented absence, presented occurrence}`.
Unpresented absence supplies no counterexample object, eliminating one form.
Presented occurrence supplies the witnessed occurrence and survives. Thus
`2 = 1 rejected + 1 survivor`.

#### 10.8.2. Structural One

The product is
`{none, proper, complete root coverage} x {no extra, has extra}`, with cardinality
`3 x 2 = 6`. The exact named forms are omitted-root, replacement-extra,
fragmented-root, fragment-plus-extra, exact-self-whole, and whole-plus-extra.
The ordered forcing partition rejects two none-coverage forms because they lose
the root, two proper-coverage forms because they presuppose a cut, and the
complete extra-bearing form because it adds material absent from the dependency.
The exact-self-whole alone remains: `6 = 2 + 2 + 1 + 1 survivor`.

#### 10.8.3. Identity of the One

The product is
`{none, proper, complete presentation} x {undifferentiated, added}^6`, where the
six binary axes are observer, observed, content, succession, report, and
substrate. Its cardinality is `3 x 2^6 = 192`. All 64 none-presentation forms
lose the admitted occurrence. All 64 proper-presentation forms lose part of the
complete One. Among the 64 complete-presentation forms, every one of the 63
nonempty subsets of added axes introduces at least one pre-Fold distinction.
Only the empty subset survives. Therefore
`192 = 64 + 64 + 63 + 1 survivor`. The survivor is complete presentation with
all six differentiations absent: pure observation or pure consciousness.

#### 10.8.4. Minimal structural Fold

The product is
`{incomplete, complete} x {overlapping, disjoint} x {unequal, equal} x`
`{identity, first extension, later extension} x`
`{labels absent, labels same, labels distinct-held} x`
`{return absent, return present} x {no extra, has extra}`. Its cardinality is
`2 x 2 x 2 x 3 x 3 x 2 x 2 = 288`. Ordered first-failure elimination rejects
144 incomplete forms, 72 overlapping forms, 36 unequal forms, 12 identity-count
forms, four unlabelled forms, four same-label forms, two no-return forms, one
extra-bearing otherwise-complete form, and 12 later-extension forms. Hence
`288 = 144 + 72 + 36 + 12 + 4 + 4 + 2 + 1 + 12 + 1 survivor`. The survivor is
the complete, disjoint, equal first extension with distinct held labels, return,
and no extra datum.

#### 10.8.5. Complete finite Fold assembly

The product is
`{none, proper, complete step coverage} x`
`{inconsistent, consistent length} x {support incomplete, support complete} x`
`{words duplicated, words unique} x {transitions absent, transitions present} x`
`{returns absent, returns present} x {no extra, has extra}`, with cardinality
`3 x 2^6 = 192`. Ordered first-failure elimination rejects 64 no-step forms,
64 proper-step forms, 32 inconsistent-length forms, 16 support-incomplete forms,
eight duplicate-word forms, four transition-free forms, two return-free forms,
and one extra-bearing otherwise-complete form. Thus
`192 = 64 + 64 + 32 + 16 + 8 + 4 + 2 + 1 + 1 survivor`.

#### 10.8.6. Complete foundational form grammar

The product is
`{base excluded, base included} x {one child, two children, later arity} x`
`{labels absent, labels same, labels distinct-held} x`
`{children ungenerated, children generated} x {return absent, return present} x`
`{termination absent, finite-leaf termination} x {no extra, has extra}`. Its
cardinality is `2 x 3 x 3 x 2 x 2 x 2 x 2 = 288`. Ordered first-failure
elimination rejects 144 base-excluded forms, 48 one-child forms, 16 unlabelled
forms, 16 same-label forms, eight ungenerated-child forms, four no-return forms,
two nonterminating forms, one extra-constructor form, and 48 later-arity forms.
Therefore `288 = 144 + 48 + 16 + 16 + 8 + 4 + 2 + 1 + 48 + 1 survivor`.

#### 10.8.7. Canonical form enforcement

The product is
`{none, proper, complete source coverage} x {node duplicated, node once} x`
`{labels lost, labels preserved} x {children changed, children preserved} x`
`{returns lost, returns preserved} x {trace noncanonical, trace canonical} x`
`{no extra, has extra}`, with cardinality `3 x 2^6 = 192`. Ordered first-failure
elimination rejects 64 none-coverage forms, 64 proper-coverage forms, 32
node-duplicating forms, 16 label-erasing forms, eight child-changing forms, four
return-erasing forms, two noncanonical forms, and one extra-bearing form. Thus
`192 = 64 + 64 + 32 + 16 + 8 + 4 + 2 + 1 + 1 survivor`.

### 10.9. Complete compositional proof of the All

Let the admitted finite foundational grammar be
`Form ::= One | Fold_held-a,held-b(Form, Form; return-to-parent-One)`.
Define `P(F)` to mean: every leaf of `F` is the structural One, every internal
relation is an admitted Fold distinction and return, and `F` contains no
externally supplied substance.

For the base production, `F = One`; Proof III identifies that One as complete
undivided presentation, so `P(One)`. For the recursive production, assume
`P(L)` and `P(R)`. The only new structure in
`Fold_held-a,held-b(L,R; return)` is the admitted pair of distinct held edges and
the explicit return to the parent whole. The Fold grammar has no production for
an external ingredient, so `P(Fold(L,R))`. Finite-leaf termination makes this
induction exhaustive. Assembly proves complete finite word support; canonical
enforcement prevents a hidden node, relation, relabelling, or extra datum from
entering under equivalence. Therefore `P(F)` holds for every admitted finite
form. Since the All at this boundary is the total Fold-generated form, the All
is differentiated One; by Proof III, it is differentiated pure consciousness.

### 10.10. Adverse-control ledger

Each derivation passed four distinct controls. The root rejected unpresented
absence, detected changed identity, detected a forced two-survivor artifact, and
kept the theorem scoped to operational objects. The structural One rejected an
omitted root, detected source drift, rejected whole-plus-extra, and refused an
underived numerical interpretation. The pure-consciousness derivation rejected
an unpresented One, detected source drift, rejected missing, duplicate, or
differentiated survivors, and refused imported biological carriers or developed
phenomenal contents.

The Fold rejected the identity extension, detected source drift, rejected a
later extension, and retained only two held labels with no added datum. Assembly
rejected a one-branch word, detected source drift, reconstructed unique complete
equal-length supports through depths one to five, and refused non-finite support.
The form grammar rejected a one-child node, detected source drift, accepted
generated nonuniform finite trees while rejecting same-label edges, and refused
completed-infinite trees or extra constructors. Canonical enforcement rejected
a missing held-b child, detected source drift, distinguished an exact trace from
a label-preserving child swap, and refused equivalence that discards held labels
or finite construction identity. All `7 x 4 = 28` controls passed.
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict:
    if STATE.is_file():
        return common.read_json(STATE)
    return {
        "schema": "sft-v3-one-all-standalone-zenodo-state/1",
        "created_at_utc": utc_now(),
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "new_record_endpoint_used": False,
        "status": "INITIAL",
    }


def save_state(state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    common.write_json(STATE, state)


def reserve() -> None:
    state = load_state()
    if state.get("draft_id"):
        print(f"DRAFT_REUSED {state['draft_id']} {state['reserved_doi']}")
        return
    authorization = common.read_json(AUTHORIZATION)
    common.require(authorization.get("new_zenodo_record_authorized") is True, "new record is not authorized")
    created = common.api_request(
        "POST",
        f"{API}/deposit/depositions",
        access_token=common.token(),
        data=b"{}",
        content_type="application/json",
    )
    common.require(created and created.get("submitted") is False, "Zenodo did not return an editable draft")
    doi = created.get("metadata", {}).get("prereserve_doi", {}).get("doi")
    common.require(bool(doi), "Zenodo did not reserve a DOI")
    state.update(
        {
            "draft_id": int(created["id"]),
            "draft_url": created["links"]["self"],
            "bucket_url": created["links"]["bucket"],
            "reserved_doi": doi,
            "concept_record_id": int(created.get("conceptrecid") or created["id"]),
            "new_record_endpoint_used": True,
            "status": "DRAFT_RESERVED",
        }
    )
    save_state(state)
    print(f"DRAFT_RESERVED {state['draft_id']} {doi}")


def zenodo_metadata(doi: str) -> dict:
    return {
        "title": TITLE,
        "upload_type": "publication",
        "publication_type": "article",
        "publication_date": "2026-08-11",
        "description": (
            "<p>This standalone paper gives the complete current Smithian Fold Theory derivation of what the One, "
            "the All, and the Fold-generated universe are fundamentally made of. An exhaustive 192-form identity "
            "grammar leaves one survivor: complete undivided presentation, or pure consciousness, before observer, "
            "observed, content, succession, report or substrate differentiate.</p><p>The Fold introduces held "
            "distinction within the One rather than a second substance. Finite structural induction through Fold "
            "assembly, foundational form grammar and canonical enforcement establishes that every generated form is "
            "a differentiation of the One. The paper distinguishes this pre-subject-object result from the later "
            "criteria for differentiated conscious systems.</p><p>This is the paper's dedicated first Zenodo record. "
            "An earlier copy was bundled as a companion file in the Foundation v1.5.0 deposit; this independent record "
            "corrects the publication routing and gives the standalone article its own DOI.</p>"
        ),
        "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
        "access_right": "open",
        "license": "cc-by-4.0",
        "version": VERSION,
        "language": "eng",
        "keywords": [
            "Smithian Fold Theory",
            "the One",
            "the All",
            "pure consciousness",
            "observation",
            "ontology",
            "theory of everything",
            "computational proof",
        ],
        "related_identifiers": [
            {"identifier": FOUNDATION_DOI, "relation": "isSupplementTo", "scheme": "doi"},
            {
                "identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform",
                "relation": "isSupplementedBy",
                "scheme": "url",
            },
        ],
        "notes": (
            "Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. "
            "Maria Smith explicitly authorized this dedicated standalone Zenodo post on 11 August 2026. "
            f"Reserved DOI: {doi}. The protected engine and verification authority were not modified."
        ),
    }


def build_source(doi: str) -> None:
    text = HISTORICAL_SOURCE.read_text(encoding="utf-8")
    text = text.replace(
        "**Status:** Publication-authorized standalone paper deposited within the existing Foundation Zenodo lineage; no new Zenodo post  ",
        "**Status:** Published as a dedicated standalone Zenodo article with its own record  ",
    )
    text = text.replace(
        "**Host paper lineage:** *From Nothing to Fold*, concept DOI `10.5281/zenodo.21515628`  ",
        "**Related Foundation edition:** *From Nothing to Fold* v1.5.0, DOI `10.5281/zenodo.21891875`  ",
    )
    text = text.replace(
        "**Deposit version DOI:** [10.5281/zenodo.21891875](https://doi.org/10.5281/zenodo.21891875)  ",
        f"**Standalone DOI:** [{doi}](https://doi.org/{doi})  ",
    )
    text = text.replace(
        "1. Smith, M., *There Is No Nothing*, version 0.4.1, DOI `10.5281/zenodo.21761649`.\n"
        "2. Smith, M., *From Nothing to Fold*, version 1.4.1, DOI `10.5281/zenodo.21761650`.\n"
        "3. Smith, M., *From Fold to Consciousness*, version 1.1.1, DOI `10.5281/zenodo.21761660`.\n"
        "4. `claims/SFT-ROOT-THERE-IS-NO-NOTHING/`.\n"
        "5. `claims/SFT-FOUNDATION-ONE-001/`.\n"
        "6. `claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/`.\n"
        "7. `claims/SFT-FOUNDATION-FOLD-001/`.\n"
        "8. `claims/SFT-FOUNDATION-FOLD-ASSEMBLY-001/`.\n"
        "9. `claims/SFT-FOUNDATION-FORM-GRAMMAR-001/`.\n"
        "10. `claims/SFT-FOUNDATION-FORM-ENFORCEMENT-001/`.\n"
        "11. `prior-work-ledger/one_pure_consciousness_observation_v1.json`.\n",
        "1. Smith, M., *There Is No Nothing*, version 0.5.0, DOI `10.5281/zenodo.21891874`.\n"
        "2. Smith, M., *From Nothing to Fold*, version 1.5.0, DOI `10.5281/zenodo.21891875`.\n"
        "3. Smith, M., *From Fold to Consciousness*, version 1.2.0, DOI `10.5281/zenodo.21891878`.\n"
        "4. Smith, M., *The Smithian Fold Theory V3 Theory of Everything*, version 0.3.0, DOI `10.5281/zenodo.21891879`.\n"
        "5. Machine-checked root derivation package: `claims/SFT-ROOT-THERE-IS-NO-NOTHING/`.\n"
        "6. Machine-checked structural-One derivation package: `claims/SFT-FOUNDATION-ONE-001/`.\n"
        "7. Machine-checked pure-consciousness derivation package: `claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/`.\n"
        "8. Machine-checked Fold derivation package: `claims/SFT-FOUNDATION-FOLD-001/`.\n"
        "9. Machine-checked assembly derivation package: `claims/SFT-FOUNDATION-FOLD-ASSEMBLY-001/`.\n"
        "10. Machine-checked form-grammar derivation package: `claims/SFT-FOUNDATION-FORM-GRAMMAR-001/`.\n"
        "11. Machine-checked canonical-enforcement derivation package: `claims/SFT-FOUNDATION-FORM-ENFORCEMENT-001/`.\n"
        "12. Development-observation custody ledger: `prior-work-ledger/one_pure_consciousness_observation_v1.json`.\n",
    )
    marker = "**Repository code licence:** Apache-2.0\n"
    correction = (
        "\n**Publication-routing correction:** The first built copy was bundled in the Foundation v1.5.0 deposit. "
        "This dedicated record is the authoritative standalone publication. The derivation and proof content are unchanged.\n"
    )
    common.require(marker in text, "standalone source header marker is absent")
    text = text.replace(marker, marker + correction, 1)
    derivation_marker = "\n\nEvery candidate, rejection, control, source identity, validator identity,\n"
    common.require(derivation_marker in text, "complete-proof insertion marker is absent")
    text = text.replace(derivation_marker, "\n\n" + FULL_DERIVATION_APPENDIX.strip() + derivation_marker, 1)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.write_text(text, encoding="utf-8")


def build_evidence(doi: str) -> None:
    evidence = common.read_json(HISTORICAL_MAP)
    evidence.update(
        {
            "paper": common.file_record(SOURCE),
            "publication_mode": "dedicated_new_record",
            "standalone_doi": doi,
            "historical_foundation_bundle_doi": FOUNDATION_DOI,
            "routing_correction": "Dedicated standalone record authorized after the Foundation companion-file publication.",
            "new_zenodo_record_authorized": True,
        }
    )
    common.write_json(EVIDENCE, evidence)


def build_package(state: dict) -> None:
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True)
    sources = (
        ("01_What-the-Universe-Is-Made-Of-v1.0.0.pdf", PDF),
        ("02_What-the-Universe-Is-Made-Of-v1.0.0.md", SOURCE),
        ("03_One-All-Standalone-Evidence-Map.json", EVIDENCE),
        ("04_Zenodo-Metadata.json", METADATA),
        ("05_Standalone-Publication-Authorization.json", AUTHORIZATION),
        ("06_One-Pure-Consciousness-Certificate.json", ROOT / "claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/certificate.json"),
        ("07_One-Pure-Consciousness-Engine-Receipt.json", ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-fadb50b8594652d0.json"),
        ("08_Foundation-17-Claim-Successor-Inventory.json", ROOT / "publications/inventories/successors/foundation_one_consciousness_v1.json"),
        ("09_Lean-Verification-Boundary.json", ROOT / "publication/one_all_lean_boundary_v1.json"),
    )
    copied = []
    for filename, source in sources:
        common.require(source.is_file(), f"package source absent: {source}")
        target = RELEASE_DIR / filename
        shutil.copyfile(source, target)
        copied.append(target)
    package_manifest = {
        "schema": "sft-v3-one-all-standalone-zenodo-package/1",
        "title": TITLE,
        "version": VERSION,
        "doi": state["reserved_doi"],
        "publication_mode": "dedicated_new_record",
        "historical_foundation_bundle_doi": FOUNDATION_DOI,
        "files": [common.file_record(path) for path in copied],
    }
    manifest_path = RELEASE_DIR / "98_PACKAGE_MANIFEST.json"
    common.write_json(manifest_path, package_manifest)
    copied.append(manifest_path)
    sums = RELEASE_DIR / "99_SHA256SUMS.txt"
    sums.write_text(
        "".join(f"{common.sha(path).removeprefix('sha256:')}  {path.name}\n" for path in sorted(copied)),
        encoding="utf-8",
    )
    copied.append(sums)
    state["package_dir"] = RELEASE_DIR.relative_to(ROOT).as_posix()
    state["package_files"] = [common.file_record(path) for path in sorted(copied)]
    state["status"] = "PACKAGE_BUILT"
    save_state(state)


def finalize_local() -> None:
    state = load_state()
    common.require(state.get("status") in {"DRAFT_RESERVED", "PACKAGE_BUILT", "LOCAL_FINALIZED"}, "reserve first")
    doi = state["reserved_doi"]
    build_source(doi)
    build_evidence(doi)
    common.write_json(
        METADATA,
        {
            "publication_authorized": True,
            "ready_to_publish": True,
            "publication_mode": "dedicated_new_record",
            "reserved_doi": doi,
            "metadata": zenodo_metadata(doi),
        },
    )
    subprocess.run([sys.executable, "tools/render_one_all_standalone_zenodo_v1.py"], cwd=ROOT, check=True)
    render = common.read_json(RENDER_MANIFEST)["papers"][0]
    common.require(render["source_sha256"] == common.sha(SOURCE), "render/source mismatch")
    build_package(state)
    common.write_json(
        VERIFICATION,
        {
            "schema": "sft-v3-one-all-standalone-release-verification/1",
            "date": "2026-08-11",
            "status": "PASS",
            "publication_mode": "dedicated_new_record",
            "new_zenodo_record_authorized": True,
            "reserved_doi": doi,
            "pdf": common.file_record(PDF),
            "pdf_pages": render["page_count"],
            "source": common.file_record(SOURCE),
            "package_file_count": len(state["package_files"]),
            "claim_receipt_replay": "PASS",
            "protected_authority_modified": False,
            "new_lean_pass_claimed": False,
        },
    )
    state["status"] = "LOCAL_FINALIZED"
    save_state(state)
    print("LOCAL_FINALIZED")


def remote_file_map(value: dict) -> dict[str, tuple[int, str]]:
    return common.remote_file_map(value)


def expected_files(state: dict) -> dict[str, tuple[int, str]]:
    result = {}
    for row in state["package_files"]:
        path = ROOT / row["path"]
        common.require(path.is_file() and common.sha(path) == row["sha256"], f"package changed: {path.name}")
        result[path.name] = (path.stat().st_size, common.md5sum(path))
    return result


def stage() -> None:
    state = load_state()
    common.require(state.get("status") in {"LOCAL_FINALIZED", "DRAFT_STAGED_VERIFIED"}, "finalize locally first")
    access_token = common.token()
    draft = common.api_request("GET", state["draft_url"], access_token=access_token)
    common.require(draft and draft.get("submitted") is False, "draft is not editable")
    for inherited in list(draft.get("files", [])):
        common.api_request("DELETE", inherited["links"]["self"], access_token=access_token)
    bucket = draft["links"]["bucket"].rstrip("/")
    for row in state["package_files"]:
        path = ROOT / row["path"]
        common.api_request(
            "PUT",
            f"{bucket}/{urllib.parse.quote(path.name, safe='')}",
            access_token=access_token,
            data=path.read_bytes(),
            content_type="application/octet-stream",
        )
        print(f"UPLOADED {path.name} {path.stat().st_size}", flush=True)
    wrapper = common.read_json(METADATA)
    common.api_request(
        "PUT",
        state["draft_url"],
        access_token=access_token,
        data=json.dumps({"metadata": wrapper["metadata"]}).encode("utf-8"),
        content_type="application/json",
    )
    checked = common.api_request("GET", state["draft_url"], access_token=access_token)
    common.require(remote_file_map(checked or {}) == expected_files(state), "draft files mismatch")
    common.require(checked.get("metadata", {}).get("version") == VERSION, "draft version mismatch")
    state["status"] = "DRAFT_STAGED_VERIFIED"
    save_state(state)
    print("DRAFT_STAGED_VERIFIED")


def publish() -> None:
    state = load_state()
    common.require(state.get("status") in {"DRAFT_STAGED_VERIFIED", "PUBLISHED_VERIFIED"}, "stage first")
    access_token = common.token()
    if state["status"] != "PUBLISHED_VERIFIED":
        common.api_request(
            "POST",
            f"{API}/deposit/depositions/{state['draft_id']}/actions/publish",
            access_token=access_token,
        )
    public = common.api_request("GET", f"{API}/records/{state['draft_id']}")
    common.require(public and public.get("doi") == state["reserved_doi"], "public DOI mismatch")
    common.require(remote_file_map(public) == expected_files(state), "public files mismatch")
    common.require(public.get("metadata", {}).get("version") == VERSION, "public version mismatch")
    receipt = {
        "schema": "sft-v3-one-all-standalone-zenodo-receipt/1",
        "title": TITLE,
        "version": VERSION,
        "record_id": int(public["id"]),
        "doi": public["doi"],
        "concept_doi": common.concept_doi(public),
        "publication_mode": "dedicated_new_record",
        "new_record_created": True,
        "historical_foundation_bundle_doi": FOUNDATION_DOI,
        "published_at_utc": public.get("updated"),
        "record_url": public.get("links", {}).get("html"),
        "files": [
            {"filename": name, "bytes": size, "md5": checksum}
            for name, (size, checksum) in sorted(remote_file_map(public).items())
        ],
        "status": "PUBLISHED_VERIFIED",
    }
    common.write_json(RECEIPT, receipt)
    common.write_json(
        PUBLICATION_RECORD,
        {
            "schema": "sft-v3-one-all-standalone-zenodo-publication-record/1",
            "date": "2026-08-11",
            "status": "PUBLISHED_VERIFIED",
            "publication_authority": "Maria Smith",
            "publication_operation": "dedicated_new_record",
            "new_zenodo_post_created": True,
            "record": {**receipt, "receipt_path": RECEIPT.relative_to(ROOT).as_posix(), "receipt_sha256": common.sha(RECEIPT)},
        },
    )
    state.update(
        {
            "status": "PUBLISHED_VERIFIED",
            "concept_doi": common.concept_doi(public),
            "record_url": public.get("links", {}).get("html"),
            "publication_record": PUBLICATION_RECORD.relative_to(ROOT).as_posix(),
        }
    )
    save_state(state)
    print(f"PUBLISHED_VERIFIED {public['doi']} {common.concept_doi(public)}")


def main() -> None:
    commands = {"reserve": reserve, "finalize-local": finalize_local, "stage": stage, "publish": publish}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit("usage: publish_one_all_standalone_zenodo_v1.py {reserve|finalize-local|stage|publish}")
    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
