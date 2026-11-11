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

The full figures V1 and V2, plus F1–F3, are discussed in the research note. Figures 6, 12, and F1 are now available as [lossless image extractions](../assets/figures/README.md). These image files do not supply their original machine-readable measurements.

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

- The final PDF is published unchanged. Deposit the matching final LaTeX project if it becomes available.
- Add the exact scripts/data/manifests behind every final report figure; the earlier PNGs are not guaranteed to use the same parameters and averaging protocol.
- The extracted simulator and focused reproduction script are tested independently. The preserved 25-cell exploratory notebook has not been executed end-to-end in a fresh session; its cell-order dependencies remain documented.
- Validate more long-time dynamics at very short periods, larger lattices, and additional temperatures where scientifically useful.

See [Research Note](../paper/README.md) for abstract and scope and [Main README](../README.md) for the project's current entry point.

## Checks added during the portfolio refactor

These are implementation/reproduction checks, separate from the physical validation summarized above. Thirteen targeted tests pass, including 156 local-energy consistency comparisons, periodic boundaries (including the L=2 repeated-bond convention), all three initial-state choices, fixed-seed reproducibility, cycle-integral signs, absolute-value ordering, and the exact settings recovered from notebook cell 5. Thirty-six seeded h/m trajectories match the original core bitwise in the tested runtime. Original function syntax trees are also unchanged.

The reproduction smoke mode completed four short runs (420 MCS total, L=6). Redrawing its cache reproduced the same statistics without changing raw measurements. It does not test the physical location of the hysteresis peak. The full Figure 6 protocol was not rerun as part of this presentation-focused update.

See [test output](test_results.txt), [check summary and tested versions](quality_checks.json), and [reproduction limitations](reproducibility.md). The earlier exact/periodic-state package remains on [its separate validation branch](https://github.com/beekeeperNI/driven-ising-model/tree/validation/finalize-numerical-validation-20261107/validation); the portfolio branch does not silently merge or reinterpret it.
