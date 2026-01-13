from core.interface.gui import MainWindow
from core.utils.data.state import state
from core.network.aria2_integration import aria2server
from core.network.aria2_integration import send_notification, update_log
from core.utils.general.shutdown import closehelper, shutdown_event
from core.utils.general.wrappers import run_thread
from core.utils.config.config import read_config
from PySide6 import QtWidgets
import qdarktheme
import darkdetect
import threading
import signal
import argparse
import sys


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true") 
args = parser.parse_args()

def run_gui():
    app = QtWidgets.QApplication([])
    if darkdetect.isDark:
        app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    else:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

def run_aria2server():
    aria2process = aria2server()
    return aria2process

def keyboardinterrupthandler(signum, frame):
    closehelper()

if __name__ == "__main__":
    read_config()
    if args.debug:
        state.debug = args.debug # override of read_config
    if state.debug:
        print("Starting Aria2 Server")
    state.aria2process = run_aria2server()
    signal.signal(signal.SIGINT, keyboardinterrupthandler)
    run_thread(threading.Thread(target=send_notification, args=(shutdown_event,), daemon=True))
    run_thread(threading.Thread(target=update_log, args=(shutdown_event,), daemon=True))
    if state.debug:
        print("Launching GUI")
    run_gui()

