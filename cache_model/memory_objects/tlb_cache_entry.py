from math import log2

class TLBCacheEntry:
    def __init__(self, vpn, pfn, valid, access_time, num_offset_bits):
        self.vpn = vpn # vpn includes both tag and index bits, store vpn for simplicity
        self.pfn = pfn
        self.valid = valid
        self.access_time = access_time
        self.num_offset_bits = num_offset_bits
    def get_vpn_from_addr(self, addr):
        return addr >> self.num_offset_bits
    def match(self, vaddr):
        target_vpn = self.get_vpn_from_addr(vaddr)
        return self.valid and (self.vpn == target_vpn)
    def translate(self, vaddr):
        paddr = (self.pfn << self.num_offset_bits) | (vaddr & (2**self.num_offset_bits - 1))
        assert(paddr == vaddr)
        return paddr
    def __str__(self):
        return f"Translation: ({self.vpn} -> {self.pfn}); Valid: {1 if self.valid else 0}; time: {self.access_time}"
