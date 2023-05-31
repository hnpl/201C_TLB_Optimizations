from .memory_device import MemoryDevice
from .tlb_cache_entry import TLBCacheEntry

from math import log2

# This is a readonly memory backend
class MemoryBackend(MemoryDevice):
    def __init__(self, name, page_size_bytes):
        super().__init__(name)
        self.translations = {}
        self.page_size_bytes = page_size_bytes
        self.num_offset_bits = round(log2(self.page_size_bytes))
    def parse_addr(self, addr):
        offset_bits = addr & ((2**self.num_offset_bits) - 1)
        vpn = addr >> self.num_offset_bits
        return (vpn, offset_bits)
    def send_request_and_receive_response(self, vaddr):
        raise NotImplementedError("Backend memory does not send request.")
    def receive_request_and_send_response(self, vaddr):
        vpn, offset_bits = self.parse_addr(vaddr)

        # come up with a translation, we can simulate fragmentation here
        if not vpn in self.translations:
            self.translations[vpn] = vpn

        return TLBCacheEntry(
            vpn = vpn,
            pfn = self.translations[vpn],
            valid = True,
            access_time = self.tick,
            num_offset_bits = self.num_offset_bits
        )
