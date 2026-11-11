"""Original notebook dynamics, extracted without changing the update or RNG order.

Source: notebooks/Simulator.ipynb, code cell 0. No plotting dependency.
The core and simulator function bodies are preserved exactly.
"""
import numpy as np
from numba import njit

# ==========================================
# 1. Initialization
# ==========================================

@njit
def initialize_lattice(L):
    lattice = np.empty((L, L), dtype=np.int8)

    for i in range(L):
        for j in range(L):
            lattice[i, j] = 1 if np.random.random() < 0.5 else -1

    return lattice


# ==========================================
# 2. Optimized Metropolis Sweep
# ==========================================

@njit
def _metropolis_sweep_fast(lattice, T, h, J, spin_sum):
    L = lattice.shape[0]

    for _ in range(L * L):
        x = np.random.randint(0, L)
        y = np.random.randint(0, L)

        s = lattice[x, y]

        neighbors = (
            lattice[(x + 1) % L, y]
            + lattice[(x - 1) % L, y]
            + lattice[x, (y + 1) % L]
            + lattice[x, (y - 1) % L]
        )

        dE = 2.0 * s * (J * neighbors + h)

        if dE <= 0.0 or np.random.random() < np.exp(-dE / T):
            lattice[x, y] = -s
            spin_sum -= 2 * s

    return spin_sum


# Optional: compatible standalone sweep function
@njit
def metropolis_sweep(lattice, T, h=0.0, J=1.0):
    _metropolis_sweep_fast(lattice, T, h, J, 0)
    return lattice


# ==========================================
# 3. External Magnetic Field
# ==========================================

@njit
def External_Field(t, h0, period):
    return h0 * np.sin(2.0 * np.pi * t / period)


# ==========================================
# 4. Compiled Simulation Engine
# ==========================================

@njit
def _simulation_core(lattice, random_start,
                     T, h0, period, n, J, seed):

    # Seed Numba's internal random generator
    np.random.seed(seed)

    L = lattice.shape[0]
    N = L * L

    if random_start:
        lattice = initialize_lattice(L)

    spin_sum = 0
    for i in range(L):
        for j in range(L):
            spin_sum += lattice[i, j]

    total_mcs = n * period

    h_values = np.empty(total_mcs, dtype=np.float64)
    m_values = np.empty(total_mcs, dtype=np.float64)

    for t in range(total_mcs):
        h = External_Field(t, h0, period)

        spin_sum = _metropolis_sweep_fast(
            lattice, T, h, J, spin_sum
        )

        h_values[t] = h
        m_values[t] = spin_sum / N

    return h_values, m_values


# ==========================================
# 5. User-Facing Simulator
# ==========================================

def simulator(L=40, T=2.0, h0=0.5, period=100,
              n=10, lattice=None, seed=None, J=1.0):

    if L < 2 or T <= 0 or period < 1 or n < 1:
        raise ValueError("Check L, T, period and n.")

    if seed is None:
        seed = int(
            np.random.default_rng().integers(0, 2**31)
        )

    if lattice is None:
        initial = np.empty((L, L), dtype=np.int8)
        random_start = True
    else:
        initial = np.asarray(lattice)

        if initial.shape != (L, L):
            raise ValueError("Initial lattice shape must be (L, L).")

        if not np.all((initial == 1) | (initial == -1)):
            raise ValueError("Spins must be +1 or -1.")

        initial = np.array(initial, dtype=np.int8, copy=True)
        random_start = False

    return _simulation_core(
        initial, random_start,
        T, h0, period, n, J, int(seed)
    )


def initial_lattice(L, state):
    """Select the original notebook's cell-24 initialization convention.

    Random means None: the original core initializes after seeding Numba.
    """
    if state == "all-up":
        return np.ones((L, L), dtype=np.int8)
    if state == "all-down":
        return -np.ones((L, L), dtype=np.int8)
    if state == "random":
        return None
    raise ValueError(f"Unknown state: {state}")
