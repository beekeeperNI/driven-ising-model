# Numerical validation of the driven two-dimensional Ising simulator

## A. Numerical methodology

We tested the existing chain `simulator → _simulation_core → _metropolis_sweep_fast`, preserving its stochastic update. Each Monte Carlo sweep (MCS) attempts L² flips at sites sampled with replacement, with periodic boundaries and acceptance min[1, exp(−ΔE/T)]. We use J=kB=1. The field is set once before each sweep; magnetization is recorded afterwards at that field. Validation executes only the original definition cell and passes explicit experiment configurations, avoiding execution-order dependence from later notebook cells that reuse global parameters.

The existing Part 1 energy observer was reused; it consumes no random numbers. Independent Hamiltonian calculations verified 444 single-spin energy differences. Twenty-four seeded comparisons, spanning equilibrium/driven fields and both initializations, reproduced the original magnetization trajectories exactly with observation enabled. These checks support implementation consistency, not universal equilibration.

Uncertainties are approximate pointwise 95% Student-t intervals across independent-run averages, rather than across correlated sweeps or cycles. Within-run window comparisons use paired differences; initial-state comparisons use Welch intervals. A practical stability target is supported only when the entire difference interval lies within ±ε; an interval wholly beyond that band indicates a detectable discrepancy at that resolution; other outcomes are inconclusive. Targets were fixed before these runs. Multiple comparisons and selective extensions make these descriptive diagnostics, not a simultaneous 95% certification.

## B. Equilibrium verification

**Existing equilibration results.** Part 1 is preserved without new simulation: eight of twelve combinations at L=20,40,80 and T=1.2,2.0,2.27,3.2 supported the energy-statistics criterion ε=0.005 per spin. T=2.27 at every size and T=1.2,L=80 remained inconclusive. The latter included prolonged random-start energy plateaus. These results assess finite-time energy stability; inconclusive outcomes are not algorithm failures or detected differences between equilibrium distributions.

**Exact finite-system benchmark.** Independent graph-based Hamiltonian enumeration covered all 512 configurations at L=3 and 65,536 at L=4, at all four temperatures. Shifted Boltzmann weights gave Z, mean energy, mean absolute magnetization and energy probabilities including degeneracies. Counts, normalization, spin-inversion symmetry and all-up energies H=−2L² were checked. Each Monte Carlo value was compared only with the exact value at the same L and T.

Sixteen random-start runs began with 5,000 discarded and 20,000 retained MCS. A single extension to 10,000 discarded and 80,000 retained MCS was allowed when a residual or sensitivity interval exceeded its target. The six non-cold cases required this extension; all stages are retained. Targets εe=0.004 and ε|m|=0.001 correspond to 0.1% of the conventional bounding spans e∈[−2,2] and |m|∈[0,1] and are exploratory precision choices, not physical constants. They do not reuse the Part 1 energy tolerance for magnetization.

Final direct residual intervals support energy precision in 7/8 cases and absolute-magnetization precision in 4/8; both in 4/8. Only the two T=1.2 cases satisfy every residual, burn-in, length and drift criterion. At L=3,T=3.2, Δe=−0.002460±0.001847 and Δ⟨|m|⟩=+0.000995±0.000848: both nominal intervals exclude zero. This unsuccessful exact comparison remains unresolved, although neither interval lies wholly outside its practical tolerance. No further extension was made to obtain a pass. At T=2, energy-distribution total-variation distances are 0.000310 (L=3) and 0.000535 (L=4); these are descriptive distances, with no asserted distribution-wide pass threshold.

Agreement across energy, magnetization and energy probabilities supports sampling of the intended finite-system Boltzmann statistics. Energy alone can hide incorrect configuration probabilities or magnetization sampling. Persistent deviations could indicate update, boundary, normalization or equilibration problems; these tests do not identify a unique cause. Enumeration scales as 2^(L²): already L=20 requires about 2.6×10^120 states. Small-system checks therefore complement, but cannot replace, larger-system finite-time diagnostics.

**Onsager–Yang reference.** No new large-lattice equilibrium runs were made. Existing Part 1 magnetization arrays were compared with m∞=[1−sinh⁻⁴(2/T)]^(1/8) below Tc=2/ln(1+√2), and zero above it ([Yang, 1952](https://journals.aps.org/pr/abstract/10.1103/PhysRev.85.808)). Low-temperature ordering, finite-size rounding and positive finite-system ⟨|m|⟩ above Tc are visible. The large random-start uncertainty at L=80,T=1.2 and critical-region limitations are preserved. Four temperatures and three sizes provide a reference comparison, not a thermodynamic-limit extrapolation or precise critical test.

## C. Nonequilibrium reliability

New driving tests used L=40,T=2,h0=0.5. Signed field work is Wk=−Σj mj(hj+1−hj), with field jumps after the recorded sweep and periodic field closure. The earlier absolute trapezoidal loop integral is retained separately. W is protocol work; interpreting it as cycle heat requires an appropriate stationary energy balance. Qk is the mean magnetization over each complete aligned cycle, and |Qk| is taken before averaging; signed Qk is retained.

A nine-period scan used eight random-start seeds with 20 discarded and 60 retained cycles. Both work definitions peak at the sampled P=125. Paired signed-work contrasts are W125−W100=0.04149±0.00733 and W125−W150=0.02063±0.00412, supporting a local maximum on this grid, not its exact continuous location.

Targeted checks at P=10,125,300 additionally compared all-up starts, later burn-in, measurement length and cycle drift. Resolution targets were 0.02 for work per spin and 0.02 for ⟨|Q|⟩. P=125 and 300 supported all tested criteria; random-start W=1.67389±0.00291 and 1.41191±0.00701, respectively. P=10 remained inconclusive after the only extension to 50 discarded plus 150 retained cycles, especially for random-start |Q| and window sensitivity.

## D. Limitations

Equilibrium checks do not establish periodic steady states. P=20,50,75 pilot window checks also remain inconclusive; other non-target periods lack initial-state comparisons. Limited seeds, adaptive sampling and rare unvisited states constrain uncertainty interpretation. The thermodynamic-limit plot retains approximate, unbounded t intervals, including one extending above the physical magnetization range. No dynamic phase transition, critical exponent, calibrated physical time, or general driven T/L dependence is established.

## E. Final assessment

The standardized work definition and the sampled non-monotonic period dependence around P=125 are sufficiently supported for qualified presentation. P=125 and 300 have additional finite-budget reliability evidence. Short-period transients, the stated exact-benchmark residuals, and the four original Part 1 cases must remain explicit limitations. The evidence supports a bounded numerical assessment, not validation of every simulation under every condition.
