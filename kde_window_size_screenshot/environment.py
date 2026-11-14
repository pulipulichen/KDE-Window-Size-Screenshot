from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum


class CheckState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


@dataclass(frozen=True)
class Check:
    name: str
    state: CheckState
    detail: str

    @property
    def ok(self) -> bool:
        return self.state is CheckState.PASS


def _check_display() -> Check:
    display = os.environ.get("DISPLAY", "").strip()
    if not display:
        return Check("DISPLAY connection", CheckState.FAIL, "DISPLAY is not set")

    xrandr = shutil.which("xrandr")
    if not xrandr:
        return Check("DISPLAY connection", CheckState.PENDING, f"{display}; cannot probe because xrandr is not installed")

    try:
        result = subprocess.run(
            [xrandr, "--query"], capture_output=True, text=True, timeout=4, check=False,
        )
    except subprocess.TimeoutExpired:
        return Check("DISPLAY connection", CheckState.FAIL, f"{display}; xrandr timed out after 4 seconds")
    except OSError as exc:
        return Check("DISPLAY connection", CheckState.FAIL, f"{display}; unable to run xrandr: {exc}")

    if result.returncode == 0:
        first_line = result.stdout.splitlines()[0] if result.stdout.splitlines() else "X11 display responded"
        return Check("DISPLAY connection", CheckState.PASS, f"{display}; {first_line}")

    error = result.stderr.strip().splitlines()
    detail = error[0] if error else f"xrandr exited with status {result.returncode}"
    return Check("DISPLAY connection", CheckState.FAIL, f"{display}; {detail}")


def inspect_environment() -> list[Check]:
    """Run passive preflight checks. This never creates or changes display resources."""
    session = os.environ.get("XDG_SESSION_TYPE", "unknown").strip().lower() or "unknown"
    session_state = CheckState.PASS if session == "x11" else CheckState.FAIL
    checks = [
        Check("Desktop session", session_state, f"{session} (this release requires X11)"),
        _check_display(),
    ]

    required_commands = ("xrandr", "xwininfo", "xprop", "xdotool", "wmctrl")
    for command in required_commands:
        path = shutil.which(command)
        if path and os.access(path, os.X_OK):
            checks.append(Check(command, CheckState.PASS, f"executable: {path}"))
        elif path:
            checks.append(Check(command, CheckState.FAIL, f"found but not executable: {path}"))
        else:
            checks.append(Check(command, CheckState.FAIL, "not installed or not on PATH"))

    candidates = [(name, shutil.which(name)) for name in ("Xephyr", "Xvfb")]
    available = [f"{name}: {path}" for name, path in candidates if path and os.access(path, os.X_OK)]
    if available:
        checks.append(Check(
            "Nested X server candidate",
            CheckState.PENDING,
            "; ".join(available) + ". Runtime dependencies, permissions, and launch conditions are untested; preflight does not start a server.",
        ))
    else:
        checks.append(Check("Nested X server candidate", CheckState.FAIL, "Neither executable Xephyr nor Xvfb is installed"))

    checks.append(Check(
        "Isolated display safety gate",
        CheckState.PENDING,
        "Manual Kubuntu 24.04 KDE X11 evidence is incomplete; capture remains blocked. Passive checks do not verify window isolation.",
    ))
    return checks


def capture_block_reason() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "unknown").lower()
    if session != "x11":
        if session == "wayland":
            return "Wayland 目前不支援截圖。請使用 KDE X11 工作階段。"
        return f"目前工作階段為「{session}」；第一版需要 KDE X11。"
    display_check = _check_display()
    if display_check.state is not CheckState.PASS:
        return f"X11 顯示連線檢查未通過：{display_check.detail}。"
    return "隔離式虛擬顯示尚未完成 Kubuntu 24.04 實機安全驗證，因此目前不會移動視窗或變更螢幕設定。"
