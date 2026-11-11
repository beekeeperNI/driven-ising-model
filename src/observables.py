"""Distinct observables for the notebook's post-sweep recording convention.

Cycle functions require complete cycles starting at field phase zero, as
returned by simulator(). They return per-cycle values; discard burn-in first.
"""
import numpy as np


def _spins(lattice):
    a = np.asarray(lattice)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or a.shape[0] < 2:
        raise ValueError("Expected a square lattice with L >= 2.")
    if not np.isin(a, [-1, 1]).all():
        raise ValueError("Spins must be -1 or +1.")
    return a


def magnetization(lattice):
    """Magnetization per spin of one configuration."""
    return float(_spins(lattice).mean())


def hamiltonian(lattice, h=0.0, J=1.0):
    """Total H, counting right/down bonds once with periodic boundaries.

    L=2 retains the original repeated-neighbor (parallel periodic bond)
    convention, rather than the simple-graph convention.
    """
    s = _spins(lattice).astype(np.int64)
    bonds = s * (np.roll(s, -1, axis=0) + np.roll(s, -1, axis=1))
    return float(-J * bonds.sum() - h * s.sum())


def _cycles(values, period):
    if isinstance(period, (bool, np.bool_)) or not isinstance(period, (int, np.integer)) or period < 1:
        raise ValueError("Period must be a positive integer.")
    a = np.asarray(values, dtype=float)
    if a.ndim != 1 or not len(a) or len(a) % period or not np.isfinite(a).all():
        raise ValueError("Need finite, one-dimensional samples comprising complete cycles.")
    return a.reshape(-1, period)


def _field_and_magnetization(h, m, period):
    fields, mags = _cycles(h, period), _cycles(m, period)
    if fields.shape != mags.shape:
        raise ValueError("Field and magnetization must have matching shapes.")
    return fields, mags


def dynamic_order(m, period):
    """Signed Q_k = mean_j m[kP+j]; one value per complete cycle."""
    return _cycles(m, period).mean(axis=1)


def mean_absolute_dynamic_order(m, period):
    """Mean of |Q_k|, NOT |mean_k Q_k|; pass retained cycles only."""
    return float(np.abs(dynamic_order(m, period)).mean())


def signed_field_work(h, m, period):
    """W_k = -sum_j m_j (h_{j+1}-h_j), with periodic FIELD closure.

    Field jumps occur after the recorded sweep. The final field of each
    complete cycle closes to its first field, matching notebook cells 23/24.
    For sinusoidal driving this is the next-cycle field up to roundoff.
    This is signed protocol work, not an absolute geometric loop integral.
    """
    fields, mags = _field_and_magnetization(h, m, period)
    dh = np.roll(fields, -1, axis=1) - fields
    return -np.sum(mags * dh, axis=1)


def absolute_hysteresis_integral(h, m, period):
    """A_k = abs(-sum_j (m_j+m_{j+1})/2 * (h_{j+1}-h_j)).

    Closes both field AND magnetization within each cycle, following cell 5's
    loop_area and cell 24. Average these A_k only AFTER the absolute value.
    It differs from both abs(W_k) and area of a phase-averaged loop.
    """
    fields, mags = _field_and_magnetization(h, m, period)
    dh = np.roll(fields, -1, axis=1) - fields
    midpoint = (mags + np.roll(mags, -1, axis=1)) / 2
    return np.abs(-np.sum(midpoint * dh, axis=1))
