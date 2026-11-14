# Implementation Status

## Phase 1 — isolated display safety gate

Status: **NOT VERIFIED — capture must remain disabled**.

Required manual evidence on Kubuntu 24.04 / KDE Plasma / X11:

- [ ] Record the X11 session and target window identifiers.
- [ ] Establish an isolated display without changing primary output mode or desktop layout.
- [ ] Confirm the desktop does not jump and unrelated windows retain position and size.
- [ ] Confirm an existing target window can be presented and controlled in that isolated display.
- [ ] Remove the temporary resources and compare the display/window state with the before snapshot.
- [ ] Repeat cleanup after a deliberately interrupted/failed attempt.
- [ ] Attach command output, display snapshots, and recovery notes to this file before enabling capture.

The current application only detects the environment and reports this gate as pending. It never invokes a window move, RandR mutation, or screenshot operation.

## Implemented scaffold

- PySide6 quick window and independent Settings window.
- Profile working copy, validation, Apply/Cancel, and JSON persistence.
- Output settings and diagnostic report copy action.
- X11/Wayland and host-command checks.
- GitHub Actions AppImage build on `main`, plus GitHub Release attachment for `v*` tags.

## Deferred until the gate passes

- Window picker and global shortcut registration.
- Window state snapshot and restoration backend.
- Exact client-area capture.
- Clipboard/PNG output from a real capture.
