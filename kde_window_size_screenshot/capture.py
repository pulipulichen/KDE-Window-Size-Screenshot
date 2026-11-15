"""X11 window resize → xwd → PNG → restore, using the proven desktop workflow."""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path


def run(*args: str, timeout: float = 8) -> str:
    result = subprocess.run(args, capture_output=True, timeout=timeout, env={**os.environ, "LC_ALL": "C"})
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace").strip() or f"{args[0]} failed")
    return result.stdout.decode(errors="replace")


def property_text(wid: str, name: str) -> str:
    return run("xprop", "-id", wid, name)


def extents(wid: str, name: str) -> tuple[int, int, int, int]:
    value = property_text(wid, name).partition("=")[2]
    numbers = re.findall(r"\d+", value)
    return tuple(map(int, numbers[:4])) if len(numbers) >= 4 else (0, 0, 0, 0)


def geometry(wid: str) -> tuple[int, int, int, int]:
    info = run("xwininfo", "-id", wid)
    keys = ("Absolute upper-left X", "Absolute upper-left Y", "Width", "Height")
    return tuple(int(re.search(rf"{key}:\s*(-?\d+)", info).group(1)) for key in keys)


@dataclass
class Snapshot:
    wid: str
    x: int
    y: int
    width: int
    height: int
    states: list[str]


STATES = ("fullscreen", "maximized_vert", "maximized_horz", "shaded")


class WindowCapture:
    def __init__(self, state_directory: Path):
        self.state_directory = state_directory

    def select(self) -> str:
        selected = int(run("xdotool", "selectwindow", timeout=60).strip(), 0)
        # Resolve frame/child picks to the managed application client drawable.
        clients = [int(row.split()[0], 16) for row in run("wmctrl", "-l").splitlines() if row.strip()]
        if selected in clients:
            return hex(selected)
        tree = run("xwininfo", "-id", hex(selected), "-tree")
        ids = {int(value, 16) for value in re.findall(r"0x[0-9a-fA-F]+", tree)}
        matches = [client for client in clients if client in ids]
        if len(matches) != 1:
            raise RuntimeError("未選取應用程式視窗；已取消截圖。")
        return hex(matches[0])

    def restore(self, saved: Snapshot) -> None:
        for state in STATES:
            run("wmctrl", "-ir", saved.wid, "-b", f"remove,{state}")
        time.sleep(0.15)
        left, _right, top, _bottom = extents(saved.wid, "_NET_FRAME_EXTENTS")
        run("wmctrl", "-ir", saved.wid, "-e",
            f"0,{saved.x-left},{saved.y-top},{saved.width},{saved.height}")
        self.wait_size(saved.wid, saved.width, saved.height, timeout=8)
        # KWin can clear maximization flags when fullscreen is restored first.
        for state in sorted(saved.states, key=lambda state: state == "fullscreen"):
            run("wmctrl", "-ir", saved.wid, "-b", f"add,{state}")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            current = property_text(saved.wid, "_NET_WM_STATE").lower()
            if (geometry(saved.wid) == (saved.x, saved.y, saved.width, saved.height)
                    and all((f"_net_wm_state_{state}" in current) == (state in saved.states) for state in STATES)):
                return
            time.sleep(0.1)
        raise RuntimeError("視窗未回到原始位置、尺寸或狀態。")

    @staticmethod
    def wait_size(wid: str, width: int, height: int, timeout: float = 3) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if geometry(wid)[2:] == (width, height):
                return
            time.sleep(0.1)
        raise RuntimeError(f"視窗無法調整為 {width} × {height}。")

    def capture(self, wid: str, width: int, height: int, progress=lambda _: None) -> tuple[bytes, str]:
        if not (1 <= width <= 16384 and 1 <= height <= 16384):
            raise ValueError("截圖尺寸必須介於 1 到 16384。")
        if re.search(rf"=\s*{os.getpid()}\b", property_text(wid, "_NET_WM_PID")):
            raise RuntimeError("請選取其他應用程式的視窗。")
        title = run("xdotool", "getwindowname", wid).strip() or "Window"
        states = property_text(wid, "_NET_WM_STATE").lower()
        saved = Snapshot(wid, *geometry(wid), [s for s in STATES if f"_net_wm_state_{s}" in states])
        self.state_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, snapshot_name = tempfile.mkstemp(prefix="restore-", suffix=".json", dir=self.state_directory)
        snapshot_path = Path(snapshot_name)
        with os.fdopen(fd, "w") as stream:
            json.dump(asdict(saved), stream)
        try:
            progress("調整視窗尺寸…")
            for state in STATES:
                run("wmctrl", "-ir", wid, "-b", f"remove,{state}")
            time.sleep(0.2)
            # GTK/Chrome may include invisible CSD shadows inside the client drawable.
            left, right, top, bottom = extents(wid, "_GTK_FRAME_EXTENTS")
            outer_width, outer_height = width + left + right, height + top + bottom
            frame_left, frame_right, frame_top, frame_bottom = extents(wid, "_NET_FRAME_EXTENTS")
            monitors = []
            for line in run("xrandr", "--listmonitors").splitlines()[1:]:
                match = re.search(r"(\d+)/\d+x(\d+)/\d+([+-]\d+)([+-]\d+)", line)
                if match:
                    mw, mh, mx, my = map(int, match.groups())
                    if mw >= outer_width + frame_left + frame_right and mh >= outer_height + frame_top + frame_bottom:
                        monitors.append((mw * mh, mx, my))
            if not monitors:
                raise RuntimeError("目前顯示區放不下指定尺寸；請選擇較小的 Profile 或啟用較大的顯示區。")
            _, mx, my = min(monitors)
            run("wmctrl", "-ir", wid, "-e", f"0,{mx},{my},{outer_width},{outer_height}")
            self.wait_size(wid, outer_width, outer_height)
            run("xdotool", "windowraise", wid)
            time.sleep(0.35)  # Allow the client to repaint after ConfigureNotify.
            progress("擷取視窗…")
            with tempfile.TemporaryDirectory(prefix="kde-window-capture-") as directory:
                source, target = Path(directory) / "window.xwd", Path(directory) / "window.png"
                run("xwd", "-silent", "-id", wid, "-out", str(source))
                run("convert", str(source), "-crop", f"{width}x{height}+{left}+{top}",
                    "+repage", "-strip", str(target))
                png = target.read_bytes()
                if png[:8] != b"\x89PNG\r\n\x1a\n" or (int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")) != (width, height):
                    raise RuntimeError("PNG 尺寸不符合 Profile。")
        finally:
            progress("還原視窗…")
            try:
                try:
                    self.restore(saved)
                except Exception:
                    self.restore(saved)
            except Exception as exc:
                raise RuntimeError(f"還原失敗：{exc} 原始狀態保留於 {snapshot_path}") from exc
            else:
                snapshot_path.unlink()
        return png, title


def save_png(directory: Path, title: str, png: bytes) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    clean_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip(" .")[:100] or "Window"
    stem = f"{clean_title}-{time.strftime('%Y%m%d-%H%M%S')}"
    for index in range(10000):
        target = directory / f"{stem}{f'-{index}' if index else ''}.png"
        try:
            stream = target.open("xb")
        except FileExistsError:
            continue
        with stream:
            stream.write(png)
        return target
    raise RuntimeError("無法建立不重複的截圖檔名。")
