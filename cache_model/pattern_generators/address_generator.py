class AddressGenerator:
    STATE_LOAD = 0
    STATE_STORE = 1
    def __init__(self, load_index_generator, store_index_generator, num_accesses, num_lanes, element_size_bytes = 8):
        self.num_accesses = (num_accesses + num_lanes - 1) // num_lanes * num_lanes # round to the nearest integer this divisible by num_lanes
        self.num_lanes = num_lanes
        self.load_index_generator = load_index_generator
        self.store_index_generator = store_index_generator
        self.element_size_bytes = element_size_bytes
        self.load_base = self.get_default_load_base()
        self.store_base = self.get_default_store_base()
        self.state = AddressGenerator.STATE_LOAD
        self.lane_idx = 0
    def get_default_load_base(self):
        return 0
    def get_default_store_base(self):
        return 2**40 # 1 TiB apart seems to be sufficient
    def _switch_state(self):
        if self.state == AddressGenerator.STATE_LOAD:
            self.state = AddressGenerator.STATE_STORE
        elif self.state == AddressGenerator.STATE_STORE:
            self.state = AddressGenerator.STATE_LOAD
        else:
            raise Error("Unknown state!")
    def __iter__(self):
        return self
    def __next__(self):
        if self.lane_idx == self.num_lanes: # switch state
            self.lane_idx = 0
            self._switch_state()
        vaddr = -1
        if self.state == AddressGenerator.STATE_LOAD:
            vaddr = self.load_base + next(self.load_index_generator) * self.element_size_bytes
        elif self.state == AddressGenerator.STATE_STORE:
            vaddr = self.store_base + next(self.store_index_generator) * self.element_size_bytes
        else:
            raise Exception("Unknown state!")
        self.lane_idx += 1
        return vaddr

