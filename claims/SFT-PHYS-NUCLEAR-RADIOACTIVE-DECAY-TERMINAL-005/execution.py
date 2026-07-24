"""Official execution binding for SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005."""

from pathlib import Path

from sft.physics.radioactive_decay_successor_execution_v1 import build_radioactive_decay_execution


def build_execution(root: Path):
    return build_radioactive_decay_execution(root, Path(__file__))
