import pandas as pd
import os
import math

from .product import Product, PreProduct
from .module import Module
from .risk import Risk
from .chain import Chain


class CSVInput:
    def __init__(self, dir):
        self.dir = dir

    def get_chain(self):

        path_product = os.path.join(self.dir, 'product_chart.csv')
        path_chain = os.path.join(self.dir, 'chain_chart.csv')
        path_module = os.path.join(self.dir, 'module_chart.csv')
        path_risk = os.path.join(self.dir, 'risk_chart.csv')

        assert os.path.isfile(path_product)
        assert os.path.isfile(path_chain)
        assert os.path.isfile(path_module)
        assert os.path.isfile(path_risk)

        ## Create Product Tree

        product_df = pd.read_csv(path_product, sep=';', index_col=0)
        products = {}

        for risk_name in product_df.index:
            # row = product_df.loc[product_name]
            prod = Product(risk_name)
            products[risk_name] = prod

        product_df = product_df.where(product_df == product_df, 0.0)

        for i, key1 in enumerate(product_df, 0):
            prod = products[key1]
            row = product_df.iloc[i]
            for j, key2 in enumerate(product_df, 0):
                num_preprod = row[key2]
                if num_preprod > 0:
                    preprod = PreProduct(products[key2], num_preprod)
                    prod.add_preproduct(preprod)

        ## Create Module Tree

        chain_df = pd.read_csv(path_chain, sep=';', index_col=0)
        module_df = pd.read_csv(path_module, sep=';', index_col=0)

        modules = {}

        for module_name in module_df.index:
            row = module_df.loc[module_name]
            risk_name = row['product']
            mod = Module(module_name, products[risk_name])
            modules[module_name] = mod

        for module_name in modules:
            row = chain_df.loc[module_name]
            for supplier in row.index:
                # if row[supplier] == row[supplier]:
                if row[supplier] == 'x':
                    modules[module_name].add_supplier(modules[supplier])

        ## Add Risks

        risk_df = pd.read_csv(path_risk, sep=';', index_col=0)

        for risk_name in risk_df.index:
            row = risk_df.loc[risk_name]
            affected_companies = row['modules'].replace(' ', '').split(',')

            for affected_company in affected_companies:
                modules[affected_company].add_risk(
                    Risk(risk_name, probability=row['probability'], capacity_reduction=row['capacity reduction'],
                         recover_time=row['recover time']))

        chain = Chain(modules)

        print('success', chain.modules)
