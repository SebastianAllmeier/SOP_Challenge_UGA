# exact method for the sop problem

from mip.model import *  # coin Or python solver
from mip.callbacks import ConstrsGenerator, CutPool
import numpy as np
from sys import stdout as out
from itertools import product
import networkx as nx


class SubTourCutGenerator(ConstrsGenerator):
    def __init__(self, prec_constraints_matrix, z):
        self.prec = prec_constraints_matrix
        self.z = z

    #def __init__(self, Fl: List[Tuple[int, int]]):
    #    self.F = Fl

    def generate_constrs(self, model: Model):
        V = range(self.prec.shape[0])
        n = self.prec.shape[0]
        cp = CutPool()
        r = []
        s = []

        valid = True # implement checker / add checker
        for v in model.vars:
            if v.name.startswith('x') and v.x > 0:
                i = int(v.name.split('(')[1].split(',')[0])
                j = int(v.name.split(')')[0].split(',')[1])
                r += [(v,(i, j))]  # add  current path

        if not valid:

            for (v, (i,j)) in r:
                cut = xsum(self.z[i,l] for (k,l) in r) - xsum(self.z[l,i] for (k,l) in r) == -1
                cp.add(cut)

            #for i in set(V) - {0}:  # for every visited node leave one package (out one less than in)
            #    model += (xsum(z[i][j] for j in V) - xsum(z[j][i] for j in V)) == -1

            for (v, (i,j)) in r:  # only variables which are included in the path can be greater 0
                cut = self.z[i][j] <= (n - 1)*v.x
                cp.add(cut)

            for (v, (i,j)) in r:  # if j must precede i, more packages must reach j than i (visit j before i)
                if self.prec[i][j]:
                    cut = xsum(self.z[k][j] for (v, (k,l)) in r) >= xsum(self.z[k][i] for (v, (k,l)) in r)
                    cp.add(cut)

                    if len(cp.cuts) > 256:
                        for cut in cp.cuts:
                            model += cut
                        return

        for cut in cp.cuts:
            model += cut
        return


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
    # for j in V:
    #    model += xsum(x[i][j]*prec_matrix[i, j] for i in V) == 0

    model += xsum(z[0][j] for j in V) == n-1  # have n-1 packages leaving from 0
    # keep this constraint ( 1 constraint )

    for i in set(V) - {0}:  # for every visited node leave one package (out one less than in)
        model += ( xsum(z[i][j] for j in V) - xsum(z[j][i] for j in V) ) == -1
    # keep this contraint ( n constraints )

    for i in V:  # only variables which are included in the path can be greater 0
        for j in V:
            model += z[i][j] <= (n-1)*x[i][j]
    # keep constraint

    for i in set(V) - {0}:  # if j must precede i, more packages must reach j than i (visit j before i)
        for j in set(V) - {0}:
            if prec_matrix[i][j]:
                model += xsum(z[l][j] for l in V) >= xsum(z[k][i] for k in V)


def plainProblem(arcs):
    """
    Generate a model for the plain problem

    :param arcs: matrix of arcs which includes precedence constrains and costs
    :return: model of the plain problem without any simplifications
    """

    # separate cost and precedence matrix
    cost_matrix = get_cost_matrix(arcs)
    prec_matrix = get_prec_matrix(arcs)

    # initialize model (MIP coin OR solver)
    model = Model()  # initialize model from mip solver

    # get number of vertices
    n = cost_matrix.shape[0]

    # add decision variables
    # add one decision variable for each connection i,j of nodes indicating whether
    # route from i to j was taken
    v = range(n)
    x = [[model.add_var(var_type=BINARY, name='x({},{})'.format(i, j)) for j in v] for i in v]
    # add variables for sub-tour elimination
    # y = [model.add_var() for i in v]
    z = [[model.add_var(var_type=INTEGER, name='z({},{})'.format(i, j)) for j in v] for i in v]


    # add objective
    model.objective = minimize(xsum(cost_matrix[i, j]*x[i][j] for i in range(n) for j in range(n)))

    add_constraints(model, x, z, prec_matrix)

    print("Solving...")

    model.optimize(max_seconds = 1000)

    if model.num_solutions:
        out.write('Path with total cost {} was found.'.format(model.objective_value))
        path = [0]
        print()
        """
        if False: # to print out the decision variables and their connection
            for i in range(n):
                for j in range(n):
                    out.write("{} ".format(x[i][j].x))
                    if x[i][j].x >= 0.99:
                        a, b = i, j
                out.write(" from {} to {}".format(a, b))
                print()
        """
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
