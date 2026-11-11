"""Compare fast and slower magnetic driving with the existing Ising simulator.

Run from the repository root: python examples/quick_demo.py
Defaults: L=40, T=2, J=1, h0=0.5, periods 10/125 MCS, eight cycles,
and seed 101 for each run. Both start all-up, so the initial bias is imposed,
not evidence of spontaneous ordering. No burn-in is discarded: the time plots
show every post-sweep sample; the response plots show cycles 6–8 in order.
Equal cycle counts mean different elapsed MCS. These are illustrative traces,
not convergence-tested measurements. The first run includes Numba compilation.

Optional: --seed 202 --L 30 --T 2.2 --output path/to/new_figure.png
Rerunning replaces only the default demo PNG; other existing files are protected.
"""
import argparse
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ising import initial_lattice, simulator
from src.observables import dynamic_order

DEFAULT_OUTPUT = ROOT / "assets/demos/quick_demo.png"
PERIODS = (10, 125)
CYCLES = 8
H0 = 0.5
J = 1.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--L", type=int, default=40, help="Square lattice side length")
    parser.add_argument("--T", type=float, default=2.0, help="Temperature, kB=1")
    args = parser.parse_args()
    if args.L < 2 or not np.isfinite(args.T) or args.T <= 0:
        parser.error("Use L >= 2 and a finite positive T.")
    if not 0 <= args.seed < 2**32:
        parser.error("Use a seed between 0 and 2**32 - 1.")
    output = args.output.resolve()
    if output.suffix.lower() != ".png":
        parser.error("The output must have a .png extension.")
    if output.exists() and (output != DEFAULT_OUTPUT or DEFAULT_OUTPUT.is_symlink()):
        parser.error("Choose a new output path; existing non-demo files are protected.")
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.85, bottom=0.25,
                        hspace=0.55, wspace=0.25)
    fig.suptitle("Can the magnetization keep up with the field?", fontsize=18, y=0.97)
    fig.text(0.5, 0.925,
             f"L={args.L} · T={args.T:g} · J=1 · h₀=0.5 · all-up start · "
             f"seed={args.seed} per run · 8 cycles", ha="center")
    colors = ("#7c3aed", "#0f9b8e", "#2563eb")

    for row, period in enumerate(PERIODS):
        h, m = simulator(L=args.L, T=args.T, h0=H0, period=period,
                         n=CYCLES, lattice=initial_lattice(args.L, "all-up"),
                         seed=args.seed, J=J)
        time_ax, loop_ax = axes[row]
        # Sample t=0 is recorded after the first sweep at h(0), as in the core.
        time_ax.plot(np.arange(len(m)), m, color="#2563eb", lw=1.6, label="Magnetization m")
        time_ax.plot(np.arange(len(h)), h / H0, color="#d97706", ls="--", lw=1.2,
                     label="Normalized field h/h₀")
        time_ax.set(title=f"P={period} MCS | All 8 cycles",
                    xlabel="Field-time index t (MCS; post-sweep samples)",
                    ylabel="m and h/h₀ (dimensionless)", xlim=(0, len(m) - 1))
        time_ax.legend(loc="lower left", fontsize=9, framealpha=0.9)

        for cycle, color in zip(range(CYCLES - 3, CYCLES), colors):
            # Include the next sample when available; never force a closed loop.
            segment = slice(cycle * period, min((cycle + 1) * period + 1, len(m)))
            loop_ax.plot(h[segment], m[segment], color=color, lw=1.6,
                         label=f"Cycle {cycle + 1}")
        loop_ax.set(title=f"P={period} MCS | Response, cycles 6–8",
                    xlabel="External field h (J=1)", ylabel="Magnetization per spin m",
                    xlim=(-0.55, 0.55))
        loop_ax.legend(loc="center", fontsize=9, framealpha=0.9)
        for ax in (time_ax, loop_ax):
            ax.set_ylim(-1.1, 1.1)
            ax.axhline(0, color="0.65", lw=0.7, zorder=0)
            ax.grid(alpha=0.18)
        q = dynamic_order(m, period)
        print(f"P={period}: {len(m)} MCS; m range [{m.min():.3f}, {m.max():.3f}]; "
              f"signed Q in cycles 6–8: {np.round(q[-3:], 3)}")

    fig.text(0.08, 0.125,
             "Read the plots: a persistent sign of m indicates a finite-window bias. Larger swings show reversals.\n"
             "Separation between outward and return paths in m versus h shows the delayed magnetic response.",
             fontsize=10, linespacing=1.5)
    fig.text(0.08, 0.055,
             "Illustrative trajectories from finite-time Metropolis simulations. These examples show how the magnetization\n"
             "response changes with driving period; they are not convergence-tested steady-state measurements.",
             fontsize=9, color="0.35", linespacing=1.4)
    fig.savefig(output, dpi=160, metadata={"Description":
                f"L={args.L}, T={args.T}, J=1, h0=0.5, P=10/125, cycles=8, "
                f"all-up initial state, seed={args.seed} for both runs; no burn-in discarded."})
    plt.close(fig)
    print(f"Saved figure: {output}")


if __name__ == "__main__":
    main()
