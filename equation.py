from variable import VarType
from copy import deepcopy
from util import timer


class Equation:
    """ Represents a constraint or objective function of
    the SimplexDictionary. Stores the scalar, nonbasic
    variables, and provides a method for redefining terms
    within the equation in terms of another. """

    def __init__(self, nonbasic):
        self.scalar = 0
        self.nonbasic = nonbasic
        self._sort()

    def redefine_term(self, expression):
        """ Redefine the equation in terms of another expression
        (another constraint equation). """
        multiplier = 0
        temp = []
        for var in self.nonbasic:
            if var.name == expression.basic.name:
                multiplier = var.coef
                self.nonbasic.remove(var)
                break
        self.scalar += expression.scalar*multiplier
        for new in expression.nonbasic:
            found = False
            for v in self.nonbasic:
                if v.name == new.name:
                    found = True
                    v.coef += new.coef*multiplier
                    break
            if not found:
                copy_variable = deepcopy(new)
                copy_variable.coef *= multiplier
                temp.append(copy_variable)
        self.nonbasic.extend(temp)
        self._sort()

    def _sort(self):
        """ Ensure that nonbasic variables are always listed in order of index.
        With optimization variables coming before slack variables always. """
        temp_opt = [v for v in self.nonbasic if v.vartype is VarType.optimization]
        temp_slack = [v for v in self.nonbasic if v.vartype is VarType.slack]
        temp_opt.sort()
        temp_slack.sort()
        temp_opt.extend(temp_slack)
        self.nonbasic = temp_opt


class Objective(Equation):

    def __init__(self, nonbasic):
        super().__init__(nonbasic)

    def __repr__(self):
        r = f"{self.scalar} "
        for nb in self.nonbasic:
            if nb.coef > 0:
                r += f"+ {nb.coef}{nb.name} "
            else:
                r += f"- {abs(nb.coef)}{nb.name} "
        return r


class Constraint(Equation):
    """ Extends the Equation class to include a basic variable.
    Provides a method for rearranging the constraint equation;
    making one of its nonbasic variables the new dependent variable. """

    def __init__(self, basic, nonbasic):
        super().__init__(nonbasic)
        self.scalar = basic.coef
        self.basic = basic
        self.basic.coef = 1
        self._sort()
    
    def rearrange_in_terms_of(self, varname):
        """ Rearrange the equation so that variables represented
        by varname is the new dependent variable. """
        temp = self.basic
        for var in self.nonbasic:
            if var.name == varname:
                self.basic = var
                self.nonbasic.remove(self.basic)
                self.basic.coef *= -1
                break
        temp.coef *= -1
        self.nonbasic.append(temp)
        divisor = self.basic.coef
        self.basic.coef = 1
        for var in self.nonbasic:
            var.coef /= divisor
        self.scalar /= divisor
        self._sort()

    def __repr__(self):
        r = f"{self.basic.coef}{self.basic.name} = {self.scalar} "
        for nb in self.nonbasic:
            if nb.coef > 0:
                r += f"+ {nb.coef}{nb.name} "
            else:
                r += f"- {abs(nb.coef)}{nb.name} "
        return r
