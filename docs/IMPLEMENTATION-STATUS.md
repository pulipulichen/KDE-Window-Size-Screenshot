# Implementation Status

## 2026-11-15 — Capture enabled; isolation gate removed

The user's latest decision replaces the old isolated-display acceptance gate. Capture no longer requests isolation confirmation, checks a verification flag, or requires Xephyr/Xvfb. Basic X11 connection and executable checks identify real dependency errors.

The previously successful workflow is now wired to Capture Window:

1. Hide the quick window and select a managed application client with the X11 crosshair picker.
2. Save the original geometry and maximized/fullscreen/shaded state to a private recovery JSON.
3. Remove those states, dynamically select a sufficiently large existing monitor, and move/resize the target.
4. Read the client drawable with `xwd`; convert to PNG with ImageMagick. Respect advertised `_GTK_FRAME_EXTENTS` when resizing/cropping CSD shadows, without scaling the image.
5. Restore the target in `finally`, verify geometry/state, retry restoration on failure, and retain the JSON if recovery still fails.
6. Decode the PNG, save it without overwriting an existing file and/or copy it to the Qt clipboard. Output errors are reported separately.

The workflow does not issue RandR mutations or create nested X servers. It temporarily moves/resizes the selected target on an existing display area. This is not described as isolated display rendering.

## Target-machine validation

On 2026-11-15, tested the backend over SSH on `pudding-rog-2025`, Kubuntu 24.04 KDE X11, `DISPLAY=:0`, using a newly created disposable `xmessage` window rather than an existing user window. Six monitors were present, including the previously used HDMI-2-3 1920 × 1080 area. The backend selected a fitting monitor dynamically.

- Normal window: produced a decodable XWD-converted PNG with a 1280 × 800 IHDR; original geometry restored.
- Maximized window: produced 1280 × 800; original geometry and both maximization flags restored.
- Fullscreen plus maximized window: produced 1280 × 800; original geometry and fullscreen/maximization flags restored.
- Injected `xwd` failure: the intentional error propagated; original geometry and states restored.
- `xrandr --query` was identical before and after all four cases. The successful test series left no pending recovery snapshots. The disposable test window was terminated.

An initial test found that restoring fullscreen before maximization made KWin drop a state flag. Restoring maximization first and fullscreen last fixed the issue; the full series passed afterward.

This validates the backend on the target KWin session, not the entire packaged GUI. Chrome-specific visual validation of client shadow extents and issue #1 black edges is still pending. The AppImage's picker/output flow and clipboard should still be checked interactively. No new acceptance gate is imposed for those pending checks.

## Other implemented features

- PySide6 quick window, independent Settings, profile working copies and persistence.
- PNG/clipboard options and actual capture outputs.
- Passive X11/Wayland, display connection and command diagnostics.
- Shared icon and compact startup geometry.
- GitHub Actions AppImage builds published directly to Releases.

## Remaining UI work

- Global shortcut registration/conflict checking.
- Hover highlight and immediate Escape cancellation in a custom picker (current crosshair selection has a timeout).
- Separate progress dialog and rolling execution logs.
