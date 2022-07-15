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

Whitespace between coefficients on a line will be ignored. Lines containing only whitespace will be ignored. It is assumed that the number of  coefficients in every constraint function will be the same, and will be equal to the number of  coefficients in the objective function (i.e., there is only one value of `n`). Coefficients may be zero.

Fractional coefficients will be represented as decimal values. It is assumed that the provided decimal expansion of a coefficient represents the full accuracy of the intended real number. These values will be converted to fractional representations internally. 

The example input above therefore would represent the following LP in standard form:

> max. (11/2)x<sub>1</sub> + 4x<sub>2</sub> + 3x<sub>2</sub>  
> s.t. 2x<sub>1</sub> + 3x<sub>2</sub> + 1x<sub>2</sub> <= 5  
> 4x<sub>1</sub> + (9/5)x<sub>2</sub> + 2x<sub>2</sub> <= 11  
> 3x<sub>1</sub> + 4x<sub>2</sub> + 2x<sub>2</sub> <= 8

## Usage
The entrypoint into the program is through `solver.py`. It is expected that an input LP encoding will be provided via `stdin`. For example:

```bash
$ python3 solver.py < input.txt
```
or
```bash
$ cat input.txt | python3 solver.py
```

This program expects to be executed in the `python3` interperter. Any version of the python interpreter version 3.x.x should suffice.

## Output Format

The output from the solver will be printed to `stdout`. A single newline is printed after each message (such that the terminal prompt is located below the output after execution of the solver). The following outputs are possible for example:

```bash
$ infeasible

$ unbounded

$ optimal
  13
  2 0 1

```

## Notes on Implementation

This solver uses the dictionary Simplex Method to solve LPs. An initial dictionary is created from the encoding of an LP provided via `stdin`. If the dictionary is feasible at the origin, then the Simplex Method is running using **Bland's Rule**. In the case that the input LP is not initially feasible after conversion to a dictionary, then an **Auxiliary LP** is created. The auxiliary problem is sovled via the dictionary Simplex Method also, using Bland's rule.

### Cycling

This solver ensures that it will not cycle on any input LP by use of Bland's Rule to determine entering and leaving variables when pivotting.

## Future Improvements

This LP solver uses the dictionary simplex method. It can initialize initially infeasible LPs, and can in principle solve LPs of arbitrary size. However, due to the object oriented design approach chosen early on for ease of development, there is a lot of overhead which increases the runtime of large LPs.

For example, I have manually verified that this solver produces the correct output on each of the `netlib` example inputs including:
- netlib_adlitle.txt
- netlib_afiro.txt
- netlib_sc105.txt
- netlib_share1b.txt

However, on the machines I have had access to, including the UVic linux server, the runtime required to solve these LPs is unreasonably large; on the order of 15 minutes in the case of `netlib_shareb.txt`. Obviously this is unacceptably long. There are some low-hanging fruit improvements which could be made with more time available:

1. The largest-coefficient or largest-increase pivot rule should be implemented and used instead of Bland's rule to reduce the average number of pivots requried to solve an LP. As well as an `is_degenerate()` method which would detect degeneracy and instead use Bland's Rule until the dictionary was no longer degenerate.

2. This implementation overuses lists in order to store the coefficients of variables in constraint equations. As implemented, these lists are scanned sequentially when searching for a variable. The solver should be refactored to expect these coefficients to be stored in dictionaries, which would greatly reduce search times for variables while pivotting.

## Novel Features

No novel features have yet been implemented. If time permits, I will pursue the largest-increase pivot rule and the primal-dual method of resolving initially infeasible LPs. If you are reading this, it has not yet been done.


