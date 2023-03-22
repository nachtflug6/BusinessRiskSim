import numpy as np

class Risk:
    def __init__(self, name, probability=0.5, capacity_multiplier=0.5, recover_time=100, gradual_recover=False):
        self.name = name
        self.probability = probability
        self.capacity_multiplier = capacity_multiplier
        self.current_capacity = 1
        self.active = False
        self.remaining_recover_time = 0
        self.recover_time = recover_time
        self.gradual_recover = gradual_recover
        self.current_capacities = []

    def evaluate(self):

        if self.active:
            self.remaining_recover_time -= 1
            if self.remaining_recover_time <= 0:
                self.active = False
                self.current_capacity = 1
            elif self.gradual_recover:
                self.current_capacity += (1 - self.capacity_multiplier) / self.recover_time

        elif np.random.uniform(0, 1) < self.probability:
            self.active = True
            self.current_capacity = self.current_capacity * self.capacity_multiplier
            self.remaining_recover_time = self.recover_time

        self.current_capacities.append(self.current_capacities)

        return self.current_capacity