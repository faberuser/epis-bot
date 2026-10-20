"""Read versioned upstream data without sharing mutable selection state."""

import json
import re
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from fuzzywuzzy import process

import settings

from .user_preferences import preferences

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "kingsraid-data"


class DataUnavailable(commands.BadArgument):
    pass


@lru_cache(maxsize=512)
def _read_json(path, modified):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_json(path) -> Any:
    path = Path(path)
    if not path.is_file():
        raise DataUnavailable(f"Data is unavailable: {path.name}.")
    return deepcopy(_read_json(str(path), path.stat().st_mtime_ns))


def clean_text(value):
    value = re.sub(r"\[(?:[0-9a-fA-F]{6,8}|-)\]", "", value)
    return re.sub(r"\{(\d+)\}", r"(\1)", value)


def _normalize(value: Any, assets: Path, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(v, assets, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v, assets) for v in value]
    if isinstance(value, str):
        if key in ("thumbnail", "splashart", "visual", "costumes"):
            candidate = (assets / value).resolve()
            if not candidate.is_relative_to(assets):
                raise DataUnavailable(
                    "An asset path points outside the data repository."
                )
            return str(candidate)
        return clean_text(value)
    return value


@lru_cache(maxsize=512)
def _entity(path, modified, root, version, language, kind):
    data = _normalize(_read_json(path, modified), root / "assets")
    info = {}
    for key, value in data.get("profile", {}).items():
        if value is None or key.endswith("Names"):
            continue
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        info[key] = str(value)
    info.setdefault("class", path.stem if kind == "bosses" else "Unknown")
    info.setdefault("story_", info.get("story", "No story available."))
    data.update(info=info, _version=version, _language=language)
    return data


def available_versions(root=DATA_ROOT):
    table = Path(root) / "table-data"
    versions = (
        sorted(
            path.name
            for path in table.iterdir()
            if path.is_dir() and (path / "en" / "heroes").is_dir()
        )
        if table.is_dir()
        else []
    )
    if not versions:
        raise DataUnavailable(
            "Game data is not initialized. Run `git submodule update --init --recursive`."
        )
    return versions


class GameData:
    def __init__(self, version=None, language=None, *, root=DATA_ROOT):
        self.root = Path(root).resolve()
        self.version = version or getattr(settings, "KR_DEFAULT_VERSION", "legacy")
        self.language = language or getattr(settings, "KR_LANGUAGE", "en")
        if self.version not in available_versions(self.root):
            raise DataUnavailable(
                f"Unknown data version `{self.version}`. Choose: {', '.join(available_versions(self.root))}."
            )
        version_root = self.root / "table-data" / self.version
        languages = [path.name for path in version_root.iterdir() if path.is_dir()]
        if self.language not in languages:
            raise DataUnavailable(
                f"Language `{self.language}` is unavailable in `{self.version}`."
            )
        self.version_root = version_root
        self.table_root = version_root / self.language
        self.label = f"{self.version} / {self.language}"

    def normalize(self, value, key=None):
        return _normalize(value, self.root / "assets", key)

    def entities(self, kind="heroes") -> dict[str, dict[str, Any]]:
        result = {}
        for path in sorted((self.table_root / kind).glob("*.json")):
            data = deepcopy(
                _entity(
                    path,
                    path.stat().st_mtime_ns,
                    self.root,
                    self.version,
                    self.language,
                    kind,
                )
            )
            # The canonical ID remains stable across translated display names.
            result[data.get("id", path.stem)] = data
        return result

    def find(self, query, kinds=("heroes", "bosses")):
        entries = {}
        aliases = {}
        for kind in kinds:
            for name, data in self.entities(kind).items():
                entries[name] = (data, kind == "bosses")
                for alias in [
                    name,
                    data["info"].get("name", name),
                    *(data.get("aliases") or []),
                ]:
                    aliases[alias.casefold()] = name
        key = query.strip().casefold()
        # Recognize identities from other versions, but never borrow their content.
        known = known_identities(self.root, self.language)
        canonical = aliases.get(key) or known.get(key)
        if canonical is not None and canonical not in entries:
            raise DataUnavailable(f"`{query}` is unavailable in {self.label}.")
        if canonical is None:
            match = process.extractOne(key, list(aliases))
            if match is None or match[1] < 60:
                raise DataUnavailable(f"No match for `{query}` in {self.label}.")
            canonical = aliases[match[0]]
        data, boss = entries[canonical]
        return canonical, data, boss

    def table(self, name) -> Any:
        path = self.table_root / name
        if not path.is_file():
            raise DataUnavailable(f"`{name}` is unavailable in {self.label}.")
        return self.normalize(read_json(path))

    def artifacts(self) -> dict[str, dict[str, Any]]:
        return {item["name"]: item for item in self.table("artifacts.json")}

    def softcaps(self):
        path = self.version_root / "softcap.json"
        if not path.is_file():
            raise DataUnavailable(f"Softcap data is unavailable in {self.label}.")
        return read_json(path)


@lru_cache(maxsize=8)
def known_identities(root, language="en"):
    names = {}
    for version in available_versions(root):
        for kind in ("heroes", "bosses"):
            for path in (root / "table-data" / version / "en" / kind).glob("*.json"):
                data = read_json(path)
                name = data.get("id", path.stem)
                aliases = [name, *(data.get("aliases") or [])]
                translated = root / "table-data" / version / language / kind / path.name
                if language != "en" and translated.is_file():
                    aliases.append(
                        read_json(translated).get("profile", {}).get("name", name)
                    )
                for alias in aliases:
                    names[alias.casefold()] = name
    return names


def available_languages(root=DATA_ROOT):
    return sorted(
        {
            path.name
            for version in available_versions(root)
            for path in (Path(root) / "table-data" / version).iterdir()
            if path.is_dir() and (path / "heroes").is_dir()
        }
    )


def selected_language(ctx):
    return preferences.language(ctx.author.id) or settings.KR_LANGUAGE


def selected_data(ctx, version=None):
    return GameData(
        version or getattr(ctx, "data_version", None), selected_language(ctx)
    )


def stamp(result, data):
    label = (
        data.label
        if isinstance(data, GameData)
        else f"{data['_version']} / {data['_language']}"
    )
    embeds = (
        result
        if isinstance(result, list)
        else [result[0] if isinstance(result, tuple) else result]
    )
    for embed in embeds:
        if isinstance(embed, discord.Embed):
            footer = embed.footer.text or ""
            embed.set_footer(text=f"{footer} | {label}" if footer else label)
    return result


async def version_autocomplete(interaction, current):
    return [
        app_commands.Choice(name=name, value=name)
        for name in available_versions()
        if current.casefold() in name.casefold()
    ][:25]
