class Design:
    def __init__(self, num_lanes, page_size_bytes, address_generator, stats_filename):
        self.num_lanes = num_lanes
        self.page_size_bytes = page_size_bytes
        self.address_generator = address_generator
        self.stats_filename = stats_filename
        self.configure()
    def configure(self):
        raise NotImplementedError("configure() should be implemented for all Design objects")
    def simulate(self):
        self.simulator.start_simulation()
