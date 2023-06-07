from parameters import Parameters
from designs.design_1 import Design1
from designs.design_2 import Design2
from designs.design_3 import Design3
from designs.design_4 import Design4
from experiments.simulation_manager import SimulationManager
from experiments.standard_workloads import (
    StandardPermutatingGatherWorkload,
    StandardGUPSWorkload,
    StandardDGEMMWorkload,
    StandardCFFTS1Workload,
    StandardStreamCopyWorkload,
    StandardStreamAddWorkload,
)

simulation_manager = SimulationManager(num_processors = 120, result_directory = "results")

for workload_class in [
    StandardPermutatingGatherWorkload,
    StandardGUPSWorkload,
    StandardDGEMMWorkload,
    StandardCFFTS1Workload,
    StandardStreamCopyWorkload,
    StandardStreamAddWorkload,
]:
    for design_class in [Design1, Design2, Design3, Design4]:
        for num_lanes in Parameters.num_lanes:
            for page_size_bytes in Parameters.page_size_bytes:
                simulation_manager.add_simulation(
                    design_class = design_class,
                    num_lanes = num_lanes,
                    page_size_bytes = page_size_bytes,
                    workload_class = workload_class
                )

simulation_manager.launch()
