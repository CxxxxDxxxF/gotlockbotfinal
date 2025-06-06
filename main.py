"""Main entry point for the GotLockz bot."""

import logging


def main() -> None:
    """Configure logging and start the bot."""
    logging.basicConfig(level=logging.INFO)
    logging.info("GotLockz bot starting...")


if __name__ == "__main__":
    main()
