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

    def get_risk_assembly(self):
        risk_chart_path = os.path.join(self.dir, 'risk_chart.csv')
        assert os.path.isfile(risk_chart_path)
        risk_df = pd.read_csv(risk_chart_path, sep=';')

        risk_assembly_df = pd.DataFrame()

        print(risk_df)

        for i in range(len(risk_df.index)):
            row = risk_df.iloc[i]
            row = row.where(row == row, 0)
            affected_companies = row['modules'].replace(' ', '').split(',')

            if row['common risk'] == 1:
                row_risk_assembly_df = pd.DataFrame(
                    data={'name': row['name'],
                          'affected_companies': [affected_companies],
                          'probability': [row['probability']],
                          'capacity': [row['probability']],
                          'reduction': [row['capacity reduction']],
                          'delay': [row['delay']],
                          'recover_time': [row['recover time']]})
                risk_assembly_df = pd.concat([risk_assembly_df, row_risk_assembly_df], ignore_index=True)

            else:
                for affected_company in affected_companies:
                    row_risk_assembly_df = pd.DataFrame(
                        data={'name': [row['name'] + ('_' + str(affected_company))],
                              'affected_companies': [[affected_company]],
                              'probability': [row['probability']],
                              'capacity': [row['probability']],
                              'reduction': [row['capacity reduction']],
                              'delay': [row['delay']],
                              'recover_time': [row['recover time']]})

                    risk_assembly_df = pd.concat([risk_assembly_df, row_risk_assembly_df], ignore_index=True)

        return risk_assembly_df

    def get_chain_assembly(self):
        path_module = os.path.join(self.dir, 'module_chart.csv')
        path_chain = os.path.join(self.dir, 'chain_chart.csv')
        path_product = os.path.join(self.dir, 'product_chart.csv')

        assert os.path.isfile(path_module)
        assert os.path.isfile(path_chain)
        assert os.path.isfile(path_product)

        module_df = pd.read_csv(path_module, sep=';', index_col=0)
        chain_df = pd.read_csv(path_chain, sep=';', index_col=0)
        product_df = pd.read_csv(path_product, sep=';', index_col=0)

        chain_assembly_df = pd.DataFrame()

        leveled_modules = []

        for module_name in module_df.index:
            row_module = module_df.loc[module_name]
            row_chain = chain_df.loc[module_name]
            row_product = product_df.loc[row_module['product']]
            row_module = row_module.where(row_module == row_module, 0)
            row_chain = row_chain.where(row_chain == row_chain, 0)
            row_product = row_product.where(row_product == row_product, 0)

            supplies = {}

            for supplier in row_chain.index:
                supplier_flag = row_chain.loc[supplier]
                if supplier_flag == 'x':
                    supplier_product = module_df.loc[supplier]['product']
                    if supplier_product in supplies:
                        supplies[supplier_product].append(supplier)
                    else:
                        supplies[supplier_product] = [supplier]

            products = {}

            for key in row_product.index:
                num_preproducts = row_product.loc[key]
                if num_preproducts > 0:
                    products[key] = num_preproducts

            if not supplies:
                leveled_modules.append(module_name)

            row_chain_assembly_df = pd.DataFrame(
                data={'name': [module_name],
                      'part_capacity': [row_module['part capacity']],
                      'product': [row_module['product']],
                      'preproduct': [products],
                      'suppliers': [supplies],
                      'level': 0,
                      })

            chain_assembly_df = pd.concat([chain_assembly_df, row_chain_assembly_df], ignore_index=True)

        level = 1

        while len(leveled_modules) < len(chain_assembly_df.index):
            current_level_modules = []
            for idx in chain_assembly_df.index:
                row = chain_assembly_df.loc[idx]
                if row['name'] not in leveled_modules:
                    level_flag = True
                    for product in row['suppliers']:
                        product_suppliers = row['suppliers'][product]
                        print(product_suppliers)
                        if not all(product_supplier in leveled_modules for product_supplier in product_suppliers):
                            level_flag = False
                    if level_flag:
                        current_level_modules.append(row['name'])
                        chain_assembly_df.at[idx, 'level'] = level

            leveled_modules += current_level_modules
            level += 1

        return chain_assembly_df
