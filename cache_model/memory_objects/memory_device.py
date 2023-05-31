class MemoryDevice:
    def __init__(self, name):
        self.tick = 0
        self.name = name
        self.lower_level_memory_device = None # there should be only one lower level device
        self.higher_level_memory_device = []
    def connect_lower_level_memory_device(self, lower_level_memory_device):
        self.lower_level_memory_device = lower_level_memory_device
    def connect_higher_level_memory_device(self, higher_level_memory_device):
        self.higher_level_memory_device.append(higher_level_memory_device)
    def receive_request_and_send_response(self, vaddr):
        raise NotImplementedError()
    def send_request_and_receive_response(self, vaddr):
        raise NotImplementedError("")
    def do_tick(self):
        self.tick += 1
        if not self.lower_level_memory_device == None:
            self.lower_level_memory_device.do_tick()
