import threading
from core.network.libtorrent_misc import cleanup_session
from core.utils.general.wrappers import run_thread

shutdown_event = threading.Event()

def closehelper():
    run_thread(threading.Thread(target=cleanup_session))
    shutdown_event.set()