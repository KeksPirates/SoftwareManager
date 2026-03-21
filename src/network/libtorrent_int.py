from network.interface import get_interface_ip
from utils.general.wrappers import run_thread
from utils.logging.logs import consoleLog
from utils.data.state import state
import libtorrent as lt
import threading
import platform
import ctypes
import time
import os


loop_running = False

def get_free_space_mb(dirname):
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize

def check_space():
    while not state.shutdown_event.is_set():
        for _, magnetdl in list(state.active_downloads.items()):
            try:
                status = magnetdl.status()
            except RuntimeError:
                continue
            
            if status.state == lt.torrent_status.downloading:
                free_space = get_free_space_mb(state.download_path)
                total_size = status.total_wanted

                if free_space < total_size:
                    consoleLog(f"Not enough free space to continue downloading: {status.name}")
                    magnetdl.pause()
                    break
        
        time.sleep(5)

def init_session():
    if state.dl_session is not None:
        return

    state.dl_session = lt.session()


    settings = {
        "upload_rate_limit": state.up_speed_limit * 1024,
        "download_rate_limit": state.down_speed_limit * 1024,
        "enable_dht": True,
        "enable_lsd": True,
        "enable_upnp": True,
        "enable_natpmp": True,
        "dht_bootstrap_nodes": "router.bittorrent.com:6881,dht.transmissionbt.com:6881",
        "connections_limit": state.max_connections,
        "active_downloads": state.max_downloads
    }
    
    if state.bound_interface:
        interface_ip = get_interface_ip(state.bound_interface)
        if interface_ip:
            settings["outgoing_interfaces"] = interface_ip
            settings["listen_interfaces"] = f"{interface_ip}:6881"
            consoleLog(f"Binding to Interface IP: {interface_ip}")
        else:
            consoleLog(f"Skipping Binding, no Interface set. ({state.bound_interface})")

    state.dl_session.apply_settings(settings)

    consoleLog("Initialized Session")


def add_download(magnet_uri):

    if state.active_downloads is None:
        state.active_downloads = {}

    init_session()
    free_space = get_free_space_mb(state.download_path)

    if magnet_uri in state.active_downloads:
        try:
            handle = state.active_downloads[magnet_uri]
            status = handle.status()

            if status.has_metadata:
                filepath = os.path.join(status.save_path, status.name)

                if not os.path.exists(filepath):

                    consoleLog(f"File Deleted, redownloading: {status.name}")
                    state.dl_session.remove_torrent(handle)
                    del state.active_downloads[magnet_uri]
                else:
                    consoleLog("Skipping Downloading, download already running...")
                    return False
            else:
                consoleLog("Skipping Downloading, download already running... ")
                return False
        except RuntimeError as e:
            consoleLog(f"Error in LibTorrent Handle: {e}")
            del state.active_downloads[magnet_uri]

    try:
        params = lt.parse_magnet_uri(magnet_uri)
        params.save_path = state.download_path

        handle = state.dl_session.add_torrent(params)
        while not handle.has_metadata():
            time.sleep(1)

        total_size = handle.get_torrent_info().total_size()

        if free_space > total_size:
            magnetdl = lt.parse_magnet_uri(magnet_uri)
            magnetdl.save_path = state.download_path
            download = state.dl_session.add_torrent(magnetdl)
        else:
            state.dl_session.remove_torrent(handle)
            consoleLog("Not enough free space to download this item.")
            return False

    except Exception as e:
        consoleLog(f"Failed to add torrent or fetch info: {e}")
        return False
    if download:
        state.active_downloads[magnet_uri] = download
    consoleLog(f"Added {magnet_uri} to downloads")

    run_thread(threading.Thread(target=dl_status_loop))
    return True


def add_seed(magnet_uri, file_path):
    if state.active_downloads is None:
        state.active_downloads = {}

    init_session()

    if magnet_uri in state.active_downloads:
        consoleLog("Already seeding this torrent")
        return False

    try:
        magnetdl = lt.parse_magnet_uri(magnet_uri)
        magnetdl.save_path = os.path.dirname(file_path)
        handle = state.dl_session.add_torrent(magnetdl)
    except Exception as e:
        consoleLog(f"Failed to add seed: {e}")
        return False
    state.active_downloads[magnet_uri] = handle
    state.seeded_magnets.add(magnet_uri)
    return True


def dl_status_loop():
    global loop_running
    if loop_running == True:
        return
    
    loop_running = True
    completed_set = set()
    
    if not state.active_downloads:
        consoleLog("No active downloads")
        loop_running = False
        return
    
    while state.active_downloads and not state.shutdown_event.is_set():
        for magnet_uri, magnetdl in list(state.active_downloads.items()):
            try:
                status = magnetdl.status()
            except RuntimeError:
                continue
            
            if status.state == lt.torrent_status.seeding and magnet_uri not in completed_set:
                consoleLog(f"Download completed: {status.name}")
                
                completed_set.add(magnet_uri)
        
        if not state.active_downloads:
            loop_running = False
            break
        
        time.sleep(1)
    
    loop_running = False

def update_settings():

    if state.dl_session is None:
        return

    settings = {
        "upload_rate_limit": state.up_speed_limit * 1024,
        "download_rate_limit": state.down_speed_limit * 1024,
        "connections_limit": state.max_connections,
        "active_downloads": state.max_downloads
    }
    
    if state.bound_interface:
        interface_ip = get_interface_ip(state.bound_interface)
        if interface_ip:
            settings["outgoing_interfaces"] = interface_ip
            settings["listen_interfaces"] = f"{interface_ip}:6881"
            consoleLog(f"Binding to Interface IP: {interface_ip}")
        else:
            consoleLog(f"Skipping Binding, no Interface set. ({state.bound_interface})")

    state.dl_session.apply_settings(settings)

def update_bound_interface():

    settings = { "outgoing_interfaces": state.bound_interface }
    
    state.dl_session.apply_settings(settings)
