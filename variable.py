from enum import Enum

from numpy import var


class VarType(Enum):
    optimization = 1
    slack = 2
    omega = 3


class DictionaryVariable:
    """ Represents a variable in either a constraint or objective function
    of the SimplexDictionary. Stores the variable type (optimization,
    slack, or omega). As well as the index and coeficient. Some boilerplate
    is defined for comparison operations. """

    def __init__(self, vartype, index, coef):
        self.vartype = vartype
        self.index = index
        self.coef = coef
        if vartype is VarType.optimization:
            self.name = f"x_{self.index}"
        elif vartype is VarType.slack:
            self.name = f"w_{self.index}"
        elif vartype is VarType.omega:
            self.name = "\u03A9"

    def __lt__(self, other):
        if type(other) is DictionaryVariable:
            if self.index < other.index:
                return True
            return False
        elif type(other) is int or type(other) is float:
            if self.coef < other:
                return True
            return False
        else:
            raise TypeError(f"'<' operator not defined on types Variable and {type(other)}")

    def __gt__(self, other):
        if type(other) is DictionaryVariable:
            if self.coef > other.coef:
                return True
            return False
        elif type(other) is int or type(other) is float:
            if self.coef > other:
                return True
            return False
        else:
            raise TypeError(f"'>' operator not defined on types Variable and {type(other)}")

    def __eq__(self, other):
        if type(other) is DictionaryVariable:
            if self.name == other.name:
                return True
            else:
                return False
        elif type(other) is str:
            if self.name == other:
                return True
            else:
                return False
        else: 
            raise TypeError(f"Unsupported type for '=', Variable and {type(other)}")

    def __repr__(self):
        return f"{self.name}: {self.coef}"
