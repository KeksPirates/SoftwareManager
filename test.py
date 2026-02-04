import psutil

addrs = psutil.net_if_addrs()
stats = psutil.net_if_stats()


def get_active_interfaces():
    active = []

    for interface, addr_list in addrs.items():
        up = stats[interface].isup
        for addr in addr_list:
            if addr.family == 2: # ipv4
                ipv4 = addr.address
                if not ipv4.startswith("127.") and not ipv4.startswith("169.254") and up == True:
                    print(f'"{interface}": True')
                    active.append(interface)
    print(active)
    return active



get_active_interfaces()

# print(addrs)
# print()
# sigmer = list()



# for interface in stats.keys():
#     print(f"{interface}: UP = {stats[interface].isup}")
#     sigmer.append(f"{interface}: {stats[interface].isup}")

# print(sigmer)