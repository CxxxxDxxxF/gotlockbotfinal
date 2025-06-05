# GotLockBot Final

GotLockBot Final is a feature-rich Discord betting assistant. Environment variables are defined in `.env.example`.

## Prerequisites
- Python 3.10+
- Tesseract OCR
- Discord Bot Token
- OpenAI API Key
- MLB Stats API Key
- The Odds API Key
- API-Sports Key
- JsonOdds Key
- Google Service Account JSON

## Installation & Setup
```bash
git clone <repo>
cp .env.example .env  # fill in secrets
pip install -r requirements.txt
sudo apt-get install tesseract-ocr libtesseract-dev
python bot.py
```

## Commands
- `/postpick <units> [#channel]`
- `/research <TeamA> vs <TeamB>`
- `/watchline <Team> <threshold> [#channel]`
- `/valuebets [threshold]`
- `/myportfolio`
- `/help`

## Deployment
Build with Docker:
```bash
docker build -t gotlockbot .
```
Use docker-compose to run main bot and daily summary.

## Testing
Run all unit tests with:
```bash
pytest -q
```
