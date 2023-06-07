class Workload:
    def __init__(self, num_lanes, array_size):
        self.num_lanes = num_lanes
        self.array_size = (array_size + num_lanes - 1) // num_lanes * num_lanes
    def __iter__(self):
        return self
    def __next__(self):
        raise NotImplementedError("__next__() must be implemented for all Workload objects")
    def get_name(self):
        raise NotImplementedError("get_name() must be implemented for all Workload objects")

# A Workload that can change its state.
# Each address generator generates a stream of indices for an array, and a state is associated with an array.
# For each state, the workload will trigger a different indices generator according to the states_generators_map.
# The array_bases map contains the base address of each array (or state).
class PhasedWorkload(Workload):
    def __init__(self, num_lanes, array_size, states_index_generators_map, array_bases, element_size_bytes, starting_state):
        super().__init__(num_lanes, array_size)
        self.states_index_generators_map = states_index_generators_map
        self.array_bases = array_bases
        self.element_size_bytes = element_size_bytes
        self.lane_idx = 0
        self.state = starting_state
    def next_state(self, current_state):
        raise NotImplementedError("next_state() must be implemented for all PhasedWorkload objects")
    def __next__(self):
        if self.lane_idx == self.num_lanes:
            self.lane_idx = 0
            self.state = self.next_state(self.state)
        vaddr = -1
        array_offset = next(self.states_index_generators_map[self.state])
        array_base = self.array_bases[self.state]
        vaddr = array_base + array_offset * self.element_size_bytes
        self.lane_idx += 1
        assert((vaddr < (1 << 48)) and "We are assuming SV48, the vaddr should be smaller than 2**48")
        return vaddr
