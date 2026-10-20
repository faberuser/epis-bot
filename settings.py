"""Typed settings from environment variables and an optional project .env file."""

import json
import os
from pathlib import Path

import discord
from dotenv import load_dotenv

EMBED_COLOR = discord.Colour.dark_red()


# Deployment environment variables take precedence over the local file.
load_dotenv(Path(__file__).resolve().parent / ".env", override=False, interpolate=False)


def _prefixes():
    try:
        values = json.loads(os.getenv("PREFIX", '["/", "."]'))
    except json.JSONDecodeError:
        raise ValueError(
            'PREFIX must be a JSON list of nonempty strings, e.g. ["/", "."]'
        ) from None
    if (
        not isinstance(values, list)
        or not values
        or any(not isinstance(value, str) or not value for value in values)
    ):
        raise ValueError("PREFIX must be a JSON list of nonempty strings")
    return values


def _guild_id():
    try:
        value = int(os.getenv("KRE_GUILD_ID", "0"))
    except ValueError:
        raise ValueError(
            "KRE_GUILD_ID must be a nonnegative integer (0 disables guides)"
        ) from None
    if value < 0:
        raise ValueError(
            "KRE_GUILD_ID must be a nonnegative integer (0 disables guides)"
        )
    return value


def _categories():
    raw = os.getenv("KRE_CATEGORIES", "").strip()
    if not raw:
        return []
    try:
        values = [int(value.strip()) for value in raw.split(",")]
    except ValueError:
        raise ValueError(
            "KRE_CATEGORIES must contain comma-separated positive integer category IDs"
        ) from None
    if any(value <= 0 for value in values):
        raise ValueError(
            "KRE_CATEGORIES must contain comma-separated positive integer category IDs"
        )
    return values


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
PREFIX = _prefixes()
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "").strip()
KR_DEFAULT_VERSION = os.getenv("KR_DEFAULT_VERSION", "legacy").strip() or "legacy"
KR_LANGUAGE = os.getenv("KR_LANGUAGE", "en").strip() or "en"
KRE_GUILD_ID = _guild_id()
KRE_CATEGORIES = _categories()
KRE_INVITE = os.getenv("KRE_INVITE", "").strip()
