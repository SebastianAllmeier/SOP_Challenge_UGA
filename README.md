# SOP Challenge UGA SF

SOP Challenge; Sebastian, Felix, Ionut

**Information**:

* regarding the **project files**:
  * methods in helper/parser.py parse .sol and .sop data to numpy arrays
  * to check whether a solution is valid use methods in helper/verification.py;
  * when the verification script is run it checks whether the solution given for the SOP challenge is valid

## Exact Method:

* (**old**) regarding the python **MIP Solver**:
  * for an introduction and examples for the mip solver (MIP python package) look into Data/python-mip.pdf
  * especially look at the traveling salesman problem, since the problem is kind of similar to the SOP problem
  
* (**new**) now using gurobi with python interface:
  * using Gurobi 8.1.0 and python 3.7.5 ( both 64 bit versions)
 
  
 

**Python Packages**:

* MIP python package (install with: `pip install mip` ) based on coin or
* numpy (install with: `pip install numpy` )
