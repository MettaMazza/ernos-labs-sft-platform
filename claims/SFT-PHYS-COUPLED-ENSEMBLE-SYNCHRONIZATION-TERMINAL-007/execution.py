"""Official execution binding for coupled-ensemble synchronization."""
from pathlib import Path
from sft.physics.coupled_ensemble_synchronization_terminal_execution_v1 import build_coupled_ensemble_synchronization_execution
def build_execution(root:Path): return build_coupled_ensemble_synchronization_execution(root,Path(__file__))
