# Compact numerical validation package

This directory adds bounded numerical validation to the original simulator. Existing repository files, the simulator notebook, and all previous results are unchanged. Read [REPORT.md](REPORT.md), [the eight-case exact table](part2_exact/table.md), and [unresolved comparisons](UNRESOLVED.md).

## Regenerate figures without simulation

From this directory, with Python and the dependencies below:

```sh
python render.py
python build_tables.py
```

Or open `Validation.ipynb` and run all cells. Its default workflow only reads caches, displays tables and redraws five new figures. `part1_existing/representative_diagnostic.png` is the preserved prior figure. PNG exports are provided at 180 dpi and vector PDF companions are also regenerated. The notebook keeps large outputs external.

## What changed

- `common/original_first_cell.py` freezes the original definition cell, with provenance hashes. The loader normally reads `../notebooks/Simulator.ipynb`, checks its syntax tree against the snapshot, and refuses an unexpected change. A standalone extracted package uses the frozen snapshot.
- `common/observation_extension.py` reuses the previous Part 1 optional energy recorder. `energy_recording.diff` records its difference from the original. The original `_metropolis_sweep_fast` function is reused unchanged. There is no second Metropolis core.
- `part2_exact/benchmark.py` independently enumerates Hamiltonians, executes the original chain, and compares exact and sampled statistics.
- `part3_reference/reuse_part1.py` derives magnetization statistics from existing Part 1 trajectories. No new large-lattice equilibrium runs were made.
- `driving/checks.py` records original magnetization trajectories and computes signed field work, signed cycle Q, per-cycle |Q| and the separate legacy absolute loop integral. These are newly generated driving results, not relabelled older figures.
- `audit.py` checks the original local energy expression against an independent Hamiltonian, observation trajectory preservation and work/Q conventions. `verify_cached.py` recomputes saved statistics from raw new data, checks extension prefixes and verifies prior-source hashes when available.

## Data and provenance

`provenance.json` identifies the original repository commit and code hashes; `environment.json` records the actual numerical runtime. Every new run records its parameters and seeds in compressed NPZ files. Equilibrium arrays store lossless integer total energy H and signed total magnetization M, including discarded sweeps. Driving arrays store signed total M, field samples and cycle observables. Dividing by L² gives per-spin values. The summaries retain every pilot, extension, independent-run mean, interval, count and unsuccessful check. Exact enumeration caches include all configuration identifiers, energies and magnetizations; `exact.json` includes Z, log Z and level degeneracies/probabilities. `MANIFEST.json` provides file hashes.

Part 1's twelve-point grid was available in the user's existing local outputs but **not** in the repository baseline. The repository's older single-case validation uses a different initialization protocol; it has been preserved and is not claimed to be an identical copy of this grid. This package copies the original twelve-point summary byte-for-byte and one existing figure. It stores derived per-run magnetization caches and SHA-256 hashes of the twelve selected source trajectory files. It does not duplicate all 26 old intermediate NPZ files. Those remain unchanged in the user's prior `outputs/parameter_validation/` and prior complete download bundle. Thus GitHub/standalone copies can redraw every final figure, but re-deriving Part 3 from the original large-lattice trajectories requires that prior archive. No missing result was reconstructed by fresh simulation.

## Statistical definitions and finite budget

The unit of uncertainty is an independent run. Student-t intervals use 15 degrees of freedom for the 16-run exact benchmark and 7 for eight-run driving averages; cross-initialization contrasts use Welch degrees of freedom. Window contrasts are paired within a run; across-period contrasts are paired by seed. A reported interval is approximate, pointwise and unadjusted for adaptive stage selection or multiple checks. Successive MCS/cycles are never counted as independent replicates. The final selection is diagnostic, not a formal sequential confidence procedure.

For difference d, half-width c and tolerance ε:

- **Supported at tolerance:** |d|+c ≤ ε.
- **Detectable discrepancy at that resolution:** |d|−c > ε.
- **Inconclusive:** neither condition holds.

Zero exclusion alone indicates nominal evidence against exact equality; it is distinct from the practical-tolerance classification. Wide intervals can be inconclusive even when their central estimates are close. Agreement is never inferred merely from overlapping error bars.

The pre-run Part 2 configuration sets εe=0.004 and ε|m|=0.001 (one part in 1000 of the conventional bounding spans e∈[−2,2] and |m|∈[0,1]), with 16 seeds, 5,000+20,000 pilot MCS and at most one 10,000+80,000 extension. Each stage compares the retained mean to exact, later burn-in by 5,000 MCS, first half vs full retained sampling, and second vs first retained half; extended cases also compare with their own pilot. Same-seed extension prefixes are checked exactly. These nested windows are correlated, which is why contrasts are computed before constructing intervals.

The driving configuration fixes εW=0.02 J/spin/cycle and ε|Q|=0.02, exploratory macroscopic resolution targets. Pilots use 80 cycles, discard 20 and compare later burn-in at 40. Only P=10,125,300 can extend once to 200 cycles, discard 50 and compare later burn-in at 100. Length, drift and extension comparisons use paired run summaries. R=8 independent seeds per initial mode; seed identities are reused across periods and accounted for by paired period contrasts. No thresholds were changed to force passing outcomes.

## Reproduce new simulations or run checks

```sh
python audit.py
python verify_cached.py
python part2_exact/benchmark.py --output /path/to/new_empty_exact_directory
python driving/checks.py --output /path/to/new_empty_driving_directory
```

The simulation scripts refuse to overwrite any existing raw NPZ. Parameters are explicit in each script's `CONFIG`; change them only for a clearly named new experiment. Default output directories contain published caches, so an accidental simulation rerun stops rather than replacing data. New output directories contain their own config, raw data and summaries. To rebuild Part 3 from prior data in a new copy with its summary cache removed, run `python part3_reference/reuse_part1.py --part1-data /path/to/parameter_validation`; this never simulates.

## Reading the figures

1. **Exact means:** upper panels show same-L exact and MC averages; lower residual panels expose deviations hidden by the broad vertical scale. Green bands are separate precision targets, not estimated errors. Lines between four temperatures are visual guides.
2. **T=2 energy distribution:** exact probabilities include degeneracy; MC intervals use run-level frequencies. Unobserved rare levels have no inferred zero uncertainty, despite zero-height markers. Total variation is descriptive.
3. **Onsager–Yang:** finite-L |m| is compared with an infinite-system reference, not required to equal it. Hollow markers preserve Part 1 energy-inconclusive labels. They do not certify or reject magnetization stability. Approximate t intervals are not truncated to [0,1].
4. **Period scan:** uses the same pilot protocol at all nine periods. Signed work and the old absolute trapezoidal area remain distinct. P=10's longer diagnostic is not substituted into the common scan.
5. **Cycle diagnostics:** signed W and Q retain individual trajectories; thick curves are ensemble means. The vertical line marks the primary discarded-cycle boundary. A smooth mean does not erase slow individual trajectories.

No unrelated refactor, new Monte Carlo algorithm, Binder analysis or full dynamic-phase-transition study is included.

The bounding-span convention is deliberately independent of L. The exact attainable range can be smaller: on the odd L=3 torus, the maximum energy per spin is 2/3 and minimum |m| is 1/9. The clarification does not change either pre-run tolerance or any classification.
