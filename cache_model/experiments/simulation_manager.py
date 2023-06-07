from pathlib import Path
import multiprocessing as mp

# https://stackoverflow.com/questions/53617425/sharing-a-counter-with-multiprocessing-pool
def init_globals(_counter):
    global counter
    counter = _counter

def process_worker(simulation, num_jobs):
    simulation.simulate()
    with counter.get_lock():
        counter.value += 1
    print(f"Status {counter.value}/{num_jobs} done: {simulation.get_name() finish}")

class SimulationManager:
    def __init__(self, num_processors):
        self.num_processors = num_processors
        self.simulations = []
        self.counter = mp.Value('i', 0)
    def add_simulation(self, design_class, num_lanes, page_size_bytes, workload):
        simulation = design_class(num_lanes, page_size_bytes, workload)
        stats_filename = simulation.stats_filename
        if Path(stats_filename).is_files():
            print(f"warn: Skipping {simulation.get_simulation_name()} as '{stats_filename}' exists.")
            return
        self.simulations.append(simulation)
    def launch(self):
        num_simulations = len(self.simulations)
        jobs = [(simulation, len(self.simulations)) for simulation in self.simulations]
        with multiprocessing.Pool(self.num_processors, initializer=init_globals, initargs=(self.counter,)) as pool:
            pool.starmap(process_worker, self.simulations)
