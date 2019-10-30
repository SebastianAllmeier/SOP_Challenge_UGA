from helper.parser import parser, filenames
from mip.model import *  # coin Or python solver
import numpy as np


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

    return np.multiply(arcs, arcs != -1)


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


def add_constraints(model, x, prec_matrix):
    """
    Add necessary constraints to the model.

    :param model:
    :param prec_matrix:
    :return:
    """

    # TODO: something is not working...
    # wrong constraints ?? wrong indexing?? missing constraints??

    V = range(prec_matrix.shape[0])

    # we will never move away from the last node
    # TODO: implement nicely, don't use a hack like this...
    # we can only leave every node once
    for i in range(prec_matrix.shape[0]-1):
        model += xsum(x[i][j] for j in V) == 1

    #model += xsum(x[prec_matrix.shape[0]-1][j] for j in V) == 0

    # we can only enter every node once
    # we never enter node 0 (sine we always start there
    # TODO: same as before...
    for j in range(0, prec_matrix.shape[0]):
        model += xsum(x[i][j] for i in V) == 1

    #model += xsum(x[j][0] for j in V) == 0


    # add precedence constraints
    model += xsum(x[i][j]*prec_matrix[i, j] for i in V for j in V) == 0





def plainProblem(arcs):
    """
    Generate a model for the plain problem

    :param arcs: matrix of arcs which includes precedence constrains and costs
    :return: model of the plain problem without any simplifications
    """
    if arcs.shape[0] >= 500:
        return

    cost_matrix = get_cost_matrix(arcs)
    prec_matrix = get_prec_matrix(arcs)

    model = Model()  # initialize model from mip solver

    n = cost_matrix.shape[0]

    x = add_variables(model, n)  # TODO: don't use an extra function here

    model.objective = minimize(xsum(cost_matrix[i,j]*x[i][j] for i in range(n) for j in range(n)))

    add_constraints(model, x, prec_matrix)

    print("Solving...")

    model.optimize(max_seconds = 30)

    print("Done; value: {}".format(model.objective_value))




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