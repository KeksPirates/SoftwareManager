from core.utils.data.state import state
import os

def closehelper():
    state.shutdown_event.set()
    try:
        from core.network.libtorrent_misc import cleanup_session
        cleanup_session()
    except Exception:
        pass

def force_exit():
    os._exit(0)