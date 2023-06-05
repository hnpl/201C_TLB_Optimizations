from math import log2

from .device import Device
from .data_cache_entry import DataCacheEntry

# A read-only 0-latency cache model
class DataCache(Device):
    def __init__(self, name, num_entries, associativity, block_size_bytes):
        super().__init__(name)
        self.num_entries = num_entries
        self.associativity = associativity
        self.block_size_bytes = block_size_bytes
        self.num_offset_bits = round(log2(block_size_bytes))
        self.num_index_bits = round(log2(num_entries // associativity))
        self.num_tag_bits = 64 - self.num_offset_bits - self.num_index_bits
        self.cache_memory = [
            [   
                DataCacheEntry(
                    tag = 0, valid = False, access_time = self.tick, block_size_bytes = block_size_bytes
                ) for _ in range(self.associativity)
            ] for __ in range(self.num_entries // self.associativity)
        ]
        self.replacement_policy = "lru"
    def regStats(self):
        self.addStat("numAccesses", 0)
        self.addStat("numMisses", 0)
    def print_cache_memory(self):
        for index in range(2**self.num_index_bits):
            print(f"Index {index}:")
            for entry in self.cache_memory[index]:
                print(str(entry))
    def parse_vaddr(self, vaddr):
        offset_bits = vaddr & ((2 ** self.num_offset_bits) - 1)
        vaddr >>= self.num_offset_bits
        index_bits = 0
        if self.num_index_bits != 0:
            index_bits = vaddr & ((2 ** self.num_index_bits) - 1)
        vaddr >>= self.num_index_bits
        tag_bits = vaddr
        return (tag_bits, index_bits, offset_bits)
    def _find_entry_position(self, vaddr): # find the position of the entry in the cache memory
        entry_position = -1
        vaddr_tag, vaddr_idx, __ = self.parse_vaddr(vaddr)
        for pos, entry in enumerate(self.cache_memory[vaddr_idx]):
            if entry.match(vaddr_tag):
                return pos
        return entry_position
    def _add_new_entry(self, new_entry, vaddr_idx):
        position = -1
        evicted_entry = None
        # first pass: find the first empty entry
        for i in range(self.associativity):
            if not self.cache_memory[vaddr_idx][i].valid:
                position = i
                break
        # second pass: if there's no empty entry, evict some entry according to the replacement policy
        # using LRU
        min_time = 2**64
        min_time_position = -1
        if position == -1:
            min_time = 2**64
            min_time_position = -1
            for i, entry in enumerate(self.cache_memory[vaddr_idx]):
                if min_time > entry.access_time:
                    min_time = entry.access_time
                    min_time_position = i
            assert(min_time_position != -1)
            evicted_entry = self.cache_memory[vaddr_idx][min_time_position]
            position = min_time_position
        self.cache_memory[vaddr_idx][position] = new_entry
        return evicted_entry
    def receive_request_and_send_response(self, vaddr):
        vaddr_tag, vaddr_idx, __ = self.parse_vaddr(vaddr)
        position = self._find_entry_position(vaddr)
        target_entry = None
        self.stats["numAccesses"] += 1
        if position == -1: # cache miss
            #print(self.name, "miss")
            self.stats["numMisses"] += 1
            response = self.send_request_and_receive_response(vaddr)
            if isinstance(response, DataCacheEntry):
                target_entry = response
            elif isinstance(response, int):
                target_entry = DataCacheEntry(
                    tag = vaddr_tag,
                    valid = True,
                    access_time = self.tick,
                    block_size_bytes = 64
                )
            else:
                assert(False and "Should not happen")
            evicted_entry = self._add_new_entry(target_entry, vaddr_idx)
        else: # cache hit
            #print(self.name, "hit")
            self.cache_memory[vaddr_idx][position].access_time = self.tick
            target_entry = self.cache_memory[vaddr_idx][position]
        return target_entry
    def send_request_and_receive_response(self, vaddr):
        assert((len(self.lower_level_devices) == 1) and "DataCache should only have one lower device")
        return self.lower_level_devices[0].receive_request_and_send_response(vaddr)

