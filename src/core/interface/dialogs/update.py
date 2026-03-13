from core.utils.network.update_checker import get_updates
from core.utils.network.updater import download_update
from PySide6.QtWidgets import QDialog, QMessageBox
from core.utils.data.state import state
import platform
import json
import os

def check_version():
    build_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "build_info.json")
    if os.path.exists(build_info_path):
        with open(build_info_path, "r") as f:
            build_info = json.load(f)
            state.version = build_info.get("version")


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
