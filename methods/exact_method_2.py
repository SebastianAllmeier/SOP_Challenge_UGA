# exact method for the sop problem

import sys
import math
import random
import itertools
from gurobipy import *
import numpy as np

n = 0
prec_matrix = None
cost_matrix = None

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        # only takes selected vars
        selected = tuplelist((i,j) for i,j in model._vars.keys() if vals[i,j] > 0.5)
        # filter the corresponding helper variables


        whole_tour = get_whole_tour(selected)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < n:
            # add subtour elimination constraint for every pair of cities in tour
            for perm in itertools.permutations(tour):
                model.cbLazy(quicksum(model._vars[perm[i], perm[(i+1) % len(perm)]]
                                      for i in range(len(perm)))
                             <= len(perm)-1)

            model.cbLazy(quicksum(model._vars[i, j]
                                  for i, j in itertools.combinations(tour, 2))
                         <= len(tour)-1)
        """
        corresp_helper = []
        for var in model._Model__vars:
            if var.VarName[0] == 'h':
                i = int(var.VarName.split('(')[1].split(',')[0])
                j = int(var.VarName.split(')')[0].split(',')[1])
                corresp_helper += [(var, (i, j))]

        for index_1, i in enumerate(whole_tour):
            for index_2, j in enumerate(whole_tour[index_1:]):
                if prec_matrix[i, j]:
                    for helper in corresp_helper:
                        if helper[1] == (i,j):
                            helper_i_j = helper[0]
                        elif helper[1] == (j,i):
                            helper_j_i =  helper[0]
                    model.cbLazy(helper_i_j - helper_j_i >= 0)
                    #m.addConstr(helper(j, i) - helper(i, j) >= 0)
        """
        #for index_1, i in enumerate(tour):
        #    for j in range(n):
        #        if prec_matrix[i, j] == 1:
        #            model.cbLazy(model._vars[i, j] == 0)

def get_whole_tour(edges):
    unvisited = list(range(n))
    cycle = []  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*') if j in unvisited]
        #if len(cycle) > len(thiscycle):
        #    cycle = thiscycle
        cycle += thiscycle
    return cycle




def subtour(edges):
    unvisited = list(range(n))
    cycle = range(n+1) # initial length has 1 more city
    while unvisited: # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i,j in edges.select(current,'*') if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


def gurobi_problem(arcs):

    ## initialization
    # create model
    m = Model()

    # separate cost and precedence matrix
    global cost_matrix
    global prec_matrix


    cost_matrix = get_cost_matrix(arcs)
    prec_matrix = get_prec_matrix(arcs)



    # size of the problem

    global n
    n = prec_matrix.shape[0]

    prec_matrix[n-1, 0] = 0


    # add decision variables to the model
    vars = tupledict()
    for i in range(n):
        for j in range(n):
            vars[i, j] = m.addVar(name='var({},{})'.format(i,j), vtype=GRB.BINARY, obj=cost_matrix[i,j])

    helper = tupledict()
    for i in range(n):
        for j in range(n):
            helper[i,j] = m.addVar(name='helper({},{})'.format(i,j), vtype=GRB.INTEGER)


    ## add easy constraints
    # sub tour and precedence constraints will be added as lazy constraints

    # can only leave every node once
    # but never leave the last node
    m.addConstrs(vars.sum(i, '*') == 1 for i in range(n))

    # artificially add connection between last and first node
    m.addConstr(vars[n-1,0] == 1)

    # have to enter every node exactly once ( except first node 0)
    m.addConstrs(vars.sum('*', j) == 1 for j in range(n))

    m.addConstrs(vars[i,i] == 0 for i in range(n))

    ###########
    # prec constraints

    m.addConstr(helper.sum(0, '*') == n-1) # have n-1 packages leaving from 0

    for i in range(n):
        for j in range(n): # only variables which are included in the path can be greater 0
            m.addConstr(helper[i,j] <= (n-1) * vars[i,j])

    # for every visited node leave one package (out one less than in)
    m.addConstrs(helper.sum(i, '*') - helper.sum('*', i) == -1 for i in range(1,n))

    for i in range(1,n):
        for j in range(1,n):
            if prec_matrix[i,j]:
                m.addConstr(helper.sum('*', j) - helper.sum('*', i) >= 0)


    m._vars = vars
    m.Params.lazyConstraints = 1
    m.optimize(subtourelim)

    vals = m.getAttr('x', vars)
    selected = tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

    tour = subtour(selected)
    assert len(tour) == n

    print('')
    print('Optimal tour: %s' % str(tour))
    print('Optimal cost: %g' % m.objVal)
    print('')

    from helper.verification import check_solution

    print("Solution valid: " + str(check_solution(arcs, np.array(tour))))

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

if __name__ == "__main__":
    from helper.parser import parser, filenames

    # specify used methods
    solution_methods = {
        'exact_method': True,
        'pso': False, # TODO: implement
        'greedy': False, # TODO: implement
        'ant_colony': False # TODO: implement
    }

    solvers = {  # the actual functions for the methods
        'exact_method': gurobi_problem,
    }

    # directory paths
    sol_path = "../Data/solutions/"
    sop_path = "../Data/course_benchmark_instances/"

    filter = 'easy'  # easy only (tries to) solve(s) instances < filter_size vertices
    filter_size = 60

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # initialize array arcs and solutions
    instances = []

    # fill arrays
    for i in range(len(sop_files) - 1):
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

