# Changelog

## [Unreleased]

- Use `assets/icon512.png` consistently for the application window, system tray, PyInstaller executable, and AppImage desktop integration.
- Set a compact, content-based initial main-window size while keeping the window resizable.
- Replace the placeholder environment summary with passive X11 connection, required-command, and nested-server availability checks. The isolated-display safety gate remains pending until manual target-machine evidence is complete.

## 2026-11-14 — Publish successful main builds to Releases

- Diagnosed successful run #4 (43608521689), commit a5e51fccc1cb0dfaddaa1e5b2e9c0db9e0d7ed96: https://github.com/pulipulichen/KDE-Window-Size-Screenshot/actions/runs/43608521689
- The publishing step was skipped because it required refs/tags/v*, while this run was a push to main. Compilation succeeded, but no Release existed. Earlier successful main runs had the same publishing condition.
- Publish main pushes and manual main builds as uniquely tagged development prereleases (run number, attempt, and commit). Version-tag builds retain their matching version Release.
- Use the same metadata for the AppImage filename and Release tag; require nonempty output and upload its verified SHA-256 checksum. Missing assets fail the workflow instead of silently producing an empty Release. Existing release assets are not overwritten.
- Keep build products on the runner until direct Release upload; no Actions artifacts are used.
- Update README download instructions and retain the current application safety limitation in release notes.
- Validation: YAML structure, shell syntax, git diff whitespace checks, and release metadata checks for main/version tags passed. Run #5 (43609111820) succeeded for commit 8bfc6d91cf9b9b0d615ea29a75c717b4befbb7d1: https://github.com/pulipulichen/KDE-Window-Size-Screenshot/actions/runs/43609111820
- Verified published prerelease https://github.com/pulipulichen/KDE-Window-Size-Screenshot/releases/tag/dev-5-1-8bfc6d9 contains a 78,329,024-byte AppImage and a 125-byte SHA-256 file. Downloaded both from Releases and sha256sum --check returned OK. The run has zero Actions artifacts.
- Version-tag metadata was checked locally; an actual stable-tag publishing run was not performed. Application desktop/capture validation remains outside this release-workflow fix.
