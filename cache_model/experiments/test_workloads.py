from workloads.irregular import PermutatingGatherWorkload, GUPSWorkload
from workloads.matrix import GEMMWorkload
from workloads.npb import CFFTS1Workload
from workloads.stream import StreamCopyWorkload, StreamAddWorkload

class TestStandardPermutatingGatherWorkload(PermutatingGatherWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10,
                         element_size_bytes = 8)

class TestStandardGUPSWorkload(GUPSWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         num_accesses = 10,
                         element_size_bytes = 8)

# DGEMM is GEMM with matrices of elements of type double
class TestStandardDGEMMWorkload(GEMMWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         matrix_dim = 16,
                         block_size = 8,
                         element_size_bytes = 8)
class TestStandardCFFTS1Workload(CFFTS1Workload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         matrix_dim = 16,
                         block_size = 8,
                         element_size_bytes = 8)

class TestStandardStreamCopyWorkload(StreamCopyWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10,
                         element_size_bytes = 8)

class TestStandardStreamAddWorkload(StreamAddWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10,
                         element_size_bytes = 8)
