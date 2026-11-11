# Figure and data provenance

## Final-paper figures

The three images displayed in the root README come directly from the unchanged [final PDF](../paper/research_note.pdf): Figure 6 (PDF page 20), Figure 12 (page 27), and Figure F1 (page 30). They were extracted from the PDF's embedded images at native resolution without redrawing curves. [Extraction records and hashes](../assets/figures/README.md) distinguish them from new simulation output.

## Animated demonstrations

The [eight-animation gallery](../assets/demos/notebook/README.md), its source-cell archive, previews, manifests, and GIF files are preserved. These are earlier illustrative exports; they were not rerendered during this portfolio update. They accompany the research story and do not replace quantitative figures or establish equilibration.

## Historical exploratory plots and data

The files in `assets/results/`, `assets/validation/`, and `results/validation_L40_T2_energy.npz` remain unchanged. They come from the earlier `tools/generate_demo_assets.py` workflow and are not substituted for final-paper results. [Archived generation notes](../archive/notes/legacy_figures_and_methods.md) document their settings. The legacy generator can overwrite its own old outputs; it is not the new reproduction entry point.

## New reproduction outputs

The [period-scan script](../scripts/reproduce_period_scan.py) matches settings recovered from notebook cell 5 for Figure 6. Only its explicitly labeled smoke mode was executed for this update. [Cached smoke measurements](../results/reproduction_checks/smoke_20261110/) are software-check artifacts, not additions to the paper's physical evidence. Full-run output is created in a separate directory on request.

Missing original machine-readable measurements and execution metadata prevent a claim of exact numerical recovery of every published figure. See [reproducibility](reproducibility.md) and [validation status](validation_status.md).
