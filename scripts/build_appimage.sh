#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
APP_DIR="${BUILD_DIR}/AppDir"
APP_NAME="KDE-Window-Size-Screenshot"
VERSION="${VERSION:-$(python3 -c 'from kde_window_size_screenshot import __version__; print(__version__)')}"

rm -rf "${BUILD_DIR}"
mkdir -p "${APP_DIR}/usr/lib/${APP_NAME}" "${APP_DIR}/usr/bin" "${APP_DIR}/usr/share/applications" "${APP_DIR}/usr/share/icons/hicolor/scalable/apps"

python3 -m pip install --upgrade pip pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name "${APP_NAME}" "${ROOT_DIR}/run_app.py"
cp -a "${ROOT_DIR}/dist/${APP_NAME}/." "${APP_DIR}/usr/lib/${APP_NAME}/"
cp "${ROOT_DIR}/assets/kde-window-size-screenshot.svg" "${APP_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg"

cat > "${APP_DIR}/AppRun" <<'APPRUN'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "${HERE}/usr/lib/KDE-Window-Size-Screenshot/KDE-Window-Size-Screenshot" "$@"
APPRUN
chmod +x "${APP_DIR}/AppRun"
ln -s ../lib/${APP_NAME}/KDE-Window-Size-Screenshot "${APP_DIR}/usr/bin/${APP_NAME}"

cat > "${APP_DIR}/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=KDE Window Size Screenshot
Comment=Capture an application client area at a chosen size
Exec=AppRun
Icon=${APP_NAME}
Categories=Graphics;Utility;
Terminal=false
EOF
cp "${APP_DIR}/${APP_NAME}.desktop" "${APP_DIR}/usr/share/applications/${APP_NAME}.desktop"
ln -s "usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg" "${APP_DIR}/${APP_NAME}.svg"

if [[ -z "${APPIMAGETOOL:-}" ]]; then
  echo "APPIMAGETOOL must point to an installed appimagetool binary." >&2
  exit 2
fi
"${APPIMAGETOOL}" "${APP_DIR}" "${ROOT_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"
