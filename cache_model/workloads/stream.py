import sys
sys.path.append("../")

from objects.workload import PhasedWorkload
from objects.pattern_generators.index_generator import LinearIndexGenerator

class StreamCopyWorkload(PhasedWorkload):
    def __init__(self, num_lanes, array_size, element_size_bytes):
        self.state_load = 0
        self.state_store = 1
        states_index_generators_map = {} # we will add the generators later after we call the parent constructors,
                                         # which will fix the array_size so that array_size is a multiple of num_lanes
        array_bases = { self.state_load: 0,
                        self.state_store: (array_size + 2**12) * element_size_bytes }
        starting_state = self.state_load
        super().__init__(num_lanes = num_lanes,
                         array_size = array_size,
                         states_index_generators_map = states_index_generators_map,
                         array_bases = array_bases,
                         element_size_bytes = element_size_bytes,
                         starting_state = starting_state)
        load_index_generator = LinearIndexGenerator(self.array_size)
        store_index_generator = LinearIndexGenerator(self.array_size)
        states_index_generators_map[self.state_load] = load_index_generator
        states_index_generators_map[self.state_store] = store_index_generator
    def next_state(self, current_state):
        next_state_map = { self.state_load: self.state_store,
                           self.state_store: self.state_load }
        return next_state_map[current_state]
    def get_name(self):
        return f"stream_copy_{self.num_lanes}_{self.array_size}_{self.element_size_bytes}"

class StreamAddWorkload(PhasedWorkload):
    def __init__(self, num_lanes, array_size, element_size_bytes):
        self.state_load_1 = 0
        self.state_load_2 = 1
        self.state_store = 2
        array_bases = { self.state_load_1: 0,
                        self.state_load_2: (array_size + 2**12) * element_size_bytes,
                        self.state_store:  2 * (array_size + 2**12) * element_size_bytes }
        states_index_generators_map = {}
        starting_state = self.state_load_1
        super().__init__(num_lanes = num_lanes,
                         array_size = array_size,
                         states_index_generators_map = states_index_generators_map,
                         array_bases = array_bases,
                         element_size_bytes = element_size_bytes,
                         starting_state = starting_state)
        load_1_index_generator = LinearIndexGenerator(self.array_size)
        load_2_index_generator = LinearIndexGenerator(self.array_size)
        store_index_generator = LinearIndexGenerator(self.array_size)
        states_index_generators_map[self.state_load_1] = load_1_index_generator
        states_index_generators_map[self.state_load_2] = load_2_index_generator
        states_index_generators_map[self.state_store] = store_index_generator
    def next_state(self, current_state):
        next_state_map = { self.state_load_1: self.state_load_2,
                           self.state_load_2: self.state_store,
                           self.state_store: self.state_load_1 }
        return next_state_map[current_state]
    def get_name(self):
        return f"stream_add_{self.num_lanes}_{self.array_size}_{self.element_size_bytes}"

