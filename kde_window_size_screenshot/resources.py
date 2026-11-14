from __future__ import annotations

import sys
from pathlib import Path


def asset_path(name: str) -> Path:
    """Return a bundled asset path in source and PyInstaller builds."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "assets" / name
    return Path(__file__).resolve().parent.parent / "assets" / name
