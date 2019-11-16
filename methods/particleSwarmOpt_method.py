import numpy as np
import os
from methods.DPSO.DPSO import DPSO
from helper.parser import parser

# SEED = 666
# np.random.seed(SEED)
# random.seed(SEED)

# def check_if_start_and_end_nodes_are_always_first_and_last():
#     base_path = '../Data/course_benchmark_instances/'
#     for file in os.listdir(base_path):
#         full_path = os.path.join(base_path, file)
#         arcs = parser(full_path, False)
#         particle_size = len(arcs)
#         M = -np.inf
#         node_start, node_end = -1, -1
#         for i in range(particle_size):
#             for j in range(particle_size):
#                 if arcs[i][j] > M:
#                     M = arcs[i][j]
#                     node_start, node_end = i, j
#         print(file, particle_size, node_start, node_end, 'FIRST=LAST' if node_end == particle_size-1 else 'DIFFERENT')
# check_if_start_and_end_nodes_are_always_first_and_last()

if __name__ == "__main__":
    # file_name = 'ESC07'
    file_name = 'ESC63'
    # file_name = 'R.700.1000.1'

    arcs = parser(f'../Data/course_benchmark_instances/{file_name}.sop', True)
    dpso = DPSO(pop_size=20, coef_inertia=3, coef_personal=5, coef_social=10, particle_size=len(arcs), weights_matrix=arcs)
    dpso.optimize(iterations=100, parallelize=True, verbose=True)

    # print('start', dpso.node_start)
    # print('end', dpso.node_end)
    # print('precedences', dpso.precedences)
    # for i, particle in enumerate(dpso.particles):
    #     print('particle', i, dpso.full_particle(particle), 'cost', dpso.cost(particle))