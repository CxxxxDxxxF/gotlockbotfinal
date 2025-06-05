import pytesseract
from PIL import Image
from config import TESSERACT_CMD_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH


def image_to_text(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


def parse_bets_from_text(raw_text: str) -> list:
    bets = []
    lines = raw_text.splitlines()
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 3:
            team_code = parts[0]
            token1 = parts[-2]
            token2 = parts[-1]
            if token1.upper() == 'ML':
                bet = {
                    'teamA': decode_team_code(team_code),
                    'teamB': None,
                    'line': 'ML',
                    'odds': int(token2)
                }
            else:
                try:
                    line_val = float(token1)
                except ValueError:
                    continue
                bet = {
                    'teamA': decode_team_code(team_code),
                    'teamB': None,
                    'line': line_val,
                    'odds': int(token2)
                }
            bets.append(bet)
    return bets


def decode_team_code(code: str) -> str:
    mapping = {
        'NYY': 'New York Yankees',
        'BOS': 'Boston Red Sox',
        'HOU': 'Houston Astros',
    }
    return mapping.get(code.upper(), code)
