from __future__ import annotations

import os
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def inspect_environment() -> list[Check]:
    session = os.environ.get("XDG_SESSION_TYPE", "unknown").lower()
    checks = [
        Check("Desktop session", session == "x11", f"{session} (first release requires X11)"),
        Check("DISPLAY", bool(os.environ.get("DISPLAY")), os.environ.get("DISPLAY", "not set")),
    ]
    for command in ("xrandr", "xwininfo", "xprop", "xdotool", "wmctrl"):
        found = shutil.which(command)
        checks.append(Check(command, found is not None, found or "not installed"))

    # This is deliberately an unresolved safety gate. A positive result must come
    # from the documented, manual Kubuntu/X11 experiment, not a heuristic probe.
    checks.append(Check(
        "Isolated display safety gate",
        False,
        "Not verified on Kubuntu 24.04 KDE X11; capture is blocked.",
    ))
    return checks


def capture_block_reason() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "unknown").lower()
    if session != "x11":
        if session == "wayland":
            return "Wayland 目前不支援截圖。請使用 KDE X11 工作階段。"
        return f"目前工作階段為「{session}」；第一版需要 KDE X11。"
    return "隔離式虛擬顯示尚未通過 Kubuntu 24.04 實機安全驗證，因此目前不會移動視窗或變更螢幕設定。"
