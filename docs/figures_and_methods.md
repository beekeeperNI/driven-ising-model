# Figures and numerical-method notes

The project archive includes the original figures and animations generated from `Simulator.ipynb`.

| Figure | Source in original notebook | Interpretation |
| --- | --- | --- |
| Period area scan | old cell 3 | L=40, T=2, h0=0.5; mean absolute trapezoidal loop integral |
| Selected hysteresis loops | old cell 4 | P=10,125,300; qualitative |
| Temperature-period scan | old cell 9 | Same absolute loop integral convention |
| Finite-size comparison | old cell 12 | Signed work `−Σm Δh`, and absolute cycle-averaged magnetization |
| Temperature field response GIF | old cell 1 | External-field **step**, not sinusoidal driving |
| Hysteresis GIFs | old cell 2 | Existing `build_multi_cycle_animation` and simulator at P=50,125 |

## Critical observable caveat

The original cells mix several distinct quantities: mean absolute single-cycle loop integrals, mean signed work `−∮m dh`, and sometimes the integral of phase-averaged loops. These are not interchangeable in finite noisy systems. Before writing a quantitative conclusion, standardize the sign, sampling time, discretization of the integral, burn-in protocol, and seed averaging.

The field is updated at the beginning of each MCS and magnetization recorded after the sweep. One MCS is L² random-site flip attempts; this is algorithmic time and has no calibrated physical-time conversion.
