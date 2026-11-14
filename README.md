# KDE Window Size Screenshot

A KDE Plasma utility for capturing an application's client area at a chosen pixel size.

> **Development status:** the isolated-display safety gate has not been validated on Kubuntu 24.04 KDE X11. Screenshot capture is intentionally disabled until that gate passes. The current build provides the application shell, settings, and environment diagnostics.

## Run from source

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m kde_window_size_screenshot
```

## Build and release

GitHub Actions builds an AppImage on pushes to `main`. Pushing a version tag such as `v0.1.0` builds the AppImage and attaches it to a GitHub Release. The Actions build is not the release download location.

## Current safety boundary

The app detects Wayland and missing host tools, but does not move windows or change monitor configuration. Capture remains blocked until the manual Kubuntu/X11 feasibility checklist in [`spec/ACCEPTANCE.md`](spec/ACCEPTANCE.md) is verified.

See [`spec/`](spec/README.md) for the product and technical specifications.
