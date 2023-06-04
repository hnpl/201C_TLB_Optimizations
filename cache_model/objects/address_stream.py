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

        # doing BFS traversal on all of the devices and calling make_progress
        to_be_visited = [stream for stream in self.streams]
        while to_be_visited:
            next_device = to_be_visited.pop(0)
            if next_device:
                next_device.make_progress()
                lower_level_device = next_device.lower_level_device
                #for lower_level_device in next_device.lower_level_device:
                if not lower_level_device in to_be_visited:
                    to_be_visited.append(lower_level_device)

        for stream in self.streams:
            stream.do_tick()

"""
stream   stream   stream
 |          |       |
 L1         L1      L1
 |          |       |
 L2         L2      L2
 |          |       |
 --------------------
            |
         PoolPTWs
 
 
"""
