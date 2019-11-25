# Greedy Method


def greedy(arcs):
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
            raise RuntimeError("Greedy algorithm failed! An implementation with backtracks may be needed.")

        visited_vertices.append(next_vertex)
        total_cost += min_weight

    print('Path:', visited_vertices)
    print('Total cost: ', total_cost)

    return visited_vertices


if __name__ == "__main__":
    pass  # some tests etc.
