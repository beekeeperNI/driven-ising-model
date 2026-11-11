# Reproducibility

The final PDF and 25-cell notebook are preserved research records. The extracted modules and period-scan script isolate the numerical method from interactive plotting and shared notebook globals.

## Recovered principal experiment

The script targets Figure 6 of the final paper. Its protocol is recovered from zero-based notebook cell 5: L=40, T=2, J=1, h0=0.5; periods 10,20,50,75,100,125,150,200,300 MCS; seeds 101,202,303,404,505; 30 cycles per run, discarding 10. The plotted observable is the mean absolute **trapezoidal** loop integral, averaged over retained cycles within each run and then across independent runs. Error bars are standard errors across runs, not across individual sweeps. The same seeds are reused across periods, so cross-period comparisons are paired.

The PDF names this observable and its error convention; its caption does not enumerate all settings. The source cell is therefore the recovered protocol, not a proof that every published pixel came from this exact execution. Original machine-readable Figure 6 measurements and its execution environment are not present on main. A new full run reproduces the recovered experiment, not a certified bitwise reproduction of the published data. No digitized or synthetic reference values are used.

More detailed execution instructions and check results accompany the extracted implementation.

## Installation and execution

Use Python 3.11 or newer with a compatible NumPy/Numba pair. The tested environment is recorded in `docs/quality_checks.json` and the saved smoke-run provenance. From the repository root:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/reproduce_period_scan.py --mode smoke --output results/period_scan_smoke
python scripts/reproduce_period_scan.py --mode full --output results/period_scan_full
```

Smoke mode uses L=6, periods 10 and 25, two seeds, and six cycles with two discarded. It checks the complete pipeline, not the physical conclusions. Full mode is 45 simulations, totaling 169,500 MCS and 271,200,000 attempted spin flips; it is deliberately opt-in. No full physical scan was needed for this refactor.

Each new run requires a new output directory and saves parameters, seeds, the full field/magnetization histories (including burn-in), code hashes, runtime versions, per-run statistics, and a PNG. It refuses to overwrite an existing output directory. Summaries contain absolute trapezoidal integrals, signed work, signed Q, and mean |Q| under separate names. Only the original absolute integral is plotted for the recovered Figure 6 protocol.

Redraw from a saved run without Monte Carlo:

```sh
python scripts/reproduce_period_scan.py --from-cache results/period_scan_full
```

`--from-cache` recomputes summaries and replaces the derived summary/PNG in that directory; raw measurements and parameters are preserved. The supplied [smoke cache](../results/reproduction_checks/smoke_20261110/) is explicitly labeled as a pipeline check and is not paper evidence.

## Extracted implementation and timing

`src/ising.py` copies the function definitions from notebook cell 0 without changing their syntax trees, removing only the plotting import and adding a module description. Its added `initial_lattice` selector follows cell 24: all-up/all-down return explicit arrays; random returns `None`, leaving initialization to the seeded original core. The original notebook stays byte-for-byte unchanged.

- `_simulation_core` seeds Numba's RNG before initializing a random lattice.
- Each sweep attempts L² site selections with replacement; periodic neighbors are unchanged.
- The field is evaluated once before the sweep: h[t]=h0 sin(2πt/P).
- m[t] is recorded after that sweep at the same field; `t=0` is already a post-sweep sample.
- The simulator copies supplied initial arrays. `seed=None` retains the original nondeterministic seed selection.
- J defaults to 1; the existing J parameter is preserved.

Fixed seeds yield bitwise-identical h/m trajectories between the extracted code and original cell in the tested runtime. This is a direct comparison, not an assumption of RNG equivalence. Cross-version or cross-platform bitwise identity is not promised.

## Observable definitions

For each complete phase-aligned cycle:

- Q_k = mean(m_j), the **signed** cycle magnetization.
- Mean absolute dynamic order = mean(|Q_k|); taking the absolute value after averaging Q is a different quantity.
- W_k = −Σ m_j(h_{j+1}−h_j), with periodic **field** closure. It is the work of field jumps after the recorded sweeps, as in cells 23/24.
- A_k = |−Σ (m_j+m_{j+1})/2 · (h_{j+1}−h_j)|, closing field and magnetization within the same cycle, as in cells 5/24. Figure 6 averages A_k across retained cycles and independent runs.

`mean(abs(W_k))`, `mean(A_k)`, and the area of a phase-averaged loop are also different. Cell 23's `all_Aabs_finite` stores the first of these, despite its historical area-related name; the extracted API does not relabel it as a trapezoidal integral. Signed work is not automatically cycle heat unless the appropriate stationary energy balance holds.

The cycle functions require complete cycles starting at the original phase zero. They reject incomplete or mismatched arrays, but cannot infer the physical phase from arbitrary user-supplied samples. L=2 uses the notebook's repeated-neighbor periodic-bond convention; L=1 is unsupported.

## Remaining limits

The whole exploratory notebook has not been rerun end-to-end. Cells 9/10 duplicate an experiment, cell 12 depends on a helper defined later, and several cells reuse names such as L, seeds, and results. Preserving that research record is intentional; the standalone script uses explicit immutable configurations instead.

The repository does not contain machine-readable source measurements and complete execution metadata for every final-paper figure, or the matching final Overleaf project. The exact small-lattice and bounded-driving package previously prepared on [its separate validation branch](https://github.com/beekeeperNI/driven-ising-model/tree/validation/finalize-numerical-validation-20261107/validation) has its own scope and does not supply every later figure. This update neither merges that branch nor treats the older legacy energy data as substitutes for final-paper data.
