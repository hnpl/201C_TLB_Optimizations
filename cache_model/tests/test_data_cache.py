import sys
sys.path.append("./")

from objects.data_cache import DataCache
from objects.memory_backend import MemoryBackend

if __name__ == "__main__":
    l1 = DataCache(name = "l1", num_entries = 4, associativity = 2, block_size_bytes = 64)
    memory = MemoryBackend(name = "memory", page_size_bytes = 2**12)
    l1.connect_lower_level_device(memory)
    memory.connect_higher_level_device(l1)
    l1.regStats()
    memory.regStats()
    for vaddr in range(0x1234, 0x10000, 64):
        print("index:", (vaddr >> 6) % 2, "tag:", vaddr >> 7)
        l1.receive_request_and_send_response(vaddr)
        l1.print_cache_memory()
        l1.do_tick()
