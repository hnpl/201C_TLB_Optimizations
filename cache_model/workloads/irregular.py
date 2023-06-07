import random
import sys
sys.path.append("../")

from objects.workload import Workload, PhasedWorkload
from objects.pattern_generators.index_generator import LinearIndexGenerator, MultiplicativeIndexGenerator

class PermutatingGatherWorkload(PhasedWorkload): # Scatter and gather are pretty similar in terms of address streams
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
        load_2_index_generator = MultiplicativeIndexGenerator(self.array_size)
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
        return f"permutating_gather_{self.num_lanes}_{self.array_size}_{self.element_size_bytes}"

class GUPSWorkload(Workload):
    def __init__(self, num_lanes, num_accesses, table_size = 2**20, batch_size = 128, element_size_bytes = 8):
        super().__init__(num_lanes, num_accesses)
        self.num_accesses = (num_accesses + num_lanes - 1) // num_lanes * num_lanes
        self.state_load_1 = 0 # loading the index
        self.state_store_1 = 1 # updating the index
        self.state_load_2 = 2 # loading the value in the table
        self.state_store_2 = 3 # updating the value in the table
        self.index_array_offset = 0
        self.table_offset = 1 << 32
        self.state = self.state_load_1
        self.table_size = table_size
        self.batch_size = batch_size
        self.element_size_bytes = element_size_bytes
        self.poly = 7
        self.period = 1317624576693539401
        self.index_array = self.get_index_array(batch_size)
        self.lane_idx = 0
        self.index_array_load_idx = 0
        self.index_array_store_idx = 0
        self.table_load_idx = 0
        self.table_store_idx = 0
        self.access_count = 0
        random.seed(10)
    def change_state(self):
        transition_map = { self.state_load_1: self.state_store_1,
                           self.state_store_1: self.state_load_2,
                           self.state_load_2: self.state_store_2,
                           self.state_store_2: self.state_load_1 }
        self.state = transition_map[self.state]
    def rng_original(self, n):
        m2 = [1 for i in range(64)]
        while n > self.period:
            n -= self.period
        if n == 0:
            return 1
        temp = 1
        for i in range(64):
            x = self.poly if (temp >= 2**63) else 0
            temp = ((temp << 1) % (2**64)) ^ x
            x = self.poly if (temp >= 2**63) else 0
            temp = ((temp << 1) % (2**64)) ^ x
        i = 62
        while (((n >> i) & 1) == 0) and (i >= 0):
            i -= 1
        ran = 2
        while i > 0:
            temp = 0
            for j in range(64):
                if ((ran >> j) & 1):
                    temp ^= m2[j]
            ran = temp
            i -= 1
            if ((n >> 1) & 1):
                x = self.poly if (ran >= (2**63)) else 0
                ran = (ran << 1) ^ x
        return ran
    def rng(self, n):
        return random.randrange(2**64)
    def get_index_array(self, batch_size):
        index_array = [0 for i in range(batch_size)]
        for i in range(batch_size):
            index_array[i] = self.rng(self.num_accesses // batch_size * i)
        return index_array
    def __next__(self):
        if self.access_count == self.num_accesses:
            raise StopIteration()
        if self.lane_idx == self.num_lanes:
            self.lane_idx = 0
            self.change_state()
        vaddr = -1
        if self.state == self.state_load_1:
            vaddr = self.index_array_offset + self.index_array_load_idx * self.element_size_bytes
            self.index_array_load_idx = (self.index_array_load_idx + 1) % self.batch_size
        elif self.state == self.state_store_1:
            vaddr = self.index_array_offset + self.index_array_store_idx * self.element_size_bytes
            x = self.poly if (self.index_array[self.index_array_store_idx]) >= 2**63 else 0
            self.index_array[self.index_array_store_idx] = ((self.index_array[self.index_array_store_idx] << 1) % (2**64)) ^ x
            self.index_array_store_idx = (self.index_array_store_idx + 1) % self.batch_size
        elif self.state == self.state_load_2:
            vaddr = self.table_offset + (self.index_array[self.table_load_idx] % self.table_size) * self.element_size_bytes
            self.table_load_idx = (self.table_load_idx + 1) % self.batch_size
        elif self.state == self.state_store_2:
            vaddr = self.table_offset + (self.index_array[self.table_store_idx] % self.table_size) * self.element_size_bytes
            self.table_store_idx = (self.table_store_idx + 1) % self.batch_size
            self.access_count += 1
        else:
            assert(False and "Unknown state!")
        self.lane_idx += 1
        return vaddr
    def get_name(self):
        return f"gups_{self.num_lanes}_{self.num_accesses}_{self.element_size_bytes}"
