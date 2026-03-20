from PySide6.QtWidgets import QDialog, QMessageBox, QProgressDialog
from utils.network.update_checker import get_updates
from utils.network.updater import download_update
from utils.logging.logs import consoleLog
from utils.data.state import state
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from pathlib import Path
import platform
import json
import os

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

class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        if state.ignore_updates is False and platform.system() == "Windows":

            assets, latest = get_updates()
            if assets != None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Update Available")
                msg.setText(f"A new version is available\n({latest})")
                msg.setInformativeText("Press Ok to download.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore)
                response = msg.exec_()
                if response == QMessageBox.StandardButton.Ok:
                    download_update(assets)

class UpdateProgressDialog(QProgressDialog):
    def __init__(self, parent=None):
        self.progress = QtWidgets.QProgressDialog("Downloading update... (0.0 MB/s)", None, 0, 100)
        self.progress.setWindowTitle("Updating")
        self.progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.setAutoClose(False)
        self.progress.setAutoReset(False)
        self.progress.setValue(0)
        self.progress.show()
        QtWidgets.QApplication.processEvents()