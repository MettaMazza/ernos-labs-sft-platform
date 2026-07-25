"""Official execution binding for PH2 exact rate-carrier correspondence."""
from pathlib import Path
from sft.physics.lyapunov_ks_correspondence_terminal_execution_v1 import build_lyapunov_ks_correspondence_execution
def build_execution(root:Path): return build_lyapunov_ks_correspondence_execution(root,Path(__file__))
