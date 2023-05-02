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

        self.input_product_assignment = th.tensor(input_product_assignment, dtype=th.int32).repeat(num_runs, 1, 1).to(
            self.device)
        self.output_product_assignment = th.tensor(output_product_assignment, dtype=th.int32).repeat(num_runs, 1, 1).to(
            self.device)
        self.origin_modules = th.tensor(origin_modules, dtype=th.int32).repeat(num_runs, 1).to(self.device)
        self.max_production_capacity = th.tensor(output_capacity, dtype=th.int32).repeat(num_runs, 1).to(self.device)
        self.input_product_assignment_helper = th.where(self.input_product_assignment == 0, th.iinfo(th.int32).max,
                                                        self.input_product_assignment).to(self.device)

        exit_transport_assignment = np.zeros((num_transport_modules, num_production_modules, num_products))
        entry_transport_assignment = np.zeros((num_transport_modules, num_production_modules, num_products))
        trans_output_capacity = np.zeros(num_transport_modules)

        for i, mod in enumerate(self.transport_modules, 0):
            exit_transport_assignment[i, mod.input_mod_idx, mod.product_idx] = 1
            entry_transport_assignment[i, mod.output_mod_idx, mod.product_idx] = 1
            trans_output_capacity[i] = mod.max_capacity

        self.exit_transport_assignment = th.tensor(exit_transport_assignment, dtype=th.int32).repeat(num_runs, 1, 1,
                                                                                                     1).to(self.device)
        self.entry_transport_assignment = th.tensor(entry_transport_assignment, dtype=th.int32).repeat(num_runs, 1, 1,
                                                                                                       1).to(
            self.device)
        self.trans_output_capacity = th.tensor(trans_output_capacity, dtype=th.int32).repeat(num_runs, 1).to(
            self.device)

    def run(self, t_run, loss_function, no_record=False):

        if no_record:
            inventory_volume = th.zeros(1, self.num_runs, 2, self.num_production_modules,
                                    self.num_production_modules).to(self.device)
            production_volume = th.zeros(1, self.num_runs, self.num_production_modules).to(self.device)
            transport_volume = th.zeros(1, self.num_runs, self.num_transport_modules).to(self.device)
        else:
            inventory_volume = th.zeros(t_run + 1, self.num_runs, 2, self.num_production_modules,
                                    self.num_production_modules).to(self.device)
            production_volume = th.zeros(t_run + 1, self.num_runs, self.num_production_modules).to(self.device)
            transport_volume = th.zeros(t_run + 1, self.num_runs, self.num_transport_modules).to(self.device)

        loss = th.zeros(t_run + 1, self.num_runs).to(self.device)

        for i in range(t_run):
            self.riskgen.step()
            capacities = self.riskgen.get_cap()

            # Production
            if no_record:
                current_production_stock = inventory_volume[0, :, 0]
            else:
                current_production_stock = inventory_volume[i, :, 0]

            prod_capacities = capacities[:, 0:self.num_production_modules]
            real_prod_capacities = self.max_production_capacity * prod_capacities
            real_prod_capacities = real_prod_capacities.to(th.int32)

            real_av_storage = th.divide(current_production_stock, self.input_product_assignment)
            real_available_to_produce = th.where(real_av_storage != real_av_storage,
                                                 th.iinfo(th.int32).max, real_av_storage)
            real_available_to_produce = th.min(real_available_to_produce, axis=2).values

            real_production = th.where(self.origin_modules > 0, real_prod_capacities,
                                       th.minimum(real_available_to_produce, real_prod_capacities))

            if no_record:
                production_volume[0] = real_production
            else:
                production_volume[i] = real_production
            loss[i] = loss_function(self.max_production_capacity[:, -1], real_production[:, -1])

            used_input_stock = self.input_product_assignment * real_production.unsqueeze(2).to(th.int32)
            produced_output_stock = self.output_product_assignment * real_production.unsqueeze(2).to(th.int32)

            if no_record:
                inventory_volume[0, :, 0] -= used_input_stock
                inventory_volume[0, :, 1] += produced_output_stock
            else:
                inventory_volume[i, :, 0] -= used_input_stock
                inventory_volume[i, :, 1] += produced_output_stock

            # Transport

            if no_record:
                current_transport_stock = inventory_volume[0, :, 1]
            else:
                current_transport_stock = inventory_volume[i, :, 1]

            trans_capacities = capacities[:, self.num_production_modules:]
            real_trans_capacities = self.trans_output_capacity * trans_capacities
            real_trans_capacities = real_trans_capacities.to(th.int32)

            real_av_storage = current_transport_stock.repeat(3, 1, 1, 1).swapaxes(0,
                                                                                  1) // self.exit_transport_assignment
            real_av_storage = th.where(real_av_storage == th.inf, 0, real_av_storage)
            real_av_storage = th.where(real_av_storage != real_av_storage, 0, real_av_storage)
            real_av_storage = th.sum(
                th.sum(th.where(real_av_storage != real_av_storage, 0, real_av_storage), axis=2),
                axis=2).to(th.int32)

            real_transport = th.minimum(real_av_storage, real_trans_capacities)

            if no_record:
                transport_volume[0] = real_transport
            else:
                transport_volume[i] = real_transport
            exit_tensor = th.sum(
                self.exit_transport_assignment * real_transport.unsqueeze(2).unsqueeze(2), axis=1)
            entry_tensor = th.sum(
                self.entry_transport_assignment * real_transport.unsqueeze(2).unsqueeze(2), axis=1)

            if no_record:
                inventory_volume[0, :, 1] -= exit_tensor
                inventory_volume[0, :, 0] += entry_tensor
            else:
                inventory_volume[i, :, 1] -= exit_tensor
                inventory_volume[i, :, 0] += entry_tensor
                inventory_volume[i + 1] = inventory_volume[i]

        return inventory_volume, production_volume, production_volume, loss

    def evaluate_risks(self, t_run, loss_function, factor=0.1, mode='p'):

        assert mode in ['p', 'i', 't']

        num_risks = self.riskgen.num_risks
        num_runs = num_risks + 1
        losses_for_risk = th.zeros(num_runs)

        for i in range(num_runs):
            if i > 0:
                match mode:
                    case 'p':
                        self.riskgen.reduce_risk_probability_i(i - 1, factor=factor)
                    case 'i':
                        self.riskgen.reduce_risk_impact_i(i - 1, factor=factor)
                    case 't':
                        self.riskgen.reduce_risk_time_i(i - 1, factor=factor)
            _, _, _, loss = self.run(t_run, loss_function, no_record=True)
            losses_for_risk[i] = th.mean(loss)

        self.riskgen.reset()

        return losses_for_risk
