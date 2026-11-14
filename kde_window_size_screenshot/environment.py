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


def _desktop_session(platform_name: str | None = None) -> tuple[str, str]:
    platform = (platform_name or "").strip().lower()
    if platform == "xcb":
        return "x11", "Qt platform xcb"
    if platform == "wayland":
        return "wayland", "Qt platform wayland"
    if platform:
        return platform, f"Qt platform {platform}"

    session = os.environ.get("XDG_SESSION_TYPE", "unknown").strip().lower() or "unknown"
    if session in {"x11", "wayland"}:
        return session, f"XDG_SESSION_TYPE={session}"
    if os.environ.get("DISPLAY"):
        return "x11", "X11 DISPLAY is set (XDG_SESSION_TYPE is unavailable)"
    return session, f"XDG_SESSION_TYPE={session}"


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


def inspect_environment(platform_name: str | None = None) -> list[Check]:
    """Run passive preflight checks. This never creates or changes display resources."""
    session, session_detail = _desktop_session(platform_name)
    session_state = CheckState.PASS if session == "x11" else CheckState.FAIL
    checks = [
        Check("Desktop session", session_state, f"{session}; {session_detail} (this release requires X11)"),
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
        "Prior tests proved capture and normal restoration. Still unverified: no desktop/output or unrelated-window changes during capture, and cleanup after an induced failure. Capture remains blocked under the current safety criteria.",
    ))
    return checks


def capture_block_reason(platform_name: str | None = None) -> str:
    session, _session_detail = _desktop_session(platform_name)
    if session != "x11":
        if session == "wayland":
            return "Wayland 目前不支援截圖。請使用 KDE X11 工作階段。"
        return f"目前工作階段為「{session}」；第一版需要 KDE X11。"
    display_check = _check_display()
    if display_check.state is not CheckState.PASS:
        return f"X11 顯示連線檢查未通過：{display_check.detail}。"
    return "X11 連線正常；先前已成功截圖並在正常結束後復原。尚未確認截圖期間桌面與其他視窗不變，也未測試中途失敗後清理，因此安全閘門仍封鎖截圖。"
