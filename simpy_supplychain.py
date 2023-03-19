import random
import numpy as np
import simpy as sp
import matplotlib.pyplot as plt


# RANDOM_SEED = 42
# PT_MEAN = 10.0         # Avg. processing time in minutes
# PT_SIGMA = 2.0         # Sigma of processing time
# MTTF = 300.0           # Mean time to failure in minutes
# BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
# REPAIR_TIME = 30.0     # Time it takes to repair a machine in minutes
# JOB_DURATION = 30.0    # Duration of other jobs in minutes
# NUM_MACHINES = 10      # Number of machines in the machine shop
# WEEKS = 4              # Simulation time in weeks
# SIM_TIME = WEEKS * 7 * 24  # Simulation time in hours


# def time_per_part():
#     """Return actual processing time for a concrete part."""
#     return random.normalvariate(PT_MEAN, PT_SIGMA)
#
#
# def time_to_failure():
#     """Return time until next failure for a machine."""
#     return random.expovariate(BREAK_MEAN)


class Risk(object):
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


def get_risk_capacities(risks):
    if type(risks) is list:
        capacity = 1
        for risk in risks:
            risk_capacity = get_risk_capacities(risk)
            if risk_capacity < capacity:
                capacity = risk_capacity

    elif type(risks) is tuple:
        capacity = 0
        for risk in risks:
            capacity += get_risk_capacities(risk)
        capacity /= len(risks)

    else:
        capacity = risks.evaluate()

    return capacity


class Company(object):
    def __init__(self, name, risks, parts_step=1000, input_warehouse_size=10, output_warehouse_size=10):
        #self.env = env
        self.name = name
        self.risks = risks
        self.parts_step = parts_step
        self.input_warehouse_size = input_warehouse_size
        self.output_warehouse_size = output_warehouse_size
        self.input_warehouse_stock = 0
        self.input_warehouse_stock = 0
        self.risks = risks
        self.capacity = 1
        self.capacities = []

    def produce(self):

        current_capacity = get_risk_capacities(self.risks)
        self.capacities.append(current_capacity)

        output_stock = self.parts_step * current_capacity

        return output_stock

    def disrupt_production(self):
        pass


risk_list = [Risk('aaa', probability=0.2, recover_time=3, gradual_recover=True),
             Risk('aaa', probability=0.1, recover_time=10, gradual_recover=True),
             Risk('aaa', probability=0.05, recover_time=100, gradual_recover=True),
             (Risk('aaa', probability=0.1, recover_time=10), Risk('aaa', probability=0.1, recover_time=10),
              Risk('aaa', probability=0.1, recover_time=10)),
             Risk('aaa', probability=0.01, recover_time=100, gradual_recover=True),
             Risk('aaa', probability=0.001, recover_time=1000, gradual_recover=True),
             Risk('aaa', probability=0.1, recover_time=1)
             ]
#
# comp = Company('comp', risk_list)
#
# for i in range(100000):
#     comp.produce()
#
# plt.plot(comp.capacities)
# plt.show()




# class Machine(object):
#     """A machine produces parts and my get broken every now and then.
#
#     If it breaks, it requests a *repairman* and continues the production
#     after the it is repaired.
#
#     A machine has a *name* and a numberof *parts_made* thus far.
#
#     """
#     def __init__(self, env, name, repairman):
#         self.env = env
#         self.name = name
#         self.parts_made = 0
#         self.broken = False

#         # Start "working" and "break_machine" processes for this machine.
#         self.process = env.process(self.working(repairman))
#         env.process(self.break_machine())
#
#     def working(self, repairman):
#         """Produce parts as long as the simulation runs.
#
#         While making a part, the machine may break multiple times.
#         Request a repairman when this happens.
#
#         """
#         while True:
#             # Start making a new part
#             done_in = time_per_part()
#             while done_in:
#                 try:
#                     # Working on the part
#                     start = self.env.now
#                     yield self.env.timeout(done_in)
#                     done_in = 0  # Set to 0 to exit while loop.
#
#                 except sp.Interrupt:
#                     self.broken = True
#                     done_in -= self.env.now - start  # How much time left?
#
#                     # Request a repairman. This will preempt its "other_job".
#                     with repairman.request(priority=1) as req:
#                         yield req
#                         yield self.env.timeout(REPAIR_TIME)
#
#                     self.broken = False
#
#             # Part is done.
#             self.parts_made += 1
#
#     def break_machine(self):
#         """Break the machine every now and then."""
#         while True:
#             yield self.env.timeout(time_to_failure())
#             if not self.broken:
#                 # Only break the machine if it is currently working.
#                 self.process.interrupt()
#
#
# def other_jobs(env, repairman):
#     """The repairman's other (unimportant) job."""
#     while True:
#         # Start a new job
#         done_in = JOB_DURATION
#         while done_in:
#             # Retry the job until it is done.
#             # It's priority is lower than that of machine repairs.
#             with repairman.request(priority=2) as req:
#                 yield req
#                 try:
#                     start = env.now
#                     yield env.timeout(done_in)
#                     done_in = 0
#                 except sp.Interrupt:
#                     done_in -= env.now - start
#
#
# # Setup and start the simulation
# print('Machine shop')
# random.seed(RANDOM_SEED)  # This helps reproducing the results
#
# # Create an environment and start the setup process
# env = sp.Environment()
# repairman = sp.PreemptiveResource(env, capacity=1)
# machines = [Machine(env, 'Machine %d' % i, repairman)
#             for i in range(NUM_MACHINES)]
# env.process(other_jobs(env, repairman))
#
# # Execute!
# env.run(until=SIM_TIME)
#
# # Analyis/results
# print('Machine shop results after %s weeks' % WEEKS)
# for machine in machines:
#     print('%s made %d parts.' % (machine.name, machine.parts_made))
