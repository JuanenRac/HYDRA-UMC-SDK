# =============================================================================
# HYDRA-UMC-SDK - Mock server unit tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

import json
import threading
import unittest
import urllib.error
import urllib.request

from hydra_umc_sdk.mock_server import EXAMPLE_PAYLOADS, create_server
from hydra_umc_sdk.validation import REQUIRED, validate


class MockServerTests(unittest.TestCase):
    def setUp(self) -> None:
        # port=0 asks the OS for a real, currently-free ephemeral port -
        # avoids ever colliding with another test run or a real service.
        self.server = create_server(port=0)
        self.host, self.port = self.server.server_address
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()

    def _get(self, path: str) -> tuple[int, dict]:
        url = f"http://{self.host}:{self.port}{path}"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            with exc:
                return exc.code, json.loads(exc.read())

    def test_has_one_example_per_known_contract(self) -> None:
        # Real completeness proof, not just an assumption: every contract
        # validate() knows about has a real example here, and vice versa -
        # mock_server.py itself already enforces this at import time, this
        # proves that enforcement actually holds right now.
        self.assertEqual(set(EXAMPLE_PAYLOADS), set(REQUIRED))

    def test_every_example_payload_is_actually_valid(self) -> None:
        for contract, payload in EXAMPLE_PAYLOADS.items():
            with self.subTest(contract=contract):
                validate(contract, payload)  # raises on failure

    def test_index_lists_every_contract(self) -> None:
        status, body = self._get("/mock/")
        self.assertEqual(status, 200)
        self.assertEqual(sorted(body["contracts"]), sorted(EXAMPLE_PAYLOADS))

    def test_serves_a_real_valid_payload_per_contract_over_http(self) -> None:
        for contract in EXAMPLE_PAYLOADS:
            with self.subTest(contract=contract):
                status, body = self._get(f"/mock/{contract}")
                self.assertEqual(status, 200)
                validate(contract, body)  # proves the real HTTP response, not just the dict, is valid

    def test_unknown_contract_is_a_clean_404_not_a_crash(self) -> None:
        status, body = self._get("/mock/NotARealContract")
        self.assertEqual(status, 404)
        self.assertIn("error", body)

    def test_unrelated_path_is_a_clean_404(self) -> None:
        status, _ = self._get("/not-mock-at-all")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
