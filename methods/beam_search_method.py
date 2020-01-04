# Greedy Method


def beam_search(arcs, beam_width):
    """
    Apply a beam search of the specified width on the sequential ordering
    problem defined by the specified matrix and return the best solution found.

    :param arcs: Matrix representation of the sequential ordering problem.
    :param beam_width: width of the beam search.
    :return: Tuple of a list of vertices in order of visit for the best solution found and the cost of that solution.
    """
    paths = [([0], 0)]
    vertices = range(arcs.shape[0])

    for _ in range(len(vertices) - 1):
        new_paths = []
        for path, cost in paths:
            for i in vertices:
                if (i not in path and
                        # all precedence constraints are respected
                        all(j in path for j in vertices if arcs[i][j] == -1)):
                    new_paths.append((path + [i], cost + arcs[path[-1]][i]))

        if len(new_paths) == 0:
            raise RuntimeError("No feasible solution found for this instance.")
        else:
            new_paths.sort(key=lambda path_and_cost: path_and_cost[1])
            paths = new_paths[:beam_width]

    return paths[0]


if __name__ == "__main__":
    from helper.parser import parser, filenames
    from helper.verification import check_solution
    import os.path
    import numpy as np
    import time

    # directory paths
    sol_path = "../Data/solutions/"
    sop_path = "../Data/course_benchmark_instances/"

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # fill arrays
    for sop_file in sop_files:
        arcs = parser(sop_file, True)
        instance_name = os.path.basename(sop_file[:-4])

        print('Applying beam search algorithm to', instance_name)
        time_start = time.clock()
        path, total_cost = beam_search(arcs, arcs.shape[0])
        print('Time:', time.clock() - time_start, 'seconds.')

        print('Path:', path)
        print('Total cost:', total_cost)
        print('Verified cost:', check_solution(arcs, np.array(path)))

        print('Saving {}.sol'.format(instance_name))
        with open(r'solutions_beam_search_method_V\{}.sol'.format(instance_name), 'w') as fp:
            fp.write(' '.join(map(str, path)) + '\n')

        print()

    print("DONE")
