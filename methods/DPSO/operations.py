import math
import random

def check_permutation(perm, lowest=1):
    """
    Permutation a is valid if it has length n > 1 and contains all numbers from lowest to n+lowest.
    :param perm: the permutation to be checked.
    :param lowest: the lwoest value for permutation (can be 0 or 1).
    :return: True is a is a valid permutation or False otherwise.
    """
    assert lowest in [0, 1], '[operations::check_permutation] lowest should be 0 or 1'
    n = len(perm)
    if n <= 1:
        return False
    for x in range(lowest, n + lowest):
        if x not in perm:
            return False
    return True

def random_round(x):
    """
    Randommy round x to floor(x) or ceil(x) with probability 0.5.
    :param x: the number to be rounded.
    :return: floor(x) or ceil(x) with probability 0.5.
    """
    u = random.uniform(a = 0.0, b = 1.0)
    return math.floor(x) if u < 0.5 else math.ceil(x)


def op_perm_sub_perm(a, b, allow_checks):
    """
    Performs operation velocity = perm - perm.
    Performs subtraction of two permutations. The result is velocity vector.
    A velocity vector is a list of tuples (i,d) where i=node and d=displacement.
    :param a: the first permutation.
    :param b: the second permutation.
    :param allow_checks: flag to check whether parameters are valid. It may slow algorithm if set to True.
    :return: v = a - b = list of insertion moves that need to be applied to b to obtain a.
    """
    if allow_checks:
        assert check_permutation(a), '[operations::difference] first permutation is not valid one'
        assert check_permutation(b), '[operations::difference] second permutation is not valid one'
        assert len(a) == len(b), '[operations::difference] both permutations must have same size'

    velocity = []
    for j, x in enumerate(b):
        i = a.index(x) # index of element x in a
        if i != j:
            velocity.append((x, i-j))
    return velocity

def op_scalar_mul_velocity(c, v):
    """
    Performs operation velocity = scalar * velocity.
    Performs multiplication w = c * v in the following way:
    if c < 1: truncate set of moves v s.t. result has size |w| = ceil(c * |v|) by randomly choosing |w| out of |v|.
    if c > 1: we obtain w = [(j_k, rr(c*d_k)) | k = 1..|v|], where rr(a) = floor(a) or ceil(a) with uniform prob 0.5.
    :param c: the constant to multiply the velocity with.
    :param v: the velocity vector to be multiplied with c.
    :return: a new velocity set w = c * v
    """
    assert c > 0, '[operations::scalar_multiplication] the constant c must be positive'
    if c < 1:
        n = len(v)
        size = math.ceil(c * n)
        indexes = random.sample(range(n), size)
        w = [v[i] for i in indexes]
        return w
    if c > 1:
        w = [(i, random_round(c * d)) for (i, d) in v]
        return w
    return v

def op_perm_sum_velocity(x, v):
    """
    Performs operation perm = perm + velocity.
    Apply insertion moves (IMs) in v to x.
    :param x: the permutation to be modified by v.
    :param v: the insertion moves (IMs) to be applied to x.
    :return: y = x + v = permutation x modified by v.
    """
    n = len(x)
    y = x.copy()
    for node, disp in v: # disp = displacement
        node_index = y.index(node)
        del y[node_index]
        insert_position = max(0, node_index + disp) if disp < 0 else min(n-1, node_index + disp)
        y.insert(insert_position, node)
    return y

def op_perm_fix(x, R):
    """
    Force x satisfy precedence constraints in R by changing as less as possible the order of nodes in x.
    In case x already satisfies precedence constraints in R, then it won't be modified in any way.
    :param x: the permutation to be modified to respect precedence constraints in R.
    :param R: the precedence constraints: R = {(i,j) meaning that i must precede j in permutation}.
    :return: y = the permutation obtained from x that respects now precedence constraints R.
    """
    n = len(x)
    y = x.copy()
    k = n - 1
    while 1 <= k:
        j = y[k]
        f = 0
        for h in range(n): # the paper goes from 1 to n-1 (if there are problems, recheck!)
            i = y[h]
            if (i, j) in R and h > f:
                f = h
        if f < k:
            k = k - 1
        else:
             del y[k]
             y.insert(f, j)
             k = f - 2
    return y