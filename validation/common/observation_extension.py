# Executed inside the original notebook namespace; no replacement sweep.
@njit
def energy_per_spin(lattice, h=0.0, J=1.0):
    """只读取构型；周期边界下每条键计算一次，不调用随机数。"""
    L = lattice.shape[0]
    E = 0.0
    for i in range(L):
        for j in range(L):
            s = lattice[i, j]
            E -= J * s * (
                lattice[(i + 1) % L, j]
                + lattice[i, (j + 1) % L]
            )
            E -= h * s
    return E / (L * L)

@njit
def _simulation_core(lattice, random_start,
                     T, h0, period, n, J, seed, e_values=None):

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

        # 可选观测：记录本次 sweep 完成后、同一外场 h 下的能量。
        if e_values is not None:
            e_values[t] = energy_per_spin(lattice, h, J)

    return h_values, m_values

def simulator(L=40, T=2.0, h0=0.5, period=100,
              n=10, lattice=None, seed=None, J=1.0,
              record_energy=False):

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

    # 缓冲区只在请求能量时分配；原核心仍返回 (h, m)。
    e_values = (
        np.empty(n * period, dtype=np.float64)
        if record_energy else None
    )
    h_values, m_values = _simulation_core(
        initial, random_start,
        T, h0, period, n, J, int(seed), e_values
    )

    if record_energy:
        return h_values, m_values, e_values
    return h_values, m_values
