import math
import random
import numpy as np
from typing import List
from .operations import op_perm_sum_velocity, op_perm_fix

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

        lower_bound_velocity = math.floor(self.particle_size / 4.)
        upper_bound_velocity = math.floor(self.particle_size / 2.)

        lower_bound_displacement = math.floor(-self.particle_size / 3.) # floor(- n / 3)
        upper_bound_displacement = math.floor(self.particle_size / 3.) # floor(+ n / 3)

        set_velocity = range(lower_bound_velocity, upper_bound_velocity + 1) # to generate velocities
        set_displacement = range(lower_bound_displacement, upper_bound_displacement + 1) # to generate displacements
        set_nodes = range(self.particle_size) # to generate nodes

        seed_perm = random.sample(set_nodes, self.particle_size)  # random permutation

        for _ in range(self.pop_size): # for each particle
            velocity_size = random.sample(set_velocity, 1)[0] # generate no. of insertion moves (IMs)

            nodes = random.sample(set_nodes, velocity_size) # generate nodes
            displacements = random.sample(set_displacement, velocity_size)

            velocity = list(zip(nodes, displacements))
            self.velocities.append(velocity)

            unfixed_particle = op_perm_sum_velocity(x=seed_perm, v=velocity)
            fixed_particle = op_perm_fix(x=unfixed_particle, P=self.precedences)
            self.particles.append(fixed_particle)

            self.pbest.append(fixed_particle.copy())
            if self.gbest is None:
                self.gbest = fixed_particle.copy()
            if self.cost(fixed_particle) < self.cost(self.gbest):
                self.gbest = fixed_particle.copy()

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
        c = sum([self.weights_matrix[ x[i] ][ x[i+1] ] for i in range(self.particle_size - 1)])
        return c

    def optimize(self) -> None:
        pass

    """
    TO DO:
        Generate permutations so that start node and end node are in their positions (else cannot compute cost)
        Check if start node and end node are always 0 and n-1
    """