import pandas as pd
import os
import math

from .product import Product, PreProduct
from .module import Module

from .chain import Chain

class CSVInput:
    def __init__(self, dir):
        self.dir = dir

    def get_chain(self):

        path_product = os.path.join(self.dir, 'product_chart.csv')
        path_chain = os.path.join(self.dir, 'chain_chart.csv')
        path_risks = os.path.join(self.dir, 'risk_chart.csv')

        assert os.path.isfile(path_product)
        assert os.path.isfile(path_chain)
        assert os.path.isfile(path_risks)


        ## Create Product Tree

        product_df = pd.read_csv(path_product, sep=';')
        products = {}

        for idx in product_df.index:
            row = product_df.iloc[idx]
            name = row['product']
            prod = Product(name)
            products[name] = prod

        product_df = product_df.drop('product', axis=1)
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

        chain_df = pd.read_csv(path_chain, sep=';')
        modules = {}

        for idx in chain_df.index:
            row = chain_df.iloc[idx]
            name = row['module']
            mod = Module(name, 1, Product(name))
            modules[name] = mod

        print(modules)

        risk_df = pd.read_csv(path_risks, sep=';')
        print(risk_df)








