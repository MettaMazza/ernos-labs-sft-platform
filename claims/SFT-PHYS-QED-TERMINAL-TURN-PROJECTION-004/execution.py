"""Official execution binding for SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_anomaly_execution_v1 import build_terminal_anomaly_execution


def build_execution(root: Path):
    return build_terminal_anomaly_execution(root, 'SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004', Path(__file__))
