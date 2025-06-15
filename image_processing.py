import pytesseract
from PIL import Image
import re

def extract_text_from_image(image_path):
    """
    Uses Tesseract OCR to extract text from the uploaded image.
    """
    return pytesseract.image_to_string(Image.open(image_path))


def parse_bet_details(text):
    """
    Parses relevant information from the OCR'd bet slip text.
    Extracts: Game matchup, bet type, odds
    """
    # Match player + bet line (ex: Hunter Dobbins Over 2.5 Earned Runs)
    player_line_match = re.search(
        r"([A-Za-z\s\-]+)\s+(Over|Under)\s+([\d\.]+)\s+(Earned Runs|Hits|Strikeouts)",
        text,
        re.IGNORECASE
    )

    # Match American odds (ex: -115, +100)
    odds_match = re.search(r"([-+]\d{2,4})", text)

    # Match team matchup (ex: Yankees @ Red Sox)
    teams_match = re.search(
        r"([A-Za-z]+)\s*@\s*([A-Za-z]+)",
        text,
        re.IGNORECASE
    )

    if not player_line_match or not odds_match or not teams_match:
        return None  # Return None if key parts can't be extracted

    bet_player = player_line_match.group(1).strip()
    bet_type = f"{player_line_match.group(2)} {player_line_match.group(3)} {player_line_match.group(4)}"
    odds = odds_match.group(1).strip()
    game = f"{teams_match.group(1)} @ {teams_match.group(2)}"

    return {
        "game": game,
        "bet": f"{bet_player} – {bet_type}",
        "odds": odds
    }
