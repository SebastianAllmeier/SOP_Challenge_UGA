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
        print(f'creating particle {index} took {time_end - time_start:.4f} seconds')

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

    def optimize(self, iterations, parallelize=False, verbose=True) -> None:
        """
        Runs Discrete Particle Swarm Optimization procedure
        :param iterations: total number of iterations to run the algorithm for
        :param parallelize: flag that indicates whether to use multiprocessing
        :param verbose: flag that indicates whether to prin information
        :return:
        """
        # with mp.Pool(mp.cpu_count() - 1) as pool:
        if verbose:
            print(f'step {0:4d}: best cost = {self.cost(self.gbest)}, best perm = {self.full_particle(self.gbest)}')
        for it in range(1, iterations + 1):
            for i in range(self.pop_size):
                # save particle because we will compute velocity at the end
                old_particle = self.particles[i].copy()

                # applyformula: v(k+1) = [inertia * v(k)] + [personal * rand() * (p(i) - x(i))] + [social * rand() * (g - x(i))]

                # compute each term inside square brackets
                velocity_inertia = op_scalar_mul_velocity(c=self.coef_inertia, v=self.velocities[i])

                diff_velocity_personal = op_perm_sub_perm(self.pbest[i], self.particles[i])
                velocity_personal = op_scalar_mul_velocity(self.coef_personal * U(0, 1), diff_velocity_personal)

                diff_velocity_social = op_perm_sub_perm(self.gbest, self.particles[i])
                velocity_social = op_scalar_mul_velocity(self.coef_social * U(0, 1), diff_velocity_social)

                # apply each velocity individually to particle because we don't have a velocity + velocity operator
                self.particles[i] = op_perm_sum_velocity(self.particles[i], velocity_inertia)
                self.particles[i] = op_perm_sum_velocity(self.particles[i], velocity_personal)
                self.particles[i] = op_perm_sum_velocity(self.particles[i], velocity_social)

                # fix current particle so that it repects precedence constraints
                self.particles[i] = op_perm_fix(x=self.particles[i], P=self.precedences)

                # compute velocity that transforms old_particle into self.patricles[i]
                self.velocities[i] = op_perm_sub_perm(self.particles[i], old_particle)

                cost = self.cost(self.particles[i])

                # update personal best in case we got a better particle than previous personal best
                if cost < self.cost(self.pbest[i]):
                    self.pbest[i] = self.particles[i].copy()

                # update global best in case we got a better particle than previous best
                if cost < self.cost(self.gbest):
                    self.gbest = self.particles[i].copy()
            if verbose:
                print(f'step {it:4d}: best cost = {self.cost(self.gbest)}, best perm = {self.full_particle(self.gbest)}')

    def _optimization_step(self):
        pass