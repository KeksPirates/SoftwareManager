from network.libtorrent_misc import cleanup_session
from utils.logging.logs import consoleLog
from utils.data.state import state
import os

def closehelper():
    state.shutdown_event.set()
    try:
        cleanup_session()
    except Exception as e:
        consoleLog(f"Exception while cleaning up LibTorrent Session: {e}")

def force_exit():
    os._exit(0)