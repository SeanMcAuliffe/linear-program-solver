# Linear Program Solver
This project provides a linear program solver which utilizes the simplex dictionary method to solve problems with an arbitrary number of optimization variables and constraints.

## Input Format
The following encoding of a linear program in standard form is expected.

```
5.5	4	3
2	3	1	5
4	1.8	2	11
3	4	2	8
```

Where the first line represents the coefficients on the objective function, of the form:

> c<sub>1</sub>x<sub>1</sub> + c<sub>2</sub>x<sub>2</sub> + ... + c<sub>n</sub>x<sub>n</sub>

And each subsequent line represents the coefficients of a constraint function, with the last number in the line representing the constraint bound:

> a<sub>1,1</sub>x<sub>1</sub> + a<sub>1,2</sub>x<sub>2</sub> + ... + a<sub>1,n</sub>x<sub>n</sub> <= b<sub>1</sub>  
> a<sub>2,1</sub>x<sub>1</sub> + a<sub>2,2</sub>x<sub>2</sub> + ... + a<sub>2,n</sub>x<sub>n</sub> <= b<sub>2</sub>  
> ...  
> a<sub>n,1</sub>x<sub>1</sub> + a<sub>n,2</sub>x<sub>2</sub> + ... + a<sub>n,n</sub>x<sub>n</sub> <= b<sub>n</sub> 

Whitespace between coefficients on a line will be ignored. Lines containing only whitespace will be ignored. It is assumed that the number of non-zero coefficients in every constraint function will be the same, and will be equal to the number of non-zero coefficients in the objective function (i.e., there is only one value of `n`).

Fractional coefficients will be represented as decimal values. It is assumed that the provided decimal expansion of a coefficient represents the full accuracy of the intended real number. These values will be converted to fractional representations internally. 

The example input above therefore would represent the following LP in standard form:

> max. (11/2)x<sub>1</sub> + 4x<sub>2</sub> + 3x<sub>2</sub>  
> s.t. 2x<sub>1</sub> + 3x<sub>2</sub> + 1x<sub>2</sub> <= 5  
> 4x<sub>1</sub> + (9/5)x<sub>2</sub> + 2x<sub>2</sub> <= 11  
> 3x<sub>1</sub> + 4x<sub>2</sub> + 2x<sub>2</sub> <= 8
# Usage
The entrypoint into the program is through `solver.py`. It is expected that an input LP encoding will be provided via `stdin`. For example:

```bash
$ cat input.txt | python solver.py
```

The output from the solver will be printed to `stdout`. The following outputs are possible:

```bash
$ infeasible
$ unbounded
$ optimal
  13  # Optimal objective value
  2 0 1  # Corresponding assignment of optimization variables
```