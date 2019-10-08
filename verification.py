# verification of given solutions
from helper.parser import parser, filenames

def solution_valid(arcs, solution):

    value = 0

    # check if shapes coincide
    if solution.shape[0] != arcs.shape[0]:
        value = -1
        return value

    # check if values are in valid range
    if solution.max() >= solution.shape[0]:
        value = -1
        return value

    # check that all solution is a permutation (no value is allowed twice)
    if len(set(solution)) != solution.shape[0]:
        value = -1
        return value

    for i in range(solution.shape[0]-1):  # cycle through solution and check constraints
        arc_weight = arcs[solution[i], solution[i+1]]

        # check if arc_weight is valid value
        if arc_weight == -1 or arc_weight == 999:
            value = -1
            return value

        for j in range(arcs.shape[0]):
            # check precedence constraints
            if arcs[solution[i], j] == -1:  # check row i for constraints
                if j not in solution[:i]:
                    # if constraint is not satisfied in solution
                    value = -1
                    return value

        value += arc_weight

    return value

if __name__ == "__main__":

    # directory paths
    sol_path = "Data/solutions/"
    sop_path = "Data/course_benchmark_instances/"

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # initialize array arcs and solutions
    instances = []

    # fill arrays
    for i in range(len(sop_files)):
        arcs = parser(sop_files[i], True)
        solution = parser(sol_files[i], True)
        instances += [(arcs, solution)]
        value = solution_valid(arcs, solution)
        print("The solution value is: " + value + "\n")

    print("")
