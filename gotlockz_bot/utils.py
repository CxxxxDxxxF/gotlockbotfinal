"""Miscellaneous utility helpers."""

import logging


def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level)
