"""Two-phase blind empirical boundary used by official experiment adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from sft.engine.canonical import sha256_identity


class TargetAccessViolation(RuntimeError):
    """Raised when target material is requested before a prediction seal."""


@dataclass(frozen=True)
class PredictionEnvelope:
    experiment_id: str
    registered_inputs: Mapping[str, str]
    withheld_target_ids: tuple[str, ...]
    frozen_relation_hash: str
    experiment_registration_hash: str


@dataclass(frozen=True)
class PredictionSeal:
    experiment_id: str
    prediction_hash: str
    trace_hash: str
    envelope_hash: str
    seal_hash: str


class BlindExperimentBoundary:
    """Keep target content outside the prediction phase and enforce seal order."""

    def __init__(self, envelope: PredictionEnvelope):
        self.envelope = envelope
        self._seal: Optional[PredictionSeal] = None

    @property
    def sealed(self) -> bool:
        return self._seal is not None

    def seal_prediction(self, prediction: object, trace: object) -> PredictionSeal:
        if self._seal is not None:
            raise TargetAccessViolation("prediction is already sealed and cannot be replaced")
        prediction_hash = sha256_identity(prediction)
        trace_hash = sha256_identity(trace)
        envelope_hash = sha256_identity(self.envelope)
        seal_hash = sha256_identity(
            {
                "experiment_id": self.envelope.experiment_id,
                "prediction_hash": prediction_hash,
                "trace_hash": trace_hash,
                "envelope_hash": envelope_hash,
            }
        )
        self._seal = PredictionSeal(
            experiment_id=self.envelope.experiment_id,
            prediction_hash=prediction_hash,
            trace_hash=trace_hash,
            envelope_hash=envelope_hash,
            seal_hash=seal_hash,
        )
        return self._seal

    def measurement_context(self, target_material: Mapping[str, object]) -> tuple[PredictionSeal, Mapping[str, object]]:
        if self._seal is None:
            raise TargetAccessViolation("target material cannot be opened before prediction seal")
        supplied = set(target_material)
        registered = set(self.envelope.withheld_target_ids)
        if supplied != registered:
            raise TargetAccessViolation("post-seal target identities do not match the registration")
        return self._seal, target_material
