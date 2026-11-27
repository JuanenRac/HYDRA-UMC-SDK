"""A full queue never drops an ABORT; a full idempotency store counts what it forgets."""
import json
import threading
from types import SimpleNamespace

from hydra_umc_sdk.bridge_transport import MessageDispatcher, is_abort_job
from hydra_umc_sdk.job_intake import IdempotencyStore


class Bridge:
    def __init__(self) -> None:
        self.gate = threading.Event()
        self.started = threading.Event()
        self.seen: list[bytes] = []

    def handle_message(self, topic: str, payload: bytes, *, retained: bool = False) -> list:
        self.started.set()
        self.gate.wait(10)
        self.seen.append(payload)
        return []


def job(phase: str, number: int) -> bytes:
    return json.dumps({"phase": phase, "n": number}).encode()


def test_an_abort_waiting_behind_a_full_queue_is_kept() -> None:
    bridge = Bridge()
    dispatcher = MessageDispatcher(bridge, "p/", max_queue=1)

    def send(payload: bytes) -> None:
        dispatcher.on_message(None, None, SimpleNamespace(topic="p/cmd/job", payload=payload, retain=False))

    send(job("PROCESS", 0))
    assert bridge.started.wait(10)
    abort = job("ABORT", 1)
    send(abort)
    for number in range(2, 6):
        send(job("PROCESS", number))
    bridge.gate.set()
    dispatcher.close()
    assert abort in bridge.seen and job("PROCESS", 5) in bridge.seen
    assert dispatcher.stats()["dropped"] == 3


def test_only_a_job_of_phase_abort_is_protected_by_default() -> None:
    assert is_abort_job("cmd/job", job(" abort ", 1))
    assert not is_abort_job("cmd/job", job("PROCESS", 1))
    assert not is_abort_job("cmd/other", job("ABORT", 1))
    assert not is_abort_job("cmd/job", b"not json")


def test_a_full_store_counts_the_keys_it_forgets() -> None:
    store = IdempotencyStore(max_entries=2)
    assert store.evicted == 0
    for key in ("a", "b", "c", "d"):
        assert store.claim(key)
    assert store.evicted == 2 and len(store) == 2
    store.close()
