from core.utils.general.logs import consoleLog
import psutil

addrs = psutil.net_if_addrs()
stats = psutil.net_if_stats()

def get_net_interfaces():
    for interface in addrs.keys():
        consoleLog(f"Found Interface: {interface}")
    return addrs.keys()


def get_active_interfaces():
    active = []

    for interface, addr_list in addrs.items():
        up = stats[interface].isup
        for addr in addr_list:
            if addr.family == 2: # ipv4
                ipv4 = addr.address
                if not ipv4.startswith("127.") and not ipv4.startswith("169.254") and up == True:
                    active.append(interface)
                    consoleLog(f"Found Active: {interface}")

    return active


def list_interfaces() -> None:

    for interface, addr_list in addrs.items():
        up = stats[interface].isup
        for addr in addr_list:
            if addr.family == 2: # ipv4
                ipv4 = addr.address
                if not ipv4.startswith("127.") and not ipv4.startswith("169.254") and up == True:
                    status = "ACTIVE"
                else:
                    status = "INACTIVE"
        consoleLog(f"Found Interface: {interface} [{status}]")

