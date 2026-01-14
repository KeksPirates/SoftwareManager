import os
import platform
import configparser
from core.utils.data.state import state

def create_config():
    config = configparser.ConfigParser()

    config["General"] = {"debug": True, "api_url": f"{state.api_url}", "aria2_threads": f"{state.aria2_threads}", "download_path": f"{state.download_path}", f"speed_limit": f"{state.speed_limit}", 
                         "ignore_updates": f"{state.ignore_updates}", "image_path": f"{state.image_path}", "autoresume": f"{state.autoresume}"}

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

    state.debug = config.getboolean("General", "debug", fallback=state.debug)
    state.api_url = config.get("General", "api_url", fallback=state.api_url)
    state.aria2_threads = config.getint("General", "aria2_threads", fallback=state.aria2_threads)
    state.download_path = config.get("General", "download_path", fallback=state.download_path)
    state.speed_limit = config.getint("General", "speed_limit", fallback=state.speed_limit)
    state.ignore_updates = config.getboolean("General", "ignore_updates", fallback=state.ignore_updates)
    state.image_path = config.get("General", "image_path", fallback=state.image_path)
    state.autoresume = config.getboolean("General", "autoresume", fallback=state.autoresume)

    create_config()