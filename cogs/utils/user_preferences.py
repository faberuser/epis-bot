"""Persist per-user language preferences in a small JSON file."""

import json
from pathlib import Path


class UserPreferences:
    def __init__(self, path):
        self.path = Path(path)

    def _read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in data.items()
        ):
            raise ValueError(
                "User preferences must map Discord user IDs to language codes"
            )
        return data

    def language(self, user_id) -> str | None:
        return self._read().get(str(user_id))

    def set_language(self, user_id, language: str | None) -> None:
        data = self._read()
        if language is None:
            data.pop(str(user_id), None)
        else:
            data[str(user_id)] = language
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)


preferences = UserPreferences(
    Path(__file__).resolve().parents[2] / "data" / "user_preferences.json"
)
