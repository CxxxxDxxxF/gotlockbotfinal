import pytesseract
from PIL import Image
import re

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_bet_details(text: str) -> dict:
    # Very basic extraction logic
    bet_details = {
        "pick": "Not found",
        "game": "Not found",
        "date": "Not found",
        "time": "Not found",
        "units": "Not found",
        "vip": "No"
    }

    # Example parsing
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if "units" in line.lower():
            match = re.search(r"(\d+(\.\d+)?)\s*units", line, re.IGNORECASE)
            if match:
                bet_details["units"] = match.group(1)
        elif "vip" in line.lower():
            bet_details["vip"] = "Yes"
        elif "vs" in line.lower():
            bet_details["game"] = line
        elif re.search(r"\b\d{1,2}/\d{1,2}\b", line):
            bet_details["date"] = line
        elif re.search(r"\b\d{1,2}:\d{2}\s*(AM|PM)?\b", line, re.IGNORECASE):
            bet_details["time"] = line
        elif "pick" in line.lower():
            bet_details["pick"] = line.split("pick")[-1].strip()

    return bet_details
