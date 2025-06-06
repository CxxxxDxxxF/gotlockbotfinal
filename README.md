# GotLockz Discord Bot

This repository contains a simple Discord bot that posts picks via a `/postpick` slash command. The bot uses `discord.py` 2.5+ and registers commands to a single guild for faster updates.

## Environment variables

- `DISCORD_TOKEN` – your bot's token
- `GUILD_ID` – ID of the guild where slash commands should be registered

These need to be configured in your local shell or in Render.com's **Environment Variables** settings.
You can copy `.env.example` to `.env` and edit it with your own values when running locally:

```bash
cp .env.example .env
```

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DISCORD_TOKEN=your_token
export GUILD_ID=123456789012345678
python bot.py
```

## Deployment on Render

1. Create a new **Web Service** from this repository.
2. Set `DISCORD_TOKEN` and `GUILD_ID` in the service's environment variables.
3. Render will build the Dockerfile and run `python bot.py` automatically.

Slash commands will sync when the bot starts. The `/postpick` command accepts a unit amount and a text channel and posts an embed in that channel while replying ephemerally to the user.

## Running tests

Run the automated test suite with `pytest`:

```bash
pytest -q
```
