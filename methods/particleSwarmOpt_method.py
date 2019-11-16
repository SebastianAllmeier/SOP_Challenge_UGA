import numpy as np
import random
from methods.DPSO.DPSO import DPSO
from helper.parser import parser

SEED = 666
np.random.seed(SEED)
random.seed(SEED)

if __name__ == "__main__":
    arcs = parser('../Data/course_benchmark_instances/ex.sop', True)
    print(arcs)

    dpso = DPSO(pop_size=5, coef_inertia=1, coef_personal=1, coef_social=1, particle_size=len(arcs), weights_matrix=arcs)

    print('start', dpso.node_start)
    print('end', dpso.node_end)
    print('precedences', dpso.precedences)
    for i, particle in enumerate(dpso.particles):
        print('particle', i, particle)