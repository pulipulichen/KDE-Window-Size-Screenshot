# Changelog

## 2026-11-14 — Publish successful main builds to Releases

- Diagnosed successful run #4 (43608521689), commit a5e51fccc1cb0dfaddaa1e5b2e9c0db9e0d7ed96: https://github.com/pulipulichen/KDE-Window-Size-Screenshot/actions/runs/43608521689
- The publishing step was skipped because it required refs/tags/v*, while this run was a push to main. Compilation succeeded, but no Release existed. Earlier successful main runs had the same publishing condition.
- Publish main pushes and manual main builds as uniquely tagged development prereleases (run number, attempt, and commit). Version-tag builds retain their matching version Release.
- Use the same metadata for the AppImage filename and Release tag; require nonempty output and upload its verified SHA-256 checksum. Missing assets fail the workflow instead of silently producing an empty Release. Existing release assets are not overwritten.
- Keep build products on the runner until direct Release upload; no Actions artifacts are used.
- Update README download instructions and retain the current application safety limitation in release notes.
- Validation: pending workflow execution and Release asset verification; to be updated after the publishing run.
