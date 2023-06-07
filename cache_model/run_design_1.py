from constants import *

from designs.design_1 import Design1
from workloads.stream import StreamCopyWorkload

if __name__ == "__main__":
    num_lanes = 8
    num_accesses = 100000
    page_size = 4 * oneKiB

    workload = StreamCopyWorkload(num_lanes = num_lanes, array_size = num_accesses, element_size_bytes = 8)

    design = Design1(num_lanes = num_lanes, page_size_bytes = page_size, address_generator = workload, stats_filename = "results/design_1_stats.txt")
    design.simulate()
