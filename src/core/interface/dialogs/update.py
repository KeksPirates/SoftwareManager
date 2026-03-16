from core.utils.network.update_checker import get_updates
from core.utils.network.updater import download_update
from PySide6.QtWidgets import QDialog, QMessageBox
from core.utils.logging.logs import consoleLog
from core.utils.data.state import state
from pathlib import Path
import platform
import json
import os

def check_version():
    # Get build info filepath
    build_info_path = Path(__file__).resolve().parents[3] / "build_info.json" # parents[3] = climb up 4 directories from the file ran
    if os.path.exists(build_info_path):
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
