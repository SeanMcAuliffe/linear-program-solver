# Linear Program Solver
# author: Sean McAuliffe, V00913346


import sys
from fractions import Fraction
from tkinter import simpledialog
from variable import DictionaryVariable as Variable, VarType
from equation import Constraint, Objective


def blands_rule(objective, constraints):
    """ Returns the name of the chosen entering and
    leaving variables, chosen using Blands Rule. """

    # Find entering variable (first pos coefficient)
    entering_index = None
    for i, var in enumerate(objective.nonbasic):
        if var.coef > 0:
            entering = var.name
            entering_index = i
            break
    
    # Find leaving variable (minimum c/m coefficient)
    min_ratio = None
    for con in constraints:
        if con.nonbasic[entering_index].coef < 0:
            ratio = abs(con.scalar / con.nonbasic[entering_index].coef)
            if min_ratio is None:
                min_ratio = ratio
                leaving = con.basic.name
            # TODO what happens when there is a tie, need to track
            # index of leaving varialbe which leads to each ratio, and choose
            # the minimum index
            if ratio < min_ratio:
                min_ratio = ratio
                leaving = con.basic.name

    return entering, leaving


class SimplexDictionary:

    def __init__(self, objective, constraints, rule):
        self.rule = rule
        self.obj = None
        self.con = []
        # Convert objective coefficients to modelling of obj function
        temp = []
        for i, coef in enumerate(objective):
            temp.append(Variable(VarType.optimization, i+1, coef))
            self.obj = Objective(temp)
        # Convert constraint coefficients to modelling of dict rows
        for i, constraint in enumerate(constraints):
            temp = []
            temp.append(Variable(VarType.slack, i+1, constraint[-1]))
            temp.extend([Variable(VarType.optimization, j+1, coef*(-1)) for j, coef in enumerate(constraint[:-1])])
            self.con.append(Constraint(temp[0], temp[1:]))
        self.highest_index = self.obj.nonbasic[-1].index

    def is_feasible(self):
        for c in self.con:
            if c.scalar < 0:
                return False
        return True

    def is_unbounded(self):
        for i, objvar in enumerate(self.obj.nonbasic):
            if objvar.coef > 0:
                all_pos = True
                for con in self.con:
                    if con.nonbasic[i].coef < 0:
                        all_pos = False
                        break
                if all_pos:
                    return True
        return False

    def is_optimal(self):
        optimal = True
        for var in self.obj.nonbasic:
            if var.coef > 0:
                optimal = False
        return optimal

    def should_continue(self):
        unbounded = self.is_unbounded()
        optimal = self.is_optimal()
        return (not optimal) and (not unbounded)

    def run(self):
        iteration = 0
        while self.should_continue():
            print(f"Iteration: {iteration}")
            iteration += 1 
            entering, leaving = self.rule(self.obj, self.con)
            for i, c in enumerate(self.con):
                if c.basic.name == leaving:
                    # Pivot entering into basis in leaving row
                    c.rearrange_in_terms_of(entering)
                    done, expression = (i, c)
                    break
            # For every other constraint row, substitue in the new defn of 
            # the leaving variable
            for i, c in enumerate(self.con):
                if i != done:
                    c.redefine_term(expression)
            # Substitude new defn into objective function
            self.obj.redefine_term(expression)
            #print(self)


    def init_from_feasible_point(self):
        # TODO: Handle initially infeasible dictionaries
        pass

    def __repr__(self):
        r = f"Feasible: {self.is_feasible()}\n"
        r += f"Optimal: {self.is_optimal()}\n"
        r += f"Unbounded: {self.is_unbounded()}\n\n"
        r += f"Objective: {self.obj.__repr__()}\n"
        r += "Constraints:\n"
        for c in self.con:
            r += f"{c.__repr__()}\n"
        return r


def main():

    # Read stdin encoding of LP
    lines = sys.stdin.readlines()
    lines = [x for x in lines if len(x.rstrip()) > 0]

    # Get the number of constaint functions
    num_constraints = len(lines) - 1

    # Convert objective function to fractional coefficients
    objective = [float(x) for x in lines[0].split()]
    objective = [Fraction.from_float(x).limit_denominator() for x in objective]

    # Convert constraint coefficients to fractional representation
    constraints = []
    for i in range(1, num_constraints+1):
        constraints.append([float(x) for x in lines[i].split()])
        constraints[i-1] = [Fraction.from_float(x).limit_denominator() for x in constraints[i-1]]

    # Construct initial dictionary representation of LP
    simplex_dictionary = SimplexDictionary(objective, constraints, blands_rule)
    if not simplex_dictionary.is_feasible():
        print("can't handle this yet")
        quit()
    simplex_dictionary.run()

    # Format Output
    if not simplex_dictionary.is_feasible():
        print("infeasible")
    elif simplex_dictionary.is_unbounded():
        print("unbounded")
    elif simplex_dictionary.is_optimal():
        print("optimal")
        print(f'{float(simplex_dictionary.obj.scalar):.9g}')
        x = [(v.basic.index, v.scalar) for v in simplex_dictionary.con if v.basic.vartype is VarType.optimization]
        x.sort(key=lambda x: x[0])
        v = []
        j = 0
        for i in range(simplex_dictionary.highest_index):
            if x[j][0] == (i+1):
                v.append(x[j])
                j += 1
            else:
                v.append((i+1,0))
        for e in v:
            print(f"{float(e[1]):.9g}", end=' ')
        print()
    else:
        print("undefined")


if __name__ == "__main__":
    main()