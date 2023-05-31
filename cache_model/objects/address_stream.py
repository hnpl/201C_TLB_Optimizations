from .device import Device

class AddressStream(Device):
    def __init__(self):
        super().__init__(self)
    def send_request_and_receive_response(self, vaddr):
        paddr = self.lower_level_device.receive_request_and_send_response(vaddr)

class AddressStreamManager:
    def __init__(self, num_lanes, address_generator):
        self.streams = [AddressStream() for _ in range(num_lanes)]
        self.address_generator = address_generator
        self.is_done = False
    def start_simulating(self):
        while not self.is_done:
            self.next_cycle()
    def next_cycle(self):
        for stream in self.streams:
            try:
                vaddr = next(self.address_generator)
                paddr = stream.send_request_and_receive_response(vaddr)
            except StopIteration:
                self.is_done = True
                break
        for stream in self.streams:
            stream.do_tick()

