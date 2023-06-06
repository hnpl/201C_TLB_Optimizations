import sys
sys.path.append("./")

from workloads.stream import StreamCopyWorkload, StreamAddWorkload
from workloads.irregular import PermutatingGatherWorkload, GUPSWorkload

if __name__ == "__main__":
    num_lanes = 8
    array_size = 100
    actual_array_size = (array_size + num_lanes - 1) // num_lanes * num_lanes

    # Stream Copy
    workload = StreamCopyWorkload(num_lanes = num_lanes, array_size = array_size, element_size_bytes = 8)
    count = 0
    for i in workload:
        count += 1
    assert(count == (actual_array_size * 2))

    # Stream Add
    workload = StreamAddWorkload(num_lanes = num_lanes, array_size = array_size, element_size_bytes = 8)
    count = 0
    for i in workload:
        count += 1
    assert(count == (actual_array_size * 3))

    # Permutating Gather
    workload = PermutatingGatherWorkload(num_lanes = num_lanes, array_size = array_size, element_size_bytes = 8)
    count = 0
    for i in workload:
        count += 1
    assert(count == (actual_array_size * 3))

    # GUPS
    workload = GUPSWorkload(num_lanes = num_lanes, num_accesses = array_size)
    count = 0
    for i in workload:
        count += 1
    assert(count == (actual_array_size * 4))
