import math
import random
from random import uniform as U
import time
import numpy as np
import multiprocessing as mp
from typing import List
from .operations import op_perm_sub_perm, op_scalar_mul_velocity, op_perm_sum_velocity, op_perm_fix

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

        lower_bound_velocity_size = math.floor(self.particle_size / 4.)
        upper_bound_velocity_size = math.floor(self.particle_size / 2.)

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
            mapping_params = [(i,) + param for i in range(self.pop_size)]
            mapping_results = pool.map(self._create_single_particle, mapping_params)
            for velocity, particle, cost in mapping_results:
                self.velocities.append(velocity)
                self.particles.append(particle.copy())
                self.pbest.append(particle.copy())
                if self.gbest is None or cost < self.cost(self.gbest):
                    self.gbest = particle.copy()
        print('best:', self.gbest, self.cost(self.gbest))

    def _create_single_particle(self, params):
        """
        This method is creating a single particle inside a process in a multiprocessing Pool
        :param params: a pair containing: index, lower_bound_velocity_size, upper_bound_velocity_size, set_nodes, set_displacement, seed_perm
        :return: a pair containing: velocity of particle, fixed particle, cost of particle
        """
        time_start = time.time()
        index, lower_bound_velocity_size, upper_bound_velocity_size, set_nodes, set_displacement, seed_perm = params

        random.seed(index)

        # generate no. of insertion moves for current velocity
        velocity_size = random.randint(lower_bound_velocity_size, upper_bound_velocity_size)

        nodes = random.sample(set_nodes, velocity_size)  # generate nodes
        displacements = random.sample(set_displacement, velocity_size)
        velocity = list(zip(nodes, displacements))

        unfixed_particle = op_perm_sum_velocity(x=seed_perm, v=velocity)
        fixed_particle = op_perm_fix(x=unfixed_particle, P=self.precedences)
        cost = self.cost(fixed_particle)

        # very important: have velocities that transform seed permutation into fixed one
        velocity = op_perm_sub_perm(fixed_particle, seed_perm)

        time_end = time.time()
        # print(f'creating particle {index} took {time_end - time_start:.4f} seconds')

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
                    self.precedences.append((j, i)) # j must precede i
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

    def optimize(self, iterations : int,
                 parallelize : bool = False,
                 verbose : bool = True,
                 auto_adjust_social_coef : bool = True) -> None:
        """
        Runs Discrete Particle Swarm Optimization procedure
        :param iterations: total number of iterations to run the algorithm for
        :param parallelize: flag that indicates whether to use multiprocessing
        :param verbose: flag that indicates whether to prin information
        :param auto_adjust_social_coef: apply formula social(k+1) = social(k) - 0.01 nr(k)
        :return:
        """
        if auto_adjust_social_coef:
            self.coef_social = 1
        if verbose:
            print(f'step {0:4d}: best cost = {self.cost(self.gbest)}, best perm = {self.full_particle(self.gbest)}')

        if parallelize:
            # parallel version updates gbest after all processes finish their job and might not be that optimal,
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
                            self.gbest = self.particles[index].copy()

                    if gbest_cost < last_cost:
                        last_cost = gbest_cost
                        # n = -2
                        if auto_adjust_social_coef:
                            n = sum([DPSO.lists_are_equal(particle, self.gbest) for particle in self.particles]) - 1 # !!!
                            self.coef_social = self.coef_social - 0.01 * n #int(10 * n * U(0.5, 1))
                            # TO DO: reset particles that are equal to gbest
                        if verbose:
                            print(f'step {it:4d}: n = {n:+5d} social = {self.coef_social:5.2f} file = {self.file_name} best cost = {self.cost(self.gbest)} best perm = {self.full_particle(self.gbest)}')
        else:
            # iterative version updates pbest and gbest as soon as a better particle is obtained (see that the update
            # is made inside "for_i" loop)
            for it in range(1, iterations + 1):
                gbest_cost = self.cost(self.gbest)
                for i in range(self.pop_size): # run optimization step for each particle
                    param = (self.particles[i], self.velocities[i], self.pbest[i], self.gbest)
                    self.particles[i], self.velocities[i], self.pbest[i], cost = self._optimization_step(param)
                    # immediately update global best in case we got a better particle than previous best
                    if cost < gbest_cost:
                        gbest_cost = cost
                        self.gbest = self.particles[i].copy()
                if verbose:
                    print(f'step {it:4d}: best cost = {self.cost(self.gbest)}, best perm = {self.full_particle(self.gbest)}')

    def _optimization_step(self, param):
        particle, velocity, pbest, gbest = param
        # save particle because we will compute velocity at the end
        old_particle = particle.copy()

        # apply formula: v(k+1) = [inertia * v(k)] + [personal * rand() * (p(i) - x(i))] + [social * rand() * (g - x(i))]

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
        particle = op_perm_fix(x=particle, P=self.precedences)

        # compute velocity that transforms old_particle into self.patricles[i]
        velocity = op_perm_sub_perm(particle, old_particle)

        cost = self.cost(particle)

        # update personal best in case we got a better particle than previous personal best
        if cost < self.cost(pbest):
            pbest = particle.copy()

        return particle, velocity, pbest, cost

    @staticmethod
    def lists_are_equal(A, B):
        nA = len(A)
        nB = len(B)
        if nA != nB: return 0
        for i in range(nA):
            if A[i] != B[i]:
                return 0
        return 1