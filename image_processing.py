#!/usr/bin/env python3
"""
image_processing.py

Handles OCR extraction and parsing of bet slip details.
"""
import logging
import re
from typing import Optional, Dict

import pytesseract
from PIL import Image
import cv2
import numpy as np

# ---- Logging Setup ----
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def preprocess_image(image_path: str) -> Image.Image:
    """
    Preprocesses the image for better OCR results:
    - Converts to grayscale
    - Applies Gaussian blur
    - Thresholds using Otsu's method
    - Resizes for clarity
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found or unreadable: {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        h, w = thresh.shape
        # scale to max width of 1024
        scale = min(1.0, 1024 / float(w))
        resized = cv2.resize(thresh, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        logger.debug("Image preprocessed: grayscale, blur, threshold, resized")
        return Image.fromarray(resized)
    except Exception as e:
        logger.exception("Error during image preprocessing")
        raise


def extract_text_from_image(image_path: str, config: Optional[str] = None) -> str:
    """
    Uses Tesseract OCR to extract text from the image with optional config.
    """
    if config is None:
        config = "--psm 6 --oem 3"
    try:
        pil_img = preprocess_image(image_path)
        text = pytesseract.image_to_string(pil_img, config=config)
        logger.info(f"OCR extracted {len(text)} characters from {image_path}")
        return text
    except Exception as e:
        logger.exception("Failed to extract text from image")
        raise


def parse_bet_details(text: str) -> Optional[Dict[str, str]]:
    """
    Parses relevant information from OCR'd text.
    Supports:
      - Player props (Over/Under)
      - Team moneyline bets
    Returns a dict with keys: game, bet, odds
    """
    logger.debug("Parsing bet details from OCR text")
    # Regex patterns
    prop_pattern = re.compile(
        r"([A-Za-z]+(?:\s[A-Za-z]+)+)\s+(Over|Under)\s+([\d\.]+)\s+([A-Za-z]+(?:\s[A-Za-z]+)*)",
        re.IGNORECASE
    )
    team_pattern = re.compile(
        r"([A-Za-z\s]+?)\s+at\s+([A-Za-z\s]+)",
        re.IGNORECASE
    )
    odds_pattern = re.compile(r"([-+]\d{2,4})")

    prop_match = prop_pattern.search(text)
    odds_match = odds_pattern.search(text)

    # Player prop
    if prop_match and odds_match:
        player = prop_match.group(1).strip()
        direction = prop_match.group(2).capitalize()
        value = prop_match.group(3)
        metric = prop_match.group(4).strip()
        odds = odds_match.group(1)
        bet_desc = f"{direction} {value} {metric}"
        logger.info(f"Detected player prop: {player} | {bet_desc} | {odds}")
        return {
            "game": player,
            "bet": bet_desc,
            "odds": odds
        }

    # Team moneyline
    team_match = team_pattern.search(text)
    if team_match and odds_match:
        team1 = team_match.group(1).strip()
        team2 = team_match.group(2).strip()
        odds = odds_match.group(1)
        logger.info(f"Detected team moneyline: {team1} @ {team2} | {odds}")
        return {
            "game": f"{team1} @ {team2}",
            "bet": f"{team1} – Moneyline",
            "odds": odds
        }

    logger.warning("No valid bet details found in OCR text")
    return None
