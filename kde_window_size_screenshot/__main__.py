from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from .settings import SettingsStore
from .ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("KDE Window Size Screenshot")
    app.setApplicationDisplayName("KDE Window Size Screenshot")
    app.setOrganizationName("PuliPuli")
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        app.setQuitOnLastWindowClosed(True)

    store = SettingsStore()
    window = MainWindow(store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
