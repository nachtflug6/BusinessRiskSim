import pandas as pd

from .module import Module


class Chain:
    def __init__(self, modules: pd.DataFrame, risks: pd.DataFrame, products: pd.DataFrame):
        self.modules = modules
        self.risks = risks
        self.products = products



