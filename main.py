from core.interface.gui import MainWindow
from core.utils.data.state import state
from core.utils.general.logs import consoleLog
from core.network.libtorrent_misc import send_notification, update_log
from core.utils.general.logs import get_download_logs
from core.utils.general.shutdown import closehelper, shutdown_event
from core.utils.general.wrappers import run_thread
from core.utils.general.loghandler import split_data, check_completed
from core.network.interface import list_interfaces, init_interfaces
from core.network.libtorrent_int import update_bound_interface
from core.utils.config.config import read_config
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import qdarktheme
import threading
import platform
import signal
import argparse
import sys


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

def run_gui():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    widget = MainWindow()
    
    if state.window_transparency and platform.system() != "Windows":
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qdarktheme.setup_theme("auto", custom_colors={"background": "#00000000"})

    from core.utils.general.logs import set_main_window
    set_main_window(widget)
    widget.show()
    sys.exit(app.exec())

def keyboardinterrupthandler(signum, frame):
    closehelper()

if __name__ == "__main__":
    read_config()
    logs = get_download_logs()
    count, downloads = split_data(logs)
    if args.debug:
        state.debug = args.debug # override of read_config
    signal.signal(signal.SIGINT, keyboardinterrupthandler)
    consoleLog("Starting SoftwareManager...")
    consoleLog("Fetching Network Interfaces...")
    list_interfaces()
    consoleLog("Initialiting Interface variables...")
    init_interfaces()
    consoleLog(f"Current Bound: {state.bound_interface}")
    run_thread(threading.Thread(target=send_notification, args=(shutdown_event,), daemon=True))
    consoleLog("Started Thread: send_notification")
    run_thread(threading.Thread(target=update_log, args=(shutdown_event,), daemon=True))
    consoleLog("Started Thread: update_log")
    run_thread(threading.Thread(target=check_completed, args=(downloads, state.autoresume)))
    consoleLog("Started Thread: check_completed")
    consoleLog("Launching GUI")
    run_gui()

