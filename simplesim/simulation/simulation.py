import torch as th
import numpy as np


class Simulation:
    def __init__(self, modules):
        self.modules = modules


    def simulate(self, num_tests: int, num_time_steps, batch_size: int):



        num_batches = np.ceil(num_time_steps / batch_size)

        for i in range(num_tests):
            for j in range(num_batches):
                pass



        # loop tests

        # loop batches

        # generate risk vector

        # loop modules

        #   outputs = module.produce(risk_vector, outputs)
        #
