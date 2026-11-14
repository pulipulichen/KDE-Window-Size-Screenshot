from __future__ import annotations

import copy
import uuid
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget, QSystemTrayIcon,
    QVBoxLayout, QWidget, QMenu,
)

from .environment import CheckState, capture_block_reason, inspect_environment
from .resources import asset_path
from .settings import SettingsStore


def profile_label(profile: dict[str, Any]) -> str:
    return f"{profile['name']} — {profile['width']} × {profile['height']}"


class MainWindow(QMainWindow):
    def __init__(self, store: SettingsStore) -> None:
        super().__init__()
        self.store = store
        self.settings_window: SettingsWindow | None = None
        self.setWindowTitle("KDE Window Size Screenshot")
        self.setMinimumSize(320, 160)
        self.setWindowState(Qt.WindowState.WindowNoState)

        central = QWidget()
        layout = QVBoxLayout(central)
        header = QHBoxLayout()
        title = QLabel("KDE Window Size Screenshot")
        title.setStyleSheet("font-size: 16px; font-weight: 600")
        header.addWidget(title)
        header.addStretch(1)
        settings_button = QPushButton("⚙")
        settings_button.setToolTip("Settings")
        settings_button.setFixedWidth(36)
        settings_button.clicked.connect(self.open_settings)
        header.addWidget(settings_button)
        layout.addLayout(header)

        self.profile_combo = QComboBox()
        self.refresh_profiles()
        self.profile_combo.currentIndexChanged.connect(self._selected_profile)
        layout.addWidget(self.profile_combo)

        self.capture_button = QPushButton("Capture Window")
        self.capture_button.setMinimumHeight(38)
        self.capture_button.clicked.connect(self.capture)
        layout.addWidget(self.capture_button)
        self.shortcut_label = QLabel()
        self.last_result = QLabel("Last capture: not yet captured")
        self.last_result.setWordWrap(True)
        layout.addWidget(self.shortcut_label)
        layout.addWidget(self.last_result)
        layout.addStretch(1)
        self.setCentralWidget(central)
        self.adjustSize()
        self.resize(max(360, self.sizeHint().width()), max(180, self.sizeHint().height()))
        self._refresh_shortcut()
        self._setup_tray()

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(str(asset_path("icon512.png"))))
        self.tray.setToolTip("KDE Window Size Screenshot")
        menu = QMenu()
        capture_action = menu.addAction("Capture")
        capture_action.triggered.connect(self.capture)
        profiles = menu.addMenu("Select Profile")
        for profile in self.store.data["profiles"]:
            action = profiles.addAction(profile_label(profile))
            action.triggered.connect(lambda checked=False, pid=profile["id"]: self.select_profile(pid))
        menu.addAction("Open GUI", self.showNormal)
        menu.addAction("Quit", QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.showNormal() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def refresh_profiles(self) -> None:
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile in self.store.data["profiles"]:
            self.profile_combo.addItem(profile_label(profile), profile["id"])
        current = self.store.data.get("current_profile_id")
        index = self.profile_combo.findData(current)
        self.profile_combo.setCurrentIndex(max(index, 0))
        self.profile_combo.blockSignals(False)

    def _selected_profile(self, index: int) -> None:
        if index >= 0:
            self.store.data["current_profile_id"] = self.profile_combo.itemData(index)
            self._persist_current()

    def select_profile(self, profile_id: str) -> None:
        index = self.profile_combo.findData(profile_id)
        if index >= 0:
            self.profile_combo.setCurrentIndex(index)

    def _persist_current(self) -> None:
        # Current selection is a lightweight preference; preserve all valid settings.
        try:
            self.store.save(self.store.data)
        except (ValueError, OSError):
            pass

    def _refresh_shortcut(self) -> None:
        self.shortcut_label.setText(f"Shortcut: {self.store.data.get('shortcut', 'Shift+Print')}")

    def capture(self) -> None:
        reason = capture_block_reason(QApplication.platformName())
        self.last_result.setText("Last capture: blocked — safety gate pending")
        QMessageBox.information(self, "Capture unavailable", reason)

    def open_settings(self) -> None:
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.store, self)
            self.settings_window.settings_applied.connect(self._settings_applied)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _settings_applied(self) -> None:
        self.refresh_profiles()
        self._refresh_shortcut()

    def closeEvent(self, event: Any) -> None:
        QApplication.quit()
        event.accept()


class SettingsWindow(QMainWindow):
    from PySide6.QtCore import Signal
    settings_applied = Signal()

    pages = ["Profiles", "Shortcut", "Output", "Application", "System"]

    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.working = store.working_copy()
        self.setWindowTitle("Settings — KDE Window Size Screenshot")
        self.resize(760, 520)

        root = QWidget()
        outer = QVBoxLayout(root)
        body = QHBoxLayout()
        self.nav = QListWidget()
        self.nav.addItems(self.pages)
        self.nav.setFixedWidth(150)
        self.stack = QStackedWidget()
        body.addWidget(self.nav)
        body.addWidget(self.stack, 1)
        outer.addLayout(body, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        buttons.rejected.connect(self.cancel)
        outer.addWidget(buttons)
        self.setCentralWidget(root)

        self._build_profiles()
        self._build_shortcut()
        self._build_output()
        self._build_application()
        self._build_system()
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

    def _page(self, title: str) -> tuple[QWidget, QFormLayout]:
        page = QWidget()
        layout = QFormLayout(page)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 18px; font-weight: 600")
        layout.addRow(heading)
        self.stack.addWidget(page)
        return page, layout

    def _build_profiles(self) -> None:
        _, layout = self._page("Profiles")
        self.profile_combo = QComboBox()
        self.name_input = QLineEdit()
        self.width_input = QSpinBox(); self.width_input.setRange(1, 16384)
        self.height_input = QSpinBox(); self.height_input.setRange(1, 16384)
        self.default_check = QCheckBox("Set as default")
        actions = QWidget(); row = QHBoxLayout(actions); row.setContentsMargins(0, 0, 0, 0)
        new_button = QPushButton("New"); delete_button = QPushButton("Delete")
        row.addWidget(new_button); row.addWidget(delete_button); row.addStretch(1)
        layout.addRow("Profile", self.profile_combo)
        layout.addRow("Profile name", self.name_input)
        layout.addRow("Width", self.width_input)
        layout.addRow("Height", self.height_input)
        layout.addRow("", self.default_check)
        layout.addRow("", actions)
        self._reload_profile_combo()
        self.profile_combo.currentIndexChanged.connect(self._load_profile)
        self.name_input.textEdited.connect(self._save_profile_form)
        self.width_input.valueChanged.connect(self._save_profile_form)
        self.height_input.valueChanged.connect(self._save_profile_form)
        self.default_check.toggled.connect(self._set_default)
        new_button.clicked.connect(self._new_profile)
        delete_button.clicked.connect(self._delete_profile)
        self._load_profile(0)

    def _selected(self) -> dict[str, Any] | None:
        pid = self.profile_combo.currentData()
        return next((p for p in self.working["profiles"] if p["id"] == pid), None)

    def _reload_profile_combo(self, select_id: str | None = None) -> None:
        self.profile_combo.blockSignals(True); self.profile_combo.clear()
        for p in self.working["profiles"]:
            self.profile_combo.addItem(profile_label(p), p["id"])
        target = select_id or self.working.get("default_profile_id")
        self.profile_combo.setCurrentIndex(max(self.profile_combo.findData(target), 0))
        self.profile_combo.blockSignals(False)

    def _load_profile(self, _index: int) -> None:
        p = self._selected()
        if not p: return
        for widget in (self.name_input, self.width_input, self.height_input, self.default_check): widget.blockSignals(True)
        self.name_input.setText(p["name"]); self.width_input.setValue(int(p["width"])); self.height_input.setValue(int(p["height"]))
        self.default_check.setChecked(p["id"] == self.working.get("default_profile_id"))
        for widget in (self.name_input, self.width_input, self.height_input, self.default_check): widget.blockSignals(False)

    def _save_profile_form(self, *_args: Any) -> None:
        p = self._selected()
        if p:
            p.update(name=self.name_input.text(), width=self.width_input.value(), height=self.height_input.value())
            index = self.profile_combo.currentIndex()
            self.profile_combo.setItemText(index, profile_label(p))

    def _set_default(self, checked: bool) -> None:
        p = self._selected()
        if checked and p:
            self.working["default_profile_id"] = p["id"]

    def _new_profile(self) -> None:
        p = {"id": uuid.uuid4().hex[:10], "name": "New Profile", "width": 1280, "height": 800}
        self.working["profiles"].append(p); self._reload_profile_combo(p["id"]); self._load_profile(0)

    def _delete_profile(self) -> None:
        p = self._selected()
        if not p: return
        if len(self.working["profiles"]) <= 1:
            QMessageBox.warning(self, "Cannot delete", "至少需要保留一個 Profile。"); return
        self.working["profiles"] = [item for item in self.working["profiles"] if item["id"] != p["id"]]
        if self.working["default_profile_id"] == p["id"]:
            self.working["default_profile_id"] = self.working["profiles"][0]["id"]
        if self.working["current_profile_id"] == p["id"]:
            self.working["current_profile_id"] = self.working["default_profile_id"]
        self._reload_profile_combo(); self._load_profile(0)

    def _build_shortcut(self) -> None:
        _, layout = self._page("Shortcut")
        self.shortcut_input = QLineEdit(self.working.get("shortcut", "Shift+Print"))
        self.shortcut_input.setReadOnly(True)
        self.record_button = QPushButton("Record Shortcut")
        layout.addRow("Current shortcut", self.shortcut_input)
        layout.addRow("", self.record_button)
        self.record_button.clicked.connect(lambda: QMessageBox.information(self, "Shortcut", "快捷鍵衝突檢查與 KDE 全域註冊將在實機驗證階段完成。"))

    def _build_output(self) -> None:
        _, layout = self._page("Output")
        self.copy_check = QCheckBox("Copy screenshot to clipboard"); self.copy_check.setChecked(self.working["copy_clipboard"])
        self.save_check = QCheckBox("Save screenshot as PNG"); self.save_check.setChecked(self.working["save_png"])
        self.output_input = QLineEdit(self.working["output_directory"])
        browse = QPushButton("Browse…")
        pathrow = QWidget(); row = QHBoxLayout(pathrow); row.setContentsMargins(0, 0, 0, 0); row.addWidget(self.output_input, 1); row.addWidget(browse)
        layout.addRow("", self.copy_check); layout.addRow("", self.save_check); layout.addRow("Output directory", pathrow)
        browse.clicked.connect(self._browse)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select output directory", self.output_input.text())
        if path: self.output_input.setText(path)

    def _build_application(self) -> None:
        _, layout = self._page("Application")
        layout.addRow(QLabel("Close exits the application. Minimize sends the window to the taskbar. KDE autostart is not configured."))

    def _build_system(self) -> None:
        _, layout = self._page("System")
        self.checks = inspect_environment(QApplication.platformName())
        for check in self.checks:
            mark = {CheckState.PASS: "✓", CheckState.FAIL: "✗", CheckState.PENDING: "…"}[check.state]
            layout.addRow(QLabel(f"{mark}  {check.name}"), QLabel(check.detail))
        report = "\n".join(f"{c.state.value} | {c.name} | {c.detail}" for c in self.checks)
        copy_button = QPushButton("Copy diagnostic report")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(report))
        layout.addRow("", copy_button)

    def apply(self) -> None:
        self._save_profile_form()
        self.working["save_png"] = self.save_check.isChecked()
        self.working["copy_clipboard"] = self.copy_check.isChecked()
        self.working["output_directory"] = str(Path(self.output_input.text()).expanduser())
        try:
            SettingsStore.validate(self.working)
            self.store.save(self.working)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Settings not applied", str(exc)); return
        self.settings_applied.emit()
        QMessageBox.information(self, "Settings applied", "設定已保存。截圖功能仍受隔離顯示安全閘門保護。")

    def cancel(self) -> None:
        self.working = copy.deepcopy(self.store.data)
        self.close()

