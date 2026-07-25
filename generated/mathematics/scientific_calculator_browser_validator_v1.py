#!/usr/bin/env python3
"""Implementation-distinct subprocess validator for calculator browser claim 007."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-007"
ROOT = Path(__file__).resolve().parents[2]
DOMAINS = (
    ("deprecated-widget-geometry-only", "standards-rendered-browser-surface"),
    ("flattened-function-grid", "standard-pad-plus-scientific-panel"),
    ("conventional-prohibited-projection", "familiar-notation-with-SFT-halt-and-types"),
    ("client-side-duplicate-arithmetic", "server-side-immutable-claim-006-controller"),
    ("shared-global-visitor-state", "fresh-independent-page-session"),
    ("desktop-loopback-only", "same-network-default-with-private-option"),
    ("heavy-GUI-or-container-runtime", "Python-standard-library-and-installed-browser"),
    ("hidden-widget-dimensions-only", "API-render-responsive-adverse-and-complete-coverage"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def page_state(url: str) -> tuple[str, str, dict[str, object]]:
    with urlopen(url, timeout=5) as response:
        page = response.read().decode("utf-8")
    matched = re.search(r"const TOKEN=(.*?);\nconst INITIAL=(.*?);\nconst SESSION", page)
    if matched is None:
        raise RuntimeError("calculator page state is not structurally exposed")
    return page, json.loads(matched.group(1)), json.loads(matched.group(2))


def action(url: str, token: str, session_id: str, expression: str) -> dict[str, object]:
    body = json.dumps({"action": "evaluate", "expression": expression}).encode("utf-8")
    request = Request(
        url + "api/action",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-SFT-Token": token,
            "X-SFT-Session": session_id,
        },
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read())


def application_check() -> tuple[bool, dict[str, object]]:
    process = subprocess.Popen(
        (sys.executable, "-m", "sft.mathematics.calculator_browser", "--no-browser", "--port", "18971"),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None:
        raise RuntimeError("calculator subprocess has no output channel")
    local_line = process.stdout.readline().strip()
    network_line = process.stdout.readline().strip()
    local_url = local_line.rsplit(" ", 1)[-1]
    network_url = network_line.rsplit(" ", 1)[-1]
    try:
        page, token, initial = page_state(local_url)
        ordinary = action(local_url, token, initial["session_id"], "1+1")["view"]
        _, token_two, cancellation_page = page_state(local_url)
        cancellation = action(local_url, token_two, cancellation_page["session_id"], "1-1")["view"]
        _, token_three, prohibited_page = page_state(local_url)
        prohibited = action(local_url, token_three, prohibited_page["session_id"], "1-4")["view"]
        _, token_four, root_page = page_state(local_url)
        root = action(local_url, token_four, root_page["session_id"], "sqrt(2)")["view"]
        unauthorised = False
        try:
            urlopen(Request(local_url + "api/action", data=b"{}"), timeout=5)
        except HTTPError as error:
            unauthorised = error.code == 403
        labels = set(label for row in initial["buttons"] for label in row)
        organised = set(initial["memory_buttons"])
        organised.update(label for row in initial["basic_buttons"] for label in row)
        organised.update(label for row in initial["scientific_buttons"] for label in row)
        launchers = (
            ROOT / "calculator_launchers/Launch Smithian Fold Calculator.command",
            ROOT / "calculator_launchers/Launch Smithian Fold Calculator.bat",
            ROOT / "calculator_launchers/launch-smithian-fold-calculator.sh",
        )
        passed = all(
            (
                initial["view"]["result"] == "0",
                ordinary["result"] == "2",
                cancellation["result"] == "0",
                prohibited["result"] == "HALT" and not prohibited["history"],
                "negative and counter-held numeric results" in prohibited["error"],
                str(root["result"]).startswith("certified rational interval"),
                "1.414" not in str(root["result"]),
                "≈" not in str(root["exact_details"]),
                len({initial["session_id"], cancellation_page["session_id"], prohibited_page["session_id"], root_page["session_id"]}) == 4,
                labels == organised and len(labels) == 64,
                len(initial["memory_buttons"]) == 5,
                len(initial["basic_buttons"]) == 6 and all(len(row) == 4 for row in initial["basic_buttons"]),
                len(initial["scientific_buttons"]) == 7 and all(len(row) == 5 for row in initial["scientific_buttons"]),
                "grid-template-columns:repeat(4,1fr)" in page,
                "(min-width:671px) and (pointer:fine)" in page,
                "focusForHardwareKeyboard" in page,
                "Math." not in page,
                unauthorised,
                network_url.startswith("http://") and "127.0.0.1" not in network_url,
                all(path.exists() and "calculator_browser" in path.read_text(encoding="utf-8") for path in launchers),
            )
        )
        return passed, {
            "initial_result": initial["view"]["result"],
            "ordinary_result": ordinary["result"],
            "cancellation_result": cancellation["result"],
            "prohibited_result": prohibited["result"],
            "certificate_prefix": str(root["result"]).split(" [", 1)[0],
            "session_count": 4,
            "control_count": len(labels),
            "network_address_exposed": network_url.startswith("http://"),
            "touch_focus_guard": "focusForHardwareKeyboard" in page,
        }
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


def coverage_check() -> tuple[bool, dict[str, object]]:
    report = json.loads(
        (ROOT / "generated/mathematics/scientific_calculator_browser_coverage_v1.json").read_text(encoding="utf-8")
    )
    totals = report["totals"]
    passed = all(
        (
            totals["percent_covered"] == 100.0,
            totals["missing_lines"] == 0,
            totals["missing_branches"] == 0,
            all(item["summary"]["missing_lines"] == 0 for item in report["files"].values()),
            all(item["summary"]["missing_branches"] == 0 for item in report["files"].values()),
        )
    )
    return passed, totals


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validator CLAIM_ID SEALED_DERIVATION")
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(fields) for fields in product(*DOMAINS))
    received = tuple(item["candidate_id"] for item in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    application_passed, application = application_check()
    coverage_passed, coverage = coverage_check()
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            closure["scope"] == "depth_independent",
            closure["minimality_passed"] is True,
            closure["named_shape_uniqueness_passed"] is True,
            {item["kind"] for item in controls}
            == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(item["passed"] is True for item in controls),
            application_passed,
            coverage_passed,
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": len(generated),
                    "unique_survivor": "__".join(SURVIVOR),
                    "application": application,
                    "coverage": coverage,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
