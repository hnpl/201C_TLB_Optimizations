from objects.tlb_cache import TLBCache
from objects.memory_backend import MemoryBackend
from constants import *

if __name__ == "__main__":
    # devices
    l1_tlb = TLBCache("L1", num_entries = 2, associativity = 2, page_size_bytes = 4 * oneKiB)
    l2_tlb = TLBCache("L2", num_entries = 4, associativity = 4, page_size_bytes = 4 * oneKiB)
    backend_memory = MemoryBackend("Mem", page_size_bytes = 4 * oneKiB)
    # connections
    ## L1 <-> L2
    l1_tlb.connect_lower_level_device(l2_tlb)
    l2_tlb.connect_higher_level_device(l1_tlb)
    ## L2 <-> mem
    l2_tlb.connect_lower_level_device(backend_memory)
    backend_memory.connect_higher_level_device(l2_tlb)

    # Some action
    for addr in range(0x1200, 0x40000, 0x600):
        l1_tlb.do_tick()
        print(f"Request {addr}; {l1_tlb.parse_vaddr(addr)}")
        translation = l1_tlb.receive_request_and_send_response(addr)
        print(translation)
        print("L1")
        l1_tlb.print_cache_memory()
        print("L2")
        l2_tlb.print_cache_memory()

