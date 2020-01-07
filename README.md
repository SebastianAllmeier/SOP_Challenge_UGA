# Sequential Ordering Problem challenge


**Autors**: Sebastian, Felix, Ionut

This README provides all necessary information to obtain results from our solution methods (Exact Method, Greedy Method, Beam Search Method, Particle Swarm Method). Within the respective sections all requirements to use the methods (such as used solvers) and an instruction on how to run the methods is given. Solutions for the methods can be retrieved in the their respective .sol files. The location of these files is given within the decription of the methods.

------------------------------------------

[**Table of results**](table_of_results.md)

[**Report**](Documentation/Report_Ionut_Felix_Sebastian.pdf)

[**Presentation**](Documentation/slides/presentation.pdf)

------------------------------------------

**General Information**:

* regarding the **helper** files:
  * methods in `helper/parser.py` parse .sol and .sop data to numpy arrays
  * to check whether a solution is valid use methods in `helper/verification.py`;
  * when the verification script is run it checks whether the solution given for the SOP challenge is valid
  
------------------------------------------

## Exact Method

### Requirements

* using gurobi with python interface:
  * using Gurobi 8.1.0 and python 3.7.5 ( both 64 bit versions)
  * to use gurobi with python the python module 'gurobipy' is required / further information on how to install it see **Python Packages**
  
### How to use the method & where to find files

* The exact method can be found in `methods/exact_method.py`.
* To run the exact method run the forementioned file.
* The file `parser.py` includes a list of files which will be parsed looking like `names = ['ESC07', 'ESC11', 'ESC12', 'ESC25', ...              'ry48p.4']`. This array specifies the instances for which the exact method will be used if `exact_method.py` is run. 
* The method saves .sol files in the `methods/solutions_exact_method` folder and more detailed data in the `methods/data_exact_method` folder.
  * The solution folder contains .sol files which have the same formatting as the .sol files given to us in the beginning of the lecture. If no solution was found the file is empty.
  * The data files include the solution, the value of the solution, the runtime of the optimizer, the stopping criterion, the gap (calculated by Gurobi abs(Objbound - ObjVal)/abs(ObjVal)) and the lower bound (refered to as objbound).
 
------------------------------------------

## Discrete Particle Swarm Method (DPSO)

### How to use the method & where to find files

* The DPSO method can be found in `methods/particleSwarmOpt_method.py` on branch first_problem_impl. [Click here to go there](https://github.com/sebs08/SOP_Challenge_UGA/tree/first_problem_impl/methods)
* The file `parser.py` includes a list of files which will be parsed looking like `names = ['ESC07', 'ESC11', 'ESC12', 'ESC25', ...              'ry48p.4']`. This array specifies the instances for which the exact method will be used if `particleSwarmOpt_method.py` is run. 
* The method saves .sol files in the [`methods/solutions_dpso`](https://github.com/sebs08/SOP_Challenge_UGA/tree/first_problem_impl/methods/solutions_dpso) folder and it uses detailed data in the `methods/data_exact_method` folder.
  * The solution folder contains .sol files which contain the following information, one per line:
    * size - the size of the problem
    * file - the name of the file (it's used in the model for verbosing)
    * best cost - the cost of the best solution in the swarm
    * best solution - the solution found so far
    * elapsed - time elapsed for the computation
------------------------------------------

## Greedy Method

### How to use the method & where to find files

* The greedy method can be found in `methods/greedy_method.py`.
* To run the greedy method run the forementioned file.
* The file `parser.py` includes a list of files which will be parsed looking like `names = ['ESC07', 'ESC11', 'ESC12', 'ESC25', ...              'ry48p.4']`. This array specifies the instances for which the exact method will be used if `greedy_method.py` is run. 
* The method saves .sol files in the `methods/solutions_greedy_method` folder.
  * The solution folder contains .sol files which have the same formatting as the .sol files given to us in the beginning of the lecture.
------------------------------------------

## Beam Search Method

### How to use the method & where to find files

* The beam search method can be found in `methods/beam_search_method.py`.
* To run the beam search method run the forementioned file.
* The file `parser.py` includes a list of files which will be parsed looking like `names = ['ESC07', 'ESC11', 'ESC12', 'ESC25', ...              'ry48p.4']`. This array specifies the instances for which the exact method will be used if `beam_search_method.py` is run. 
* The method saves .sol files in the `methods/solutions_beam_search_method` folder.
  * The solution folder contains .sol files which have the same formatting as the .sol files given to us in the beginning of the lecture.
------------------------------------------

**Python Packages**:

* Exact method: gurobipy - (here with Gurobi 8.1.0) go to the installation directory of gurobi and install with `python setup.py install`
* numpy - (install with: `pip install numpy` )
