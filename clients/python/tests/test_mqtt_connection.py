# =============================================================================
# HYDRA-UMC-SDK - MQTT connection settings tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import os
import tempfile
import unittest

from hydra_umc_sdk.mqtt_connection import MqttConnectionSettings, apply_connection_settings, settings_from_env


class FakeClient:
    def __init__(self):
        self.credentials = None
        self.tls = None

    def username_pw_set(self, username, password=None):
        self.credentials = (username, password)

    def tls_set(self, ca_certs=None):
        self.tls = ca_certs


class SettingsFromEnvTests(unittest.TestCase):
    def test_nothing_set_is_an_anonymous_plain_connection(self):
        self.assertEqual(settings_from_env({}), MqttConnectionSettings())

    def test_user_password_and_ca(self):
        settings = settings_from_env({"HYDRA_MQTT_USERNAME": " bridge ", "HYDRA_MQTT_PASSWORD": "s3cret", "HYDRA_MQTT_TLS_CA": "/etc/ca.pem"})
        self.assertEqual((settings.username, settings.password, settings.tls_ca_path), ("bridge", "s3cret", "/etc/ca.pem"))

    def test_system_ca_tls_and_a_client_certificate(self):
        self.assertTrue(settings_from_env({"HYDRA_MQTT_TLS": "1"}).tls)
        self.assertFalse(settings_from_env({"HYDRA_MQTT_TLS": "0"}).tls)
        mutual = settings_from_env({"HYDRA_MQTT_TLS_CERT": "/c.pem", "HYDRA_MQTT_TLS_KEY": "/k.pem"})
        self.assertTrue(mutual.tls)
        self.assertEqual((mutual.tls_cert_path, mutual.tls_key_path), ("/c.pem", "/k.pem"))
        with self.assertRaises(ValueError):
            settings_from_env({"HYDRA_MQTT_TLS_CERT": "/c.pem"})

    def test_a_missing_password_file_is_a_clear_error(self):
        with self.assertRaises(ValueError) as caught:
            settings_from_env({"HYDRA_MQTT_USERNAME": "u", "HYDRA_MQTT_PASSWORD_FILE": "/does/not/exist"})
        self.assertIn("HYDRA_MQTT_PASSWORD_FILE", str(caught.exception))

    def test_a_password_alone_is_refused_when_applying(self):
        class Client:
            def username_pw_set(self, *args):
                raise AssertionError("must not be called")

        with self.assertRaises(ValueError):
            apply_connection_settings(Client(), settings_from_env({}), password="x")

    def test_password_without_user_is_refused(self):
        with self.assertRaises(ValueError):
            settings_from_env({"HYDRA_MQTT_PASSWORD": "s3cret"})

    def test_password_from_a_file_and_the_variable_wins(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as handle:
            handle.write("from-file\n")
            path = handle.name
        try:
            self.assertEqual(settings_from_env({"HYDRA_MQTT_USERNAME": "b", "HYDRA_MQTT_PASSWORD_FILE": path}).password, "from-file")
            self.assertEqual(settings_from_env({"HYDRA_MQTT_USERNAME": "b", "HYDRA_MQTT_PASSWORD": "inline", "HYDRA_MQTT_PASSWORD_FILE": path}).password, "inline")
        finally:
            os.unlink(path)


class ApplyTests(unittest.TestCase):
    def test_environment_credentials_and_tls_are_put_on_the_client(self):
        client = FakeClient()
        apply_connection_settings(client, MqttConnectionSettings("bridge", "pw", "/ca.pem"))
        self.assertEqual(client.credentials, ("bridge", "pw"))
        self.assertEqual(client.tls, "/ca.pem")

    def test_an_anonymous_setting_touches_nothing(self):
        client = FakeClient()
        apply_connection_settings(client, MqttConnectionSettings())
        self.assertIsNone(client.credentials)
        self.assertIsNone(client.tls)

    def test_explicit_credentials_win_and_never_mix_with_the_environment_password(self):
        client = FakeClient()
        apply_connection_settings(client, MqttConnectionSettings("env-user", "env-pw"), username="given", password=None)
        self.assertEqual(client.credentials, ("given", None))


if __name__ == "__main__":
    unittest.main()
