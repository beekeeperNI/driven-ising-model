# Repository publishing and maintenance

**Published repository:** https://github.com/beekeeperNI/driven-ising-model

The project currently contains a cleaned copy of the original simulator notebook, exploratory plots, generated GIF demonstrations, a numerical-validation draft, and a reproduction script. The GitHub Action at `.github/workflows/build-assets.yml` rebuilds the visual assets from the shared Metropolis core when its generation script or workflow changes.

## Working locally

```bash
git clone https://github.com/beekeeperNI/driven-ising-model.git
cd driven-ising-model
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tools/generate_demo_assets.py
```

The generator produces GIFs, PNG figures, and raw energy histories in `results/`. It may take several minutes, and the figures are exploratory rather than final validated scientific results.

## Updating the research note

Replace the working draft in `paper/validation_draft.md` with a fully reviewed report when the numerical checks and physical interpretation are complete. Do not confuse this section's older screenshot-derived numerical estimates with the newly regenerated GitHub validation data; compute any reported numbers from `results/validation_L40_T2_energy.npz`.

## Authorship and license

The shared Physics 77 baseline and collaborators' contributions should remain credited. The code and documentation used AI assistance; clarify independent contributions before using the repository as a formal academic work sample. No software license has been selected yet.
