class IndexGenerator:
    def __init__(self, num_accesses):
        self.num_accesses = num_accesses
        self.pattern = self.sequence_generator()
    def sequence_generator(self):
        raise NotImplementedError("All IndexGenerator objects must implement sequence_generator")
    def __iter__(self):
        return self
    def __next__(self):
        return next(self.pattern)

class FileGenerator(IndexGenerator):
    def __init__(self, num_accesses, filepath):
        super().__init__(num_accesses)
        self.sequence = []
        with open(filepath, "r") as f:
            self.sequence = f.readline().strip().split(",")
    def sequence_generator(self):
        n = len(self.sequence)
        for i in range(self.num_accesses):
            yield self.sequence[i%n]

class LinearGenerator(IndexGenerator):
    def __init__(self, num_accesses):
        super().__init__(num_accesses)
    def sequence_generator(self):
        for i in range(self.num_accesses):
            yield i

class StrideGenerator(IndexGenerator):
    def __init__(self, num_accesses, stride, offset = 0):
        super().__init__(num_accesses)
        self.offset = offset
        self.stride = stride
    def sequence_generator(self):
        for i in range(self.num_accesses):
            yield self.offset + i * self.stride

class MultiplicativeGenerator(IndexGenerator):
    # multiplier should be a prime number such that multiplicative_order(Mod(multiplier, modulo)) == module - 1
    # for page size of 4KiB and element size of 8 bytes, multiplier should be bigger than 512 so that (almost) all adjacent indices will touch different pages
    def __init__(self, num_accesses, multiplier = 523, modulo = 10**7 + 79):
        super().__init__(num_accesses)
        self.multiplier = multiplier
        self.modulo = modulo
    def sequence_generator(self):
        w = 1
        for i in range(self.num_accesses):
            w = (w * self.multiplier) % self.modulo
            yield w

