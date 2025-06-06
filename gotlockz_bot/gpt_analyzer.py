"""Utilities for analyzing text with OpenAI."""

import os
import openai


def analyze_text(text: str) -> str:
    """Return a short analysis of the given text using the OpenAI API."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        max_tokens=50,
    )
    return response.choices[0].message["content"].strip()
