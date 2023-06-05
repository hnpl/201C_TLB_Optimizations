from math import log2

from .device import Device
from .data_cache import DataCache

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
        assert((len(self.lower_level_devices) == 1) and "PooledPTWs should have only one lower level device")
        return self.lower_level_devices[0].receive_request_and_send_response(vaddr)
    def receive_request_and_send_response(self, vaddr):
        self.stats["requestReceived"] += 1
        self.requests.append(vaddr)
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

class PooledPTWsBaseline(PooledPTWs):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name, page_table_size)
    def make_progress(self):
        for vaddr in self.requests:
            for vpn_i in parse_vaddr(vaddr, self.page_size_bytes):
                self.access_memory(vpn_i)
        self.requests = []

class PooledPTWs1(PooledPTWs):
    def __init__(self, name, page_table_size = 2**12):
        super().__init__(name, page_table_size)
    def make_progress(self):
        vpns = set()
        for vaddr in self.requests:
            vpns.add(vaddr >> self.num_offset_bits)
        for vaddr in vpns:
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
                self.access_memory(sub_vpn)
                to_be_visited.append(child_node)
        self.requests = []

class PooledPTWs3(PooledPTWs):
    def __init__(self, name, memory_backend, page_table_size = 2**12):
        super().__init__(name, page_table_size)
        # Since we are simulating going to actual addresses in memory with a cache system, we have to provide somewhat accurate addresses
        # Assume that each page table entry is of size 8 bytes, then the locations of the page table entry of a vaddr are at,
        #   Level 1 page table entry: satp + vpn0 * 8
        #   Level 2 page table entry: satp + (2**9) * 8 + cat(vpn0, vpn1) * 8
        #   Level 3 page table entry: satp + (2**9 + 2**18) * 8 + cat(vpn0, vpn1, vpn2) * 8
        #   Level 4 page table entry: satp + (2**9 + 2**18 + 2**27)*8 + cat(vpn0, vpn1, vpn2, vpn3) * 8
        # Let satp = 1 << 32
        # Then the max page table entry address is [(1 << 32) + (2**9 + 2**18 + 2**27)*8 + ((1<<36) - 1)*8], which is presentable using 40 bits
        self.satp = 1 << 32
        # Add a small cache caching Level 1 page table entry
        self.l1_pte_cache = DataCache(name = "l1_pte_cache", num_entries = 32, associativity = 8, block_size_bytes = 64)
        self.l1_pte_cache.connect_lower_level_device(memory_backend)
        memory_backend.connect_higher_level_device(self.l1_pte_cache)
        self.add_child_device(self.l1_pte_cache)
        # Add a small cache caching Level 2 page table entry
        self.l2_pte_cache = DataCache(name = "l2_pte_cache", num_entries = 32, associativity = 8, block_size_bytes = 64)
        self.l2_pte_cache.connect_lower_level_device(memory_backend)
        memory_backend.connect_higher_level_device(self.l2_pte_cache)
        self.add_child_device(self.l2_pte_cache)
        # Add a small cache caching Level 3 page table entry, this causes a lot of misses
        #self.l3_pte_cache = DataCache(name = "l3_pte_cache", num_entries = 32, associativity = 8, block_size_bytes = 64)
        #self.l3_pte_cache.connect_lower_level_device(memory_backend)
        #memory_backend.connect_higher_level_device(self.l3_pte_cache)
        #self.add_child_device(self.l3_pte_cache)
    def add_path_to_graph(sub_vpns, vpn_graph_root):
        w = vpn_graph_root
        concat_vpn = 0
        for level, sub_vpn in enumerate(sub_vpns):
            # different from PooledPTWs3, here we concat the vpn
            # e.g. (vpn0, vpn1, vpn2, vpn3) = (1, 32, 85, 92)
            # then, concat_vpn0 = 1
            #       concat_vpn1 = (1 << 9) | 32
            #       concat_vpn2 = (concat_vpn1 << 9) | 85
            #       concat_vpn3 = (concat_vpn2 << 9) | 92
            concat_vpn = (concat_vpn << 9) | (sub_vpn)
            if not (level, concat_vpn) in w:
                w[(level, concat_vpn)] = {}
            w = w[(level, concat_vpn)]
    def make_progress(self):
        vpn_graph_root = {}
        for vaddr in self.requests:
            sub_vpns = parse_vaddr(vaddr, self.page_size_bytes)
            PooledPTWs3.add_path_to_graph(sub_vpns, vpn_graph_root)
        # using BFS to traverse the vpn graph and making one memory request per node
        to_be_visited = [vpn_graph_root]
        while to_be_visited:
            node = to_be_visited.pop(0)
            for level_concat_vpn, child_node in node.items():
                level, concat_vpn = level_concat_vpn
                if level == 1:
                    pte_address = self.satp + concat_vpn * 8
                    self.l1_pte_cache.receive_request_and_send_response(pte_address)
                elif level == 2:
                    pte_address = self.satp + (2**9) * 8 + concat_vpn * 8
                    self.l2_pte_cache.receive_request_and_send_response(pte_address)
                #elif level == 3:
                #    pte_address = self.satp + (2**9 + 2**18) * 8 + concat_vpn * 8
                #    self.l3_pte_cache.receive_request_and_send_response(pte_address)
                else:
                    self.access_memory(concat_vpn)
                to_be_visited.append(child_node)
        self.requests = []
