import random
import sys
sys.path.append("../")

from objects.workload import Workload, PhasedWorkload

class GEMMWorkload(Workload):
    def __init__(self, num_lanes, matrix_dim, block_size, element_size_bytes = 8):
        super().__init__(num_lanes, 0)
        self.matrix_dim = matrix_dim
        self.block_size = block_size
        self.element_size_bytes = element_size_bytes
        assert((matrix_dim % block_size) == 0)
        assert((block_size % num_lanes) == 0)
        self.A_offset = 0
        self.B_offset = (matrix_dim * matrix_dim + 2**12) * element_size_bytes
        self.C_offset = 2 * (matrix_dim * matrix_dim + 2**12) * element_size_bytes
        self.lane_idx = 0
        self.generator = self.index_generator()
    def matrix_index_to_address(self, base_address, row, col):
        return base_address + (row * self.matrix_dim + col) * self.element_size_bytes
    def index_generator(self):
        # https://csapp.cs.cmu.edu/public/waside/waside-blocking.pdf
        # blocked-ikj
        for outer_j in range(0, self.matrix_dim, self.block_size):
            for outer_k in range(0, self.matrix_dim, self.block_size):
                for i in range(0, self.matrix_dim, 1):
                    for k in range(outer_k, outer_k + self.block_size, 1):
                        # load A[i][k] to one vector
                        for lane_idx in range(self.num_lanes):
                            yield self.matrix_index_to_address(self.A_offset, i, k)
                        for j in range(outer_j, outer_j + self.block_size, self.num_lanes):
                            # load C[i][j+lane_idx]
                            for lane_idx in range(self.num_lanes):
                                yield self.matrix_index_to_address(self.C_offset, i, j+lane_idx)
                            # load B[k][j+lane_idx]
                            for lane_idx in range(self.num_lanes):
                                yield self.matrix_index_to_address(self.B_offset, k, j+lane_idx)
                            # store C[i][j+lane_idx]
                            for lane_idx in range(self.num_lanes):
                                yield self.matrix_index_to_address(self.C_offset, i, j+lane_idx)
    def __next__(self):
        return next(self.generator)
