# =============================================================================
# HYDRA-UMC-SDK - How a bridge connects to the MQTT broker: credentials and TLS from the environment
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The connection settings every bridge needs to reach a HYDRA-UMC-MQTT-BROKER that demands a user and a password (a production broker does), once instead of eight times.

A bridge used to connect with a bare `mqtt.Client()`: it could not reach a broker that required credentials, and nothing protected the link. The settings come from the environment
of the service (a systemd `Environment=`/`EnvironmentFile=`, a Docker `-e`), never from a file that is committed:

* `HYDRA_MQTT_USERNAME` / `HYDRA_MQTT_PASSWORD`: the MQTT credentials (the password only together with the user name). The broker binds the credential to a client ID prefix and evaluates its
  ACL for that identity, so the bridge's client ID must start with the prefix of its credential.
* `HYDRA_MQTT_PASSWORD_FILE`: the password read from a file (a Docker/systemd secret) instead of the environment; ignored when HYDRA_MQTT_PASSWORD is set.
* `HYDRA_MQTT_TLS_CA`: the CA certificate (a file) that signed the broker's certificate: the connection is then TLS and the broker's certificate is verified.

Pure standard library: the paho client is passed in, never imported here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class MqttConnectionSettings:
    username: Optional[str] = None
    password: Optional[str] = None
    tls_ca_path: Optional[str] = None


def settings_from_env(env: Optional[Mapping[str, str]] = None) -> MqttConnectionSettings:
    """The settings the environment asks for (all absent = an anonymous plain connection, as before). A password with no user name is refused: it was meant to be both."""
    source = os.environ if env is None else env
    username = (source.get("HYDRA_MQTT_USERNAME") or "").strip() or None
    password = source.get("HYDRA_MQTT_PASSWORD") or None
    password_file = (source.get("HYDRA_MQTT_PASSWORD_FILE") or "").strip()
    if password is None and password_file:
        with open(password_file, encoding="utf-8") as handle:
            password = handle.read().rstrip("\r\n") or None
    ca = (source.get("HYDRA_MQTT_TLS_CA") or "").strip() or None
    if password is not None and username is None:
        raise ValueError("HYDRA_MQTT_PASSWORD was given without HYDRA_MQTT_USERNAME - MQTT credentials need both")
    return MqttConnectionSettings(username=username, password=password, tls_ca_path=ca)


def apply_connection_settings(client: object, settings: MqttConnectionSettings, *, username: Optional[str] = None, password: Optional[str] = None) -> None:
    """Put the credentials and the TLS configuration on a paho client before it connects.

    `username`/`password` given explicitly win over the environment (and the password then comes from the same source as the user name, so a user name from the call is never
    paired with a password from the environment).
    """
    user = username if username is not None else settings.username
    secret = password if username is not None else settings.password
    if user is not None:
        client.username_pw_set(user, secret)  # type: ignore[attr-defined]
    if settings.tls_ca_path is not None:
        client.tls_set(ca_certs=settings.tls_ca_path)  # type: ignore[attr-defined]
