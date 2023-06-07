from math import log2
import random
import sys
sys.path.append("../")

from objects.workload import Workload, PhasedWorkload

class CFFTS1Workload(Workload):
    def __init__(self, num_lanes, matrix_dim, block_size, element_size_bytes = 8):
        super().__init__(num_lanes, 0)
        self.matrix_dim = matrix_dim
        self.block_size = block_size
        self.element_size_bytes = element_size_bytes
        assert((matrix_dim % block_size) == 0)
        assert((block_size % num_lanes) == 0)
        padding_size = 2**12
        x_size = (self.matrix_dim ** 3) * self.element_size_bytes
        xout_size = x_size
        y1_size = self.matrix_dim * self.block_size * self.element_size_bytes
        y2_size = y1_size
        self.x_offset = 0 # 3d
        self.xout_offset = x_size + padding_size # 3d
        self.y1_offset = x_size + xout_size + 2 * padding_size # 2d
        self.y2_offset = x_size + xout_size + y1_size + 3 * padding_size # 2d
        self.generator = self.address_generator()
    def index2_to_address(self, base_address, n_x, n_y, x, y):
        return base_address + (x * n_y + y) * self.element_size_bytes
    def index3_to_address(self, base_address, n_x, n_y, n_z, x, y, z):
        return base_address + (x * (n_y * n_z) + y * n_z + z) * self.element_size_bytes
    def fftz2(self, l, m, n, ny, x, y):
        lk = 2**l
        li = 2**(m-l+1)
        lj = 2 * lk
        ku = li+1
        for fftz_i in range(li):
            i11 = fftz_i * lk
            i12 = i11 + self.matrix_dim // 2
            i21 = fftz_i + lj
            i22 = i21 + lk
            # ignore load u(ku+i)
            for fftz_k in range(lk):
                for fftz_j in range(0, self.block_size, self.num_lanes):
                    # load x(i11+k, j) [note: x in fftz2 is y1 in cffts1]
                    for fftz_lane_idx in range(self.num_lanes):
                        yield self.index2_to_address(x,
                                                     self.matrix_dim, self.block_size,
                                                     i11 + fftz_k, fftz_j + fftz_lane_idx)
                    # load x(i12+k, j)
                    for fftz_lane_idx in range(self.num_lanes):
                        yield self.index2_to_address(x,
                                                     self.matrix_dim, self.block_size,
                                                     i12 + fftz_k, fftz_j + fftz_lane_idx)
                    # store y(i21+k, j) [note: y in fftz2 is y2 in cffts1]
                    for fftz_lane_idx in range(self.num_lanes):
                        yield self.index2_to_address(y,
                                                     self.matrix_dim, self.block_size,
                                                     i21 + fftz_k, fftz_j + fftz_lane_idx)
                    # load x(i12+k, j)
                    for fftz_lane_idx in range(self.num_lanes):
                        yield self.index2_to_address(y,
                                                     self.matrix_dim, self.block_size,
                                                     i22 + fftz_k, fftz_j + fftz_lane_idx)
    def address_generator(self):
        for k in range(self.matrix_dim):
            for j_base in range(0, self.matrix_dim, self.block_size):
                for j_offset in range(self.block_size):
                    j = j_base + j_offset
                    for i in range(0, self.matrix_dim, self.num_lanes):
                        for lane_idx in range(self.num_lanes):
                            # load x(k, j, i)
                            yield self.index3_to_address(self.x_offset,
                                                         self.matrix_dim, self.matrix_dim, self.matrix_dim,
                                                         k, j, i + lane_idx)
                        for lane_idx in range(self.num_lanes):
                            # store y1(i, j)
                            yield self.index2_to_address(self.y1_offset,
                                                         self.matrix_dim, self.block_size,
                                                         i + lane_idx, j)
                # call cfftz(is, logd1, d1, y1, y2)
                #            is,     m,  n,  x,  y
                #   for l = range(0, m, 2):
                #       call fftz2(is, l, m, n, block_size, pad, u, x, y)
                #                  is, l, m, n,         ny, ny1, u, x, y
                #           lk = 2**(l - 1)
                #           li = 2**(m-l)
                #           ku = li + 1
                #           for i in range(li):
                #               load u(ku+i)
                #               for k = 0, lk - 1
                #                   for j = 0, ny
                #                       load x(i*lk+1+k, j)
                #                       load x(i*lk+1+k+n/2, j)
                #                       store y(i*lj+1+k, j)
                #                       store y(i*lj+1+k+lk, j)
                # start function cfftz()
                m = round(log2(self.matrix_dim))
                for l in range(0, m, 2):
                    yield from self.fftz2(l, m, self.matrix_dim, self.block_size, self.y1_offset, self.y2_offset)
                    if i + 1 == m:
                        break
                    yield from self.fftz2(l+1, m, self.matrix_dim, self.block_size, self.y2_offset, self.y1_offset)
                # end function cfftz()
                for j_offset in range(self.block_size):
                    j = j_base + j_offset
                    for i in range(0, self.matrix_dim, self.num_lanes):
                        for lane_idx in range(self.num_lanes):
                            # load y1(i, j)
                            yield self.index2_to_address(self.y1_offset,
                                                         self.matrix_dim, self.block_size,
                                                         i + lane_idx, j)
                            # store xout(i, j, k)
                            yield self.index3_to_address(self.xout_offset,
                                                         self.matrix_dim, self.matrix_dim, self.matrix_dim,
                                                         k, j, i + lane_idx)
    def __next__(self):
        return next(self.generator)
