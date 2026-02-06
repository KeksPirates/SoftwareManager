import time
from core.utils.general.wrappers import run_thread
from core.network.interface import get_interface_ip
import threading
import libtorrent as lt
from core.utils.data.state import state
from core.utils.general.logs import consoleLog


global loop_running
loop_running = False

def init_session():
    if state.dl_session is not None:
        return

    state.dl_session = lt.session()


    settings = {
        "upload_rate_limit": state.up_speed_limit,
        "download_rate_limit": state.down_speed_limit,
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
            consoleLog(f"Error finding IP for Interface {state.bound_interface}")

    state.dl_session.apply_settings(settings)

    consoleLog("Initialized Session")


def add_download(magnet_uri, dl_path=state.download_path):

    if state.active_downloads is None:
        state.active_downloads = {}

    init_session()

    if magnet_uri in state.active_downloads:
        consoleLog("Skipping, download already running...")
        return

    magnetdl = lt.parse_magnet_uri(magnet_uri)
    magnetdl.save_path = dl_path

    download = state.dl_session.add_torrent(magnetdl)
    state.active_downloads[magnet_uri] = download
    consoleLog(f"Added {magnet_uri} to downloads")

    run_thread(threading.Thread(target=dl_status_loop))



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
    
    while state.active_downloads:
        for magnet_uri, magnetdl in list(state.active_downloads.items()):
            status = magnetdl.status()
            
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
        "upload_rate_limit": state.up_speed_limit,
        "download_rate_limit": state.down_speed_limit,
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
            consoleLog(f"Error finding IP for Interface {state.bound_interface}")

    state.dl_session.apply_settings(settings)

def update_bound_interface():

    settings = { "outgoing_interfaces": state.bound_interface }
    
    state.dl_session.apply_settings(settings)

