# Linear Program Solver
# author: Sean McAuliffe, V00913346


import sys
from fractions import Fraction
from variable import DictionaryVariable as Variable, VarType
from equation import Constraint, Objective
#from util import timing
from copy import deepcopy
from time import time

#@timing
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
            # If new ratio is less, it is obv the min
            if ratio < min_ratio:
                min_ratio = ratio
                leaving = con.basic.name
            # If it is equal, need to compare indices of leaving vars
            elif ratio == min_ratio:
                challenger = con.basic.index # new possible leaving var index
                # Previously selected leaving var index
                # TODO: This breaks with omega
                champion = int(''.join(c for c in leaving if c.isdigit())) if leaving != "\u03A9" else challenger+1
                if challenger < champion:
                    leaving = con.basic.name

    return entering, leaving


class SimplexDictionary:
    # TODO: Represent nonbasic variables in objective, constraints using dict, not list
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

    def get_auxiliary_lp(self):
        auxiliary_lp = deepcopy(self)
        # Replace objective function with just -omega
        auxiliary_lp.obj.scalar = 0
        for var in auxiliary_lp.obj.nonbasic:
            var.coef = 0
        auxiliary_lp.obj.nonbasic.append(Variable(VarType.omega, self.highest_index+1, -1))
        # Add omega to each constraint
        for constraint in auxiliary_lp.con:
            constraint.nonbasic.append(Variable(VarType.omega, self.highest_index+1, 1))
        # If not initially feasible, perform initial pivot
        if not auxiliary_lp.is_feasible():
            leaving = self.least_feasible_constraint()
            entering = "\u03A9"
            auxiliary_lp.pivot(entering, leaving)
        return auxiliary_lp

    def least_feasible_constraint(self):
        """ Returns the name of the basic variable in the least 
        feasible constraint. """
        least_feasible = self.con[0]
        for constraint in self.con:
            if constraint.scalar < least_feasible.scalar:
                least_feasible = constraint
        return least_feasible.basic.name

    #@timing
    def is_feasible(self):
        for c in self.con:
            if c.scalar < 0:
                return False
        return True

    #@timing
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

    #@timing
    def is_optimal(self):
        optimal = True
        for var in self.obj.nonbasic:
            if var.coef > 0:
                optimal = False
        return optimal

    #@timing
    def should_continue(self):
        unbounded = self.is_unbounded()
        optimal = self.is_optimal()
        return (not optimal) and (not unbounded)

    def pivot(self, entering, leaving):
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
                c.redefine_term_constraint(expression)
        # Substitude new defn into objective function
        self.obj.redefine_term_objective(expression)

    #@timing
    def run(self):
        while self.should_continue():
            entering, leaving = self.rule(self.obj, self.con)
            #print(f"Pivoting: entering = {entering}, leaving = {leaving}")
            self.pivot(entering, leaving)

    def init_from_feasible_point(self):
        # TODO: Handle initially infeasible dictionaries
        pass

    def report(self):
        # Format Output
        if not self.is_feasible():
            print("infeasible")
        elif self.is_unbounded():
            print("unbounded")
        elif self.is_optimal():
            # TODO: Refactor this output method
            # It errors out on vanberbei_example3.6.txt
            # And others, like optimal_3x3_8.txt
            print("optimal")
            print(f"{float(self.obj.scalar):.7g}")
            coords = self.coordinates()
            for c in coords:
                print(f"{float(c[1]):.7g}", end=' ')
            print()
        else:
            print("undefined")

    def coordinates(self):
        coords = []
        x = [(v.basic.index, v.scalar) for v in self.con if v.basic.vartype is VarType.optimization]
        x.sort(key=lambda x: x[0])
        j = 0
        for i in range(self.highest_index):
            # TODO: Understand why try / except works here
            try:
                if x[j][0] == (i+1):
                    coords.append(x[j])
                    j += 1
                else:
                    coords.append((i+1,0))
            except IndexError:
                coords.append((i+1,0))  
        return coords

    def convert(self):
        feasible_lp = deepcopy(self)
        for var in feasible_lp.obj.nonbasic:
            if var.name == "\u03A9":
                feasible_lp.obj.nonbasic.remove(var)
                break
        for constraint in feasible_lp.con:
            for var in constraint:
                if var.name == "\u03A9":
                    constraint.remove(var)
                    break

    def __repr__(self):
        r = f"Feasible: {self.is_feasible()}\n"
        r += f"Optimal: {self.is_optimal()}\n"
        r += f"Unbounded: {self.is_unbounded()}\n\n"
        r += f"Objective: {self.obj.__repr__()}\n"
        r += "Constraints:\n"
        for c in self.con:
            r += f"{c.__repr__()}\n"
        return r


def main(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        lines = [x for x in lines if len(x.rstrip()) > 0]
    #print("In main")
    #ts = time()
    # Read stdin encoding of LP
    # lines = sys.stdin.readlines()
    # lines = [x for x in lines if len(x.rstrip()) > 0]

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
        #return [["infeasible"], ["initially infeasible"]]
        auxiliary_lp = simplex_dictionary.get_auxiliary_lp()
        #print("Received the auxiliary problem:")
        #print(auxiliary_lp)
        #print("Running the aux LP")
        print("initially infeasible")
        quit()
        sys.stderr.write("Starting auxiliary LP\n")
        auxiliary_lp.run()
        sys.stderr.write("Finished auxiliary LP\n")
        if auxiliary_lp.is_unbounded():
            print("infeasible")
            quit()
        elif auxiliary_lp.obj.scalar != 0:
            print("infeasible")
            quit()
        else:
            print("initially infeasible")
            quit()
            print("Initial LP determined to be feasible at:")
            print([c[1].__str__() for c in auxiliary_lp.coordinates()])
            print(auxiliary_lp)
            quit()
            feasible_dictionary = auxiliary_lp.convert()
    else:
        simplex_dictionary.run()
        #return ["optimal", f"{float(simplex_dictionary.obj.scalar):.7g}", [f"{float(x[1]):.7g}" for x in simplex_dictionary.coordinates()]]
        simplex_dictionary.report()

    # # Format Output
    # if not simplex_dictionary.is_feasible():
    #     print("infeasible")
    # elif simplex_dictionary.is_unbounded():
    #     print("unbounded")
    # elif simplex_dictionary.is_optimal():
    #     # TODO: Refactor this output method
    #     # It errors out on vanberbei_example3.6.txt
    #     print("optimal")
    #     print(f'{float(simplex_dictionary.obj.scalar):.9g}')
    #     x = [(v.basic.index, v.scalar) for v in simplex_dictionary.con if v.basic.vartype is VarType.optimization]
    #     x.sort(key=lambda x: x[0])
    #     v = []
    #     j = 0
    #     for i in range(simplex_dictionary.highest_index):
    #         if x[j][0] == (i+1):
    #             v.append(x[j])
    #             j += 1
    #         else:
    #             v.append((i+1,0))
    #     for e in v:
    #         print(f"{float(e[1]):.9g}", end=' ')
    #     print()
    # else:
    #     print("undefined")
   # te = time()
    #print(f"Overall execution time: {te-ts}")

if __name__ == "__main__":
    main(sys.argv[1])
