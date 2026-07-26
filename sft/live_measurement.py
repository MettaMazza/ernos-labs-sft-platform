"""Post-seal live comparison with machine-accessible measurement records.

This module is deliberately outside :mod:`sft.engine`. It cannot admit a
claim or alter a receipt. Complete derivation replay finishes first; only then
does this checker fetch the current authoritative table and compare the
already-forced results with its complete reported intervals.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sft.physics.atomic_constants import inverse_fine_structure
from sft.physics.atomic_constants_validation import codata_inverse_alpha_interval
from sft.physics.charged_lepton_validation import (
    SOURCE_PATH,
    comparison_record,
    koide_source_interval,
    source_interval,
)
from sft.physics.matter_flavour_terminal_proton_validation_v1 import (
    terminal_proton_prediction_interval,
)
from sft.physics.terminal_lepton_law import terminal_product_invariant


NIST_CODATA_URL = "https://physics.nist.gov/cuu/Constants/Table/allascii.txt"
USER_AGENT = "Ernos-Labs-SFT-V3-live-measurement/1"


class LiveMeasurementError(RuntimeError):
    """Raised when an authoritative row is unavailable or contradicts a seal."""


@dataclass(frozen=True)
class LiveMeasurementReport:
    source_id: str
    source_url: str
    exact_checks: tuple[str, ...]


def _fetch_nist_codata(timeout_seconds: int = 30) -> str:
    request = Request(NIST_CODATA_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise LiveMeasurementError(
            f"current NIST CODATA table is unavailable: {exc}"
        ) from exc
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LiveMeasurementError("current NIST CODATA table is not UTF-8") from exc
    if "inverse fine-structure constant" not in text:
        raise LiveMeasurementError("current NIST CODATA response lacks its required rows")
    return text


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LiveMeasurementError(message)


def run_live_measurement_checks(timeout_seconds: int = 30) -> LiveMeasurementReport:
    """Fetch current CODATA and compare already-forced V3 results exactly."""

    text = _fetch_nist_codata(timeout_seconds)
    checks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="sft-live-codata-") as temporary:
        root = Path(temporary)
        table = root / SOURCE_PATH
        table.parent.mkdir(parents=True)
        table.write_text(text, encoding="utf-8")

        alpha_lower, _, alpha_upper = codata_inverse_alpha_interval(table)
        _require(
            alpha_lower <= inverse_fine_structure() <= alpha_upper,
            "sealed inverse fine-structure result is outside current CODATA uncertainty",
        )
        checks.append("inverse-fine-structure-complete-interval")

        lepton = comparison_record(root, terminal_product_invariant())
        _require(
            bool(lepton["muon_electron"]["overlap"]),
            "sealed terminal muon/electron interval misses current CODATA uncertainty",
        )
        checks.append("terminal-muon-electron-complete-interval")
        _require(
            bool(lepton["muon_tau"]["overlap"]),
            "sealed terminal muon/tau interval misses current CODATA uncertainty",
        )
        checks.append("terminal-muon-tau-complete-interval")

        koide_lower, koide_upper = koide_source_interval(table)
        _require(
            koide_lower <= Fraction(2, 3) <= koide_upper,
            "sealed exact Koide two-thirds is outside the current CODATA-derived interval",
        )
        checks.append("koide-complete-two-row-interval")

        proton_lower, proton_upper = terminal_proton_prediction_interval()
        source_lower, _, source_upper = source_interval(
            table, "proton-electron mass ratio"
        )
        _require(
            source_lower <= proton_lower <= proton_upper <= source_upper,
            "sealed terminal proton/electron interval is outside current CODATA uncertainty",
        )
        checks.append("terminal-proton-electron-complete-interval")

    return LiveMeasurementReport(
        source_id="NIST-CODATA-CURRENT-ALL-CONSTANTS",
        source_url=NIST_CODATA_URL,
        exact_checks=tuple(checks),
    )


__all__ = (
    "LiveMeasurementError",
    "LiveMeasurementReport",
    "NIST_CODATA_URL",
    "run_live_measurement_checks",
)
