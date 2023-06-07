from objects.design import Design
from objects.tlb_cache import TLBCache
from objects.memory_backend import MemoryBackend
from objects.address_stream import AddressStreamManager
from objects.ptw import *
from objects.simulator import Simulator
from objects.address_coalescer import AddressCoalescer

class Design3(Design):
    def __init__(self, num_lanes, page_size_bytes, address_generator, stats_filename):
        super().__init__("design_3", num_lanes, page_size_bytes, address_generator, stats_filename)
    def configure(self):
        # Devices
        address_stream_manager = AddressStreamManager("address_stream_manager", num_lanes = self.num_lanes, address_generator = self.address_generator)
        l1_tlbs = []
        # https://en.wikichip.org/wiki/amd/microarchitectures/zen_4
        for i in range(self.num_lanes):
            l1_tlbs.append(TLBCache(f"l1_tlb_{i}", num_entries = 72, associativity = 72, page_size_bytes = self.page_size_bytes))
        address_coalescer = AddressCoalescer("address_coalescer", page_size_bytes = self.page_size_bytes)
        l2_tlb = TLBCache(f"l2_tlb", num_entries = 3072, associativity = 24, page_size_bytes = self.page_size_bytes)
        pooled_ptws = PooledPTWs2("ptw_pool", page_table_size = self.page_size_bytes)
        backend_memory = MemoryBackend("Memory", page_size_bytes = self.page_size_bytes)

        # connections
        ## stream <-> L1
        for i in range(self.num_lanes):
            # stream <-> L1
            address_stream_manager.streams[i].connect_lower_level_device(l1_tlbs[i])
            l1_tlbs[i].connect_higher_level_device(address_stream_manager.streams[i])
            ## L1 <-> AddressCoalescer
            l1_tlbs[i].connect_lower_level_device(address_coalescer)
            address_coalescer.connect_higher_level_device(l1_tlbs[i])
        # AddressCoalescer <-> L2
        address_coalescer.connect_lower_level_device(l2_tlb)
        l2_tlb.connect_higher_level_device(address_coalescer)
        # L2 <-> PTWs
        l2_tlb.connect_lower_level_device(pooled_ptws)
        pooled_ptws.connect_higher_level_device(l2_tlb)
        ## PTW <-> Mem
        pooled_ptws.connect_lower_level_device(backend_memory)
        backend_memory.connect_higher_level_device(pooled_ptws)
    
        # start simulation
        self.simulator = Simulator(root_object = address_stream_manager, stats_filename=self.stats_filename)
