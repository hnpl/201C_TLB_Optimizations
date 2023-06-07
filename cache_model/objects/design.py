class Design:
    def __init__(self, name, num_lanes, page_size_bytes, address_generator, stats_filename = ""):
        self.name = name
        self.num_lanes = num_lanes
        self.page_size_bytes = page_size_bytes
        self.address_generator = address_generator
        if len(stats_filename) == 0:
            self.stats_filename = self.get_simulation_name()
        else:
            self.stats_filename = stats_filename
        self.configure()
    def set_stats_filename(self, stats_filename):
        self.simulator.stats_filename = stats_filename
    def configure(self):
        raise NotImplementedError("configure() should be implemented for all Design objects")
    def simulate(self):
        self.simulator.start_simulation()
    def get_name(self):
        return self.name
    def get_simulation_name(self):
        return f"{self.name}_{self.page_size_bytes}_{self.address_generator.get_name()}"
