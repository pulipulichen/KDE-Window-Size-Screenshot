# KDE Window Size Screenshot

A KDE Plasma utility for capturing an application's client area at a chosen pixel size.

Capture is enabled on X11. Click **Capture Window**, then click the target window. The app finds an existing display area that can accommodate the selected profile, temporarily moves/resizes the target, captures it with `xwd`, converts it to PNG with ImageMagick, and restores the window. No isolation confirmation or verification flag is required.

The default profile is **1280 × 800**. PNG saving and clipboard output are independently configurable in Settings. The output excludes external window-manager decorations; advertised GTK client shadow extents are cropped without scaling or deleting black content pixels.

## Host dependencies

On Kubuntu 24.04:

```bash
sudo apt install x11-xserver-utils x11-utils x11-apps xdotool wmctrl imagemagick
```

Required commands: `xrandr`, `xwininfo`, `xprop`, `xdotool`, `wmctrl`, `xwd`, `convert`. Xephyr and Xvfb are not required. Wayland is not supported by this X11 backend.

## Run from source

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m kde_window_size_screenshot
```

## Build and release

GitHub Actions builds and publishes an AppImage on pushes to `main` and manual runs on `main`. Each successful build creates a unique development prerelease named `dev-<run>-<attempt>-<commit>`, with the AppImage and its SHA-256 checksum. Download development builds from [GitHub Releases](https://github.com/pulipulichen/KDE-Window-Size-Screenshot/releases), including prereleases.

Pushing a version tag such as `v0.1.0` publishes the matching version Release. Build outputs are uploaded directly to Releases, without Actions artifacts.

## Current behavior and limitations

The backend queries existing monitors; it does not add outputs or change their modes or arrangement. The target window temporarily moves and changes size, then returns to its previous geometry and fullscreen/maximized state, including when capture fails. A recovery JSON is written before changes and retained if restoration fails after a retry. An unavailable display, missing command, unsuitable display size, or application that refuses resizing produces a specific error.

Selection uses the X11 crosshair picker (60-second timeout). Global shortcut registration, hover highlighting, and a separate progress dialog are not yet implemented. Chrome-specific visual black-edge validation remains tracked in issue #1; exact dimensions alone do not prove all client decorations are excluded.

See [`docs/IMPLEMENTATION-STATUS.md`](docs/IMPLEMENTATION-STATUS.md) for validation and [`spec/`](spec/README.md) for the specifications.
