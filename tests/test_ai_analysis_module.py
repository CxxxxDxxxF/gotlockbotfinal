import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ai_analysis

class DummyMessage:
    def __init__(self, content):
        self.content = content

class DummyChoice:
    def __init__(self, message):
        self.message = message

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(DummyMessage(content))]

class DummyCompletions:
    async def create(self, *args, **kwargs):
        return DummyResponse("dummy")

class DummyClient:
    def __init__(self):
        self.chat = type("obj", (), {"completions": DummyCompletions()})()

def test_generate_analysis_no_api_key(monkeypatch):
    monkeypatch.setattr(ai_analysis, "_client", None)
    result = asyncio.run(ai_analysis.generate_analysis({}))
    assert result == "AI analysis unavailable"

def test_generate_analysis_with_client(monkeypatch):
    monkeypatch.setattr(ai_analysis, "_client", DummyClient())
    result = asyncio.run(ai_analysis.generate_analysis({}))
    assert result == "dummy"
