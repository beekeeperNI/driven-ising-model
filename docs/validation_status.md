# Numerical validation: findings, limits, and data provenance

This document distinguishes the **broader tests reported in the final research note** from the **older single-condition validation assets** already present in this repository.

## Findings reported in the November 2026 research note

| Check | Reported evidence | Important limitation |
| --- | --- | --- |
| Metropolis implementation | 444 local-energy differences agree with independent full-Hamiltonian changes; 24 seeded trajectory comparisons unchanged by energy logging. | Checks implementation consistency, not global convergence. |
| Zero-field energy stability | 8 of 12 parameter combinations meet selected practical stability criteria. | Inconclusive for `T=2.27` at `L=20,40,80`, and `T=1.2,L=80`. |
| Exact Boltzmann | On `L=3` and `L=4`, 7/8 energy and 4/8 absolute-magnetization comparisons meet precision targets. | Only two conditions pass every additional burn-in, measurement, and drift test. |
| Periodic-state checks | For `L=40,T=2,h0=0.5`, `P=125,300` supported by selected stability criteria. | `P=10` remains inconclusive even after prolonged observation. |
| Hysteresis response | Signed work peaks near `P=125` on the period grid; comparisons with neighboring periods are positive within reported intervals. | Not a continuous optimization of the peak and not validation of every temperature/size. |
| Finite-size reliability | At `P=50,T=2`, additional 3,000-MCS burn-in / 6,000-MCS measurement tests with eight seeds per initial state preserve substantial size variation in mean absolute `Q`. | Only three sizes and finite time windows; no thermodynamic-limit claim. |

The full figures V1 and V2, plus F1–F3, are discussed in the research note. The final paper figures and their precise source data are **not yet published as separate files in this repository**.

**Observables:** The early period/temperature scans use the mean absolute trapezoidal cycle integral. The dedicated work checks and finite-size scan use signed discrete field work. Do not interchange them or infer dissipation from a mean absolute integral without qualification.

**Confidence intervals:** The report uses independent-run summaries and approximate pointwise intervals. Success or failure at a chosen numerical tolerance is not a mathematical proof of reaching a steady state.

## Historical single-condition energy experiment (already in GitHub)

At `L=40,T=2,J=1,h=0` with periodic boundaries, a separate generation script produced eight new runs per initial-state group, 10,000 MCS each, with the first 5,000 discarded. The source is [`tools/generate_demo_assets.py`](../tools/generate_demo_assets.py); raw histories are in [`results/validation_L40_T2_energy.npz`](../results/validation_L40_T2_energy.npz).

Available plots:

- [Raw trajectories](../assets/validation/01_raw_energy_L40_T2.png)
- [250-MCS block relaxation](../assets/validation/02_block_relaxation_L40_T2.png)
- [Run-wise retained means](../assets/validation/03_retained_energy_L40_T2.png)
- [Late drift](../assets/validation/04_late_drift_L40_T2.png)

These are regenerated **historical exploratory** results and should not be cited as the source for the final note's multi-temperature tests. The earlier screenshot-derived approximate means of -1.7468 and -1.7463 were not computed from these regenerated runs.

## Outstanding reproducibility work

- Publish final PDF and, if available, the matching final LaTeX project.
- Add the exact scripts/data/manifests behind every final report figure; the earlier PNGs are not guaranteed to use the same parameters and averaging protocol.
- Run the updated 25-cell notebook in a fresh environment, resolve any cell-order dependencies, and document failed cells or software version requirements.
- Validate more long-time dynamics at very short periods, larger lattices, and additional temperatures where scientifically useful.

See [Research Note](../paper/README.md) for abstract and scope and [Main README](../README.md) for the project's current entry point.