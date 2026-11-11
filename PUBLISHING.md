# Publishing and maintenance

**Repository:** https://github.com/beekeeperNI/driven-ising-model

## Publication status — 10 November 2026

- **Updated on GitHub:** the latest 25-cell `notebooks/Simulator.ipynb` (outputs cleared), a reorganized project README ending in **Further Research Directions**, the research-note abstract/reading guide, numerical-validation overview, updated dependency list, and revised animation provenance notes.
- **Still to upload:** the supplied 35-page **final PDF**, intended as `paper/research_note.pdf`. The GitHub connector supports text-file updates but did not expose a way to transfer the attached binary PDF directly.
- **Not included as final source:** the complete latest Overleaf `.tex` tree. An older LaTeX export exists in the conversation files but is not necessarily identical to the current 35-page PDF.

### One remaining PDF upload

1. Download the final `research_note.pdf` from the project handoff in the ChatGPT conversation.
2. Open [the paper folder](https://github.com/beekeeperNI/driven-ising-model/tree/main/paper) in GitHub.
3. Select **Add file → Upload files** (or **Upload files**), and upload the file as `paper/research_note.pdf`.
4. Commit on `main`. Confirm the file appears and renders in GitHub.
5. In `README.md` and `paper/README.md`, replace the temporary “PDF upload pending” notice with a link to `paper/research_note.pdf`.

If the final Overleaf project is shared later, publish its matching `.tex` and `figures/` files together; do **not** attach the earlier LaTeX export as though it produced the newly edited PDF.

## Code and animation consistency

The updated notebook was uploaded with all **25 latest code cells intact**, but generated notebook outputs were cleared to reduce size. The GIF gallery remains a valid archive of earlier demonstrations; those animations have **not** been rerendered from the new notebook and should not be treated as final numerical validation.

Run the notebook in a clean environment before advertising it as turnkey reproducible:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/Simulator.ipynb
```

Some cells depend on preceding variable definitions and some parameters may be computationally expensive. `%matplotlib widget` requires `ipympl`, now listed in `requirements.txt`.

The historical generator `tools/generate_demo_assets.py` regenerates *exploratory* figures, not the final-paper figure suite. Any future publication-quality figure should be accompanied by its exact source script, parameter manifest, random seeds, raw data, and code revision.

## Scientific conventions

- The older driving-period and temperature figures use an **absolute trapezoidal loop integral**.
- The dedicated driven validation and finite-size work use **signed discrete field work**.
- `P=10` long-time behavior was inconclusive under the reported stability tests.
- Three lattice sizes and finite observation windows do not prove a thermodynamic limit.

These distinctions are explained in the [main README](README.md), [paper overview](paper/README.md), and [validation documentation](docs/validation_status.md).

## Project provenance

The Physics 77 capstone supplied a collaborative starting point, including Group A's periodic-drive focus. The later research note includes personal extension, numeric checks, and AI-assisted coding, visualization, and editing. The repository does not claim that every component of the group baseline was solely authored. No code reuse license has been granted; choose an explicit license only if redistribution is intended.
