from objects.tlb_cache import TLBCache
from objects.memory_backend import MemoryBackend
from objects.address_stream import AddressStreamManager

from constants import *
from generators import *

def stream(n):
    for i in range(n):
        yield i

if __name__ == "__main__":
    # Address generator
    #address_generator = stream_generator(20)
    address_generator = permutation_generator()

    # Devices
    num_lanes = 8
    address_stream_manager = AddressStreamManager(num_lanes = num_lanes, address_generator = address_generator)
    l1_tlbs = []
    l2_tlbs = []
    for i in range(num_lanes):
        l1_tlbs.append(TLBCache(f"L1 {i}", num_entries = 2, associativity = 2, page_size_bytes = 4 * oneKiB))
        l2_tlbs.append(TLBCache(f"L2 {i}", num_entries = 4, associativity = 4, page_size_bytes = 4 * oneKiB))
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
