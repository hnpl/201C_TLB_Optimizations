from .stats import StatsGroup

class Device(StatsGroup):
    def __init__(self, name):
        super().__init__()
        self.tick = 0
        self.name = name
        self.lower_level_devices = [] # in most cases, there should be only one lower level device
        self.higher_level_devices = []
        self.stat_registered = False
        self.stat_dumped = False
        self.is_done = False # should only be used by Root object
    def connect_lower_level_device(self, lower_level_device):
        self.lower_level_devices.append(lower_level_device)
    def connect_higher_level_device(self, higher_level_device):
        self.higher_level_devices.append(higher_level_device)
    def make_progress(self): # this function is meant for the AddressCoalescer and the Pool devices
        pass
    def receive_request_and_send_response(self, vaddr):
        raise NotImplementedError(f"{self.name} receive_request_and_send_response() must be defined for all Device objects!")
    def send_request_and_receive_response(self, vaddr):
        raise NotImplementedError(f"{self.name} send_request_and_receive_response() must be defined for all Device objects!")
    def do_tick(self):
        self.tick += 1
        for lower_level_device in self.lower_level_devices:
            lower_level_device.do_tick()
    def regStats(self):
        raise NotImplementedError(f"{self.name} regStats() must be defined for all Device objects!")
    def populateStats(self):
        for lower_level_device in self.lower_level_devices:
            lower_level_device.populateStats()
        if self.stat_registered:
            return
        self.stat_registered = True
        self.regStats()
    def dumpStats(self, output_stream):
        for lower_level_device in self.lower_level_devices:
            lower_level_device.dumpStats(output_stream)
        if self.stat_dumped:
            return
        self.stat_dumped = True
        for stat_name, stat_val in self.stats.items():
            output_stream.write(f"{self.name}.{stat_name}: {stat_val}\n")
