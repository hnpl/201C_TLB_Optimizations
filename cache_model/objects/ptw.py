from math import log2

from .device import Device
from .tlb_cache_entry import TLBCacheEntry

def page_size_bytes_to_num_page_table_levels(page_size_bytes):
    num_offset_bits = round(log2(page_size_bytes))
    if (num_offset_bits == 12):
        # offset = 0-11, vpn3 = 12-20, vpn2 = 21-29, vpn1 = 30-38, vpn0 = 39-47
        return 4
    elif (num_offset_bits == 21):
        # offset = 0-20, vpn2 = 21-29, vpn1 = 30-38, vpn0 = 39-47
        return 3
    elif (num_offset_bits == 30):
        # offset = 0-29, vpn1 = 30-38, vpn0 = 39-47
        return 2
    else:
        raise NotImplementedError

"""
    - This function takes a virtual address and the page size and returns,
        (vpn0, vpn1, vpn2, vpn3) if page size is 4KiB
        (vpn0, vpn1, vpn2) if page size is 2MiB
        (vpn0, vpn1) if page size is 1GiB
"""
def parse_vaddr(vaddr, page_size_bytes):
    vpnA, vpnB, vpnC, vpnD = 0, 0, 0, 0
    num_offset_bits = round(log2(page_size_bytes))
    vaddr >>= num_offset_bits
    mask = (1 << 9) - 1
    vpnA = vaddr & mask
    vaddr >>= 9
    vpnB = vaddr & mask
    vaddr >>= 9
    vpnC = vaddr & mask
    vaddr >>= 9
    vpnD = vaddr & mask
    vaddr >>= 9
    if page_size_bytes == 2**12: # 4 KiB
        return vpnD, vpnC, vpnB, vpnA
    if page_size_bytes == 2**21: # 2 MiB
        return vpnC, vpnB, vpnA
    if page_size_bytes == 2**30: # 1 GiB
        return vpnB, vpnA
    else:
        raise NotImplementedError
    

# Virtual address [vpn0 | vpn1 | vpn2 | vpn3 | offset]
# 1. PTW receives a virtual address
# 2. Use vpn0 to find the next level table
# 3. Use vpn1 to find the next level table
# 4. Use vpn2 to find the next level table
# 5. Use vpn3 to find the next level table

# Assuming RISC-V SV48 virtual address space
# Each vpn is 9 bits 
# 4KiB page size (2^12) -> 4 levels of page table -> 12+9+9+9+9
# 2MiB page size (2^21) -> 3 levels of page table -> 21+9+9+9
# 1GiB page size (2^30) -> 2 levels of page table -> 30+9+9

class PageTableWalker(Device):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name)
        self.num_offset_bits = round(log2(page_table_size))
        self.num_page_table_levels = page_size_bytes_to_num_page_table_levels(page_table_size)
        
    def regStats(self):
        self.addStat("requestReceived", 0)
        self.addStat("requestSent", 0)

    def send_request_and_receive_response(self, vaddr):
        self.lower_level_device.receive_request_and_send_response(vaddr)

    def receive_request_and_send_response(self, vaddr):
        self.stats["requestReceived"] += 1
        for access_idx in range(self.num_page_table_levels):
            self.stats["requestSent"] += 1
            self.send_request_and_receive_response(vaddr)
        return vaddr >> self.num_offset_bits

"""
|--------------||--------------||--------------||--------------||--------------||--------------||--------------||--------------|
|      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      |
|--------------||--------------||--------------||--------------||--------------||--------------||--------------||--------------|

|------------------------------------------------------------------------------------------------------------------------------|
|                                                           PooledPTWs                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
"""

"""
- PooledPTWs makes progress after *all* L2 sent their requests.
"""
class PooledPTWs(Device):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name)
        self.num_offset_bits = round(log2(page_table_size))
        self.page_size_bytes = page_table_size
        self.num_page_table_levels = page_size_bytes_to_num_page_table_levels(page_table_size)
        self.requests = []
    def regStats(self):
        self.addStat("requestReceived", 0)
        self.addStat("requestSent", 0)
    def send_request_and_receive_response(self, vaddr):
        return self.lower_level_device.receive_request_and_send_response(vaddr)
    def receive_request_and_send_response(self, vaddr):
        self.stats["requestReceived"] += 1
        self.requests.append(vaddr)
        print("receive", vaddr)
        return vaddr >> self.num_offset_bits # sending a fake response since we are not doing any real translation
    def make_progress(self):
        raise NotImplementedError(f"{self.name} make_progress() must be implemented for all PooledPTWs devices")
    def access_memory(self, vaddr):
        self.stats["requestSent"] += 1
        self.send_request_and_receive_response(vaddr)

"""
- Baseline: make 1 translation per request                                (the PageTableWalker class)
- Optimization 1: coalescing the requests using VPN                       (the PooledPTWs1 class)
- Optimization 2: coalescing the requests using VPN0, VPN1, VPN2, VPN3    (the PooledPTWs2 class)
- Optimization 3: optimization 2 + cache                                  (the PooledPTWs3 class)
"""

"""
    - (vpn0, vpn1, vpn2, vpn3) = (1, 42, 85, 22)
    - (vpn0, vpn1, vpn2, vpn3) = (1, 32, 85, 91)
    - (vpn0, vpn1, vpn2, vpn3) = (1, 32, 85, 92)
    Resulting requests:
        1. (1, 42, 85, 22) accumulates to 4 requests
        2. (1, 32, 85, 91) accumulates to 4 requests
        3. (1, 32, 85, 92) accumulates to 4 requests
"""

class PooledPTWs1(PooledPTWs):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name, page_table_size)
    def make_progress(self):
        vpns = set()
        for vaddr in self.requests:
            vpns.add(vaddr >> self.num_offset_bits)
        for vaddr in self.requests:
            for vpn_i in parse_vaddr(vaddr, self.page_size_bytes):
                self.access_memory(vpn_i)
        self.requests = []

"""
    - (vpn0, vpn1, vpn2, vpn3) = (1, 42, 85, 22)
    - (vpn0, vpn1, vpn2, vpn3) = (1, 32, 85, 91)
    - (vpn0, vpn1, vpn2, vpn3) = (1, 32, 85, 92)
    VPN graph:
                1
               / \
             42   32 
            /    /
          85    85
          /    /  \
         22   91   92
    Resulting requests:
        1. page table at vpn0 = 1
        2. page table at vpn0 = 1, vpn1 = 42
        3. page table at vpn0 = 1, vpn1 = 32
        4. page table at vpn0 = 1, vpn1 = 42, vpn2 = 85
        5. page table at vpn0 = 1, vpn1 = 32, vpn2 = 85
        6. page table at vpn0 = 1, vpn1 = 42, vpn2 = 85, vpn3 = 22
        7. page table at vpn0 = 1, vpn1 = 32, vpn2 = 85, vpn3 = 91
        8. page table at vpn0 = 1, vpn1 = 32, vpn2 = 85, vpn3 = 92

"""
class PooledPTWs2(PooledPTWs):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name, page_table_size)
        self.count = 0
    def add_path_to_graph(sub_vpns, vpn_graph_root):
        w = vpn_graph_root
        for sub_vpn in sub_vpns:
            if not sub_vpn in w:
                w[sub_vpn] = {}
            w = w[sub_vpn]
    def make_progress(self):
        vpn_graph_root = {}
        for vaddr in self.requests:
            sub_vpns = parse_vaddr(vaddr, self.page_size_bytes)
            PooledPTWs2.add_path_to_graph(sub_vpns, vpn_graph_root)
        # using BFS to traverse the vpn graph and making one memory request per node
        to_be_visited = [vpn_graph_root]
        while to_be_visited:
            node = to_be_visited.pop(0)
            for sub_vpn, child_node in node.items():
                self.count += 1
                self.access_memory(sub_vpn)
                to_be_visited.append(child_node)
        self.requests = []
        print("make_progress", self.count)


class PooledPTWs3(PooledPTWs):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name, page_table_size)
    def make_progress(self):
        self.requests = []
