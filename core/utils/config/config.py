import os
import platform
import configparser
from core.utils.data.state import state

def create_config():
    config = configparser.ConfigParser()

    config["General"] = {
        "debug": True,
        "ignore_updates": f"{state.ignore_updates}",
        "autoresume": f"{state.autoresume}",        
        "window_transparency": f"{state.window_transparency}"
    }

    config["Network"] = {
        "api_url": f"{state.api_url}",
        "download_path": f"{state.download_path}",
        "download_speed_limit": f"{state.down_speed_limit}",
        "upload_speed_limit": f"{state.up_speed_limit}",
        "max_connections": f"{state.max_connections}",
        "max_downloads": f"{state.max_downloads}"
    }

    config["Paths"] = {
        "bound_interface": f"{state.bound_interface}",
        "image_path": f"{state.image_path}"
    }

    if platform.system() == "Windows":
        config_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    else:
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    state.settings_path = os.path.join(config_dir, "SoftwareManager")
    os.makedirs(state.settings_path, exist_ok=True)

    with open(os.path.join(state.settings_path, "config.yml"), 'w') as cf:
        config.write(cf)


def read_config():

    config = configparser.ConfigParser()

    if platform.system() == "Windows":
        config_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    else:
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    state.settings_path = os.path.join(config_dir, "SoftwareManager")
    config_file = os.path.join(state.settings_path, "config.yml")

    if not os.path.exists(config_file):
        create_config()
        return

    config.read(config_file)
    
    # General
    state.debug = config.getboolean("General", "debug", fallback=state.debug)
    state.ignore_updates = config.getboolean("General", "ignore_updates", fallback=state.ignore_updates)
    state.autoresume = config.getboolean("General", "autoresume", fallback=state.autoresume)
    state.window_transparency = config.getboolean("General", "window_transparency", fallback=state.window_transparency)

    # Network
    state.api_url = config.get("Network", "api_url", fallback=state.api_url)
    state.download_path = config.get("Network", "download_path", fallback=state.download_path)
    state.down_speed_limit = config.getint("Network", "download_speed_limit", fallback=state.down_speed_limit)
    state.up_speed_limit = config.getint("Network", "upload_speed_limit", fallback=state.up_speed_limit)
    state.max_connections = config.getint("Network", "max_connections", fallback=state.max_connections)
    state.max_downloads = config.getint("Network", "max_downloads", fallback=state.max_downloads)

    # Paths
    state.bound_interface = config.get("Paths", "bound_interface", fallback=state.bound_interface)
    state.image_path = config.get("Paths", "image_path", fallback=state.image_path)
    
    create_config()
