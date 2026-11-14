from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QStandardPaths


DEFAULT_SETTINGS: dict[str, Any] = {
    "profiles": [
        {"id": "default", "name": "Default", "width": 1280, "height": 800}
    ],
    "default_profile_id": "default",
    "current_profile_id": "default",
    "shortcut": "Shift+Print",
    "save_png": True,
    "copy_clipboard": False,
    "output_directory": str(Path.home() / "Pictures" / "Screenshots"),
}


class SettingsStore:
    """Small JSON store with working-copy semantics for the Settings dialog."""

    def __init__(self) -> None:
        root = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.ConfigLocation))
        self.path = root / "kde-window-size-screenshot" / "settings.json"
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("profiles"), list) and loaded["profiles"]:
                merged = copy.deepcopy(DEFAULT_SETTINGS)
                merged.update(loaded)
                return merged
        except (OSError, json.JSONDecodeError):
            pass
        return copy.deepcopy(DEFAULT_SETTINGS)

    def working_copy(self) -> dict[str, Any]:
        return copy.deepcopy(self.data)

    def save(self, data: dict[str, Any]) -> None:
        self.validate(data)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
        self.data = copy.deepcopy(data)

    @staticmethod
    def validate(data: dict[str, Any]) -> None:
        profiles = data.get("profiles")
        if not profiles:
            raise ValueError("至少需要保留一個 Profile。")
        ids: set[str] = set()
        for profile in profiles:
            if not str(profile.get("name", "")).strip():
                raise ValueError("Profile 名稱不可空白。")
            if int(profile.get("width", 0)) < 1 or int(profile.get("height", 0)) < 1:
                raise ValueError("Profile 寬度與高度必須是正整數。")
            if profile["id"] in ids:
                raise ValueError("Profile ID 必須唯一。")
            ids.add(profile["id"])
        if data.get("default_profile_id") not in ids:
            raise ValueError("請選擇有效的預設 Profile。")
        if not data.get("save_png") and not data.get("copy_clipboard"):
            raise ValueError("至少啟用一種輸出方式。")

