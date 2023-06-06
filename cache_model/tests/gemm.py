import numpy as np

np.random.seed(12)

def GEMM(A, B, blk_size):
    n = len(A)
    blk_n = n // blk_size
    C = np.zeros((n, n))
    C = C.tolist()
    for outer_k in range(0, n, blk_n):
        for outer_j in range(0, n, blk_n):
            for i in range(0, n, 1):
                for k in range(outer_k, outer_k+blk_n, 1):
                    for j in range(outer_j, outer_j+blk_n, 1):
                        C[i][j] += A[i][k] * B[k][j]
    return C


def GEMM_Vector(A, B, blk_size, n_lanes):
    n = len(A)
    blk_n = n // blk_size
    C = np.zeros((n, n))
    C = C.tolist()
    for outer_k in range(0, n, blk_size):
        for outer_j in range(0, n, blk_size):
            for i in range(0, n, 1):
                for k in range(outer_k, outer_k+blk_size, 1):
                    for j in range(outer_j, outer_j+blk_size, n_lanes):
                        for lane_idx in range(n_lanes):
                            print(i, k, j, j+lane_idx)
                            C[i][j+lane_idx] += A[i][k] * B[k][j+lane_idx]
    return C


A = np.random.randint(128, size=(32, 32))
B = np.random.randint(128, size=(32, 32))
C = np.matmul(A, B)

C2 = GEMM_Vector(A.tolist(), B.tolist(), 16, 8)

print(np.sum(np.abs(C-C2)))
