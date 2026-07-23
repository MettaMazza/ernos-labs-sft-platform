"""Cross-platform host mechanics quarantined from scientific semantics."""

from __future__ import annotations

import os
import platform
from typing import Mapping, Optional


SUPPORTED_HOST_FAMILIES = ("macos", "windows", "linux")


def host_family(system_name: Optional[str] = None) -> str:
    """Return a receipt-only host family, never a scientific branch selector."""

    detected = platform.system() if system_name is None else system_name
    normalized = detected.strip().lower()
    mapping = {"darwin": "macos", "windows": "windows", "linux": "linux"}
    if normalized not in mapping:
        raise RuntimeError(f"unsupported host family: {detected}")
    return mapping[normalized]


def portable_subprocess_environment(
    source: Optional[Mapping[str, str]] = None,
) -> dict[str, str]:
    """Build a minimal environment that also permits Windows process startup.

    Only host launch mechanics are retained. Arbitrary parent variables, API
    keys and possible target-bearing variables are excluded.
    """

    parent = dict(os.environ if source is None else source)
    allowed_names = {
        "comspec",
        "path",
        "pathext",
        "systemdrive",
        "systemroot",
        "temp",
        "tmp",
        "windir",
    }
    environment = {
        key: value
        for key, value in parent.items()
        if key.lower() in allowed_names
    }
    environment.update(
        {
            "LANG": "C",
            "LC_ALL": "C",
            "PYTHONHASHSEED": "0",
        }
    )
    return environment
