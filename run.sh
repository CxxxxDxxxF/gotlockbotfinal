#!/bin/bash
# Helper script to run the GotLockz bot locally.

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the bot
exec python bot.py
