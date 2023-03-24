from .module import Module

class Chain:
    def __init__(self, output_modules: list[Module]):
        self.output_modules = output_modules