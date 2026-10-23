# =============================================================================
# HYDRA-UMC-SDK - Client of the claim, jog arming and safety-limit routes
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Typed access to the routes of HYDRA-UMC-SERVER that decide who controls a
robot and how far a jog may go: ``claim``, ``release``, ``jog-arm``,
``GET /api/claims``, ``GET /api/safety-limits`` and
``PUT /api/admin/safety-limits``, plus the optional ``controllerId`` of
``command``.

Two layers, both dependency-free:

* request builders and response parsers (``claim_request``,
  ``parse_claim_result``, ...) that never touch the network, so any HTTP
  stack can carry them; and
* ``ServerClient``, a thin client over an injectable transport (the default
  uses ``urllib``).

Everything is additive. A request without a controller id is the v1 request;
a response field this module does not know is ignored; an error code it does
not know is kept as a plain ``ApiError``. The server decides: nothing here
checks a limit, a claim or an arming on its own, it only builds the request
and tells the answers apart.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

CONTROLLER_ID_HEADER = "X-Controller-Id"
_CONTROLLER_ID = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")

CODE_OTHER_ACCOUNT = "other-account"
CODE_OTHER_CONTROLLER = "other-controller"
CODE_CONTROLLER_ID_REQUIRED = "controller-id-required"
CODE_INVALID_CONTROLLER_ID = "invalid-controller-id"
CODE_JOG_NOT_ARMED = "jog-not-armed"
KNOWN_ERROR_CODES: tuple[str, ...] = (
    CODE_OTHER_ACCOUNT,
    CODE_OTHER_CONTROLLER,
    CODE_CONTROLLER_ID_REQUIRED,
    CODE_INVALID_CONTROLLER_ID,
    CODE_JOG_NOT_ARMED,
)


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------
class ServerRequestError(ValueError):
    """A request that the client refuses to build (a malformed controller id,
    an empty command, a robot id that is not an integer). Nothing was sent."""


class ApiError(Exception):
    """An error answer of the server: the HTTP status, the readable ``error``
    text, the stable ``code`` when the server sent one and the whole body."""

    def __init__(self, status: int, message: str, code: str | None = None, body: Any = None):
        super().__init__(f"{status} {code + ': ' if code else ''}{message}")
        self.status = status
        self.message = message
        self.code = code
        self.body = body


class ClaimConflictError(ApiError):
    """The robot is claimed by someone else: ``code`` is ``other-account`` or
    ``other-controller`` (``None`` for a server that predates the codes) and
    ``reservation`` is the claim that blocks the caller."""

    def __init__(self, status: int, message: str, code: str | None, body: Any, reservation: "Reservation | None"):
        super().__init__(status, message, code, body)
        self.reservation = reservation


class ControllerIdRequiredError(ClaimConflictError):
    """The claim has a controller (409) or the server demands one to claim
    (400): send a ``controllerId``."""


class InvalidControllerIdError(ApiError):
    """The server refused the shape of the ``controllerId`` (400)."""


class JogNotArmedError(ApiError):
    """A jog was refused because the robot is not armed (403); arm it with
    ``jog_arm_request`` / ``ServerClient.jog_arm`` first."""


# --------------------------------------------------------------------------
# Values
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Reservation:
    owner_id: Any
    owner_username: str
    claimed_at: int | float
    expires_at: int | float
    controller_id: str | None = None


@dataclass(frozen=True)
class ClaimResult:
    reservation: Reservation | None
    history: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class JogArmResult:
    armed: bool
    expires_at: int | float | None = None
    ttl_ms: int | float | None = None


@dataclass(frozen=True)
class ClaimEntry:
    robot_id: int
    robot_name: str | None
    cell_id: Any
    owner_id: Any
    owner_username: str
    controller_id: str | None
    claimed_at: int | float
    expires_at: int | float


@dataclass(frozen=True)
class RobotSafety:
    id: int
    model: str | None
    jog: Mapping[str, Any]
    temperature: Mapping[str, Any]
    jog_armed_until: int | float | None = None


@dataclass(frozen=True)
class SafetyLimitsView:
    limits: Mapping[str, Any]
    defaults: Mapping[str, Any]
    hard_limits: Mapping[str, Any]
    robot: RobotSafety | None = None


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    body: Mapping[str, Any] | None = None
    headers: Mapping[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Request builders
# --------------------------------------------------------------------------
def is_valid_controller_id(value: object) -> bool:
    """1 to 64 characters of letters, digits and ``. _ : -``."""
    return isinstance(value, str) and _CONTROLLER_ID.fullmatch(value) is not None


def _robot_id(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ServerRequestError("robot_id must be an integer")
    return value


def _controller(value: str | None) -> str | None:
    if value is None:
        return None
    if not is_valid_controller_id(value):
        raise ServerRequestError("controller_id must be 1 to 64 characters: letters, digits, . _ : -")
    return value


def _number(value: object, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ServerRequestError(f"{name} must be a number")
    return value


def claim_request(
    robot_id: int,
    *,
    ttl_ms: int | float | None = None,
    force: bool | None = None,
    reason: str | None = None,
    controller_id: str | None = None,
) -> Request:
    body: dict[str, Any] = {}
    if ttl_ms is not None:
        body["ttlMs"] = _number(ttl_ms, "ttl_ms")
    if force is not None:
        body["force"] = bool(force)
    if reason is not None:
        body["reason"] = str(reason)
    controller = _controller(controller_id)
    if controller is not None:
        body["controllerId"] = controller
    return Request("POST", f"/api/robot/{_robot_id(robot_id)}/claim", body)


def release_request(robot_id: int, *, reason: str | None = None, controller_id: str | None = None) -> Request:
    body: dict[str, Any] = {}
    if reason is not None:
        body["reason"] = str(reason)
    controller = _controller(controller_id)
    if controller is not None:
        body["controllerId"] = controller
    return Request("POST", f"/api/robot/{_robot_id(robot_id)}/release", body)


def jog_arm_request(
    robot_id: int,
    armed: bool,
    *,
    ttl_ms: int | float | None = None,
    controller_id: str | None = None,
) -> Request:
    if not isinstance(armed, bool):
        raise ServerRequestError("armed must be true or false")
    body: dict[str, Any] = {"armed": armed}
    if ttl_ms is not None:
        body["ttlMs"] = _number(ttl_ms, "ttl_ms")
    controller = _controller(controller_id)
    if controller is not None:
        body["controllerId"] = controller
    return Request("POST", f"/api/robot/{_robot_id(robot_id)}/jog-arm", body)


def list_claims_request() -> Request:
    return Request("GET", "/api/claims")


def safety_limits_request(robot_id: int | None = None) -> Request:
    path = "/api/safety-limits"
    if robot_id is not None:
        path += f"?robotId={_robot_id(robot_id)}"
    return Request("GET", path)


def update_safety_limits_request(patch: Mapping[str, Any]) -> Request:
    if not isinstance(patch, Mapping):
        raise ServerRequestError("patch must be an object")
    return Request("PUT", "/api/admin/safety-limits", dict(patch))


def command_request(
    robot_id: int,
    command: str,
    params: Mapping[str, Any] | None = None,
    *,
    controller_id: str | None = None,
) -> Request:
    if not isinstance(command, str) or not command:
        raise ServerRequestError("command must be a non-empty string")
    body: dict[str, Any] = {"command": command}
    if params is not None:
        body["params"] = dict(params)
    controller = _controller(controller_id)
    if controller is not None:
        body["controllerId"] = controller
    return Request("POST", f"/api/robot/{_robot_id(robot_id)}/command", body)


# --------------------------------------------------------------------------
# Response parsers
# --------------------------------------------------------------------------
def _object(value: Any, what: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ServerRequestError(f"{what} must be a JSON object")
    return value


def parse_reservation(value: Any) -> Reservation | None:
    """A ``reservation`` object, or ``None`` when the robot has no claim."""
    if value is None:
        return None
    data = _object(value, "reservation")
    controller = data.get("controllerId")
    return Reservation(
        owner_id=data.get("ownerId"),
        owner_username=str(data.get("ownerUsername", "")),
        claimed_at=data.get("claimedAt", 0),
        expires_at=data.get("expiresAt", 0),
        controller_id=controller if isinstance(controller, str) else None,
    )


def parse_claim_result(body: Any) -> ClaimResult:
    """The answer of ``claim`` and of ``release`` (the reservation is ``None``
    after a release)."""
    data = _object(body, "claim answer")
    history = data.get("reservationHistory")
    return ClaimResult(
        reservation=parse_reservation(data.get("reservation")),
        history=tuple(entry for entry in history if isinstance(entry, Mapping)) if isinstance(history, list) else (),
    )


def parse_jog_arm_result(body: Any) -> JogArmResult:
    data = _object(body, "jog-arm answer")
    armed = data.get("armed")
    if not isinstance(armed, bool):
        raise ServerRequestError("jog-arm answer has no boolean 'armed'")
    return JogArmResult(armed=armed, expires_at=data.get("expiresAt"), ttl_ms=data.get("ttlMs"))


def parse_claims(body: Any) -> tuple[ClaimEntry, ...]:
    data = _object(body, "claims answer")
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ServerRequestError("claims answer has no 'claims' list")
    entries = []
    for raw in claims:
        item = _object(raw, "claim")
        controller = item.get("controllerId")
        name = item.get("robotName")
        entries.append(
            ClaimEntry(
                robot_id=item.get("robotId"),
                robot_name=name if isinstance(name, str) else None,
                cell_id=item.get("cellId"),
                owner_id=item.get("ownerId"),
                owner_username=str(item.get("ownerUsername", "")),
                controller_id=controller if isinstance(controller, str) else None,
                claimed_at=item.get("claimedAt", 0),
                expires_at=item.get("expiresAt", 0),
            )
        )
    return tuple(entries)


def parse_safety_limits(body: Any) -> SafetyLimitsView:
    """The answer of ``GET`` and ``PUT`` of the safety limits. The sections are
    kept as the server sent them: the server owns their shape."""
    data = _object(body, "safety-limits answer")
    robot = data.get("robot")
    parsed_robot = None
    if robot is not None:
        item = _object(robot, "robot")
        model = item.get("model")
        parsed_robot = RobotSafety(
            id=item.get("id"),
            model=model if isinstance(model, str) else None,
            jog=_object(item.get("jog", {}), "robot.jog"),
            temperature=_object(item.get("temperature", {}), "robot.temperature"),
            jog_armed_until=item.get("jogArmedUntil"),
        )
    return SafetyLimitsView(
        limits=_object(data.get("limits", {}), "limits"),
        defaults=_object(data.get("defaults", {}), "defaults"),
        hard_limits=_object(data.get("hardLimits", {}), "hardLimits"),
        robot=parsed_robot,
    )


def parse_api_error(status: int, body: Any) -> ApiError:
    """Turns an error answer into the most specific typed error. ``body`` is
    the decoded JSON (or ``None`` when the answer was not JSON)."""
    data = body if isinstance(body, Mapping) else {}
    message = data.get("error") if isinstance(data.get("error"), str) else f"HTTP {status}"
    code = data.get("code") if isinstance(data.get("code"), str) else None
    reservation = None
    if isinstance(data.get("reservation"), Mapping):
        reservation = parse_reservation(data["reservation"])
    if code == CODE_CONTROLLER_ID_REQUIRED:
        return ControllerIdRequiredError(status, message, code, body, reservation)
    if code in (CODE_OTHER_ACCOUNT, CODE_OTHER_CONTROLLER):
        return ClaimConflictError(status, message, code, body, reservation)
    if code == CODE_INVALID_CONTROLLER_ID:
        return InvalidControllerIdError(status, message, code, body)
    if code == CODE_JOG_NOT_ARMED:
        return JogNotArmedError(status, message, code, body)
    if status == 409 and reservation is not None:
        return ClaimConflictError(status, message, code, body, reservation)
    return ApiError(status, message, code, body)


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------
Transport = Callable[[str, str, Mapping[str, str], bytes | None], "tuple[int, bytes]"]


def urllib_transport(timeout: float = 10.0) -> Transport:
    """The default transport: ``urllib``. Returns ``(status, body bytes)`` and
    never raises for an HTTP error status."""

    def send(method: str, url: str, headers: Mapping[str, str], data: bytes | None) -> tuple[int, bytes]:
        request = urllib.request.Request(url, data=data, method=method, headers=dict(headers))
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - the caller picks the URL
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    return send


class ServerClient:
    """Calls the routes above. ``controller_id`` is the identity this client
    picked for its session; it is sent with every request that accepts one
    unless a call passes its own."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        *,
        controller_id: str | None = None,
        transport: Transport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.controller_id = _controller(controller_id)
        self._transport = transport or urllib_transport()

    def _send(self, request: Request) -> Any:
        headers = {"Accept": "application/json", **request.headers}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if request.body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(request.body).encode("utf-8")
        status, raw = self._transport(request.method, self.base_url + request.path, headers, data)
        try:
            decoded = json.loads(raw.decode("utf-8")) if raw else None
        except (UnicodeDecodeError, ValueError):
            decoded = None
        if status >= 400:
            raise parse_api_error(status, decoded)
        return decoded

    def _controller_for(self, controller_id: str | None) -> str | None:
        return controller_id if controller_id is not None else self.controller_id

    def claim(self, robot_id: int, *, ttl_ms=None, force=None, reason=None, controller_id=None) -> ClaimResult:
        request = claim_request(robot_id, ttl_ms=ttl_ms, force=force, reason=reason, controller_id=self._controller_for(controller_id))
        return parse_claim_result(self._send(request))

    def release(self, robot_id: int, *, reason=None, controller_id=None) -> ClaimResult:
        request = release_request(robot_id, reason=reason, controller_id=self._controller_for(controller_id))
        return parse_claim_result(self._send(request))

    def jog_arm(self, robot_id: int, armed: bool, *, ttl_ms=None, controller_id=None) -> JogArmResult:
        request = jog_arm_request(robot_id, armed, ttl_ms=ttl_ms, controller_id=self._controller_for(controller_id))
        return parse_jog_arm_result(self._send(request))

    def list_claims(self) -> tuple[ClaimEntry, ...]:
        return parse_claims(self._send(list_claims_request()))

    def safety_limits(self, robot_id: int | None = None) -> SafetyLimitsView:
        return parse_safety_limits(self._send(safety_limits_request(robot_id)))

    def update_safety_limits(self, patch: Mapping[str, Any]) -> SafetyLimitsView:
        return parse_safety_limits(self._send(update_safety_limits_request(patch)))

    def command(self, robot_id: int, command: str, params: Mapping[str, Any] | None = None, *, controller_id=None) -> Any:
        """Sends a robot command and returns the decoded answer unchanged."""
        request = command_request(robot_id, command, params, controller_id=self._controller_for(controller_id))
        return self._send(request)
