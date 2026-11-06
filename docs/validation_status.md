# Equilibrium validation: evidence and open questions

**Current scope:** `L=40`, `T=2`, `J=1`, `h=0`, periodic boundary conditions. This is an intermediate project note, not a claim of global convergence.

Eight independent runs per initial-state group (all-up and random) are newly generated from the repository's original Metropolis update function, with 10,000 MCS and the first 5,000 discarded. Plotted energy variable: `e(t) = H(t)/L²`. Source: `tools/generate_demo_assets.py`; underlying raw histories: `results/validation_L40_T2_energy.npz`.

1. **Raw energy trajectories:** one run from each initial condition shows markedly different initial relaxation followed by similar energy ranges.
2. **Block relaxation:** 250-MCS means averaged over eight runs per group show their energy trends becoming similar.
3. **Retained means:** the pre-repository screenshots showed approximate means −1.7468 (all-up) and −1.7463 (random). Those values are historical screenshot readings, not necessarily the means of the newly generated figures. For current statistics, use the raw NPZ file.
4. **Late drift:** differences between second and first halves of retained intervals are consistent with zero within plotted SEM.

These plots support initial-state insensitivity of the **energy observable only** under the tested conditions. They do not establish convergence of the entire distribution, equilibration at all temperatures or sizes, or correct Boltzmann statistics.

**Data provenance:** The four original validation graphics are available in the accompanying project archive, but the raw validation time series and the generating notebook were not included in the original uploaded `Simulator.ipynb`.

## Remaining checks

- Inspect both `|m|` and energy over multiple temperatures and lattice sizes, especially near `Tc ≈ 2.269`.
- Benchmark small-lattice equilibrium statistics against exact enumeration, and compare finite-size magnetization with Onsager–Yang theory.
- Under driving, evaluate cycle-by-cycle observables, burn-in, seed variability, field update interval, and the definition of signed work.
