# Greedy randomized method
import random


def greedy_randomized(arcs):
    """
    Find a feasible solution for the sequential ordering problem
    defined by the specified matrix using a greedy randomized algorithm.

    :param arcs: Matrix representation of the sequential ordering problem.
    :return: List of vertices in order of visit for the solution found.
    """
    total_cost = 0
    visited_vertices = [0]
    vertices = range(arcs.shape[0])
    last_vertex = vertices[-1]

    while visited_vertices[-1] != last_vertex:
        possible_next_vertices = []
        next_vertices_costs = []

        for i in vertices:
            if (i not in visited_vertices and
                    0 <= arcs[visited_vertices[-1]][i] and
                    # all precedence constraints are respected
                    all(j in visited_vertices for j in vertices if arcs[i][j] == -1)):
                possible_next_vertices.append(i)
                next_vertices_costs.append(arcs[visited_vertices[-1]][i])

        if not possible_next_vertices:
            raise RuntimeError("No feasible solution found for this instance.")

        min_cost = min(next_vertices_costs)
        cost_difference = max(next_vertices_costs) - min_cost
        visited_vertices += random.choices(possible_next_vertices,
                                           # Map the costs inversely to weights
                                           # between 0.5 (max cost) and 1.5 (min cost)
                                           (1.5 - (cost - min_cost) / cost_difference for cost in next_vertices_costs)
                                           if cost_difference > 0 else None)
        total_cost += arcs[visited_vertices[-2]][visited_vertices[-1]]

    return visited_vertices, total_cost


def best_greedy_randomized(arcs):
    """
    Find a feasible solution for the sequential ordering problem defined by the specified
    matrix using a randomized greedy algorithm repeatedly and choosing the best result.

    :param arcs: Matrix representation of the sequential ordering problem.
    :return: List of vertices in order of visit for the solution found.
    """
    best_path = []
    best_cost = arcs.max() * arcs.shape[0]  # Impossibly large cost

    # Run the greedy randomized function n^2 times where n is the number of vertices.
    for i in range(arcs.size):
        path, cost = greedy_randomized(arcs)
        if cost < best_cost:
            best_path = path
            best_cost = cost

    return best_path, best_cost


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
        path, total_cost = greedy_randomized(arcs)

        print('Path:', path)
        print('Total cost:', total_cost)

        print('Saving {}.sol'.format(instance_name))
        with open(r'solutions_greedy_randomized_method\{}.sol'.format(instance_name), 'w') as fp:
            fp.write(' '.join(map(str, path)) + '\n')

        print()

    print("DONE")
