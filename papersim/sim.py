import torch as th
import numpy as np

from .modules.sim_modules import *
from .modules.risk_generator import RiskGen


class SupplyChain:
    def __init__(self):
        pass


class GoodFlowSim:

    def __init__(self, production_modules, transport_modules, risks, num_products, num_runs=10, device='cpu'):
        self.production_modules = production_modules
        self.transport_modules = transport_modules
        self.risks = risks
        self.num_runs = num_runs
        self.device = device
        self.num_products = num_products

        num_production_modules = len(production_modules)
        num_transport_modules = len(transport_modules)
        num_total_modules = num_transport_modules + num_production_modules

        self.num_production_modules = num_production_modules
        self.num_transport_modules = num_transport_modules
        self.num_total_modules = num_total_modules
        self.inventory_shape = (2, num_production_modules, num_transport_modules)
        self.riskgen = RiskGen(self.risks, self.num_total_modules, num_runs, device=self.device)

        input_product_assignment = np.zeros((num_production_modules, num_products))
        output_product_assignment = np.zeros_like(input_product_assignment)
        output_capacity = np.zeros(num_production_modules)
        origin_modules = np.zeros(num_production_modules)

        for i, mod in enumerate(self.production_modules, 0):
            input_product_assignment[i] = mod.product_vec
            output_product_assignment[i, mod.product_idx] = 1
            output_capacity[i] = mod.max_capacity
            if th.sum(mod.product_vec) <= 0:
                origin_modules[i] = 1

        self.input_product_assignment = th.tensor(input_product_assignment, dtype=th.int32).repeat(num_runs, 1, 1)
        self.output_product_assignment = th.tensor(output_product_assignment, dtype=th.int32).repeat(num_runs, 1, 1)
        self.origin_modules = th.tensor(origin_modules, dtype=th.int32).repeat(num_runs, 1)
        self.output_capacity = th.tensor(output_capacity, dtype=th.int32).repeat(num_runs, 1)
        self.input_product_assignment_helper = th.where(self.input_product_assignment == 0, th.iinfo(th.int32).max,
                                                        self.input_product_assignment)

        substract_tensor = np.zeros((num_transport_modules, num_production_modules, num_products))
        add_tensor = np.zeros((num_transport_modules, num_production_modules, num_products))
        trans_output_capacity = np.zeros(num_transport_modules)

        for i, mod in enumerate(self.transport_modules, 0):
            substract_tensor[i, mod.input_mod_idx, mod.product_idx] = 1
            add_tensor[i, mod.output_mod_idx, mod.product_idx] = 1
            trans_output_capacity[i] = mod.max_capacity

        self.subtract_tensor = th.tensor(substract_tensor, dtype=th.int32).repeat(num_runs, 1, 1, 1)
        self.add_tensor = th.tensor(add_tensor, dtype=th.int32).repeat(num_runs, 1, 1, 1)
        self.trans_output_capacity = trans_output_capacity

    def run(self, t_run, loss_function):

        inventory_volume = th.zeros(t_run + 1, self.num_runs, 2, self.num_production_modules,
                                    self.num_production_modules).to(self.device)
        production_volume = th.zeros(t_run + 1, self.num_runs, self.num_production_modules).to(self.device)
        # transport_volume = th.zeros(t_run + 1, self.num_runs, self.num_transport_modules).to(self.device)
        loss = th.zeros(t_run + 1, self.num_runs).to(self.device)

        for i in range(t_run):
            self.riskgen.step()
            capacities = self.riskgen.get_cap()
            prod_capacities = capacities[:, 0:self.num_production_modules]
            trans_capacities = capacities[:, self.num_production_modules:]

            available_produce = th.min(th.where(self.input_product_assignment > 0,
                                                inventory_volume[i, :, 0] // self.input_product_assignment_helper,
                                                th.iinfo(th.int32).max), axis=2).values.to(th.int32)
            current_capacity = th.floor(prod_capacities * self.output_capacity).to(th.int32)
            current_production = th.floor(th.where(self.origin_modules > 0, current_capacity,
                                                   th.where(current_capacity > available_produce, available_produce,
                                                            current_capacity))).to(th.int32)

            real_production = current_production.unsqueeze(1).repeat(1, self.num_production_modules,
                                                                     1) * self.output_product_assignment

            production_volume[i] = th.sum(real_production, axis=2)

            inventory_volume[i, :, 0] -= self.input_product_assignment * production_volume[i].repeat(4, 1, 1).swapaxes(0, 1)
            inventory_volume[i, :, 1] += real_production

            real_transportation_subtract = (trans_capacities * self.trans_output_capacity).to(th.int32)
            real_transportation_subtract = th.sum(
                self.subtract_tensor * real_transportation_subtract.repeat(self.num_production_modules,
                                                                           self.num_products, 1,
                                                                           1).swapaxes(0, 2).swapaxes(1, 3), axis=1)

            balance = inventory_volume[i, :, 1] - real_transportation_subtract
            balance = th.where(balance < 0, 0, balance)
            real_transportation_subtract = inventory_volume[i, :, 1] - balance
            real_transportation_volume = th.sum(real_transportation_subtract, axis=2)[:, :-1]


            real_transportation_add = th.sum(
                self.add_tensor * real_transportation_volume.repeat(self.num_production_modules, self.num_products, 1,
                                                                    1).swapaxes(0, 2).swapaxes(1, 3), axis=1)

            inventory_volume[i, :, 0] = inventory_volume[i, :, 0] + real_transportation_add
            inventory_volume[i, :, 1] = inventory_volume[i, :, 1] - real_transportation_subtract

            loss[i] = loss_function(prod_capacities[:, -1], current_production[:, -1])

            inventory_volume[i + 1] = inventory_volume[i]

        return inventory_volume, production_volume, loss

    #
    #
    #         for mod in self.production_modules:
    #             mod.current_capacity = self.riskgen.get_cap_i(mod.idx)
    #             inventory, production = mod.process(inventory_volume[k, i], production_volume[k, i], self.device)
    #             inventory_volume[k, i] = inventory
    #             production_volume[k, i] = production
    #
    #         for mod in self.transport_modules:
    #             mod.current_capacity = self.riskgen.get_cap_i(mod.idx)
    #             inventory, transport = mod.process(inventory_volume[k, i], transport_volume[k, i], self.device)
    #             inventory_volume[k, i] = inventory
    #             transport_volume[k, i] = transport
    #
    #         loss[k, i] = loss_function(self.production_modules[-1].max_capacity, production_volume[k, i, 0, -1])
    #
    #         inventory_volume[k, i + 1] = inventory_volume[k, i]
    #
    #     return inventory_volume[:, :-1], production_volume[:, :-1], transport_volume[:, :-1], loss[:, :-1]
    #
    # def evaluate_risks(self, num_run, t_run, loss_function, factor=0.1):
    #
    #     num_risks = self.riskgen.num_risks
    #     num_runs = num_risks + 1
    #     losses_for_risk = th.zeros(num_runs)
    #
    #     for i in range(num_runs):
    #         print(i, '/', num_runs)
    #         if i > 0:
    #             self.riskgen.reduce_risk_i(i, factor=factor)
    #         _, _, _, loss = self.run(num_run, t_run, loss_function)
    #         losses_for_risk[i] = th.sum(loss)
    #
    #     return losses_for_risk
