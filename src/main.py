from core.network.libtorrent_misc import send_notification, update_log, check_deleted_files
from core.utils.logging.loghandler import split_data, check_completed, check_downloads
from core.network.interface import list_interfaces, init_interfaces
from core.utils.logging.logs import get_download_logs
from core.utils.logging.logs import set_main_window
from core.utils.general.shutdown import closehelper
from core.utils.general.wrappers import run_thread
from core.utils.general.shutdown import force_exit
from core.utils.config.config import read_config
from core.utils.logging.logs import consoleLog
from core.interface.gui import MainWindow
from core.utils.data.state import state
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import qdarktheme
import threading
import platform
import signal
import time
import sys

def run_gui():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    widget = MainWindow()
    
    # Check OS for window transparency compatibility and apply
    if state.window_transparency and platform.system() != "Windows":
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qdarktheme.setup_theme("auto", custom_colors={"background": "#00000000"})

    set_main_window(widget)
    widget.show()
    sys.exit(app.exec())

def keyboardinterrupthandler(signum, frame):
    closehelper()
    force_exit()


def main():
    # Begin counting startup time
    start_time = time.perf_counter()
    # Parse saved files
    read_config()
    logs = get_download_logs()
    _, downloads = split_data(logs)
    # Initialize Keyboardinterrupt signal
    signal.signal(signal.SIGINT, keyboardinterrupthandler)
    consoleLog("Starting SoftwareManager...")
    # Get network interface info
    list_interfaces()
    init_interfaces()
    consoleLog(f"Current Bound: {state.bound_interface}")
    # Start background daemon threads
    run_thread(threading.Thread(target=send_notification, args=(state.shutdown_event,), daemon=True))
    run_thread(threading.Thread(target=update_log, args=(state.shutdown_event,), daemon=True))
    run_thread(threading.Thread(target=check_deleted_files, args=(state.shutdown_event,), daemon=True))
    # Start background non-daemon threads
    run_thread(threading.Thread(target=check_completed, args=(downloads, state.autoresume)))
    run_thread(threading.Thread(target=check_downloads, args=(downloads,)))
    # Finish counting startup time
    elapsed = time.perf_counter() - start_time
    consoleLog(f"Initialization completed in {elapsed:.2f}s. Launching GUI")
    # Launch GUI
    run_gui()

if __name__ == "__main__":
    main()