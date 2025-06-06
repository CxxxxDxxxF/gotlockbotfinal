"""Main entry point for the GotLockz bot."""

from __future__ import annotations

import argparse
import logging
import os


logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    The log level may also be set via the ``LOG_LEVEL`` environment variable.
    """

    parser = argparse.ArgumentParser(description="Start the GotLockz bot")
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (default from LOG_LEVEL or INFO)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Configure logging and start the bot."""

    args = parse_args(argv)
    logging.basicConfig(level=args.log_level.upper())
    logger.info("GotLockz bot starting...")


if __name__ == "__main__":
    main()
