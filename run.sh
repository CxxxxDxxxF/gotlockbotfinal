\#!/usr/bin/env bash

# run.sh: Helper script to run the GotLockz bot locally

# Load environment variables from .env if present

if \[ -f .env ]; then

# Export variables, ignoring commented and blank lines

export \$(grep -Ev '^\s\*#' .env | xargs)
fi

# Ensure tmp directory exists for OCR processing

mkdir -p tmp

# Execute the main entrypoint

exec python main.py
