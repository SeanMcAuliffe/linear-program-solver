# Linear Program Solver
# author: Sean McAuliffe, V00 913346

import sys
from enum import Enum
from fractions import Fraction


class VarType(Enum):
    optimization = 1
    slack = 2
    omega = 3


class Variable:

    def __init__(self, vartype, index, value):
        self.vartype = vartype
        self.index = index
        self.value = value

    def __lt__(self, other):
        if type(other) is Variable:
            if self.value < other.value:
                return True
            return False
        elif type(other) is int:
            if self.value < other:
                return True
            return False
        else:
            raise TypeError(f"'<' operator not defined on types Variable and {type(other)}")

    def __repr__(self):
        r = ""
        if self.vartype is VarType.optimization:
            r += "x_"
        else:
            r += "w_"
        r += f"{self.index} = {self.value}"
        return r


class SimplexDictionary:

    def __init__(self, objective, constraints):
        self.value = 0
        self.obj = []
        self.con = []
        # Convert objective coefficients to modelling of obj function
        for i, coef in enumerate(objective):
            self.obj.append(Variable(VarType.optimization, i+1, coef))
        # Convert constraint coefficients to modelling of dict rows
        for i, constraint in enumerate(constraints):
            self.con.append([Variable(VarType.slack, i+1, constraint[-1])])
            self.con[i].extend([Variable(VarType.optimization, j+1, coef*(-1)) for j, coef in enumerate(constraint[:-1])])

    def is_feasible(self):
        for c in self.con:
            if c[0] < 0:
                return False
        return True

    def is_unbounded(self):
        pass

    def pivot(self):
        pass

    def bland_pivot(self):
        pass

    def large_coef_pivot(self):
        pass

    def large_inc_pivot(self):
        pass

    def init_from_feasible_point(self):
        pass

    def __repr__(self):
        r = f"Value: {self.value}\n"
        r += f"Objective: {[x.__repr__() for x in self.obj]}\n"
        r += "Constraints:\n"
        for c in self.con:
            r += f"{[x.__repr__() for x in c]}\n"
        return r


def main():

    # Read stdin encoding of LP
    lines = sys.stdin.readlines()
    lines = [x for x in lines if len(x.rstrip()) > 0]
    print("stdin decoding:")

    # Get the number of constaint functions
    num_constraints = len(lines) - 1

    # Convert objective function to fractional coefficients
    objective = [float(x) for x in lines[0].split()]
    objective = [Fraction.from_float(x).limit_denominator() for x in objective]
    print([x.__str__() for x in objective])

    # Convert constraint coefficients to fractional representation
    constraints = []
    for i in range(1, num_constraints+1):
        constraints.append([float(x) for x in lines[i].split()])
        constraints[i-1] = [Fraction.from_float(x).limit_denominator() for x in constraints[i-1]]
        print([x.__str__() for x in constraints[i-1]])

    # Construct initial dictionary representation of LP
    initial_dictionary = SimplexDictionary(objective, constraints)
    print(f"Initial dictionary:\n{initial_dictionary}")
    print(initial_dictionary.is_feasible())


if __name__ == "__main__":
    main()