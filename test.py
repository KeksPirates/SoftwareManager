import psutil

addrs = psutil.net_if_addrs()
stats = psutil.net_if_stats()

for interface in addrs.keys():
    print(interface)

print(addrs)
print()
print(stats)