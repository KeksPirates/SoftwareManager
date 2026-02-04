from core.utils.general.logs import consoleLog
import psutil



def get_net_interfaces():
    addrs = psutil.net_if_addrs()
    for interface in addrs.keys():
        consoleLog(f"Found Interface: {interface}")
    return addrs.keys()