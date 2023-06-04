from .device import Device

class AddressStream(Device):
    def __init__(self, name):
        super().__init__(name)
    def regStats(self):
        self.addStat("numAddressesGenerated", 0)
    def send_request_and_receive_response(self, vaddr):
        assert((len(self.lower_level_devices) == 1) and ("AddressStream should only have one lower level device"))
        self.stats["numAddressesGenerated"] += 1
        paddr = self.lower_level_devices[0].receive_request_and_send_response(vaddr)

class AddressStreamManager(Device):
    def __init__(self, name, num_lanes, address_generator):
        super().__init__(name)
        self.streams = [AddressStream(f"address_stream_{i}") for i in range(num_lanes)]
        for stream in self.streams:
            self.connect_lower_level_device(stream)
            stream.connect_higher_level_device(self)
        self.address_generator = address_generator
        self.is_done = False
    def send_request_and_receive_response(self, vaddr):
        pass
    def receive_request_and_send_response(self, vaddr):
        pass
    def regStats(self):
        pass
    def next_cycle(self):
        for i, stream in enumerate(self.streams):
            try:
                vaddr = next(self.address_generator)
                paddr = stream.send_request_and_receive_response(vaddr)
            except StopIteration:
                self.is_done = True
                break
