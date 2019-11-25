### Main Script for the SOP Challenge
### This script allows the user to specify the used methods and instances which should be solved
### used methods can be found in the methods folder; helpers in the helpers folder

# imports
from helper.parser import parser, filenames


if __name__ == "__main__":
    # import methods
    from methods.antColony_method import antColony
    from methods.exact_method import *
    from methods.greedy_method import greedy, best_greedy_randomized
    from methods.particleSwarmOpt_method import pso

    # specify used methods
    solution_methods = {
        'exact_method': True,
        'pso': False,  # TODO: implement
        'greedy': True,
        'best_greedy_randomized': True,
        'ant_colony': False  # TODO: implement
    }

    solvers = {  # the actual functions for the methods
        'exact_method': plainProblem,
        'pso': pso,
        'greedy': greedy,
        'best_greedy_randomized': best_greedy_randomized,
        'ant_colony': antColony
    }

    # directory paths
    sol_path = "Data/solutions/"
    sop_path = "Data/course_benchmark_instances/"

    filter = 'easy'  # easy only (tries to) solve(s) instances < filter_size vertices
    filter_size = 500

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # initialize array arcs and solutions
    instances = []

    # fill arrays
    for i in range(len(sop_files)):
        solution = parser(sol_files[i], True)
        if solution.size > filter_size and filter == 'easy':  # filter out 'big' instances
            continue
        arcs = parser(sop_files[i], True)
        instances += [(arcs, solution)]

    for instance in instances:  # for each instance
        for method in solution_methods:  # go through all methods
            if solution_methods[method]:  # and use the specified ones
                solvers[method](instance[0])  # to solve the problem

    print("DONE")
