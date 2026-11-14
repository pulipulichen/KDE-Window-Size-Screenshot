# Implementation Status

## Phase 1 — isolated display safety gate

Status: **NOT VERIFIED — capture must remain disabled**.

### Passive preflight implementation

Settings → System now reports individual `PASS`, `FAIL`, or `PENDING` results. It checks the session type, actually attempts a read-only `xrandr --query` against the current `DISPLAY`, checks that required commands are executable, and reports whether Xephyr or Xvfb is installed. The checks do not start nested servers, move windows, or change RandR state. A successful display connection or the presence of Xephyr is not treated as proof of isolation.

### Target-machine observation (2026-11-15)

Read-only inspection over SSH confirmed Ubuntu 24.04.3 LTS, an active X11 session on `:0`, and an X screen size of 4480 × 1800 with multiple connected outputs. `Xephyr` is installed; `Xvfb` is not. These facts establish that a suitable X11 session and a nested-server candidate exist, but they do not show that existing windows can be safely presented and controlled in an isolated display. No display resource or window was changed during this inspection. The mandatory isolation experiment, before/after window comparison, failure cleanup, and screenshots have not been performed, so this evidence does not pass the gate.

Required manual evidence on Kubuntu 24.04 / KDE Plasma / X11:

- [ ] Record the X11 session and target window identifiers.
- [ ] Establish an isolated display without changing primary output mode or desktop layout.
- [ ] Confirm the desktop does not jump and unrelated windows retain position and size.
- [ ] Confirm an existing target window can be presented and controlled in that isolated display.
- [ ] Remove the temporary resources and compare the display/window state with the before snapshot.
- [ ] Repeat cleanup after a deliberately interrupted/failed attempt.
- [ ] Attach command output, display snapshots, and recovery notes to this file before enabling capture.

The current application performs passive checks and reports this gate as pending. It never invokes a window move, RandR mutation, or screenshot operation.

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
