from .device import Device

from math import log2

def is_power_of_2(n):
    return (n & (n-1)) == 0

class AddressCoalescer(Device):
    def __init__(self, name, page_size_bytes = 2**12):
        super().__init__(name)
        self.num_offset_bits = round(log2(page_size_bytes))
        self.requests = []
    def regStats(self):
        self.addStat("numAccesses", 0)
        self.addStat("numRequestSent", 0)
    def send_request_and_receive_response(self, vaddr):
        # TODO: might have to deal with a bunch of L2
        self.stats["numRequestSent"] += 1
        if len(self.lower_level_devices) == 1:
            return self.lower_level_devices[0].receive_request_and_send_response(vaddr)
        else:
            assert(is_power_of_2(len(self.lower_level_devices)))
            # we are going to use a few least significant bits of vpn to choose which L2 to go to
            num_idx_bits = round(log2(len(self.lower_level_devices)))
            mask = (1 << num_idx_bits) - 1
            vpn = vaddr >> self.num_offset_bits
            idx_bits = vpn & mask
            return self.lower_level_devices[idx_bits].receive_request_and_send_response(vaddr)
    def _get_vpn(self, vaddr):
        return vaddr >> self.num_offset_bits
    def receive_request_and_send_response(self, vaddr):
        self.stats["numAccesses"] += 1
        vpn = self._get_vpn(vaddr)
        self.requests.append(vpn)
        # returning a fake response
        return vpn
    def make_progress(self):
        self.requests = set(self.requests)
        for vpn in self.requests:
            # we have to do this as the send_request_and_receive_response function only accepts vaddr
            vaddr = vpn << self.num_offset_bits
            self.send_request_and_receive_response(vaddr)
        self.requests = []
