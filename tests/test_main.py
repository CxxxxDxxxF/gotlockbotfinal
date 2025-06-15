import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main

class DummyUser:
    def __str__(self):
        return "testuser#1234"


def test_ready_message_uses_timestamp(monkeypatch):
    monkeypatch.setattr(main, "current_timestamp", lambda: "2025-06-06 12:34:56 UTC")
    assert (
        main.ready_message(DummyUser())
        == "\u2714\ufe0f GotLockz bot logged in as testuser#1234 at 2025-06-06 12:34:56 UTC"
    )


def test_current_timestamp_utc():
    ts = main.current_timestamp()
    assert ts.endswith("UTC")
