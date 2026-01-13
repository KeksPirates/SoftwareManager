from core.utils.data.state import state
from core.utils.general.shutdown import kill_aria2server
from .config import create_config

def restart_aria2c():
    import main # had to do this because of circle import :(
    import signal
    import atexit
    kill_aria2server()
    state.aria2process.wait()
    state.aria2process = main.run_aria2server()
    signal.signal(signal.SIGINT, main.keyboardinterrupthandler)
    atexit.unregister(kill_aria2server)
    atexit.register(kill_aria2server)

def save_settings(thread_count=None, close=lambda: None, apiurl=None, download_path=None, speed_limit=None, image_path=None, autoresume=None):
    if thread_count is not None:
        state.aria2_threads = thread_count
    if apiurl is not None:
        state.api_url = apiurl
    if download_path is not None:
        state.download_path = download_path
    if speed_limit is not None:
        state.speed_limit = speed_limit
    if image_path is not None:
        state.image_path = image_path
    if autoresume is not None:
        state.autoresume = autoresume
    
    
    create_config()
    restart_aria2c()
    close()
