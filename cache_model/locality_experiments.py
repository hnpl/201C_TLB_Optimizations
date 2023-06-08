from math import log2

from experiments.standard_workloads import StandardCFFTS1Workload, StandardDGEMMWorkload
from constants import *

num_lanes = 32
page_size_bytes = 4 * oneKiB

def get_vpn_histogram(workload, page_size_bytes):
    num_offset_bits = round(log2(page_size_bytes))
    freq = {i: 0 for i in range(num_lanes+1)}
    seen_vpn = set()
    for i, vaddr in enumerate(workload):
        if i != 0 and (i % num_lanes) == 0:
            freq[len(seen_vpn)] += 1
            seen_vpn = set()
        vpn = vaddr >> num_offset_bits
        seen_vpn.add(vpn)
    freq[len(seen_vpn)] += 1
    return freq

def freq_to_csv(freq):
    keys = sorted(list(freq.keys()))
    s = []
    for key in keys:
        s.append(str(key) + "," + str(freq[key]))
    return "\n".join(s)

workload = StandardCFFTS1Workload(num_lanes = num_lanes)
freq = get_vpn_histogram(workload, page_size_bytes)
csv = freq_to_csv(freq)
print(csv)

workload = StandardDGEMMWorkload(num_lanes = num_lanes)
freq = get_vpn_histogram(workload, page_size_bytes)
csv = freq_to_csv(freq)
print(csv)
