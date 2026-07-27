"""Post-seal authoritative evidence for the Materials successor claims."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import json
from pathlib import Path
import platform
import re

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.materials.derivation import MaterialsBlueprint
from sft.materials.successor_derivation import MATERIALS_SUCCESSOR_BLUEPRINTS


PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/materials_v1_v2_successor_complete_pre_source.json"


@dataclass(frozen=True)
class Source:
    source_id: str
    uri: str
    path: str
    digest: str


@dataclass(frozen=True)
class Requirement:
    source_id: str
    fragment: str


SOURCES = (
    Source("NIST-QUASICRYSTAL-APERIODIC-2026-07-27", "https://www.nist.gov/news-events/news/2025/04/rare-crystal-shape-found-increase-strength-3d-printed-metal", "experiments/external_sources/materials/snapshots/nist-quasicrystal-measurement.html", "sha256:a1b7cc0a5882502bb31b9706225b926c9ffb1e8d93ea5c0043249376c4d6ff18"),
    Source("NIST-PHONON-THERMAL-LIMITS-2026-07-27", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf", "experiments/external_sources/materials/snapshots/nist-phonon-thermal-limits-2026-07-27.txt", "sha256:208d3ff48584c6548ccb00d3b1559ba63d66b1fabe027af9bb499504d5cad64b"),
    Source("NIST-PN-RECTIFICATION-2026-07-27", "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir4414.pdf", "experiments/external_sources/materials/snapshots/nist-pn-rectification-2026-07-27.txt", "sha256:ca301b8fc47ba509909982ca2b077c238b92f3ff4978ed7377d086071c519ba4"),
    Source("NIST-SUPERCONDUCTING-ISOTOPE-2026-07-27", "https://nvlpubs.nist.gov/nistpubs/jres/094/jresv94n3p147_A1b.pdf", "experiments/external_sources/materials/snapshots/nist-superconducting-isotope-2026-07-27.txt", "sha256:48fa89f9f63d467e9259e766f81fd8f854924ad479ec0006d14075cfe48d3ae3"),
    Source("NIST-FERRIMAGNETIC-SUBLATTICES-2026-07-27", "https://www.nist.gov/publications/thickness-dependent-magnetism-variation-ferrimagnetic-rare-earthtransition-metal-fe1", "experiments/external_sources/materials/snapshots/nist-ferrimagnetism-2026-07-27.html", "sha256:685872920e5663b2ec71636b953d0e7ddec3d1cb679fb4f17bb94b6d6d811795"),
    Source("NIST-HALL-QUANTIZATION-2026-07-27", "https://www.nist.gov/programs-projects/integer-and-fractional-quantum-hall-effect", "experiments/external_sources/materials/snapshots/nist-hall-quantization-2026-07-27.html", "sha256:4536e34ab401e72216f8b9010bafc9f1cacdbbfc47ca8fc998b781fa9125994c"),
    Source("NIST-WATER-THERMOPHYSICAL-2026-07-27", "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=FFF&Units=CAL", "experiments/external_sources/materials/snapshots/nist-water-complete-2026-07-27.html", "sha256:ba9fc5225bc8d0d89cbe15703bff2d9dc06ef64244598c420c7666931f1befbf"),
    Source("NIST-LIQUID-WATER-DENSITY-2026-07-27", "https://www.nist.gov/document/jpcrd38200921ppdf", "experiments/external_sources/materials/snapshots/nist-liquid-water-properties-2026-07-27.txt", "sha256:b3af256bcffd7ff87fbf2aa00f545910a531d5a1b285fa9bb9f926f7afad9e24"),
    Source("NIST-ICE-DENSITY-2026-07-27", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=926353", "experiments/external_sources/materials/snapshots/nist-ice-properties-2026-07-27.txt", "sha256:7073b61255cf73163595c9ca25646dcf2c323dd2aca942d797f9f0e4dd6c178e"),
)
SOURCE_BY_ID = {row.source_id: row for row in SOURCES}

BINDINGS = {
    "SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002": (Requirement("NIST-QUASICRYSTAL-APERIODIC-2026-07-27", "pattern that fills the space, but never repeats"), Requirement("NIST-QUASICRYSTAL-APERIODIC-2026-07-27", "fivefold rotational symmetry")),
    "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002": (Requirement("NIST-PHONON-THERMAL-LIMITS-2026-07-27", "onelongitudinalmodeandthetwoshear"), Requirement("NIST-PHONON-THERMAL-LIMITS-2026-07-27", "dulongandpetitlimit")),
    "SFT-MAT-SEMI-RECTIFICATION-002": (Requirement("NIST-PN-RECTIFICATION-2026-07-27", "thisdirectionofpolarityiscalledforwardbias"), Requirement("NIST-PN-RECTIFICATION-2026-07-27", "obstructscurrentintheoppositedirection")),
    "SFT-MAT-SC-ISOTOPE-RESPONSE-002": (Requirement("NIST-SUPERCONDUCTING-ISOTOPE-2026-07-27", "in the isotope effect, the critical tem-"), Requirement("NIST-SUPERCONDUCTING-ISOTOPE-2026-07-27", "depends on the isotopic mass")),
    "SFT-MAT-MAG-FERRIMAGNETISM-002": (Requirement("NIST-FERRIMAGNETIC-SUBLATTICES-2026-07-27", "antiferromagnetically-aligned rare earth and transition metal sublattices"), Requirement("NIST-FERRIMAGNETIC-SUBLATTICES-2026-07-27", "reversal of the dominant magnetic sublattice")),
    "SFT-MAT-HALL-QUANTIZATION-002": (Requirement("NIST-HALL-QUANTIZATION-2026-07-27", "sharp, quantized energy levels"), Requirement("NIST-HALL-QUANTIZATION-2026-07-27", "fractional quantum hall effect"), Requirement("NIST-HALL-QUANTIZATION-2026-07-27", "even-denominator states")),
    "SFT-MAT-TOPO-EDGE-COUNT-002": (Requirement("NIST-HALL-QUANTIZATION-2026-07-27", "quantum hall edge states"), Requirement("NIST-HALL-QUANTIZATION-2026-07-27", "different colored plateaus")),
    "SFT-MAT-BULK-WATER-RESPONSE-002": (Requirement("NIST-WATER-THERMOPHYSICAL-2026-07-27", "373.17"), Requirement("NIST-WATER-THERMOPHYSICAL-2026-07-27", "liquid phase heat capacity"), Requirement("NIST-LIQUID-WATER-DENSITY-2026-07-27", "997.068 360"), Requirement("NIST-ICE-DENSITY-2026-07-27", "0 0.9167")),
}


@dataclass(frozen=True)
class SuccessorSpec:
    blueprint: MaterialsBlueprint
    source_ids: tuple[str, ...]
    target_id: str
    def __getattr__(self, name):
        return getattr(self.blueprint, name)
    @property
    def expected_observation_label(self):
        return self.blueprint.predicted_observation_label
    def validate(self):
        self.blueprint.validate()
        if not self.source_ids or any(x not in SOURCE_BY_ID for x in self.source_ids):
            raise ValueError("invalid successor source binding")


SPECS = tuple(SuccessorSpec(row, tuple(dict.fromkeys(x.source_id for x in BINDINGS[row.claim_id])), row.claim_id.lower()+"-external") for row in MATERIALS_SUCCESSOR_BLUEPRINTS)


def corpus(root: Path, source_id: str) -> str:
    text = (root / SOURCE_BY_ID[source_id].path).read_text(encoding="utf-8", errors="ignore")
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", text)).casefold().split())


def validate_pre_source_seal(root: Path) -> str:
    doc = json.loads((root / PRE_SOURCE_SEAL_PATH).read_text())
    claimed = doc.pop("sealed_payload_hash")
    if sha256_identity(doc) != claimed or doc["external_source_identities_selected"] is not False or doc["required_claim_count"] != 8:
        raise ValueError("successor pre-source seal invalid")
    for path, digest in doc["source_files"].items():
        if hash_file(root / path) != digest:
            raise ValueError("sealed successor source changed")
    return claimed


def prediction_document(spec):
    return {"schema":"sft-v3-fold-program/1","program_id":spec.experiment_id+"-prediction","instructions":[{"opcode":"input","destination":"premise","arguments":["registered-premise"]},{"opcode":"label","destination":"prediction","arguments":["materials-observation",spec.expected_observation_label]},{"opcode":"emit","destination":"","arguments":["prediction"]}]}


class BlindSuccessorMaterialsValidator:
    def __init__(self, root: Path, spec: SuccessorSpec): self.root, self.spec = root.resolve(), spec
    def validate(self, sealed):
        validate_pre_source_seal(self.root); self.spec.validate()
        receipts=[]
        for req in BINDINGS[self.spec.claim_id]:
            src=SOURCE_BY_ID[req.source_id]
            if hash_file(self.root/src.path)!=src.digest or req.fragment.casefold() not in corpus(self.root,req.source_id):
                raise ValueError("successor external source mismatch")
            receipts.append((req.source_id,src.digest,req.fragment))
        registration_hash=sha256_identity((self.spec.claim_id,validate_pre_source_seal(self.root),tuple(receipts)))
        program_document=prediction_document(self.spec); program=fold_program_from_mapping(program_document)
        inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}
        envelope=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},(self.spec.target_id,),sealed.seal_hash,registration_hash)
        vault=TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id+"-custodian",
            targets={self.spec.target_id:HeldLabel("external-observation",self.spec.expected_observation_label)},
            custody_nonce=sha256_identity(tuple(receipts)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before=snapshot_protected_tree(self.root); execution=CapabilityClosedFoldInterpreter().execute(program,inputs); boundary=BlindExperimentBoundary(envelope); prediction_seal=boundary.seal_prediction(execution.output,execution.trace); after=snapshot_protected_tree(self.root)
        audited,audit=HostilePackageAuditor().audit_program_document(program_document,before,after)
        if sha256_identity(audited)!=execution.program_hash or not audit.passed: raise ValueError("hostile audit failed")
        release=vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction_seal); boundary.measurement_context(release.targets)
        observed=release.targets[self.spec.target_id].label; passed=execution.output.label==observed
        isolation=seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id+"-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("successor-source-check",self.spec.experiment_id)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity=target_identity_from_release(release)
        custody=seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        return EmpiricalValidation(sealed.seal_hash,registration_hash,isolation,custody,True,True,True,self.spec.source_ids,(f"sealed prediction equals complete source-derived observation: {passed}","all registered rows preserved","tampered changed label rejected"),sha256_identity((registration_hash,tuple(receipts),passed)),self.spec.falsification_condition,passed)


__all__=("BlindSuccessorMaterialsValidator","PRE_SOURCE_SEAL_PATH","SOURCES","SOURCE_BY_ID","BINDINGS","SPECS","validate_pre_source_seal")
