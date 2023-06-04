class Simulator:
    def __init__(self, root_object, stats_filename):
        self.root_object = root_object
        self.stats_filename = stats_filename
        self.is_done = False
    def pre_simulation(self):
        self.root_object.populateStats()
    def post_simulation(self):
        with open(self.stats_filename, "w") as f:
            self.root_object.dumpStats(f)
    def start_simulation(self):
        self.pre_simulation()
        while not self.is_done:
            self.next_cycle()
        self.post_simulation()
    def next_cycle(self):
        try:
            self.root_object.next_cycle()
        except AttributeError as e:
            print("Error: the root_object should have next_cycle() defined")
            raise e
        self.is_done = self.root_object.is_done

        # doing BFS traversal on all of the devices and calling make_progress
        to_be_visited = [self.root_object]
        while to_be_visited:
            next_device = to_be_visited.pop(0)
            if next_device:
                next_device.make_progress()
                for lower_level_device in next_device.lower_level_devices:
                    if not lower_level_device in to_be_visited:
                        to_be_visited.append(lower_level_device)

        self.root_object.do_tick()
