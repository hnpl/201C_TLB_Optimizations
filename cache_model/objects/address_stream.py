from .device import Device

class AddressStream(Device):
    def __init__(self, name):
        super().__init__(name)
    def regStats(self):
        self.addStat("numAddressesGenerated", 0)
    def send_request_and_receive_response(self, vaddr):
        self.stats["numAddressesGenerated"] += 1
        paddr = self.lower_level_device.receive_request_and_send_response(vaddr)

class AddressStreamManager:
    def __init__(self, num_lanes, address_generator):
        self.streams = [AddressStream(f"address_stream_{i}") for i in range(num_lanes)]
        self.address_generator = address_generator
        self.is_done = False
    def pre_simulation(self):
        for stream in self.streams:
            stream.populateStats()
    def post_simulation(self):
        with open("stats.txt", "w") as f:
            for stream in self.streams:
                stream.dumpStats(f)
    def start_simulating(self):
        self.pre_simulation()
        while not self.is_done:
            self.next_cycle()
        self.post_simulation()
    def next_cycle(self):
        for i, stream in enumerate(self.streams):
            try:
                vaddr = next(self.address_generator)
                paddr = stream.send_request_and_receive_response(vaddr)
            except StopIteration:
                self.is_done = True
                break
        for stream in self.streams:
            stream.do_tick()

