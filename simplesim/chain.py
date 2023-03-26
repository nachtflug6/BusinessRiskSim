from .module import Module

class Chain:
    def __init__(self, modules: dict, risks={}):
        self.modules = modules