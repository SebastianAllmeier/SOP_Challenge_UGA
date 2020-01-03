# Greedy Method


def greedy(arcs):
    """
    Find a feasible solution for the sequential ordering problem
    defined by the specified matrix using a greedy algorithm.

    :param arcs: Matrix representation of the sequential ordering problem.
    :return: List of vertices in order of visit for the solution found.
    """
    total_cost = 0
    visited_vertices = [0]
    big_value = arcs.max() + 1
    vertices = range(arcs.shape[0])
    last_vertex = vertices[-1]

    while visited_vertices[-1] != last_vertex:
        min_weight = big_value
        next_vertex = -1

        for i in vertices:
            if (i not in visited_vertices and
                    0 <= arcs[visited_vertices[-1]][i] < min_weight and
                    # all precedence constraints are respected
                    all(j in visited_vertices for j in vertices if arcs[i][j] == -1)):
                min_weight = arcs[visited_vertices[-1]][i]
                next_vertex = i

        if next_vertex == -1:
            raise RuntimeError("No feasible solution found for this instance.")

        visited_vertices.append(next_vertex)
        total_cost += min_weight

    return visited_vertices, total_cost


if __name__ == "__main__":
    from helper.parser import parser, filenames
    import os.path

    # directory paths
    sol_path = "../Data/solutions/"
    sop_path = "../Data/course_benchmark_instances/"

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # fill arrays
    for sop_file in sop_files:
        arcs = parser(sop_file, True)
        instance_name = os.path.basename(sop_file[:-4])

        print('Applying greedy algorithm to', instance_name)
        path, total_cost = greedy(arcs)

        print('Path:', path)
        print('Total cost:', total_cost)

        print('Saving {}.sol'.format(instance_name))
        with open(r'solutions_greedy_method\{}.sol'.format(instance_name), 'w') as fp:
            fp.write(' '.join(map(str, path)) + '\n')

        print()

    print("DONE")
