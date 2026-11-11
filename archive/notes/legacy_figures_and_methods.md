# Historical figure-generation notes

These notes describe the earlier exploratory assets, not the final-paper figure extractions. See [current figure provenance](../../docs/figures_and_methods.md).

---

# Figures and numerical-method notes

The separately downloadable project archive contains originally extracted figures and animations. The GitHub `assets/` directory is regenerated from the original notebook's shared Metropolis core by `tools/generate_demo_assets.py`; the new figures use documented seeds and parameters and need not match earlier screenshots pixel-for-pixel.

| Figure | Source in original notebook | Interpretation |
| --- | --- | --- |
| Period area scan | original period-scan method; rebuilt script | L=40, T=2, h0=0.5; 3 seeds, 24 cycles (8 discarded); mean absolute trapezoidal loop integral |
| Selected hysteresis loops | old cell 4 | P=10,125,300; qualitative |
| Temperature-period scan | rebuilt script | Same absolute loop integral convention; selected temperatures, exploratory sampling |
| Finite-size comparison | rebuilt script | Signed work `−Σm Δh` and absolute cycle-averaged magnetization; 3 lattice sizes |
| Temperature field response GIF | existing sweep core | External-field **step**, not sinusoidal driving; newly rendered animation |
| Hysteresis GIFs | existing simulator | Newly rendered three-cycle GIFs at P=50,125 |

## Critical observable caveat

The original cells mix several distinct quantities: mean absolute single-cycle loop integrals, mean signed work `−∮m dh`, and sometimes the integral of phase-averaged loops. These are not interchangeable in finite noisy systems. Before writing a quantitative conclusion, standardize the sign, sampling time, discretization of the integral, burn-in protocol, and seed averaging.

The field is updated at the beginning of each MCS and magnetization recorded after the sweep. One MCS is L² random-site flip attempts; this is algorithmic time and has no calibrated physical-time conversion.

## Reproduction

Run `python tools/generate_demo_assets.py` from the repository root after installing `requirements.txt`. This produces the README GIFs, four exploratory results plots, four energy-equilibration plots, and `results/validation_L40_T2_energy.npz`. The energy runs use the same existing `_metropolis_sweep_fast()` routine and separately compute the full zero-field Hamiltonian after each MCS. This is a new, independent energy-logging wrapper, **not** a rerun of the exact original user-supplied validation notebook.
