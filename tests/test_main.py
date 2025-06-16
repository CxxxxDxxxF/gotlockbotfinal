import pytest
import os

import image_processing
from image_processing import parse_bet_details, extract_text_from_image
from PIL import Image


def test_parse_player_prop():
    text = "Hunter Dobbins Over 2.5 Earned Runs -110"
    expected = {
        "game": "Hunter Dobbins",
        "bet": "Over 2.5 Earned Runs",
        "odds": "-110"
    }
    assert parse_bet_details(text) == expected


def test_parse_moneyline():
    text = "New York Yankees at Boston Red Sox +150"
    expected = {
        "game": "New York Yankees @ Boston Red Sox",
        "bet": "New York Yankees – Moneyline",
        "odds": "+150"
    }
    assert parse_bet_details(text) == expected


def test_parse_invalid_text():
    # Text that doesn't contain bet info
    text = "This has no betting details"
    assert parse_bet_details(text) is None


def test_extract_text_from_image_monkeypatched(monkeypatch, tmp_path):
    # Create an empty dummy file path
    dummy_file = tmp_path / "dummy.png"
    dummy_file.write_bytes(b"")

    # Prepare a fake PIL Image to return
    fake_img = Image.new('RGB', (10, 10))
    # Monkeypatch the preprocessing step to bypass OpenCV
    monkeypatch.setattr(image_processing, 'preprocess_image', lambda path: fake_img)
    # Monkeypatch pytesseract to return fixed text
    monkeypatch.setattr(image_processing.pytesseract, 'image_to_string', lambda img, config=None: "SAMPLE OCR OUTPUT")

    # Call the function under test
    result = extract_text_from_image(str(dummy_file))
    assert result == "SAMPLE OCR OUTPUT"


def test_preprocess_image_file_not_found():
    # Expect FileNotFoundError for non-existent path
    with pytest.raises(FileNotFoundError):
        image_processing.preprocess_image("nonexistent_file.png")
