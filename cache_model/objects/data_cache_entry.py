from math import log2

class DataCacheEntry:
    def __init__(self, tag, valid, access_time, block_size_bytes):
        self.tag = tag
        self.valid = valid
        self.access_time = access_time
        self.block_size = block_size_bytes
    def match(self, tag):
        return self.valid and (self.tag == tag)
    def __str__(self):
        return f"Cache Block: Tag: {self.tag}; Valid: {1 if self.valid else 0}; Time: {self.access_time}"
