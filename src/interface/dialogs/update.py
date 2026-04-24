from PySide6.QtWidgets import QDialog, QMessageBox, QCheckBox
from utils.network.update_checker import get_updates
from utils.network.updater import download_update
from utils.config.config import create_config
from utils.logging.logs import consoleLog
from utils.data.state import state
from pathlib import Path
import webbrowser
import platform
import json
import os

RELEASES_URL = "https://github.com/KeksPirates/SoftwareManager/releases/latest"

def _get_build_info_path() -> (Path | None):
    current_dir = Path(__file__).resolve().parent

    for _ in range(6): # Climb max 6 directories
        file = current_dir / "build_info.json"
        if file.exists():
            return file
        # Go up one directory if file isn't found
        current_dir = current_dir.parent

    return None


def get_version() -> None:
    # Get build info filepath
    build_info_path = _get_build_info_path()
    if build_info_path and os.path.exists(build_info_path):
        with open(build_info_path, "r") as f:
            build_info = json.load(f)
            state.version = build_info.get("version")
    else:
        consoleLog(f"Could not find build info file (Path: {build_info_path})")


def _show_notify_dialog(latest: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Update Available")
    msg.setText(f"A new version is available: <b>{latest}</b>")
    msg.setInformativeText("Visit the releases page to download it.")

    dont_show = QCheckBox("Don't show again")
    msg.setCheckBox(dont_show)

    open_btn = msg.addButton("Open Releases Page", QMessageBox.ButtonRole.AcceptRole)
    msg.addButton("Dismiss", QMessageBox.ButtonRole.RejectRole)

    msg.exec()

    if dont_show.isChecked():
        state.ignore_updates = True
        create_config()

    if msg.clickedButton() == open_btn:
        webbrowser.open(RELEASES_URL)


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        if state.ignore_updates:
            return

        assets, latest = get_updates()
        if assets is None:
            return

        if platform.system() == "Windows":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Update Available")
            msg.setText(f"A new version is available\n({latest})")
            msg.setInformativeText("Press Ok to download.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore)
            response = msg.exec_()
            if response == QMessageBox.StandardButton.Ok:
                download_update(assets)
        else:
            _show_notify_dialog(latest)

