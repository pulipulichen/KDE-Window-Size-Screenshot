# Implementation Status

## Phase 1 — isolated display safety gate

Status: **NOT VERIFIED — capture must remain disabled**.

### Passive preflight implementation

Settings → System now reports individual `PASS`, `FAIL`, or `PENDING` results. It identifies X11/Wayland from Qt's active platform (`xcb`/`wayland`), falling back to session environment values when needed; this also works when a remote launch does not inherit `XDG_SESSION_TYPE`. It attempts a read-only `xrandr --query` against the current `DISPLAY`, checks that required commands are executable, and reports whether Xephyr or Xvfb is installed. The checks do not start nested servers, move windows, or change RandR state. A successful display connection or the presence of Xephyr is not treated as proof of isolation.

### Target-machine observation (2026-11-15)

Earlier functional testing on the target machine did capture the existing “布丁FB - Facebook” window at 1280 × 800, then returned the desktop to six outputs and 4480 × 1800 and restored the target window's prior position, size, and maximized state. That proves the capture path can work and the normal completion path restored the observed state. It used `xrandr` to expand the desktop beyond its original 4480-pixel width (the root screen reached 10624 × 1800) and temporarily moved/resized the target window, so it does not prove a no-layout-change isolated display. The retrieved test record also does not verify unrelated windows before/after or cleanup after an induced failure.

Read-only inspection on 2026-11-15 confirmed Ubuntu 24.04.3 LTS, an active X11 session on `:0`, and an X screen size of 4480 × 1800 with multiple connected outputs. `Xephyr` is installed; `Xvfb` is not. No display resource or window was changed during this inspection. The stricter no-layout-change isolation experiment and failure-cleanup evidence are still incomplete, so the gate remains pending under the current acceptance criteria.

Required manual evidence on Kubuntu 24.04 / KDE Plasma / X11:

- [ ] Record the X11 session and target window identifiers.
- [ ] Establish an isolated display without changing primary output mode or desktop layout.
- [ ] Confirm the desktop does not jump and unrelated windows retain position and size.
- [ ] Confirm an existing target window can be presented and controlled in that isolated display.
- [ ] Remove the temporary resources and compare the display/window state with the before snapshot.
- [ ] Repeat cleanup after a deliberately interrupted/failed attempt.
- [ ] Attach command output, display snapshots, and recovery notes to this file before enabling capture.

The current application performs passive checks and reports this gate as pending. It never invokes a window move, RandR mutation, or screenshot operation. At startup it explicitly requests a normal window state and reapplies a compact size after KWin maps the window, to clear a restored maximized or oversized state for the app's window class.

## Implemented scaffold

- PySide6 quick window and independent Settings window.
- Profile working copy, validation, Apply/Cancel, and JSON persistence.
- Output settings and diagnostic report copy action.
- X11/Wayland, live X display connection, host-command, and nested-server-candidate checks.
- `assets/icon512.png` is the single application icon source for the window, system tray, and AppImage integration.
- The main window starts at a compact content-based size and remains resizable.
- GitHub Actions AppImage build on `main`, plus GitHub Release attachment for `v*` tags.

## Deferred until the gate passes

- Window picker and global shortcut registration.
- Window state snapshot and restoration backend.
- Exact client-area capture.
- Clipboard/PNG output from a real capture.
