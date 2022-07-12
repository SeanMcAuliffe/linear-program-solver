from variable import VarType
from copy import deepcopy

class Objective:
    # TODO: Have this inherit from a parent class, Equation
    
    def __init__(self, nonbasic):
        self.scalar = 0
        self.nonbasic = nonbasic
        #self._sort()

    def redefine_term(self, ex):
        expression = deepcopy(ex)
        elimination = False
        multiplier = 0
        for var in self.nonbasic:
            if var.name == expression.basic.name:
                elimination = True
                multiplier = var.coef
                self.nonbasic.remove(var)
                break
        if not elimination:
            raise Exception("Elimination term not in nonbasic list.")
        self.scalar += expression.scalar*multiplier
        new_terms = [v for v in expression.nonbasic]
        for new in new_terms:
            new.coef *= multiplier
        for new in new_terms:
            found = False
            for v in self.nonbasic:
                if v.name == new.name:
                    found = True
                    v.coef += new.coef
                    break
            if not found:
                self.nonbasic.append(new)
       # self._sort()

    def _sort(self):
        """ Ensure that nonbasic variables are always listed in order of index.
        With optimization variables coming before slack variables always. """
        temp_opt = [v for v in self.nonbasic if v.vartype is VarType.optimization]
        temp_slack = [v for v in self.nonbasic if v.vartype is VarType.slack]
        temp_opt.sort()
        temp_slack.sort()
        temp_opt.extend(temp_slack)
        self.nonbasic = temp_opt

    def __repr__(self):
        r = f"{self.scalar} "
        for nb in self.nonbasic:
            if nb.coef > 0:
                r += f"+ {nb.coef}{nb.name} "
            else:
                r += f"- {abs(nb.coef)}{nb.name} "
        return r


class Constraint:
    # TODO: Have this inherit from a parent class, Equation

    def __init__(self, basic, nonbasic):
        self.scalar = basic.coef
        self.basic = basic
        self.nonbasic = nonbasic
        self.basic.coef = 1
        #self._sort()
    
    def rearrange_in_terms_of(self, name):
        varname = deepcopy(name)
        """ Rearrange the equation so that `variable` is the 
        new dependent variable. """
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
        #self._sort()

    def redefine_term(self, ex):
        expression = deepcopy(ex)
        """ The definition of `variable` is being replaced with
        an `expression` in terms of the other variables in this 
        linear equation. The expression is another constraint object,
        representing the definition of its basic variable. """
        elimination = False
        multiplier = 0
        for var in self.nonbasic:
            if var.name == expression.basic.name:
                elimination = True
                multiplier = var.coef
                self.nonbasic.remove(var)
                break
        if not elimination:
            raise Exception("Elimination term not in nonbasic list.")
        self.scalar += expression.scalar*multiplier
        new_terms = [v for v in expression.nonbasic]
        for new in new_terms:
            new.coef *= multiplier
        for new in new_terms:
            found = False
            for v in self.nonbasic:
                if v.name == new.name:
                    found = True
                    v.coef += new.coef
                    break
            if not found:
                self.nonbasic.append(new)
        #self._sort()

    def _sort(self):
        """ Ensure that nonbasic variables are always listed in order of index.
        With optimization variables coming before slack variables always. """
        temp_opt = [v for v in self.nonbasic if v.vartype is VarType.optimization]
        temp_slack = [v for v in self.nonbasic if v.vartype is VarType.slack]
        temp_opt.sort()
        temp_slack.sort()
        temp_opt.extend(temp_slack)
        self.nonbasic = temp_opt

    def __repr__(self):
        r = f"{self.basic.coef}{self.basic.name} = {self.scalar} "
        for nb in self.nonbasic:
            if nb.coef > 0:
                r += f"+ {nb.coef}{nb.name} "
            else:
                r += f"- {abs(nb.coef)}{nb.name} "
        return r

            