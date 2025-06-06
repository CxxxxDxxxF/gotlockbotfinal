import pytesseract
from PIL import Image
import re
from datetime import datetime

def extract_text_from_image(image_path: str) -> str:
    """
    Run Tesseract OCR on the given image file and return the raw text.
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_bet_details(text: str) -> dict:
    """
    Very basic extraction logic. Scans OCR text for
    - a “pick” line
    - a “game” line (contains “vs”)
    - a date line (matches MM/DD or MM/DD/YYYY)
    - a time line (matches HH:MM AM/PM)
    - a “units” line (e.g. “2.5 units”)
    - a “vip” indicator (if the word “vip” appears)
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

        lower = line.lower()

        # Units
        if "units" in lower:
            match = re.search(r"(\d+(\.\d+)?)\s*units", line, re.IGNORECASE)
            if match:
                bet_details["units"] = match.group(1)

        # VIP
        if "vip" in lower:
            bet_details["vip"] = "Yes"

        # Game (expects something like "Tampa Bay Rays vs New York Yankees")
        if "vs" in lower:
            bet_details["game"] = line

        # Date (matches 6/5/25 or 06/05/2025, etc.)
        date_match = re.search(r"\b(\d{1,2})/(\d{1,2})(/(\d{2,4}))?\b", line)
        if date_match:
            try:
                # Try to normalize into MM/DD/YYYY (4-digit year)
                month = int(date_match.group(1))
                day = int(date_match.group(2))
                year = date_match.group(4)
                if year is None:
                    # If no year given, assume current year
                    year = datetime.utcnow().year
                else:
                    year = int(year)
                    if year < 100:  # e.g. "25" -> "2025"
                        year += 2000
                dt = datetime(year, month, day)
                bet_details["date"] = dt.strftime("%Y-%m-%d")
            except Exception:
                bet_details["date"] = line  # leave raw if parsing fails

        # Time (matches "7:05 PM" or "12:30 AM" etc.)
        time_match = re.search(r"\b(\d{1,2}:\d{2}\s*(AM|PM)?)\b", line, re.IGNORECASE)
        if time_match:
            bet_details["time"] = time_match.group(1).upper()

        # Pick (line containing the word "pick")
        if "pick" in lower and bet_details["pick"] == "Not found":
            # e.g. "Pick: Tampa Bay Rays ML (-110)"
            parts = re.split(r"pick[:\-]", line, flags=re.IGNORECASE)
            if len(parts) >= 2:
                bet_details["pick"] = parts[-1].strip()
            else:
                bet_details["pick"] = line  # fallback

    return bet_details
