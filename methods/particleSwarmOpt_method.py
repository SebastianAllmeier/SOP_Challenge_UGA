import os
from datetime import datetime
from methods.DPSO.DPSO import DPSO
from helper.parser import parser, filenames

if __name__ == "__main__":
    files_sop, files_sol = filenames(('./solutions_dpso/', '../Data/course_benchmark_instances/'))
    for f_sop, f_sol in zip(files_sop, files_sol):
        start_time = datetime.now()
        print('started at', start_time)

        arcs = parser(f_sop, True)
        size = len(arcs)

        # in paper, values for inertia and personal are both equal to 4.5
        # the value for social parameter is automatically adjusted, but I didn't have time to implement it
        dpso = DPSO(pop_size=280, coef_inertia=4.5, coef_personal=4.5, coef_social=size, particle_size=size, weights_matrix=arcs)
        dpso.file_name = f_sop # will be added to constructor in the future
        dpso.optimize(iterations=5000, verbose=True)

        str_cost = str(dpso.cost(dpso.gbest))
        str_particle = ','.join(map(lambda x: str(x), dpso.full_particle(dpso.gbest)))

        print('best cost', str_cost)
        print('best solution', str_particle)

        end_time = datetime.now()

        with open(f_sol, 'w') as w:
            w.write(f'size: {size}\n')
            w.write(f'file: {os.path.basename(f_sop)}\n')
            w.write(f'best cost: {str_cost}\n')
            w.write(f'best solution: [{str_particle}]\n')
            w.write(f'elapsed: {end_time - start_time}\n')

        print('ended at', end_time)
        print('elapsed', (end_time - start_time))
