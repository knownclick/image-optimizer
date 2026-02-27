"""Profile CRUD — JSON-based metadata profile persistence."""

from __future__ import annotations

import json
import re
from pathlib import Path

_PROFILES_DIR = Path(__file__).parent / "profiles"


def _slugify(name: str) -> str:
    """Convert a profile name to a safe filename slug."""
    slug = re.sub(r"[^\w\s-]", "", name.lower().strip())
    slug = re.sub(r"[\s_-]+", "_", slug)
    return slug or "profile"


def list_profiles() -> list[str]:
    """Return sorted list of profile names from disk."""
    _PROFILES_DIR.mkdir(exist_ok=True)
    names = []
    for f in _PROFILES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            names.append(data["name"])
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(names)


def load_profile(name: str) -> dict[str, str]:
    """Load a profile's fields dict by display name."""
    _PROFILES_DIR.mkdir(exist_ok=True)
    for f in _PROFILES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data["name"] == name:
                return data.get("fields", {})
        except (json.JSONDecodeError, KeyError):
            continue
    return {}


def save_profile(name: str, fields: dict[str, str]) -> None:
    """Create or overwrite a profile JSON file."""
    _PROFILES_DIR.mkdir(exist_ok=True)
    slug = _slugify(name)
    path = _PROFILES_DIR / f"{slug}.json"
    data = {"name": name, "fields": fields}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_profile(name: str) -> None:
    """Remove a profile file by display name."""
    _PROFILES_DIR.mkdir(exist_ok=True)
    for f in _PROFILES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data["name"] == name:
                f.unlink()
                return
        except (json.JSONDecodeError, KeyError):
            continue
