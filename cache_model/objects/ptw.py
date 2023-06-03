from math import log2

from .device import Device
from .tlb_cache_entry import TLBCacheEntry

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
    def __init__(self, page_table_size = 2**12):
    	super().__init__(name)
        
        self.num_offset_bits = round(log(page_table_size))
        if (self.num_offset_bits == 12):
            # offset = 0-11, vpn3 = 12-20, vpn2 = 21-29, vpn1 = 30-38, vpn0 = 39-47
            self.num_page_tables = 4
        elif (self.num_offset_bits == 21):
            # offset = 0-20, vpn2 = 21-29, vpn1 = 30-38, vpn0 = 39-47
            self.num_page_tables = 3
        elif (self.num_offset_bits == 30):
            # offset = 0-29, vpn1 = 30-38, vpn0 = 39-47
            self.num_page_tables = 2
        else:
            raise NotImplementedError
        
    def regStats(self):
        self.addStat("requestReceived", 0)
        self.addStat("requestSent", 0)

    def receive_request_and_send_response(self, vaddr):
        self.stats["requestReceived"] += 1
        self.stats["requestSent"] += 1
        for access_idx in self.num_page_tables:
            self.send_request_and_receive_response(self, vaddr)


"""
|--------------||--------------||--------------||--------------||--------------||--------------||--------------||--------------|
|      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      ||      L2      |
|--------------||--------------||--------------||--------------||--------------||--------------||--------------||--------------|

|------------------------------------------------------------------------------------------------------------------------------|
|                                                  PageTableWalkerManager                                                      |
|------------------------------------------------------------------------------------------------------------------------------|

|--------------||--------------||--------------||--------------||--------------||--------------|
|     PTW      ||     PTW      ||     PTW      ||     PTW      ||     PTW      ||     PTW      |
|--------------||--------------||--------------||--------------||--------------||--------------|
"""
class PageTableWalkerManager(Device):
    pass
    