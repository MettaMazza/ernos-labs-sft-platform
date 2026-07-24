#!/usr/bin/env python3
"""Scaffold terminal turn, electron-anomaly and muon-anomaly packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.matter_flavour_terminal_anomaly_laws_v1 import ANOMALY_SPECS  # noqa: E402
from sft.physics.matter_flavour_terminal_anomaly_validation_v1 import (  # noqa: E402
    EMPIRICAL_SPEC_BY_ID,
    SOURCE_HASH,
    SOURCE_ID,
)
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402
from tools.scaffold_physics_measurement_claims import experiment_registration  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for spec in ANOMALY_SPECS:
        empirical = EMPIRICAL_SPEC_BY_ID.get(spec.claim_id)
        cardinality = 2 ** len(spec.axes)
        package = ROOT / "claims" / spec.claim_id
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": spec.claim_id,
            "title": spec.title,
            "branch": "physics",
            "status": "registered",
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "provenance_classes": [row.value for row in spec.provenance],
            "candidate_grammar": {
                "generator": spec.generation_rule,
                "boundary": spec.grammar_boundary,
                "completeness_certificate": sha256_identity(completeness_record(spec)),
            },
            "excluded_inputs": list(spec.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": (
                f"One engine receipt requiring all {cardinality:,} typed forms, one survivor, "
                "implementation-distinct exact reconstruction and complete hostile controls"
                + (
                    "."
                    if empirical is None
                    else ", followed by capability-gated release of the complete measurement interval."
                )
            ),
            "empirical_protocol": (
                None
                if empirical is None
                else f"experiments/physics/{empirical.experiment_id}/registration.json"
            ),
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-24",
        }
        axes = "\n".join(
            f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}"
            for axis in spec.axes
        )
        witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in spec.witnesses)
        exclusions = "\n".join(f"- {row}" for row in spec.exclusions)
        protocol = (
            "This is a formal exact Fold result and does not open a measurement target."
            if empirical is None
            else (
                "This uses the observational-derivation empirical prediction protocol. Observation informs "
                "the explicit law; the target is then placed behind the capability boundary; target-inaccessible "
                "engine execution enumerates every form, selects the sole survivor and seals the exact prediction; "
                "only then is the complete registered measurement interval released for comparison."
            )
        )
        note = f"""# {spec.claim_id}: WHY / DERIVATION / CHECK

## WHY

{spec.statement}

{protocol}

## DERIVATION

Grammar boundary: {spec.grammar_boundary}

The complete {len(spec.axes)}-axis grammar contains {cardinality:,} forms. Exactly one survives:

`{survivor_id(spec)}`

{axes}

Base: {spec.induction_base}

Successor: {spec.induction_step}

Exact result: {spec.exact_result}

## CHECK

{witnesses}

The engine regenerates all {cardinality:,} forms, retains one survivor, passes four hostile controls and
requires an implementation-distinct exact reconstruction. {"No target is opened." if empirical is None else "The measurement capability opens only after the derivation seal."}

## EXCLUSIONS

{exclusions}
"""
        execution = f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_anomaly_execution_v1 import build_terminal_anomaly_execution


def build_execution(root: Path):
    return build_terminal_anomaly_execution(root, {spec.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        if empirical is not None:
            experiment = experiment_registration(empirical)
            experiment["evidence_mode"] = "observational_derivation"
            experiment["development_observations"] = [{
                "source_id": SOURCE_ID,
                "role": "development_only",
                "content_hash": SOURCE_HASH,
            }]
            target = ROOT / "experiments" / "physics" / empirical.experiment_id
            write(target / "registration.json", json.dumps(experiment, indent=2) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
