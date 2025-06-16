#!/usr/bin/env bash
# run.sh: Helper script to run the GotLockz bot locally

# Create tmp directory for OCR
mkdir -p tmp

# Execute the main entrypoint
exec python main.py
