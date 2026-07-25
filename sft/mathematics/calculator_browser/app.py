"""Local-only HTTP adapter over the immutable claim-006 calculation controller."""

from __future__ import annotations

from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import socket
from threading import RLock, Thread
from typing import Any
import webbrowser

from sft.mathematics.calculator.values import CalculatorHalt
from sft.mathematics.calculator_complete.controller import (
    CalculatorController,
    FUNCTION_CATALOG,
    MAIN_BUTTON_ROWS,
)
from sft.mathematics.calculator_complete.explorer import RegisteredMathematicsExplorer

from .page import render_page
from .native import contains_counter, native_view


MAX_REQUEST_BYTES = 65_536
LOCAL_HOST = "127.0.0.1"
LAN_HOST = "0.0.0.0"
MEMORY_BUTTONS = ("MC", "MR", "M+", "M−", "MS")
BASIC_BUTTON_ROWS = (
    ("%", "CE", "C", "⌫"),
    ("1/x", "x²", "√", "÷"),
    ("7", "8", "9", "×"),
    ("4", "5", "6", "−"),
    ("1", "2", "3", "+"),
    ("±", "0", ".", "="),
)
SCIENTIFIC_BUTTON_ROWS = (
    ("sin", "cos", "tan", "π", "e"),
    ("asin", "acos", "atan", "(", ")"),
    ("sinh", "cosh", "tanh", "φ", "exp"),
    ("asinh", "acosh", "atanh", "ln", "log"),
    ("log₂", "cbrt", "xʸ", "n!", "nCr"),
    ("nPr", "Ans", "floor", "ceil", "|x|"),
    ("gcd", "lcm", "mod", "root", "empty"),
)


class CalculatorWebApplication:
    """Stateful, local-only presentation adapter for one calculator session."""

    def __init__(self, *, places: int = 18, operation_limit: int = 10000, share: bool = True):
        self.places = places
        self.operation_limit = operation_limit
        self.explorer = RegisteredMathematicsExplorer()
        self.token = secrets.token_urlsafe(24)
        self.share = share
        self.entry_path = "/"
        self.network_url = ""
        self.lock = RLock()
        self.server: ThreadingHTTPServer | None = None
        self.sessions: dict[str, CalculatorController] = {}
        self.default_session_id = self._new_session()
        self.controller = self.sessions[self.default_session_id]

    def _new_session(self) -> str:
        session_id = secrets.token_urlsafe(18)
        self.sessions[session_id] = CalculatorController(
            places=self.places,
            operation_limit=self.operation_limit,
        )
        return session_id

    def new_page_payload(self) -> dict[str, Any]:
        return self.initial_payload(self._new_session())

    def _session(self, session_id: str | None) -> tuple[str, CalculatorController]:
        selected = self.default_session_id if session_id is None else session_id
        if selected not in self.sessions:
            raise CalculatorHalt("the calculator session is not retained")
        return selected, self.sessions[selected]

    def initial_payload(self, session_id: str | None = None) -> dict[str, Any]:
        selected, controller = self._session(session_id)
        return {
            "view": native_view(controller),
            "session_id": selected,
            "buttons": [list(row) for row in MAIN_BUTTON_ROWS],
            "memory_buttons": list(MEMORY_BUTTONS),
            "basic_buttons": [list(row) for row in BASIC_BUTTON_ROWS],
            "scientific_buttons": [list(row) for row in SCIENTIFIC_BUTTON_ROWS],
            "functions": [list(row) for row in FUNCTION_CATALOG],
            "laws": list(self.explorer.claim_ids()),
            "network_url": self.network_url,
        }

    def _view(self, controller: CalculatorController) -> dict[str, Any]:
        return {"ok": True, "view": native_view(controller)}

    @staticmethod
    def _snapshot(controller: CalculatorController) -> tuple[object, ...]:
        return (
            controller.expression,
            controller.result,
            controller.exact_details,
            controller.error,
            controller.just_evaluated,
            controller.session.answer,
            controller.session.memory,
            list(controller.session.history),
            controller.session.angle_mode,
        )

    @staticmethod
    def _restore(controller: CalculatorController, snapshot: tuple[object, ...]) -> None:
        (
            controller.expression,
            controller.result,
            controller.exact_details,
            controller.error,
            controller.just_evaluated,
            controller.session.answer,
            controller.session.memory,
            history,
            controller.session.angle_mode,
        ) = snapshot
        controller.session.history[:] = history

    @staticmethod
    def _state_has_counter(controller: CalculatorController) -> bool:
        return any(
            (
                contains_counter(controller.session.answer),
                contains_counter(controller.session.memory),
                any(contains_counter(item.calculation.value) for item in controller.session.history),
            )
        )

    def apply(self, payload: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
        action = payload.get("action")
        with self.lock:
            try:
                _, controller = self._session(session_id)
                if "expression" in payload:
                    expression = payload["expression"]
                    if not isinstance(expression, str):
                        raise CalculatorHalt("the editable expression must be text")
                    controller.set_expression(expression)
                snapshot = self._snapshot(controller)
                if action == "state":
                    return self._view(controller)
                if action == "evaluate":
                    controller.evaluate()
                elif action == "press":
                    label = payload.get("label")
                    if not isinstance(label, str):
                        raise CalculatorHalt("a calculator control label is required")
                    controller.press(label)
                elif action == "mode":
                    mode = payload.get("mode")
                    if not isinstance(mode, str):
                        raise CalculatorHalt("an angle mode is required")
                    controller.set_angle_mode(mode)
                elif action == "function":
                    name = payload.get("name")
                    if not isinstance(name, str):
                        raise CalculatorHalt("a function name is required")
                    controller.insert_catalog(name)
                elif action == "history":
                    index = payload.get("index")
                    if not isinstance(index, int):
                        raise CalculatorHalt("a counted history position is required")
                    controller.restore_history(index)
                elif action == "clear_history":
                    controller.clear_history()
                else:
                    raise CalculatorHalt("unknown calculator application action")
                if self._state_has_counter(controller):
                    attempted_expression = controller.expression or str(payload.get("expression", ""))
                    self._restore(controller, snapshot)
                    controller.expression = attempted_expression
                    controller.result = "HALT"
                    controller.error = (
                        "result crosses below structural empty One; negative and counter-held numeric results "
                        "are outside the admitted calculator domain"
                    )
                    controller.exact_details = "The attempted result was rejected before admission to answer, memory or history."
                    controller.just_evaluated = False
                return self._view(controller)
            except (CalculatorHalt, KeyError, ValueError) as error:
                fallback = self.sessions.get(session_id or self.default_session_id, self.controller)
                return {"ok": False, "error": str(error), "view": native_view(fallback)}

    def law(self, claim_id: str, *, replay: bool) -> dict[str, Any]:
        with self.lock:
            try:
                if replay:
                    content: Any = json.loads(self.explorer.replay(claim_id).to_json())
                else:
                    content = asdict(self.explorer.summary(claim_id))
                return {"ok": True, "content": content}
            except (CalculatorHalt, KeyError, ValueError, json.JSONDecodeError) as error:
                return {"ok": False, "error": str(error)}

    def request_shutdown(self) -> None:
        if self.server is not None:
            Thread(target=self.server.shutdown, name="sft-calculator-shutdown", daemon=True).start()

    def handler_type(self):
        application = self

        class CalculatorRequestHandler(BaseHTTPRequestHandler):
            server_version = "SFTCalculator/1"

            def log_message(self, _format: str, *_arguments: object) -> None:
                return

            def _headers(self, status: int, content_type: str, length: int) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(length))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
                self.end_headers()

            def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
                body = json.dumps(payload, sort_keys=True).encode("utf-8")
                self._headers(status, "application/json; charset=utf-8", len(body))
                self.wfile.write(body)

            def _authorised(self) -> bool:
                return secrets.compare_digest(self.headers.get("X-SFT-Token", ""), application.token)

            def _session_id(self) -> str:
                return self.headers.get("X-SFT-Session", "")

            def _read_json(self) -> dict[str, Any]:
                raw_length = self.headers.get("Content-Length", "")
                if not raw_length.isdigit():
                    raise ValueError("a counted request length is required")
                length = int(raw_length)
                if length < 1 or length > MAX_REQUEST_BYTES:
                    raise ValueError("request exceeds the local application boundary")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("request must be a JSON object")
                return payload

            def do_GET(self) -> None:  # noqa: N802
                if self.path == application.entry_path:
                    body = render_page(application.token, application.new_page_payload()).encode("utf-8")
                    self._headers(200, "text/html; charset=utf-8", len(body))
                    self.wfile.write(body)
                    return
                if self.path == "/health":
                    self._send_json({"ok": True, "service": "smithian-fold-calculator"})
                    return
                self._send_json({"ok": False, "error": "not found"}, 404)

            def do_POST(self) -> None:  # noqa: N802
                if not self._authorised():
                    self._send_json({"ok": False, "error": "local application token rejected"}, 403)
                    return
                try:
                    payload = self._read_json()
                except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
                    self._send_json({"ok": False, "error": str(error)}, 400)
                    return
                if self.path == "/api/action":
                    self._send_json(application.apply(payload, self._session_id()))
                elif self.path == "/api/law":
                    claim_id = payload.get("claim_id")
                    if not isinstance(claim_id, str):
                        self._send_json({"ok": False, "error": "a law identifier is required"}, 400)
                    else:
                        self._send_json(application.law(claim_id, replay=bool(payload.get("replay"))))
                elif self.path == "/api/close":
                    self._send_json({"ok": True, "message": "calculator closed"})
                    application.request_shutdown()
                else:
                    self._send_json({"ok": False, "error": "not found"}, 404)

        return CalculatorRequestHandler

    def bind(self, *, host: str | None = None, start_port: int = 8765, attempts: int = 24) -> ThreadingHTTPServer:
        expected_host = LAN_HOST if self.share else LOCAL_HOST
        host = expected_host if host is None else host
        if host != expected_host:
            raise CalculatorHalt("the calculator binding does not match its declared private or local-network mode")
        if start_port < 1024 or start_port > 65_511:
            raise CalculatorHalt("the local application port is outside its declared boundary")
        for offset in range(attempts):
            try:
                server = ThreadingHTTPServer((host, start_port + offset), self.handler_type())
                server.daemon_threads = True
                self.server = server
                return server
            except OSError:
                continue
        raise CalculatorHalt("no local calculator application port is available")


def launch_browser_calculator(
    *,
    start_port: int = 8765,
    places: int = 18,
    operation_limit: int = 10000,
    open_browser: bool = True,
    share: bool = True,
) -> None:
    application = CalculatorWebApplication(
        places=places,
        operation_limit=operation_limit,
        share=share,
    )
    server = application.bind(start_port=start_port)
    port = server.server_address[1]
    local_url = f"http://{LOCAL_HOST}:{port}{application.entry_path}"
    print(f"Smithian Fold Scientific Calculator: {local_url}", flush=True)
    if share:
        network_url = f"http://{_local_network_address()}:{port}{application.entry_path}"
        application.network_url = network_url
        print(f"Phone or local-network address: {network_url}", flush=True)
        print("Devices on the same local network can open that address.", flush=True)
    print("Use the Close button in the calculator when finished.", flush=True)
    if open_browser:
        webbrowser.open(local_url, new=1, autoraise=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _local_network_address() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("1.1.1.1", 80))
        address = probe.getsockname()[0]
    except OSError:
        address = socket.gethostbyname(socket.gethostname())
    finally:
        probe.close()
    if address.startswith("127."):
        raise CalculatorHalt("a local-network address could not be resolved")
    return address


__all__ = ("CalculatorWebApplication", "LAN_HOST", "LOCAL_HOST", "launch_browser_calculator")
