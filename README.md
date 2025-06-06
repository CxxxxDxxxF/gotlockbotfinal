# Gotlockz Bot

This repository contains a simple Discord bot with a collection of helper modules.
The bot provides a few sample commands for interacting with the OpenAI API and
retrieving MLB data. The supporting modules offer lightweight wrappers around
APIs such as Tesseract OCR, the MLB Stats API and Google Sheets.

## Usage

Install the requirements and set the required environment variables, e.g.:

```bash
pip install -r requirements.txt
export DISCORD_TOKEN=<your token>
export OPENAI_API_KEY=<your key>
```

Run the bot with:

```bash
python bot.py
```

## Docker

You can also run the bot in a container. Build the image and run it while
providing the required environment variables:

```bash
docker build -t gotlockz-bot .
docker run -e DISCORD_TOKEN=<your token> -e OPENAI_API_KEY=<your key> gotlockz-bot
```

The bot currently implements the following commands:

- `/ping` – respond with "Pong!".
- `/analyze <text>` – send the text to OpenAI and return a short analysis.
- `/games` – list today's MLB games.

These examples can be expanded by building on the helper modules in
`gotlockz_bot/`.
