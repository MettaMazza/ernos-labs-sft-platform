from __future__ import annotations

import json
import http.client
from pathlib import Path
import runpy
from threading import Thread
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from sft.mathematics.calculator.values import CalculatorHalt, CertifiedInterval, forward
from sft.mathematics.calculator_browser.app import CalculatorWebApplication
from sft.mathematics.calculator_browser import app as browser_app
from sft.mathematics.calculator_browser import __main__ as browser_main
from sft.mathematics.calculator_browser.page import render_page
from sft.mathematics.calculator_browser.native import native_value


def request_json(
    url: str,
    *,
    token: str | None = None,
    session: str | None = None,
    payload: dict | None = None,
):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {} if token is None else {"X-SFT-Token": token, "Content-Type": "application/json"}
    if session is not None:
        headers["X-SFT-Session"] = session
    request = Request(url, data=data, headers=headers)
    with urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read())


def raw_post(
    url: str,
    path: str,
    token: str,
    session: str,
    body: bytes,
    content_length: str | None = None,
):
    host_port = url.removeprefix("http://")
    host, port = host_port.split(":")
    connection = http.client.HTTPConnection(host, int(port), timeout=3)
    headers = {"X-SFT-Token": token, "X-SFT-Session": session, "Content-Type": "application/json"}
    if content_length is not None:
        headers["Content-Length"] = content_length
    connection.request("POST", path, body=body, headers=headers)
    response = connection.getresponse()
    payload = json.loads(response.read())
    connection.close()
    return response.status, payload


@pytest.fixture()
def live_application():
    application = CalculatorWebApplication()
    server = application.bind(start_port=18765)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield application, url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_page_has_familiar_and_progressive_controls():
    application = CalculatorWebApplication()
    payload = application.initial_payload()
    page = render_page(application.token, payload)
    assert "Smithian Fold Scientific Calculator" in page
    assert "Type 1 + 1" in page
    assert "Show SFT proof" in page
    assert "Exact result and proof trace" in page
    assert "Phone access on the same local network" in page
    assert "focusForHardwareKeyboard" in page
    assert "(min-width:671px) and (pointer:fine)" in page
    for label in ("MC", "sin", "7", "π", "nCr", "empty"):
        assert label in page
    source = {label for row in payload["buttons"] for label in row}
    organised = set(payload["memory_buttons"])
    organised.update(label for row in payload["basic_buttons"] for label in row)
    organised.update(label for row in payload["scientific_buttons"] for label in row)
    assert organised == source
    assert sum(map(len, payload["basic_buttons"])) == 24
    assert all(len(row) == 4 for row in payload["basic_buttons"])
    assert all(len(row) == 5 for row in payload["scientific_buttons"])


def test_api_executes_exact_kernel_and_retains_proof(live_application):
    application, url = live_application
    status, health = request_json(url + "/health")
    assert status == 200 and health["ok"] is True
    status, result = request_json(
        url + "/api/action",
        token=application.token,
        session=application.default_session_id,
        payload={"action": "evaluate", "expression": "1+1"},
    )
    assert status == 200 and result["ok"] is True
    assert result["view"]["result"] == "2"
    assert "Proof trace" in result["view"]["exact_details"]
    assert result["view"]["history"] == ["1+1  =  2"]


def test_api_surfaces_fail_closed_result(live_application):
    application, url = live_application
    _, result = request_json(
        url + "/api/action",
        token=application.token,
        session=application.default_session_id,
        payload={"action": "evaluate", "expression": "1/0"},
    )
    assert result["ok"] is True
    assert result["view"]["result"] == "HALT"
    assert result["view"]["error"]


def test_api_rejects_missing_token(live_application):
    _application, url = live_application
    with pytest.raises(HTTPError) as captured:
        request_json(url + "/api/action", payload={"action": "state"})
    assert captured.value.code == 403


def test_api_exposes_the_preexisting_registered_law_summary(live_application):
    application, url = live_application
    claim_id = application.explorer.claim_ids()[0]
    _, result = request_json(
        url + "/api/law",
        token=application.token,
        payload={"claim_id": claim_id, "replay": False},
    )
    assert result["ok"] is True
    assert result["content"]["claim_id"] == claim_id
    assert result["content"]["model_admitted"] is True
    assert result["content"]["receipt_hash"].startswith("sha256:")


def test_every_application_action_and_fail_closed_input_branch():
    application = CalculatorWebApplication()
    application.request_shutdown()
    assert application.apply({"action": "state"})["ok"] is True
    assert application.apply({"action": "state", "expression": 1})["ok"] is False
    assert application.apply({"action": "press"})["ok"] is False
    assert application.apply({"action": "press", "label": "1"})["view"]["expression"] == "1"
    assert application.apply({"action": "mode"})["ok"] is False
    assert application.apply({"action": "mode", "mode": "DEG"})["view"]["angle_mode"] == "DEG"
    assert application.apply({"action": "function"})["ok"] is False
    assert application.apply({"action": "function", "name": "mean"})["view"]["expression"].endswith("mean(")
    assert application.apply({"action": "evaluate", "expression": "1+1"})["view"]["result"] == "2"
    assert application.apply({"action": "history"})["ok"] is False
    assert application.apply({"action": "history", "index": 0})["view"]["expression"] == "1+1"
    assert application.apply({"action": "clear_history"})["view"]["history"] == ()
    assert application.apply({"action": "not-an-action"})["ok"] is False


def test_primary_results_are_sft_native_without_prohibited_scalar_projection():
    application = CalculatorWebApplication()
    assert application.initial_payload()["view"]["result"] == "0"
    held = application.apply({"action": "evaluate", "expression": "1-4"})["view"]
    assert held["result"] == "HALT"
    assert "negative and counter-held numeric results" in held["error"]
    assert held["history"] == ()
    assert application.controller.session.answer.__class__.__name__ == "EmptyOne"
    root = application.apply({"action": "evaluate", "expression": "sqrt(2)"})["view"]
    assert root["result"].startswith("certified rational interval [")
    assert "1.414" not in root["result"] and "≈" not in root["result"]
    assert "1.414" not in root["exact_details"] and "≈" not in root["exact_details"]
    fibres = application.apply({"action": "evaluate", "expression": "complex(2,3)"})["view"]
    assert fibres["result"] == "Fold fibres (real: 2; orthogonal: 3)"
    assert native_value(CertifiedInterval(forward(2), forward(2), ("exact",))) == "2"


def test_prohibited_result_rolls_back_answer_memory_and_history_transactionally():
    application = CalculatorWebApplication()
    accepted = application.apply({"action": "evaluate", "expression": "2+2"})["view"]
    assert accepted["result"] == "4"
    rejected = application.apply({"action": "evaluate", "expression": "1-4"})["view"]
    assert rejected["result"] == "HALT"
    assert rejected["history"] == ("2+2  =  4",)
    application.controller.error = ""
    memory_rejected = application.apply({"action": "press", "label": "M−", "expression": ""})["view"]
    assert memory_rejected["result"] == "HALT"
    assert application.controller.session.memory.__class__.__name__ == "EmptyOne"


def test_each_page_receives_a_fresh_independent_calculator_session():
    application = CalculatorWebApplication()
    first = application.new_page_payload()
    second = application.new_page_payload()
    assert first["session_id"] != second["session_id"]
    application.apply({"action": "evaluate", "expression": "sqrt(2)"}, first["session_id"])
    assert application.initial_payload(first["session_id"])["view"]["result"].startswith(
        "certified rational interval"
    )
    assert application.initial_payload(second["session_id"])["view"]["result"] == "0"
    assert application.apply({"action": "state"}, "missing-session")["ok"] is False


def test_law_replay_and_law_fail_closed_paths():
    application = CalculatorWebApplication()
    claim_id = application.explorer.claim_ids()[0]
    replay = application.law(claim_id, replay=True)
    assert replay["ok"] is True and replay["content"]["claim_id"] == claim_id
    assert application.law("missing-law", replay=False)["ok"] is False
    with patch.object(application.explorer, "replay") as replay_mock:
        replay_mock.return_value.to_json.return_value = "not-json"
        assert application.law(claim_id, replay=True)["ok"] is False


def test_http_page_not_found_malformed_boundaries_and_close():
    application = CalculatorWebApplication(share=False)
    server = application.bind(start_port=18791)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urlopen(url + "/", timeout=3) as response:
            page = response.read().decode()
            assert response.status == 200 and "Smithian Fold Scientific Calculator" in page
            assert response.headers["Cache-Control"] == "no-store"
        with pytest.raises(HTTPError) as missing:
            request_json(url + "/missing")
        assert missing.value.code == 404
        session = application.default_session_id
        status, result = raw_post(url, "/api/action", application.token, session, b"", "0")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/action", application.token, session, b"{}", "65537")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/action", application.token, session, b"[]")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/action", application.token, session, b"{")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/action", application.token, session, b"\xff")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/law", application.token, session, b"{}")
        assert status == 400 and result["ok"] is False
        status, result = raw_post(url, "/api/missing", application.token, session, b"{}")
        assert status == 404 and result["ok"] is False
        status, result = raw_post(url, "/api/close", application.token, session, b"{}")
        assert status == 200 and result["ok"] is True
        thread.join(timeout=3)
        assert not thread.is_alive()
    finally:
        server.server_close()


def test_http_rejects_non_numeric_content_length(live_application):
    application, url = live_application
    status, result = raw_post(
        url,
        "/api/action",
        application.token,
        application.default_session_id,
        b"{}",
        "letters",
    )
    assert status == 400 and result["ok"] is False


def test_bind_is_local_only_and_bounded():
    application = CalculatorWebApplication(share=False)
    with pytest.raises(CalculatorHalt, match="binding"):
        application.bind(host="0.0.0.0")
    with pytest.raises(CalculatorHalt, match="port"):
        application.bind(start_port=80)


def test_network_share_is_the_accessible_default_and_private_mode_is_explicit():
    application = CalculatorWebApplication()
    assert application.share is True
    assert application.entry_path == "/"
    with pytest.raises(CalculatorHalt, match="binding"):
        application.bind(host="127.0.0.1", start_port=18790)
    server = application.bind(start_port=18790)
    try:
        assert server.server_address[0] == "0.0.0.0"
    finally:
        server.server_close()


def test_bind_advances_busy_ports_and_halts_when_none_are_available():
    first = CalculatorWebApplication(share=False)
    server = first.bind(start_port=18793)
    try:
        second = CalculatorWebApplication(share=False)
        alternate = second.bind(start_port=18793, attempts=2)
        try:
            assert alternate.server_address[1] == 18794
        finally:
            alternate.server_close()
    finally:
        server.server_close()
    with patch.object(browser_app, "ThreadingHTTPServer", side_effect=OSError("busy")):
        with pytest.raises(CalculatorHalt, match="no local"):
            CalculatorWebApplication(share=False).bind(start_port=18793, attempts=2)


def test_launch_paths_close_server_open_browser_and_handle_interrupt(capsys):
    fake_server = Mock()
    fake_server.server_address = ("0.0.0.0", 18795)
    fake_server.serve_forever.side_effect = KeyboardInterrupt
    fake_application = Mock()
    fake_application.entry_path = "/"
    fake_application.bind.return_value = fake_server
    with (
        patch.object(browser_app, "CalculatorWebApplication", return_value=fake_application),
        patch.object(browser_app, "_local_network_address", return_value="192.168.1.9"),
        patch.object(browser_app.webbrowser, "open") as open_browser,
    ):
        browser_app.launch_browser_calculator(start_port=18795, share=True, open_browser=True)
        open_browser.assert_called_once_with("http://127.0.0.1:18795/", new=1, autoraise=True)
        assert fake_application.network_url == "http://192.168.1.9:18795/"
        fake_server.server_close.assert_called_once()
    assert "Phone or local-network address" in capsys.readouterr().out

    private_server = Mock()
    private_server.server_address = ("127.0.0.1", 18796)
    private_application = Mock(entry_path="/")
    private_application.bind.return_value = private_server
    with (
        patch.object(browser_app, "CalculatorWebApplication", return_value=private_application),
        patch.object(browser_app.webbrowser, "open") as open_browser,
    ):
        browser_app.launch_browser_calculator(start_port=18796, share=False, open_browser=False)
        open_browser.assert_not_called()
        private_server.server_close.assert_called_once()


def test_network_address_success_fallback_and_loopback_halt():
    probe = Mock()
    probe.getsockname.return_value = ("192.168.1.8", 12345)
    with patch.object(browser_app.socket, "socket", return_value=probe):
        assert browser_app._local_network_address() == "192.168.1.8"
        probe.close.assert_called_once()

    fallback = Mock()
    fallback.connect.side_effect = OSError("offline")
    with (
        patch.object(browser_app.socket, "socket", return_value=fallback),
        patch.object(browser_app.socket, "gethostname", return_value="machine"),
        patch.object(browser_app.socket, "gethostbyname", return_value="192.168.1.7"),
    ):
        assert browser_app._local_network_address() == "192.168.1.7"

    loopback = Mock()
    loopback.connect.side_effect = OSError("offline")
    with (
        patch.object(browser_app.socket, "socket", return_value=loopback),
        patch.object(browser_app.socket, "gethostname", return_value="machine"),
        patch.object(browser_app.socket, "gethostbyname", return_value="127.0.0.1"),
    ):
        with pytest.raises(CalculatorHalt, match="could not be resolved"):
            browser_app._local_network_address()


def test_command_entry_translates_arguments(monkeypatch):
    launch = Mock()
    monkeypatch.setattr(browser_main, "launch_browser_calculator", launch)
    monkeypatch.setattr(
        "sys.argv",
        ["smithian-fold-calculator", "--no-browser", "--private", "--port", "18797", "--places", "12", "--limit", "99"],
    )
    assert browser_main.main() == 0
    launch.assert_called_once_with(
        start_port=18797,
        places=12,
        operation_limit=99,
        open_browser=False,
        share=False,
    )


@pytest.mark.filterwarnings("ignore:.*found in sys.modules.*:RuntimeWarning")
def test_module_guard_exits_cleanly(monkeypatch):
    monkeypatch.setattr(browser_app, "launch_browser_calculator", Mock())
    monkeypatch.setattr("sys.argv", ["smithian-fold-calculator", "--no-browser", "--private"])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("sft.mathematics.calculator_browser.__main__", run_name="__main__")
    assert stopped.value.code == 0


def test_new_adapter_does_not_modify_frozen_engine_or_claim_006_source():
    root = Path(__file__).resolve().parents[1]
    files = tuple((root / "sft/mathematics/calculator_browser").glob("*.py"))
    assert files
    assert all("sft/engine" not in path.as_posix() for path in files)
    assert all("calculator_complete" not in path.parent.name for path in files)
