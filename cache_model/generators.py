def stream_generator(n, element_size_bytes = 8):
    for i in range(n):
        yield i * element_size_bytes                              # load
        yield i * element_size_bytes + 2 * n * element_size_bytes # store

def strided_generator(num_accesses, stride, element_size_bytes = 8):
    load_base = 0
    store_base = num_accesses * stride * element_size_bytes * 2
    for i in range(num_accesses):
        yield load_base + i * stride * element_size_bytes
        yield store_base + i * stride * element_size_bytes

def permutation_generator(element_size_bytes = 8):
    w = 1
    for i in range(10_000_019):
        w = (w * 37) % 10_000_019
        yield w * element_size_bytes
