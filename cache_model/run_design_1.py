from constants import *
from pattern_generators.address_generator import *
from pattern_generators.index_generator import *

from designs.design_1 import Design1

if __name__ == "__main__":
    num_lanes = 8
    num_accesses = 100000
    page_size = 4 * oneKiB
    num_accesses = (num_accesses + num_lanes - 1) // num_lanes * num_lanes

    # Address generator
    address_generator = AddressGenerator(
        load_index_generator = MultiplicativeGenerator(num_accesses = num_accesses),
        store_index_generator = LinearGenerator(num_accesses = num_accesses),
        num_accesses = num_accesses,
        num_lanes = num_lanes
    )

    design = Design1(num_lanes = num_lanes, page_size_bytes = page_size, address_generator = address_generator, stats_filename = "results/design_1_stats.txt")
    design.simulate()
