"""Reproduce the Figure 6 protocol recovered from notebook cell 5.

The full mode matches recovered settings; original figure raw data are missing.
Smoke mode tests the pipeline only and is NOT evidence for the paper's peak.
"""
from pathlib import Path
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import platform
import sys
import time
import importlib.metadata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.ising import simulator
from src.observables import absolute_hysteresis_integral, signed_field_work, dynamic_order


@dataclass(frozen=True)
class ScanConfig:
    mode: str
    L: int
    T: float
    h0: float
    J: float
    periods: tuple
    seeds: tuple
    cycles: int
    burn_cycles: int


FULL = ScanConfig("full", 40, 2.0, 0.5, 1.0,
                  (10, 20, 50, 75, 100, 125, 150, 200, 300),
                  (101, 202, 303, 404, 505), 30, 10)
SMOKE = ScanConfig("smoke", 6, 2.0, 0.5, 1.0, (10, 25), (101, 202), 6, 2)


def summarize(values):
    """Input is independent-run means, never individual MCS/cycles."""
    values = np.asarray(values)
    return dict(mean=float(values.mean()), sem=float(values.std(ddof=1)/np.sqrt(len(values))),
                run_means=values.tolist())


def analyze_cache(directory):
    directory = Path(directory)
    config = json.loads((directory / "parameters.json").read_text())
    rows = []
    for period in config["periods"]:
        with np.load(directory / f"P{period}.npz") as data:
            cut = config["burn_cycles"] * period
            # Recompute all observables from saved ORIGINAL h and m arrays.
            areas, works, qabs, qsigned = [], [], [], []
            for h, m in zip(data["h"], data["m"]):
                h, m = h[cut:], m[cut:]
                areas.append(absolute_hysteresis_integral(h, m, period).mean())
                works.append(signed_field_work(h, m, period).mean())
                q = dynamic_order(m, period)
                qabs.append(np.abs(q).mean()); qsigned.append(q.mean())
            rows.append(dict(period=period,absolute_trapezoidal_integral=summarize(areas),
                             signed_field_work=summarize(works),mean_abs_Q=summarize(qabs),
                             signed_Q=summarize(qsigned)))
    result = dict(mode=config["mode"],source="Notebook cell 5 (zero-based), final PDF Figure 6",
                  comparison="Recovered protocol; original Figure 6 raw measurements unavailable.",
                  error_bars="SEM across independent-run means; common seeds across periods",
                  results=rows)
    (directory / "summary.json").write_text(json.dumps(result, indent=2)+"\n")
    fig, ax = plt.subplots(figsize=(8, 5))
    periods = [r["period"] for r in rows]
    for i, seed in enumerate(config["seeds"]):
        ax.scatter(periods, [r["absolute_trapezoidal_integral"]["run_means"][i] for r in rows],
                   s=25, alpha=.55, label=f"Seed {seed}")
    ax.errorbar(periods, [r["absolute_trapezoidal_integral"]["mean"] for r in rows],
                yerr=[r["absolute_trapezoidal_integral"]["sem"] for r in rows],
                fmt="ko-", capsize=4, label="Mean ± SEM")
    ax.set(xlabel="Driving period P (MCS)", ylabel="Mean absolute trapezoidal loop integral",
           title="Smoke test only" if config["mode"]=="smoke" else "Recovered Figure 6 protocol")
    ax.grid(alpha=.25); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(directory / "period_scan.png", dpi=160); plt.close(fig)
    return result


def run(config, directory):
    directory = Path(directory)
    # Avoid replacing archived data or silently mixing partial runs.
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "parameters.json").write_text(json.dumps(asdict(config), indent=2)+"\n")
    started = time.perf_counter()
    for period in config.periods:
        h_all, m_all = [], []
        for seed in config.seeds:
            h, m = simulator(L=config.L, T=config.T, J=config.J, h0=config.h0,
                             period=period, n=config.cycles, lattice=None, seed=seed)
            assert len(m)==period*config.cycles and np.isfinite(m).all()
            h_all.append(h); m_all.append(m)
        np.savez_compressed(directory / f"P{period}.npz", h=np.array(h_all), m=np.array(m_all),
                            seeds=np.array(config.seeds), period=period, L=config.L, T=config.T,
                            J=config.J, h0=config.h0, cycles=config.cycles, burn_cycles=config.burn_cycles)
        print(f"Completed P={period} ({len(config.seeds)} seeds)", flush=True)
    source_files = [ROOT / "src/ising.py", ROOT / "src/observables.py", Path(__file__)]
    provenance = dict(elapsed_seconds=time.perf_counter()-started, python=platform.python_version(),
                      packages={p:importlib.metadata.version(p) for p in ("numpy","numba","matplotlib")},
                      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in source_files})
    (directory / "provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    return analyze_cache(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke","full"), default="smoke")
    parser.add_argument("--output", type=Path, default=ROOT / "results/period_scan_smoke")
    parser.add_argument("--from-cache", type=Path, help="Redraw an existing output directory; no simulation.")
    args = parser.parse_args()
    result = analyze_cache(args.from_cache) if args.from_cache else run(FULL if args.mode=="full" else SMOKE, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
