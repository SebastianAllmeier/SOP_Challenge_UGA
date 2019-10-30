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

    return arcs == -1

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
    :return:
    """
    pass

def add_constraints(model, prec_matrix, cost_matrix):
    """
    Add necessary constraints to the model.

    :param model:
    :param prec_matrix:
    :param cost_matrix:
    :return:
    """
    pass

def plainProblem(arcs):
    """
    Generate a model for the plain problem

    :param arcs: matrix of arcs which includes precedence constrains and costs
    :return: model of the plain problem without any simplifications
    """
    pass

def solve(model):
    pass



if __name__ == "__main__":
    pass