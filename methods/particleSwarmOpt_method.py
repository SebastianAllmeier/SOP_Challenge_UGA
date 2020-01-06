import os
import pickle
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

        pop_size = 70
        coef_inertia = 4.5
        coef_personal = 4.5
        coef_social = 2
        iterations = 5000

        f_evo = f_sol.replace('solutions_dpso', 'solutions_evo').replace('.sol', '.evo')

        f_pkl = f_sol.replace('solutions_dpso', 'solutions_pkl').replace('.sol', '.pkl')
        if os.path.isfile(f_pkl):
            print('LOADED OBJECT FROM PICKLE')
            with open(f_pkl, mode='rb') as reader:
                dpso = pickle.load(reader)
        else:
            print('CREATED OBJECT FROM SCRATCH')
            # in paper, values for inertia and personal are both equal to 4.5 "social" parameter is automatically set
            dpso = DPSO(pop_size=pop_size, coef_inertia=coef_inertia, coef_personal=coef_personal, coef_social=coef_social, particle_size=size, weights_matrix=arcs)
            dpso.file_name = f_sop # will be added to constructor in the future

        dpso.optimize(out_file=f_evo, iterations=iterations, verbose=True)

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

            w.write(f'pop_size = {pop_size}\n')
            w.write(f'coef_inertia = {coef_inertia}\n')
            w.write(f'coef_personal = {coef_personal}\n')
            w.write(f'coef_social = {coef_social}\n')
            w.write(f'iterations = {iterations}\n')

        with open(f_pkl, 'wb') as w:
            pickle.dump(dpso, w)

        print('ended at', end_time)
        print('elapsed', (end_time - start_time))
