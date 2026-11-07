# Exact Boltzmann comparisons

MC estimates are mean ± approximate pointwise 95% Student-t half-width across 16 independent runs. Δ = MC − exact. The exact value has no sampling error. S = interval entirely inside the declared tolerance; I = inconclusive at that precision. Energy tolerance: 0.004; absolute-magnetization tolerance: 0.001. These are separate observables with separate tolerances.

| L | T | Burn / retained MCS | Exact e | MC e ± 95% | Δe | Exact ⟨abs(m)⟩ | MC ⟨abs(m)⟩ ± 95% | Δ⟨abs(m)⟩ | Direct e / abs(m) | All diagnostics |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
| 3 | 1.2 | 5000 / 20000 | -1.988221 | -1.988525 ± 0.000516 | -0.000304 | 0.996830 | 0.996918 ± 0.000157 | +0.000088 | S / S | S |
| 3 | 2 | 10000 / 80000 | -1.767678 | -1.768114 ± 0.002242 | -0.000435 | 0.925985 | 0.926163 ± 0.000756 | +0.000178 | S / S | I |
| 3 | 2.27 | 10000 / 80000 | -1.610734 | -1.610953 ± 0.002684 | -0.000219 | 0.870888 | 0.871073 ± 0.001027 | +0.000185 | S / I | I |
| 3 | 3.2 | 10000 / 80000 | -1.050432 | -1.052892 ± 0.001847 | -0.002460 | 0.660885 | 0.661880 ± 0.000848 | +0.000995 | I / I | I |
| 4 | 1.2 | 5000 / 20000 | -1.988566 | -1.988634 ± 0.000375 | -0.000067 | 0.997006 | 0.997018 ± 0.000115 | +0.000012 | S / S | S |
| 4 | 2 | 10000 / 80000 | -1.755380 | -1.754956 ± 0.001636 | +0.000424 | 0.918943 | 0.918813 ± 0.000720 | -0.000130 | S / S | I |
| 4 | 2.27 | 10000 / 80000 | -1.564986 | -1.565814 ± 0.002317 | -0.000829 | 0.843597 | 0.844007 ± 0.001096 | +0.000409 | S / I | I |
| 4 | 3.2 | 10000 / 80000 | -0.906798 | -0.905623 ± 0.002306 | +0.001176 | 0.549819 | 0.548960 ± 0.001324 | -0.000859 | S / I | I |

Only the two T=1.2 cases satisfy every residual and window-sensitivity criterion. Direct residual precision is supported for energy in 7/8 cases and absolute magnetization in 4/8; both direct criteria in 4/8. At L=3, T=3.2, both nominal 95% residual intervals exclude zero (energy below exact, magnetization above exact). This unsuccessful comparison is retained; neither interval lies wholly outside its practical tolerance. Intervals are pointwise, not simultaneous, and adaptive stage selection does not preserve a simple unconditional 95% guarantee.

See `summary.json` for every pilot, extension, interval endpoint, seed-level mean and energy-level count. Overlap of error bars is not used as an agreement criterion.
