from helper.parser import parser, filenames
from mip.model import *  # coin Or python solver
import numpy as np
from sys import stdout as out
from itertools import product


def get_prec_matrix(arcs):
    """
    Extract the precedence constraints from the initial arcs matrix.

    :param arcs: numpy array
    :return: numpy array, same size as input;
    matrix with only with precedence constraints
    (a_ij is one if i must precede j, 0 otherwise)
    """

    return (arcs == -1).astype(float)

def get_cost_matrix(arcs):
    """
    Extract only the costs for traversing the arcs from the initial arcs matrix.

    :param arcs: numpy array
    :return: numpy array, same size as input; returns only the costs of the arcs given by the problem
    (no recedence constraints included in this matrix)
    """

    return np.multiply(arcs, arcs != -1).astype(int)


def add_variables(model, n=0):
    """
    Add the required amount of variables to the problem.

    :param model:
    :param n: (square root of) numbers of variables (will get squared)
    :return: model with added decision variables
    """
    v = range(n)

    # add one descision variable for each connection i,j of nodes indicating whether
    # route from i to j was taken
    return [[model.add_var(var_type=BINARY) for j in v] for i in v]


def add_constraints(model, x, z, prec_matrix):
    """
    Add necessary constraints to the model.

    :param model:
    :param prec_matrix:
    :return:
    """

    V = range(prec_matrix.shape[0])
    n =  prec_matrix.shape[0]

    # we will never move away from the last node
    # we can only leave every node once
    for i in range(prec_matrix.shape[0]-1):
        model += xsum(x[i][j] for j in V) == 1

    model += xsum(x[i][j] for j in V for i in V) == prec_matrix.shape[0]-1

    # we can only enter every node once
    # we never enter node 0 (sine we always start there
    for j in range(1, prec_matrix.shape[0]):
        model += xsum(x[i][j] for i in V) == 1

    for i in V:
        model += x[i][i] == 0

    # add precedence constraints
    # for each vertex, we can only reach it if all precedence constraints are satisfied
    # for each node look at incoming connections and make sure that there is no precedence constraints
    # on the connection
    #for j in V:
    #    model += xsum(x[i][j]*prec_matrix[i, j] for i in V) == 0

    model += xsum(z[0][j] for j in V) == n-1

    for i in set(V) - {0}:
        model += ( xsum(z[i][j] for j in V) - xsum(z[j][i] for j in V) ) == -1

    for i in V:
        for j in V:
            model += z[i][j] <= (n-1)*x[i][j]

    for i in set(V) - {0}:
        for j in set(V) - {0}:
            if prec_matrix[i][j]:
                model += xsum(z[l][j] for l in V) >= xsum(z[k][i] for k in V)





    #n = prec_matrix.shape[0]
    # TODO: no subpaths/cicles/subtours are allowed!!
    #for (i, j) in set(product(set(V) - {0}, set(V) - {0})):
    #    model += y[i] - (n+1)*x[i][j] >= y[j]-n











def plainProblem(arcs, filter="easy"):
    """
    Generate a model for the plain problem

    :param arcs: matrix of arcs which includes precedence constrains and costs
    :return: model of the plain problem without any simplifications
    """
    # filter easy
    if filter == "easy":
        if arcs.shape[0] >= 500:
            print("Problem has more than 500 verticies and will not be solved due to its size.")
            return

    # separate cost and precedence matrix
    cost_matrix = get_cost_matrix(arcs)
    prec_matrix = get_prec_matrix(arcs)

    #initialize model (MIP coin OR solver)
    model = Model()  # initialize model from mip solver

    # get number of verticies
    n = cost_matrix.shape[0]

    # add decision variables
    # add one descision variable for each connection i,j of nodes indicating whether
    # route from i to j was taken
    v = range(n)
    x = [[model.add_var(var_type=BINARY) for j in v] for i in v]
    # add variables for sub-tour elimination
    # y = [model.add_var() for i in v]
    z = [[model.add_var(var_type=INTEGER) for j in v] for i in v]


    # add objective
    model.objective = minimize(xsum(cost_matrix[i, j]*x[i][j] for i in range(n) for j in range(n)))

    add_constraints(model, x, z, prec_matrix)

    print("Solving...")

    model.optimize(max_seconds = 1000)

    if model.num_solutions:
        out.write('Path with total cost {} was found.'.format(model.objective_value))
        path = [0]
        print()
        if False: # to print out the decision variables and their connection
            for i in range(n):
                for j in range(n):
                    out.write("{} ".format(x[i][j].x))
                    if x[i][j].x >= 0.99:
                        a, b = i, j
                out.write(" from {} to {}".format(a, b))
                print()
        while path[-1] != cost_matrix.shape[0]-1:
            path += [j for j in range(n) if x[path[-1]][j].x >= 0.99]

        out.write("-----------------\n\n")
        out.write("The path takes the following route: \n")
        for i, vertex in enumerate(path):
            if ((i) % 10) == 0:
                out.write('\n')
            if vertex != cost_matrix.shape[0]-1:
                out.write('{}\t -> '.format(vertex))
            else:
                out.write('{}'.format(vertex))
        out.write(';\n\nLength of the path: {}\n\n'.format(len(path)))
        out.write('-----------------\n\n')
    #print("Done; value: {}".format(model.objective_value))






if __name__ == "__main__":
    # directory paths
    sol_path = "Data/solutions/"
    sop_path = "Data/course_benchmark_instances/"

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # initialize array arcs and solutions
    instances = []

    # fill arrays
    for i in range(len(sop_files) - 1):
        arcs = parser(sop_files[i], True)
        solution = parser(sol_files[i], True)
        instances += [(arcs, solution)]
        plainProblem(arcs)

    print("DONE")