from objects.tlb_cache import TLBCache
from objects.memory_backend import MemoryBackend
from objects.address_stream import AddressStreamManager

from constants import *
from pattern_generators.address_generator import *
from pattern_generators.index_generator import *

def stream(n):
    for i in range(n):
        yield i

if __name__ == "__main__":
    num_lanes = 8
    num_accesses = 1000
    num_accesses = (num_accesses + num_lanes - 1) // num_lanes * num_lanes

    # Address generator
    address_generator = AddressGenerator(
        load_index_generator = MultiplicativeGenerator(num_accesses = num_accesses),
        store_index_generator = LinearGenerator(num_accesses = num_accesses),
        num_accesses = num_accesses,
        num_lanes = num_lanes
    )

    # Devices
    address_stream_manager = AddressStreamManager(num_lanes = num_lanes, address_generator = address_generator)
    l1_tlbs = []
    l2_tlbs = []
    for i in range(num_lanes):
        l1_tlbs.append(TLBCache(f"l1_tlb_{i}", num_entries = 32, associativity = 32, page_size_bytes = 4 * oneKiB))
        l2_tlbs.append(TLBCache(f"l2_tlb_{i}", num_entries = 3 * 1024, associativity = 12, page_size_bytes = 4 * oneKiB))
    backend_memory = MemoryBackend("Mem", page_size_bytes = 4 * oneKiB)

    # connections
    ## stream <-> L1
    for i in range(num_lanes):
        # stream <-> L1
        address_stream_manager.streams[i].connect_lower_level_device(l1_tlbs[i])
        l1_tlbs[i].connect_higher_level_device(address_stream_manager.streams[i])
        ## L1 <-> L2
        l1_tlbs[i].connect_lower_level_device(l2_tlbs[i])
        l2_tlbs[i].connect_higher_level_device(l1_tlbs[i])
        ## L2 <-> mem
        l2_tlbs[i].connect_lower_level_device(backend_memory)
        backend_memory.connect_higher_level_device(l2_tlbs[i])

    # start simulation
    address_stream_manager.start_simulating()
    print("final state")
    print("L1[0]")
    l1_tlbs[0].print_cache_memory()
    print("L2[0]")
    l2_tlbs[0].print_cache_memory()
