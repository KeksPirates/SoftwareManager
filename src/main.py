from network.libtorrent_misc import send_notification, update_log, check_deleted_files
from utils.logging.loghandler import split_data, check_completed, check_downloads
from network.interface import list_interfaces, init_interfaces
from utils.logging.logs import get_download_logs
from utils.logging.logs import set_main_window
from network.libtorrent_int import check_space
from utils.general.shutdown import closehelper
from utils.general.wrappers import run_thread
from interface.assets.base64_icons import logo_base64
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from utils.general.shutdown import force_exit
from utils.config.config import read_config
from utils.logging.logs import consoleLog
from interface.gui import MainWindow
from utils.data.state import state
from PySide6.QtGui import QAction, QPixmap
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import qdarktheme
import threading
import platform
import base64
import signal
import time
import sys

def run_gui(app):
    custom_colors = {}
    if state.accent_color:
        custom_colors["primary"] = state.accent_color
    qdarktheme.setup_theme("auto", custom_colors=custom_colors if custom_colors else None)
    widget = MainWindow()

    pixmap = QPixmap()
    image_data = base64.b64decode(logo_base64)
    pixmap.loadFromData(image_data)

    tray = QSystemTrayIcon()
    tray.setIcon(pixmap)
    tray.setVisible(True)

    menu = QMenu()

    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    tray.setContextMenu(menu)
    
    # Check OS for window transparency compatibility and apply
    if state.window_transparency and platform.system() != "Windows":
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        transparent_colors = {"background": "#00000000", **custom_colors}
        qdarktheme.setup_theme("auto", custom_colors=transparent_colors)

    set_main_window(widget)
    widget.show()
    sys.exit(app.exec())

def keyboardinterrupthandler(signum, frame):
    closehelper()
    force_exit()


def main():
    # Begin counting startup time
    start_time = time.perf_counter()
    
    # Initialize UI Engine
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

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
    run_thread(threading.Thread(target=check_space, args=()))
    # Finish counting startup time
    elapsed = time.perf_counter() - start_time
    consoleLog(f"Initialization completed in {elapsed:.2f}s. Launching GUI")
    # Launch GUI
    run_gui(app)

if __name__ == "__main__":
    main()
