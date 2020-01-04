import math
import random
from random import uniform as U
import numpy as np
import multiprocessing as mp
from typing import List
from .operations import op_perm_sub_perm, op_scalar_mul_velocity, op_perm_sum_velocity, op_perm_fix
from copy import deepcopy

class DPSO:
    def __init__(self,
                 pop_size : int,
                 coef_inertia : float,
                 coef_personal : float,
                 coef_social : float,
                 particle_size : int,
                 weights_matrix : List[List]) -> None:
        """
        Initializes a new instance of Discrete Particle Swarm Optimization
        :param pop_size: number of particles in population
        :param coef_inertia: coefficient of speed at previous iteration
        :param coef_personal: coefficient of difference from current perm to personal best perm
        :param coef_social: coefficient of distance from current perm to global best perm
        :param particle_size: the size of one particle
        :param weights_matrix: matrix of edge weights and precedence constraints (Wij = -1 => j must precede i)
        """
        self.file_name = None
        self.pop_size = pop_size
        self.coef_inertia = coef_inertia
        self.coef_personal = coef_personal
        self.coef_social = coef_social
        self.particle_size = particle_size
        self.weights_matrix = weights_matrix

        self.particles = [] # population
        self.velocities = []
        self.pbest = []
        self.gbest = None

        self.precedences = None  # will contain precedence constraints as a list of pairs (created in _generate_precedences)
        self.node_start = None
        self.node_stop = None

        self._generate_precedences_and_start_stop_nodes()
        self._initialize()

    def _initialize(self) -> None:
        """
        Initializes particles, velocities, personal best and global best
        """
        # initial velocities have lengths uniformly generated between n/2 and n/4
        lower_bound_velocity_size = math.floor(self.particle_size / 4.)
        upper_bound_velocity_size = math.floor(self.particle_size / 2.)

        # initial velocities have displacements uniformly generated between -n/3 and n/3
        lower_bound_displacement = math.floor(-self.particle_size / 3.) # floor(- n / 3)
        upper_bound_displacement = math.floor(self.particle_size / 3.) # floor(+ n / 3)

        # set to generate values of nodes from (exclude start and end nodes)
        set_nodes = set(range(self.particle_size)) - {self.node_start, self.node_end}

        # set to generate values of displacements from
        set_displacement = range(lower_bound_displacement, upper_bound_displacement + 1)

        # initial permutation that does not contain start and end nodes
        seed_perm = random.sample(set_nodes, self.particle_size - 2)  # random permutation without start and end nodes

        # parallelize the creation of each particle because fixing procedure is quite slow
        with mp.Pool(processes=mp.cpu_count() - 1) as pool: # use max_cpu - 1 processes to avoid PC freezing
            param = (lower_bound_velocity_size, upper_bound_velocity_size, set_nodes, set_displacement, seed_perm)
            mapping_params = [(i,) + param for i in range(self.pop_size)] # (i,) is process number for random seed
            mapping_results = pool.map(self._create_single_particle, mapping_params)
            for velocity, particle, cost in mapping_results:
                self.velocities.append(deepcopy(velocity))
                self.particles.append(deepcopy(particle))
                self.pbest.append(deepcopy(particle))
                if self.gbest is None or cost < self.cost(self.gbest):
                    self.gbest = deepcopy(particle)
        print('initial best:', self.gbest, self.cost(self.gbest))

    def _create_single_particle(self, params):
        """
        This method is creating a single particle inside a process in a multiprocessing Pool
        :param params: a pair containing: index, lower_bound_velocity_size, upper_bound_velocity_size, set_nodes, set_displacement, seed_perm
        :return: a pair containing: velocity of particle, fixed particle, cost of particle
        """
        index, lower_bound_velocity_size, upper_bound_velocity_size, set_nodes, set_displacement, seed_perm = params

        random.seed(index)

        # generate no. of insertion moves for current velocity
        velocity_size = random.randint(lower_bound_velocity_size, upper_bound_velocity_size)

        nodes = random.sample(set_nodes, velocity_size)  # generate nodes
        displacements = random.sample(set_displacement, velocity_size)
        velocity = list(zip(nodes, displacements))

        unfixed_particle = op_perm_sum_velocity(x=seed_perm, v=velocity)
        fixed_particle = op_perm_fix(x=self.full_particle(unfixed_particle), P=self.precedences)
        cost = self.cost(fixed_particle)

        # very important: have velocities that transform seed permutation into fixed one
        velocity = op_perm_sub_perm(fixed_particle, seed_perm)

        return velocity, fixed_particle, cost

    def _generate_precedences_and_start_stop_nodes(self) -> None:
        """
        Generates a list of precedences self.precedences = {(j,i) | Mij = -1}.
        Determines start node as row# and end node as col# of max value in cost matrix.
        """
        M = -np.inf
        self.node_start, self.node_end = -1, -1
        self.precedences = []
        for i in range(self.particle_size):
            for j in range(self.particle_size):
                v = self.weights_matrix[i][j]
                if v == -1: # create precedences
                    self.precedences.append((j, i)) # j must be visited before i
                elif v > M: # determine start / end node
                    M = v
                    self.node_start, self.node_end = i, j

    def cost(self, x : list) -> float:
        """
        Computes the cost for a givem permutation x
        :param x: the permutation to compute the cost for
        :return: the cost of the permutation
        """
        weight_1st_edge = self.weights_matrix[self.node_start][x[0]]
        weight_2nd_edge = self.weights_matrix[x[-1]][self.node_end]

        c = sum([self.weights_matrix[x[i]][x[i + 1]] for i in range(self.particle_size - 2 - 1)])

        return c + weight_1st_edge + weight_2nd_edge

    def full_particle(self, x):
        """
        Generates a complete particle by adding the first node and last node
        :param x: the particle to be modified
        :return: a complete particle containing all nodes from 0 to particle_size-1 (valid permutation in math sense)
        """
        return [self.node_start] + x + [self.node_end]

    def optimize(self, out_file : str, iterations : int, verbose : bool = True) -> None:
        """
        Runs Discrete Particle Swarm Optimization procedure
        :param out_file: the file name to print the information to disk
        :param iterations: total number of iterations to run the algorithm for
        :param verbose: flag that indicates whether to print information to console
        :return:
        """
        with open(out_file, mode='w', buffering=1) as w:
            out_str = f'step {0:4d}: best cost = {self.cost(self.gbest)}, best perm = {self.full_particle(self.gbest)}'
            w.write(out_str + '\n')
            if verbose:
                print(out_str)

            # parallelism updates gbest after all processes finish their job and might not be that optimal,
            # but it saves some time
            with mp.Pool(mp.cpu_count() - 1) as pool:
                last_cost = np.inf
                for it in range(1, iterations + 1):
                    mapping_params = list(zip(self.particles, self.velocities, self.pbest, [self.gbest] * self.pop_size))
                    mapping_results = pool.map(self._optimization_step, mapping_params)
                    self.particles, self.velocities, self.pbest, costs = map(list, zip(*mapping_results))

                    gbest_cost = self.cost(self.gbest)
                    for index, cost in enumerate(costs):
                        if cost < gbest_cost:
                            gbest_cost = cost
                            self.gbest = deepcopy(self.particles[index])

                    if gbest_cost < last_cost:
                        last_cost = gbest_cost
                    if it % 100 == 0:
                        out_str = f'step {it:4d} / {iterations} file = {self.file_name} best cost = {self.cost(self.gbest)} best perm = {self.full_particle(self.gbest)}'
                        w.write(out_str + '\n')
                        if verbose:
                            print(out_str)
                out_str = f'END file = {self.file_name} best cost = {self.cost(self.gbest)} best perm = {self.full_particle(self.gbest)}'
                w.write(out_str + '\n')
                if verbose:
                    print(out_str)

    def _optimization_step(self, param):
        """
        This method is run on a separate process at each iteration.
        Applies the formula (*) - see it below - for one particle
        :param param: contains particle, velocity, pbest and gbest, all needed to implement formula
        :return: returns updated values for particle, velocity, pbest and gbest
        """
        particle, velocity, pbest, gbest = param
        # save particle because we will compute velocity at the end
        old_particle = deepcopy(particle)
        old_particle = op_perm_fix(x=self.full_particle(old_particle),P=self.precedences)

        # apply formula (*): v(k+1) = [inertia * v(k)] + [personal * rand() * (p(i) - x(i))] + [social * rand() * (g - x(i))]

        # compute each term inside square brackets
        velocity_inertia = op_scalar_mul_velocity(c=self.coef_inertia, v=velocity)

        diff_velocity_personal = op_perm_sub_perm(pbest, particle)
        velocity_personal = op_scalar_mul_velocity(self.coef_personal * U(0, 1), diff_velocity_personal)

        diff_velocity_social = op_perm_sub_perm(gbest, particle)
        velocity_social = op_scalar_mul_velocity(self.coef_social * U(0, 1), diff_velocity_social)

        # apply each velocity individually to particle because we don't have a velocity + velocity operator
        particle = op_perm_sum_velocity(particle, velocity_inertia)
        particle = op_perm_sum_velocity(particle, velocity_personal)
        particle = op_perm_sum_velocity(particle, velocity_social)

        # fix current particle so that it repects precedence constraints
        particle = op_perm_fix(x=self.full_particle(particle), P=self.precedences)

        # compute velocity that transforms old_particle into self.patricles[i]
        velocity = op_perm_sub_perm(particle, old_particle)

        cost = self.cost(particle)

        # update personal best in case we got a better particle than previous personal best
        if cost < self.cost(pbest):
            pbest = deepcopy(particle)
        if cost < self.cost(self.gbest):
            self.gbest = deepcopy(particle)

        return particle, velocity, pbest, cost

    def respects_precedences(self, particle):
        """
        Checks if the current particle respects precedence constraints
        :param particle: the particle without start and end nodes
        :return:
        """
        fp = self.full_particle(particle)
        for i in range(len(fp) - 1):
            if self.weights_matrix[fp[i]][fp[i+1]] < 0:
                return False
        return True

    @staticmethod
    def lists_are_equal(A, B):
        """
        Check if lists A and B are equal
        :param A:
        :param B:
        :return:
        """
        nA = len(A)
        nB = len(B)
        if nA != nB: return 0
        for i in range(nA):
            if A[i] != B[i]:
                return 0
        return 1