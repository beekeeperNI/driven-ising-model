# Research Note

**Nonequilibrium Dynamics of the Two-Dimensional Ising Model Under Periodic Magnetic Driving**  
**Fengrui Yang** · November 2026 · 35-page Undergraduate Computational Physics Research Note

**[Read the complete Research Note (PDF)](research_note.pdf)** — 35 pages, November 2026.

## Abstract

In this study, we investigate the nonequilibrium behavior of the two-dimensional Ising model under a periodically oscillating external magnetic field using Metropolis Monte Carlo simulations. We focus on how the magnetization dynamics and hysteresis response depend on the driving period, temperature, and lattice size.

We observe a non-monotonic dependence of the hysteresis response on the driving period, with the largest response occurring at an intermediate period. As the temperature decreases, the period corresponding to the maximum response shifts toward larger values, consistent with a slower magnetization reversal process. By introducing the dynamic order parameter, we also distinguish persistent magnetization bias under fast driving from the more symmetric magnetization reversal observed at longer periods.

Our finite-size investigation suggests that the hysteresis response is relatively insensitive to lattice size within the investigated range, while the dynamic order parameter exhibits stronger size dependence. Numerical validation supports the simulation implementation and several qualitative findings, although limitations in equilibration and periodic steady-state sampling remain.

These results illustrate how thermal fluctuations, driving timescales, and finite-size effects influence the nonequilibrium dynamics of the Ising model.

## Reading guide

The research note comprises a cover, abstract, and the main text on:

1. Project background and the Ising/Metropolis model.
2. Numerical validation: implementation checks, exact Boltzmann comparison, Onsager–Yang reference, periodic-state diagnostics.
3. Main physical investigations: driving period and hysteresis, dynamic order and initial states, temperature and period, and finite size.
4. Limitations and scope of conclusions, conclusion, and references.

Readers primarily interested in physics results can begin at **The Driving Period**, but the validation section is important when interpreting how strong each conclusion is.

## Other project materials

- [Latest 25-cell simulator](../notebooks/Simulator.ipynb) — source code preserved and generated outputs removed.
- [Animation gallery](../assets/demos/notebook/README.md) — qualitative demonstrations associated with the research questions.
- [Numerical validation documentation](../docs/validation_status.md).
- [Repository README](../README.md) — current findings, restrictions, provenance, and **Further Research Directions**.

The existing [`validation_draft.md`](validation_draft.md) is a **historical draft**, not the final manuscript.

The final PDF is stored in this folder as [`research_note.pdf`](research_note.pdf). The matching final Overleaf source has not been deposited in the repository; no earlier LaTeX export is represented as the authoritative source.
