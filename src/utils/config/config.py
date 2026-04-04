from interface.dialogs.notificationpopup import NotificationPopup
from utils.logging.logs import consoleLog
from utils.data.state import state
import configparser
import platform
import time
import os


def create_config():
    config = configparser.ConfigParser()

    config["General"] = {
        "debug": str(state.debug),
        "ignore_updates": str(state.ignore_updates),
        "autoresume": str(state.autoresume),        
        "window_transparency": str(state.window_transparency)
    }

    config["Network"] = {
        "api_url": str(state.api_url),
        "bound_interface": str(state.bound_interface) if state.bound_interface is not None else "None",
        "download_speed_limit": str(state.down_speed_limit),
        "upload_speed_limit": str(state.up_speed_limit),
        "max_connections": str(state.max_connections),
        "max_downloads": str(state.max_downloads)
    }

    config["Paths"] = {
        "download_path": str(state.download_path),
        "image_path": str(state.image_path)
    }

    config["Image"] = {
        "enable_image": str(state.image_enabled),
        "image_width": str(state.image_width),
        "image_offset": str(state.image_offset),
        "image_opacity": str(state.image_opacity)
    }

    if platform.system() == "Windows":
        config_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    else:
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    state.settings_path = os.path.join(config_dir, "SoftwareManager")
    os.makedirs(state.settings_path, exist_ok=True)

    with open(os.path.join(state.settings_path, "config.ini"), 'w') as cf:
        config.write(cf)


def read_config():
    config = configparser.ConfigParser()

    if platform.system() == "Windows":
        config_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    else:
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    
    state.settings_path = os.path.join(config_dir, "SoftwareManager")
    
    # Temporary migration logic, keep for a while
    old_config_file = os.path.join(state.settings_path, "config.yml")
    new_config_file = os.path.join(state.settings_path, "config.ini")

    if os.path.exists(old_config_file):
        try:
            os.replace(old_config_file, new_config_file)
            consoleLog("Successfully migrated config.yml to config.ini")
        except Exception as e:
            consoleLog(f"Failed to migrate config file: {e}")

    if not os.path.exists(new_config_file):
        create_config()
        return
    try:
        config.read(new_config_file)
        
        # General
        state.debug = config.getboolean("General", "debug", fallback=state.debug)
        state.ignore_updates = config.getboolean("General", "ignore_updates", fallback=state.ignore_updates)
        state.autoresume = config.getboolean("General", "autoresume", fallback=state.autoresume)
        state.window_transparency = config.getboolean("General", "window_transparency", fallback=state.window_transparency)

        # Network
        state.api_url = config.get("Network", "api_url", fallback=state.api_url)
        state.bound_interface = config.get("Network", "bound_interface", fallback=state.bound_interface)
        if state.bound_interface == "None":
            state.bound_interface = None
        state.down_speed_limit = config.getint("Network", "download_speed_limit", fallback=state.down_speed_limit)
        state.up_speed_limit = config.getint("Network", "upload_speed_limit", fallback=state.up_speed_limit)
        state.max_connections = config.getint("Network", "max_connections", fallback=state.max_connections)
        state.max_downloads = config.getint("Network", "max_downloads", fallback=state.max_downloads)

        # Paths
        state.download_path = config.get("Paths", "download_path", fallback=state.download_path)
        state.image_path = config.get("Paths", "image_path", fallback=state.image_path)

        # Image
        state.image_enabled = config.getboolean("Image", "enable_image", fallback=state.image_enabled)
        state.image_width = config.getint("Image", "image_width", fallback=state.image_width)
        state.image_offset = config.getint("Image", "image_offset", fallback=state.image_offset)
        state.image_opacity = config.getint("Image", "image_opacity", fallback=state.image_opacity)

        create_config()

    except configparser.Error as e:
        consoleLog(f"Error: Configuration file corrupted ({e}). Resetting to defaults.")
        backup_config(new_config_file) # Back up corrupted config
        create_config() # Create new config file
        NotificationPopup(
            title="Config Reset",
            text="Your configuration file has been reset due to a structural error.",
            infotext="A backup of your old configuration file is available in the settings folder."
        ).exec()

    except ValueError as e:
        consoleLog(f"Error: Invalid data types in configuration file ({e}). Resetting to defaults.")
        backup_config(new_config_file) # Back up corrupted config
        create_config() # Create new config file
        NotificationPopup(
            title="Config Reset",
            text="Your configuration file has been reset due to invalid data types.",
            infotext="A backup of your old configuration file is available in the settings folder."
        ).exec()

    except Exception as e:
        consoleLog(f"Unexpected error occurred while loading settings: {e}")
        NotificationPopup(
            title="Unexpected Error",
            text="An unknown error occurred while loading your settings.",
            infotext=f"System returned: {e}\n\nThe application may not function as expected."
        ).exec()

def backup_config(config_path):
    if os.path.exists(config_path):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = f"{config_path}.{timestamp}.bak"
        try:
            os.replace(config_path, backup_path)
            consoleLog(f"Successfully created backup of corrupted config: {backup_path}")
        except Exception as e:
            consoleLog(f"Failed to create backup of corrupted config: {e}")