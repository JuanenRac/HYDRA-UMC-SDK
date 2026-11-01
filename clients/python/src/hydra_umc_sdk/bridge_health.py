# =============================================================================
# HYDRA-UMC-SDK - Bridge health on one retained topic
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Where a bridge says how it is: `hydra/bridges/<name>/health`, retained, QoS 1, in the shape of the `HealthReport` contract.

The server and the dashboard used to probe every bridge, or to read `availability` (only "online" or "offline") and guess the rest. With the health topic on, each bridge
publishes its state there when it connects (`READY`, with the check `link` passing), whenever it has something to say (`DEGRADED`, `INHIBITED`, `FAULT`, `SAFE_STOP`, with
the checks that explain it) and has the broker publish `FAULT` there if the link dies (the Last Will). One topic family replaces one probe per bridge.

An MQTT connection has one Last Will, and it cannot be on `availability` and on `health` at the same time. So the health topic is a switch (`HYDRA_UMC_<NAME>_BRIDGE_HEALTH`, yes
or no; off by default and then nothing changes): when it is on, the Last Will of the bridge is the `FAULT` report, `availability` is no longer maintained (the retained message
that an earlier run left there is cleared when the bridge connects, so nobody keeps reading an old "online") and a consumer reads the health topic only.

The report says what the bridge observes about itself and its link, never a command: nothing here gives anybody authority over the machine.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping, Optional

from .bridge_transport import MqttPublish
from .validation import ContractValidationError, validate

HEALTH_STATES: tuple[str, ...] = ("READY", "DEGRADED", "INHIBITED", "FAULT", "SAFE_STOP")
BRIDGE_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"", "0", "false", "no", "off"}
LINK_CHECK = "link"


def health_topic(name: str) -> str:
    """`hydra/bridges/<name>/health`; the name is the lowercase name of the bridge (`cnc`, `laser`, `openpnp`, ...)."""
    if not isinstance(name, str) or not BRIDGE_NAME.fullmatch(name):
        raise ValueError("a bridge name is 1 to 32 lowercase letters, digits, dashes or underscores")
    return f"hydra/bridges/{name}/health"


def health_enabled_from_environment(name: str, environ: Optional[Mapping[str, str]] = None) -> bool:
    """`HYDRA_UMC_<NAME>_BRIDGE_HEALTH` (yes switches the health topic on). A value that is neither a clear yes nor a clear no raises `ValueError` naming the variable."""
    env = os.environ if environ is None else environ
    variable = f"HYDRA_UMC_{name.upper()}_BRIDGE_HEALTH"
    raw = env.get(variable, "").strip().lower()
    if raw in _FALSE:
        return False
    if raw in _TRUE:
        return True
    raise ValueError(f"{variable} must be yes or no, not {raw!r}")


def health_report(state: str, checks: Optional[Mapping[str, Mapping[str, object]]] = None, *, now: Optional[datetime] = None) -> dict[str, object]:
    """A `HealthReport` for `state` with the given checks (each `{"state": "PASS" | "FAIL", "detail": ...}`); validated before it is returned."""
    if state not in HEALTH_STATES:
        raise ValueError(f"state must be one of {', '.join(HEALTH_STATES)}")
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    report: dict[str, object] = {
        "schema_version": "1.0",
        "state": state,
        "timestamp_utc": moment.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": {name: dict(check) for name, check in (checks or {}).items()},
    }
    validate("HealthReport", report)
    return report


@dataclass(frozen=True)
class BridgeHealth:
    """The health topic of one bridge. `clock` returns the moment a report is made (a test passes a fixed one)."""

    name: str
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        health_topic(self.name)

    @property
    def topic(self) -> str:
        return health_topic(self.name)

    def _publish(self, state: str, checks: Optional[Mapping[str, Mapping[str, object]]]) -> MqttPublish:
        return MqttPublish(self.topic, json.dumps(health_report(state, checks, now=self.clock())), retain=True, qos=1)

    def online(self) -> MqttPublish:
        """`READY`, with the link passing: what the bridge publishes when its connection is accepted."""
        return self._publish("READY", {LINK_CHECK: {"state": "PASS"}})

    def report(self, state: str, checks: Optional[Mapping[str, Mapping[str, object]]] = None) -> MqttPublish:
        """The report for `state`. The link check is added as passing unless the caller gave one, so a report always says that the bridge itself is reachable."""
        merged = {LINK_CHECK: {"state": "PASS"}, **(checks or {})}
        return self._publish(state, merged)

    def will(self) -> MqttPublish:
        """The Last Will: `FAULT`, with the link failing, retained at QoS 1. The broker publishes it when the bridge disappears."""
        return self._publish("FAULT", {LINK_CHECK: {"state": "FAIL", "detail": "the bridge disconnected without saying goodbye"}})

    def goodbye(self) -> MqttPublish:
        """What a bridge that stops on purpose publishes before it disconnects: `FAULT` with the reason, since nothing is watching the machine any more."""
        return self._publish("FAULT", {LINK_CHECK: {"state": "FAIL", "detail": "the bridge stopped"}})


def read_health(payload: bytes) -> dict[str, object]:
    """The `HealthReport` in a message of a health topic; raises `ContractValidationError` when it is not one."""
    try:
        decoded = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as error:
        raise ContractValidationError(f"the health message is not JSON: {error}") from error
    if not isinstance(decoded, dict):
        raise ContractValidationError("the health message must be a JSON object")
    validate("HealthReport", decoded)
    return decoded
