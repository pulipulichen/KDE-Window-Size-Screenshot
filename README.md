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

GitHub Actions builds and publishes an AppImage on pushes to `main` and manual runs on `main`. Each successful build creates a unique development prerelease named `dev-<run>-<attempt>-<commit>`, with the AppImage and its SHA-256 checksum. Download development builds from [GitHub Releases](https://github.com/pulipulichen/KDE-Window-Size-Screenshot/releases), including prereleases.

Pushing a version tag such as `v0.1.0` publishes the matching version Release. Build outputs are uploaded directly to Releases, without Actions artifacts. Development builds retain the safety limitation described above.

## Current safety boundary

The app checks the desktop session, live X11 display connection, required host tools, and whether a nested X server candidate is installed. These checks are passive: they do not move windows or change monitor configuration, and they do not claim that isolation is safe. Capture remains blocked until the manual Kubuntu/X11 feasibility checklist in [`spec/ACCEPTANCE.md`](spec/ACCEPTANCE.md) is verified.

See [`spec/`](spec/README.md) for the product and technical specifications.
