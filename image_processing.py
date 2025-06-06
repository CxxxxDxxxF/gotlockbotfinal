import pytesseract
from PIL import Image
import re

def extract_text_from_image(image_path: str) -> str:
    """
    Opens the image at image_path and returns all OCR’d text as one string.
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_bet_details(text: str) -> dict:
    """
    Given OCR’d text, attempts to parse:
      - pick   (e.g. "Tampa Bay Rays Money Line" or "Zack Wheeler 6+ Strikeouts")
      - game   (e.g. "Tampa Bay Rays vs New York Yankees")
      - date   (e.g. "6/5/25")
      - time   (e.g. "7:00 PM EST")
      - units  (e.g. "12")
      - vip    ("Yes" or "No")
    Returns a dict with keys ["pick","game","date","time","units","vip"].
    """
    bet_details = {
        "pick": "Not found",
        "game": "Not found",
        "date": "Not found",
        "time": "Not found",
        "units": "Not found",
        "vip": "No"
    }

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Units: “12 units” or “1.5 units”
        if "units" in line.lower():
            match = re.search(r"(\d+(\.\d+)?)\s*units", line, re.IGNORECASE)
            if match:
                bet_details["units"] = match.group(1)

        # VIP flag
        if "vip" in line.lower():
            bet_details["vip"] = "Yes"

        # Game: “Team A vs Team B” (we’ll normalize later)
        if "vs" in line.lower():
            bet_details["game"] = line

        # Date like “6/5/25” or “06/05/2025”
        if re.search(r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b", line):
            bet_details["date"] = line

        # Time like “7:00 PM” or “19:05”
        if re.search(r"\b\d{1,2}:\d{2}\s*(AM|PM)?\b", line, re.IGNORECASE):
            bet_details["time"] = line

        # Pick details (anything after “Pick:” for example)
        if "pick" in line.lower():
            # split on “pick” and keep everything after it
            parts = re.split(r"pick[:\-]?", line, flags=re.IGNORECASE)
            if len(parts) >= 2 and parts[1].strip():
                bet_details["pick"] = parts[1].strip()

    return bet_details

