import pytest
import openai
import os

import ai_analysis  # assuming your module is named ai_analysis.py


def test_generate_analysis_success(monkeypatch):
    # Prepare fake bet_details
    bet_details = {
        'game': 'Team A @ Team B',
        'pick': 'Team A to win',
        'units': '3',
        'date': '06/16/25',
        'time': '19:05',
        'vip': True
    }

    # Create a dummy response object
    class DummyChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)

    class DummyResponse:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    # Monkey-patch ChatCompletion.create
    def fake_create(model, messages):
        # Assert model name
        assert model == 'gpt-4'
        # Assert system and user messages present
        assert any(m['role'] == 'system' for m in messages)
        assert any(m['role'] == 'user' for m in messages)
        return DummyResponse("This is a fake analysis.")

    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)

    # Call the function
    result = ai_analysis.generate_analysis(bet_details)
    assert result == "This is a fake analysis."


def test_generate_analysis_error(monkeypatch):
    bet_details = {'game': 'X', 'pick': 'Y', 'units': '1', 'date': 'd', 'time': 't', 'vip': False}

    # Monkey-patch to raise an exception
    def fake_error(*args, **kwargs):
        raise Exception("API failure")

    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_error)

    # Expect the error message returned
    result = ai_analysis.generate_analysis(bet_details)
    assert result.startswith("Error generating analysis:")
