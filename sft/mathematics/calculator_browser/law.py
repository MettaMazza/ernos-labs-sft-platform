"""Force the accessible, SFT-native browser adapter over calculator claim 006."""

from __future__ import annotations

import json
from pathlib import Path

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension

from .app import (
    BASIC_BUTTON_ROWS,
    CalculatorWebApplication,
    MEMORY_BUTTONS,
    SCIENTIFIC_BUTTON_ROWS,
)
from .page import render_page


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-007"
DEPENDENCIES = ("SFT-MATH-SCIENTIFIC-CALCULATOR-006",)


def _dimension(key: str, rejected: str, rejected_reason: str, admitted: str, admitted_reason: str):
    return binary_dimension(
        key,
        key.replace("_", " ") + "?",
        rejected,
        rejected_reason,
        admitted,
        admitted_reason,
    )


_ordinary = CalculatorWebApplication(share=False)
_ordinary_result = _ordinary.apply({"action": "evaluate", "expression": "1+1"})["view"]
_cancellation = CalculatorWebApplication(share=False)
_cancellation_result = _cancellation.apply({"action": "evaluate", "expression": "1-1"})["view"]
_prohibited = CalculatorWebApplication(share=False)
_prohibited_result = _prohibited.apply({"action": "evaluate", "expression": "1-4"})["view"]
_root = CalculatorWebApplication(share=False)
_root_result = _root.apply({"action": "evaluate", "expression": "sqrt(2)"})["view"]
_sessions = CalculatorWebApplication(share=False)
_first_page = _sessions.new_page_payload()
_second_page = _sessions.new_page_payload()
_sessions.apply({"action": "evaluate", "expression": "2+2"}, _first_page["session_id"])
_second_state = _sessions.initial_payload(_second_page["session_id"])["view"]
_page = render_page(_sessions.token, _second_page)
_source_labels = set(label for row in _second_page["buttons"] for label in row)
_organised_labels = set(MEMORY_BUTTONS)
_organised_labels.update(label for row in BASIC_BUTTON_ROWS for label in row)
_organised_labels.update(label for row in SCIENTIFIC_BUTTON_ROWS for label in row)
_coverage_path = Path(__file__).resolve().parents[3] / "generated/mathematics/scientific_calculator_browser_coverage_v1.json"
_coverage = json.loads(_coverage_path.read_text(encoding="utf-8"))["totals"]


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Accessible SFT-native scientific calculator application",
    statement=(
        "The admitted exact calculator extends to one dependency-free standards-rendered application whose familiar "
        "calculator notation never selects the mathematics: displayed zero retains empty-One semantics; negative-result "
        "attempts halt transactionally; certified intervals and orthogonal fibres remain typed exact objects; every page "
        "has an independent session; the conventional standard pad remains structurally coherent; scientific functions "
        "are progressively disclosed; and the same application is reachable on macOS, Windows, Linux and same-network phones."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Hold the immutable claim-006 evaluator fixed and exhaust eight independent presentation completions: rendered "
        "surface, keypad organisation, value boundary, kernel route, session state, network reach, dependency boundary and validation."
    ),
    grammar_boundary=(
        "The complete eight-coordinate binary product of presentation adapters over the immutable claim-006 controller; "
        "no coordinate may alter arithmetic, value construction, expression parsing, proof law or engine protocol."
    ),
    dimensions=(
        _dimension("rendered_surface", "deprecated-widget-geometry-only", "Mapped geometry did not ensure painted controls on the target macOS runtime.", "standards-rendered-browser-surface", "The installed browser paints semantic HTML controls through a local standard-library service."),
        _dimension("keypad_organisation", "flattened-function-grid", "Arbitrary reflow destroys the familiar four-column calculator grammar.", "standard-pad-plus-scientific-panel", "Memory, standard four-column keys and scientific functions retain separate coherent organisations."),
        _dimension("value_boundary", "conventional-prohibited-projection", "Displaying a negative or irrational-style decimal silently reimports a prohibited scalar.", "familiar-notation-with-SFT-halt-and-types", "Zero is familiar empty-One notation, negative-result attempts halt, and non-scalar results remain exact typed certificates."),
        _dimension("kernel_route", "client-side-duplicate-arithmetic", "A second arithmetic implementation could diverge from the admitted evaluator.", "server-side-immutable-claim-006-controller", "Every visible action reaches the same admitted controller and the browser performs no arithmetic."),
        _dimension("session_state", "shared-global-visitor-state", "One visitor or test can contaminate another visitor's landing value.", "fresh-independent-page-session", "Every page load receives a fresh retained controller identity while its own history and memory persist."),
        _dimension("network_reach", "desktop-loopback-only", "A computer-only default blocks ordinary same-network phone use.", "same-network-default-with-private-option", "The default binds to the local network and displays its phone address; private mode remains explicit."),
        _dimension("dependency_boundary", "heavy-GUI-or-container-runtime", "A heavy platform runtime violates the accessibility requirement.", "Python-standard-library-and-installed-browser", "HTTP service, exact controller and page assets require no third-party runtime or container."),
        _dimension("validation", "hidden-widget-dimensions-only", "Widget dimensions did not detect the observed blank window.", "API-render-responsive-adverse-and-complete-coverage", "The corrected route checks HTTP behavior, semantic rendering, mobile structure, prohibited results, session isolation and complete active-file coverage."),
    ),
    exact_result=(
        "The unique completion is a familiar calculator-first local web application with a coherent standard pad, optional "
        "scientific and proof panels, fresh per-page state, same-network default access and one immutable exact SFT evaluation route."
    ),
    laws=(
        "presentation notation may describe an admitted value but cannot create a new value type",
        "displayed 0 denotes structural empty One and does not admit a numerical-zero proof object",
        "a result containing any counter-held scalar or bound halts before answer, memory or history mutation",
        "a certified rational interval is a typed certificate and is never displayed as one irrational decimal scalar",
        "each browser page owns one fresh controller state and cannot inherit another page's tested answer",
        "the standard four-column keypad grammar is invariant under phone-width reflow",
        "touch-keypad actions never focus the editable field or summon the phone keyboard",
        "the browser performs interaction and presentation only; all evaluation remains in claim 006",
    ),
    induction_base=(
        "Claim 006 supplies the exact evaluator, controller, proof trace and complete scientific expression language; "
        "one fresh page begins with its familiar displayed 0 and empty history."
    ),
    induction_step=(
        "Adding one interaction, viewport or visitor is lawful only when it preserves the standard keypad organisation, "
        "routes to the same exact controller, retains a distinct session and rejects every prohibited result transactionally."
    ),
    boundary_exclusions=(
        "no edit to the frozen engine or immutable claim-006 source",
        "no browser-side arithmetic or alternate evaluator",
        "no displayed negative, irrational scalar, imaginary scalar, NaN or infinity",
        "no counter-held result retained in answer, memory or history",
        "no shared landing-state contamination between page sessions",
        "no automatic expression focus on a touch-width calculator",
        "no heavy GUI framework, container or network service beyond the user's local network",
    ),
    witnesses=(
        Witness("ordinary-result", "1+1 displays familiar exact 2.", _ordinary_result["result"] == "2"),
        Witness("empty-one-display", "1-1 displays familiar 0 while the evaluator retains empty One.", _cancellation_result["result"] == "0"),
        Witness("negative-result-halt", "1-4 halts without retaining history.", _prohibited_result["result"] == "HALT" and not _prohibited_result["history"]),
        Witness("certificate-not-irrational", "sqrt(2) displays exact rational bounds without an irrational-style decimal.", str(_root_result["result"]).startswith("certified rational interval") and "1.414" not in str(_root_result["result"]) and "≈" not in str(_root_result["exact_details"])),
        Witness("fresh-session", "A calculation in one page leaves the next page at 0.", _first_page["session_id"] != _second_page["session_id"] and _second_state["result"] == "0"),
        Witness("complete-key-partition", "All sixty-four controls occur exactly once across memory, standard and scientific organisations.", _source_labels == _organised_labels and len(_organised_labels) == 64),
        Witness("standard-keypad", "The visible standard calculator is six complete four-key rows.", len(BASIC_BUTTON_ROWS) == 6 and all(len(row) == 4 for row in BASIC_BUTTON_ROWS)),
        Witness("responsive-contract", "The page declares phone disclosure, four-column standard layout and horizontal-overflow prevention.", "Show scientific functions" in _page and "grid-template-columns:repeat(4,1fr)" in _page and ".layout>*{min-width:0}" in _page),
        Witness("touch-focus-contract", "Phone keypad taps do not automatically open the keyboard.", "focusForHardwareKeyboard" in _page and "(min-width:671px) and (pointer:fine)" in _page),
        Witness("one-kernel-route", "The browser sends actions to the local API and defines no JavaScript arithmetic model.", "fetch(path" in _page and "Math." not in _page),
        Witness("complete-active-coverage", "Every active adapter statement and branch is executed.", _coverage["percent_covered"] == 100.0 and _coverage["missing_lines"] == 0 and _coverage["missing_branches"] == 0),
    ),
    why=(
        "A proof-producing calculator is accessible only when the ordinary surface remains familiar and the complicated "
        "distinctions stay available underneath. A painted, responsive and state-isolated surface is therefore part of the application boundary."
    ),
    derivation=(
        "Claim 006 fixes every mathematical operation. Exhausting the eight presentation distinctions eliminates the blank "
        "deprecated widget path, arbitrary keypad reflow, conventional prohibited projections, duplicate arithmetic, shared "
        "visitor state, computer-only reach, heavy dependencies and geometry-only testing. The remaining adapter changes no law."
    ),
    check=(
        "Enumerate all 256 adapters; require one all-admitted survivor; execute ordinary, cancellation, negative-halt, exact-certificate, "
        "fresh-session, complete-control, standard-layout, responsive-contract, single-kernel and complete-coverage witnesses; "
        "then independently start the application as a subprocess and replay its HTTP boundary."
    ),
    limitations=(
        "Closure covers the current calculator presentation and declared browser-standard route. It does not claim every future "
        "browser or device has been physically tested. Manual review remains a separate publication gate, and lawful extensions remain open."
    ),
    correspondence_terms=(
        "scientific calculator",
        "responsive web application",
        "local-first software",
        "exact arithmetic interface",
        "proof-producing calculator",
    ),
)


__all__ = ("CLAIM_ID", "DEPENDENCIES", "SPEC")
