"""Target commitment and post-seal release for portable blind experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from sft.engine.canonical import is_sha256_identity, sha256_identity
from sft.engine.empirical import PredictionSeal


class CustodyHalt(RuntimeError):
    """Fail-closed target commitment or release violation."""


@dataclass(frozen=True)
class TargetCommitment:
    experiment_id: str
    custodian_id: str
    target_ids: tuple[str, ...]
    target_identity_hash: str
    expected_envelope_hash: str
    commitment_hash: str


@dataclass(frozen=True)
class TargetRelease:
    experiment_id: str
    custodian_id: str
    prediction_seal_hash: str
    target_identity_hash: str
    targets: Mapping[str, object]
    custody_nonce: str
    release_hash: str


class TargetVault:
    """Distinct custodian state that cannot release before a matching seal."""

    def __init__(
        self,
        *,
        experiment_id: str,
        custodian_id: str,
        targets: Mapping[str, object],
        custody_nonce: str,
        expected_envelope_hash: str,
    ):
        if not experiment_id.strip() or not custodian_id.strip() or not custody_nonce.strip():
            raise CustodyHalt("target vault requires experiment, custodian and nonce identities")
        if not targets or any(not isinstance(key, str) or not key.strip() for key in targets):
            raise CustodyHalt("target vault requires complete named target support")
        if not is_sha256_identity(expected_envelope_hash):
            raise CustodyHalt("target vault requires the preregistered prediction-envelope identity")
        self._targets = dict(targets)
        self._nonce = custody_nonce
        self._released = False
        target_ids = tuple(sorted(targets))
        target_identity_hash = sha256_identity(
            tuple((target_id, custody_nonce, targets[target_id]) for target_id in target_ids)
        )
        commitment_payload = {
            "experiment_id": experiment_id,
            "custodian_id": custodian_id,
            "target_ids": target_ids,
            "target_identity_hash": target_identity_hash,
            "expected_envelope_hash": expected_envelope_hash,
        }
        self.commitment = TargetCommitment(
            commitment_hash=sha256_identity(commitment_payload),
            **commitment_payload,
        )

    def release(self, seal: PredictionSeal) -> TargetRelease:
        if self._released:
            raise CustodyHalt("target vault has already released its registered package")
        if seal.experiment_id != self.commitment.experiment_id:
            raise CustodyHalt("prediction seal belongs to a different experiment")
        if seal.envelope_hash != self.commitment.expected_envelope_hash:
            raise CustodyHalt("prediction seal is not bound to the preregistered envelope")
        payload = {
            "experiment_id": self.commitment.experiment_id,
            "custodian_id": self.commitment.custodian_id,
            "prediction_seal_hash": seal.seal_hash,
            "target_identity_hash": self.commitment.target_identity_hash,
            "targets": self._targets,
            "custody_nonce": self._nonce,
        }
        release = TargetRelease(release_hash=sha256_identity(payload), **payload)
        self._released = True
        return release


class CrossPlatformCustodyExchange:
    """Verify one commitment/release protocol independently of host paths."""

    exchange_id = "sft-v3-portable-target-exchange/1"

    @staticmethod
    def verify(commitment: TargetCommitment, release: TargetRelease, seal: PredictionSeal) -> None:
        violations: list[str] = []
        if release.experiment_id != commitment.experiment_id or seal.experiment_id != commitment.experiment_id:
            violations.append("experiment identities differ")
        if release.custodian_id != commitment.custodian_id:
            violations.append("custodian identity differs")
        if release.prediction_seal_hash != seal.seal_hash:
            violations.append("release is bound to a different prediction seal")
        if seal.envelope_hash != commitment.expected_envelope_hash:
            violations.append("prediction seal is bound to a different envelope")
        target_ids = tuple(sorted(release.targets))
        if target_ids != commitment.target_ids:
            violations.append("released target support differs from the commitment")
        target_identity_hash = sha256_identity(
            tuple((target_id, release.custody_nonce, release.targets[target_id]) for target_id in target_ids)
        )
        if target_identity_hash != commitment.target_identity_hash or release.target_identity_hash != commitment.target_identity_hash:
            violations.append("released target content differs from the pre-seal commitment")
        payload = {
            "experiment_id": release.experiment_id,
            "custodian_id": release.custodian_id,
            "prediction_seal_hash": release.prediction_seal_hash,
            "target_identity_hash": release.target_identity_hash,
            "targets": release.targets,
            "custody_nonce": release.custody_nonce,
        }
        if release.release_hash != sha256_identity(payload):
            violations.append("target release identity differs from its contents")
        if violations:
            raise CustodyHalt("; ".join(violations))


def target_identity_from_release(release: TargetRelease) -> str:
    """Expose the verified identity used by the isolation certificate."""

    if not is_sha256_identity(release.target_identity_hash):
        raise CustodyHalt("release target identity is invalid")
    return release.target_identity_hash
