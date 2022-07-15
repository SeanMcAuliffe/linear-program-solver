# Linear Program Solver
# author: Sean McAuliffe, V00913346
# date: 07/15/2022

# This LP solver uses the dictionary simplex method.
# It can initialize initially infeasible LPs, and can
# in principle solve LPs of arbitrary size. However,
# due to the object oriented design approach chosen
# early on for ease of development, there is a lot of
# overhead which increases the runtime of large LPs.


import sys
from fractions import Fraction
from variable import DictionaryVariable as Variable, VarType
from equation import Constraint, Objective
from copy import deepcopy


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
    
    # Find leaving variable (minimum c/m coefficient) with
    # indices breaking ties and x < omega < w
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
                challenger = con.basic.name 
                champion = leaving 
                if challenger.startswith('x') and champion.startswith('x'):
                    chal = ''.join(c for c in challenger if c.isdigit())
                    cham = ''.join(c for c in champion if c.isdigit())
                    if chal < cham:
                        leaving = challenger
                    else:
                        pass
                elif challenger.startswith('x') and champion.startswith('w'):
                    leaving = challenger
                elif challenger.startswith('w') and champion.startswith('x'):
                    pass
                else: # challenger is w and champion is w
                    chal = ''.join(c for c in challenger if c.isdigit())
                    cham = ''.join(c for c in champion if c.isdigit())
                    if chal < cham:
                        leaving = challenger
                    else:
                        pass

    return entering, leaving


class SimplexDictionary:
    # TODO: Represent nonbasic variables in objective, constraints using dict, not list
    def __init__(self, objective, constraints, rule):
        self.rule = rule
        self.obj = None
        self.con = []
        self.original_obj = None
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
        self.omega_index = self.highest_index + 1

    def get_auxiliary_lp(self):
        auxiliary_lp = deepcopy(self)
        auxiliary_lp.original_obj = deepcopy(self.obj)
        # Replace objective function with just -omega
        auxiliary_lp.obj.scalar = 0
        for var in auxiliary_lp.obj.nonbasic:
            var.coef = 0
        auxiliary_lp.obj.nonbasic.append(Variable(VarType.optimization, self.omega_index, Fraction(-1, 1)))
        # Add omega to each constraint
        for constraint in auxiliary_lp.con:
            constraint.nonbasic.append(Variable(VarType.optimization, self.omega_index, Fraction(1,1)))
        if not auxiliary_lp.is_feasible():
            leaving = self.least_feasible_constraint()
            entering = f"x_{self.omega_index}"
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

    def pivot(self, entering, leaving):
        for i, c in enumerate(self.con):
            if c.basic.name == leaving:
                # Pivot entering into basis in leaving row
                c.rearrange_in_terms_of(entering)
                done, expression = (i, c)
                break
        # For every other constraint row,
        # substitue in the new defn of 
        # the leaving variable
        for i, c in enumerate(self.con):
            if i != done:
                c.redefine_term(expression)
        # Substitude new defn into objective function
        self.obj.redefine_term(expression)

    def run(self):
        while self.should_continue():
            entering, leaving = self.rule(self.obj, self.con)
            self.pivot(entering, leaving)

    def report(self):
        """ Generates an output string in accordance
        with the project spec. """
        # Format Output
        if not self.is_feasible():
            print("infeasible")
        elif self.is_unbounded():
            print("unbounded")
        elif self.is_optimal():
            print("optimal")
            print(f"{float(self.obj.scalar):.7g}")
            coords = self.coordinates()
            for c in coords:
                print(f"{float(c[1]):.7g}", end=' ')
            print()
        else:
            # This should never happend
            print("infeasible")

    def coordinates(self):
        """ Returns the values of the optimization variables
        of the dictionary in its current state. The values are
        formatted as a list of tuples, with the first element
        representing the variable index, and the second element
        representing the value. """
        coords = []
        x = [(v.basic.index, v.scalar) for v in self.con if v.basic.vartype is VarType.optimization]
        x.sort(key=lambda x: x[0])
        j = 0
        for i in range(self.highest_index):
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
        # Remove omega column
        omega_name = f"x_{self.omega_index}"
        for var in feasible_lp.obj.nonbasic:
            if var.name == omega_name:
                feasible_lp.obj.nonbasic.remove(var)
                break
        for constraint in feasible_lp.con:
            for var in constraint.nonbasic:
                if var.name == omega_name:
                    constraint.nonbasic.remove(var)
                    break
        # Redefine original objective function
        temp_obj = deepcopy(self.original_obj)
        feasible_lp.obj = deepcopy(self.original_obj)
        for term in temp_obj.nonbasic:
            for constraint in feasible_lp.con:
                if constraint.basic.name == term.name:
                    feasible_lp.obj.redefine_term(constraint)
                    break
        return feasible_lp

    def __repr__(self):
        r = f"Feasible: {self.is_feasible()}\n"
        r += f"Optimal: {self.is_optimal()}\n"
        #r += f"Unbounded: {self.is_unbounded()}\n\n"
        r += f"Objective: {self.obj.__repr__()}\n"
        r += "Constraints:\n"
        for c in self.con:
            r += f"{c.__repr__()}\n"
        return r


def main():

    # Read STDIN encoding of LP
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
    input_dictionary = SimplexDictionary(objective, constraints, blands_rule)

    # Solve LP if initial dictionary is feasible
    if input_dictionary.is_feasible():
        input_dictionary.run()
        input_dictionary.report()
    else:
        # Construct and solve the auxiliary LP
        auxiliary_lp = input_dictionary.get_auxiliary_lp()
        auxiliary_lp.run()
        # If auxiliary LP is unbounded, or has nonzero objective value
        # Then original LP is infeasible
        if auxiliary_lp.is_unbounded():
            print("infeasible")
        elif auxiliary_lp.obj.scalar != 0:
            print("infeasible")
        else:
            # Otherwise, convert to an initially feasible dictionary and solve
            feasible_dictionary = auxiliary_lp.convert()
            feasible_dictionary.run()
            feasible_dictionary.report()


if __name__ == "__main__":
    main()
