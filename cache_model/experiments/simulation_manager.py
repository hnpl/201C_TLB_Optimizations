from pathlib import Path
import multiprocessing as mp

# https://stackoverflow.com/questions/53617425/sharing-a-counter-with-multiprocessing-pool
def init_globals(_counter):
    global counter
    counter = _counter

def process_worker(design_class, num_lanes, page_size_bytes, workload_class, result_directory, num_jobs):
    simulation = design_class(num_lanes, page_size_bytes, workload_class(num_lanes=num_lanes))
    stats_filename = str(Path(result_directory) / Path(simulation.stats_filename))
    simulation.set_stats_filename(stats_filename)
    if Path(stats_filename).is_file():
        print(f"warn: Skipping {simulation.get_simulation_name()} as '{stats_filename}' exists.")
    else:
        simulation.simulate()
    with counter.get_lock():
        counter.value += 1
    print(f"Status {counter.value}/{num_jobs} done: {simulation.get_simulation_name()} finish")

class SimulationManager:
    def __init__(self, num_processors, result_directory):
        self.num_processors = num_processors
        self.simulations = []
        self.counter = mp.Value('i', 0)
        self.result_directory = result_directory
    def add_simulation(self, design_class, num_lanes, page_size_bytes, workload_class):
        self.simulations.append((design_class, num_lanes, page_size_bytes, workload_class))
    def launch(self):
        num_simulations = len(self.simulations)
        jobs = [(*simulation_args, self.result_directory, len(self.simulations)) for simulation_args in self.simulations]
        with mp.Pool(self.num_processors, initializer=init_globals, initargs=(self.counter,)) as pool:
            pool.starmap(process_worker, jobs)
