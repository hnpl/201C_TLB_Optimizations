from workloads.irregular import PermutatingGatherWorkload, GUPSWorkload
from workloads.matrix import GEMMWorkload
from workloads.npb import CFFTS1Workload
from workloads.stream import StreamCopyWorkload, StreamAddWorkload

class StandardPermutatingGatherWorkload(PermutatingGatherWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10**7,
                         element_size_bytes = 8)

class StandardGUPSWorkload(GUPSWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         num_accesses = 2**22,
                         element_size_bytes = 8)

# DGEMM is GEMM with matrices of elements of type double
class StandardDGEMMWorkload(GEMMWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         matrix_dim = 384,
                         block_size = 32,
                         element_size_bytes = 8)
class StandardCFFTS1Workload(CFFTS1Workload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         matrix_dim = 192,
                         block_size = 32,
                         element_size_bytes = 8)

class StandardStreamCopyWorkload(StreamCopyWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10**7,
                         element_size_bytes = 8)

class StandardStreamAddWorkload(StreamAddWorkload):
    def __init__(self, num_lanes):
        super().__init__(num_lanes = num_lanes,
                         array_size = 10**7,
                         element_size_bytes = 8)