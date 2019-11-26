# Sequential Ordering Problem challenge


**Autors**: Sebastian, Felix, Ionut

This README provides all necessary information to obtain results from our solution methods (Exact Method, Greedy Method, Particle Swarm Method). Within the respective sections all requirements to use the methods (such as used solvers) and an instruction on how to run the methods is given. 

Find the table of results in the table_of_results.md file within this repository or klick on the link below.

------------------------------------------

**Table of results**: [link](table_of_results.md)

------------------------------------------

**General Information**:

* TODO: project structure... description

* regarding the **helper** files:
  * methods in `helper/parser.py` parse .sol and .sop data to numpy arrays
  * to check whether a solution is valid use methods in `helper/verification.py`;
  * when the verification script is run it checks whether the solution given for the SOP challenge is valid


------------------------------------------

## Exact Method

### preliminaries

* now using gurobi with python interface:
  * using Gurobi 8.1.0 and python 3.7.5 ( both 64 bit versions)
  * to use gurobi with python the python module 'gurobipy' for further in information on how to install it see **Python Packages**
  
### how to use

* the exact method can be found in methods/exact_method.py
* who can it be run?
* what is the output?
 
 
------------------------------------------

## Particle Swarm Method
 
------------------------------------------

## Greedy Method

------------------------------------------

**Python Packages**:

* Exact method

  * gurobipy - (here with Gurobi 8.1.0) go to the installation directory of gurobi and install with `python setup.py install`
  * numpy - (install with: `pip install numpy` )


