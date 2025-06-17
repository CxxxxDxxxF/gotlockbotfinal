# image_processing.py

#!/usr/bin/env python3
"""
image_processing.py

Handles OCR extraction and parsing of bet slip details.
"""
import logging
import re
from typing import Optional, Dict, Union

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


def preprocess_image(image_input: Union[str, bytes]) -> np.ndarray:
    """
    Loads and preprocesses an image (from a file path or raw bytes) for OCR:
    - Reads via OpenCV
    - Converts to grayscale
    - Applies Gaussian blur
    - Thresholds via Otsu
    - Resizes to max width 1024px
    Returns the processed binary NumPy array.
    """
    # load
    if isinstance(image_input, (bytes, bytearray)):
        arr = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError("Image bytes could not be decoded.")
    else:
        img = cv2.imread(image_input)
        if img is None:
            raise FileNotFoundError(f"Image not found or unreadable: {image_input}")

    # grayscale + blur + threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # resize to max width 1024
    h, w = thresh.shape
    scale = min(1.0, 1024.0 / w)
    resized = cv2.resize(
        thresh,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_CUBIC
    )

    logger.debug("Image preprocessed: grayscale, blur, threshold, resized")
    return resized


def extract_text_from_image(
    image_input: Union[str, bytes],
    config: Optional[str] = None
) -> str:
    """
    Uses Tesseract OCR to extract text from the preprocessed image.
    Accepts either a file path or raw image bytes.
    """
    if config is None:
        config = "--psm 6 --oem 3"
    try:
        bin_img = preprocess_image(image_input)
        pil_img = Image.fromarray(bin_img)
        text = pytesseract.image_to_string(pil_img, config=config)
        logger.info(f"OCR extracted {len(text)} characters")
        return text
    except Exception:
        logger.exception("Failed to extract text from image")
        raise


def parse_bet_details(text: str) -> Optional[Dict[str, str]]:
    """
    Parses relevant information from OCR'd text.
    - Team moneyline: "Yankees at Red Sox +150"
    - Player props:    "Player Over 1.5 Hits -120"
    Returns a dict:
      Team ML -> {"away":..., "home":..., "bet":..., "odds":...}
      Prop    -> {"player":..., "bet":..., "odds":...}
    """
    logger.debug("Parsing bet details from OCR text")

    # patterns
    prop_pat = re.compile(
        r"([A-Za-z]+(?:\s[A-Za-z]+)+)\s+(Over|Under)\s+([\d\.]+)\s+([A-Za-z]+(?:\s[A-Za-z]+)*)",
        re.IGNORECASE
    )
    team_pat = re.compile(r"([A-Za-z\s]+?)\s+at\s+([A-Za-z\s]+)", re.IGNORECASE)
    odds_pat = re.compile(r"([-+]\d{2,4})")

    prop_m = prop_pat.search(text)
    odds_m = odds_pat.search(text)

    if prop_m and odds_m:
        player = prop_m.group(1).strip()
        direction = prop_m.group(2).capitalize()
        value = prop_m.group(3)
        metric = prop_m.group(4).strip()
        odds = odds_m.group(1)
        bet_desc = f"{direction} {value} {metric}"
        logger.info(f"Detected player prop: {player} | {bet_desc} | {odds}")
        return {
            "player": player,
            "bet": bet_desc,
            "odds": odds
        }

    team_m = team_pat.search(text)
    if team_m and odds_m:
        team1 = team_m.group(1).strip()
        team2 = team_m.group(2).strip()
        odds = odds_m.group(1)
        logger.info(f"Detected team moneyline: {team1} @ {team2} | {odds}")
        return {
            "away": team1,
            "home": team2,
            "bet": f"{team1} – Moneyline",
            "odds": odds
        }

    logger.warning("No valid bet details found in OCR text")
    return None
