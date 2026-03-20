from network.direct_download.handle import DirectDownloadHandle
from utils.logging.logs import consoleLog
from utils.data.state import state
from PySide6 import QtWidgets
import libtorrent as lt
import subprocess
import tempfile
import hashlib
import time
import sys
import os


def _verify_hash(file_path: str, expected_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}" == expected_hash


def download_update(assets: list):
    filename = None
    setup_hash = None
    url = None

    for asset in assets:
        if "-windows-setup.exe" in asset["name"]:
            filename = asset["name"]
            setup_hash = asset["hash"]
            url = asset["url"]
            break

    if not filename:
        consoleLog("Error: No Windows installer found in release assets")
        return

    installer_path = os.path.join(tempfile.gettempdir(), filename)

    from interface.dialogs.update import UpdateProgressDialog
    progress = UpdateProgressDialog()

    original_limit = state.down_speed_limit
    state.down_speed_limit = 0
    handle = DirectDownloadHandle(url, filename, tempfile.gettempdir())
    handle.start()

    while True:
        QtWidgets.QApplication.processEvents()
        status = handle.status()

        if status.error:
            state.down_speed_limit = original_limit
            progress.close()
            consoleLog(f"Update download failed: {status.error}")
            return

        if status.total_wanted > 0:
            pct = int(status.total_wanted_done * 100 / status.total_wanted)
            speed_mb = status.download_rate / (1024 * 1024)
            progress.setValue(pct)
            progress.setLabelText(f"Downloading update... ({speed_mb:.1f} MB/s)")

        if status.state == lt.torrent_status.seeding:
            break

        time.sleep(0.1)

    state.down_speed_limit = original_limit

    if setup_hash:
        if _verify_hash(installer_path, setup_hash):
            consoleLog(f"Successfully validated installer hash ({setup_hash})")
        else:
            progress.close()
            consoleLog("Error: Invalid file hash, file may be corrupted")
            sys.exit(0)
    else:
        consoleLog("Skipping hash verification (no hash found for release)")

    progress.setLabelText("Installing update...")
    progress.setValue(100)
    QtWidgets.QApplication.processEvents()

    subprocess.Popen([installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/SP-", "/CLOSEAPPLICATIONS"])
    time.sleep(1)
    sys.exit(0)
