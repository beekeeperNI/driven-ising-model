"""Build human-readable tables from recorded summaries, without simulation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def main():
    load=lambda p:json.loads((ROOT/p).read_text())
    p1=load('part1_existing/summary_original.json')['records']
    lines=['# Existing Part 1 results (unchanged)','', 'Eight runs per initial state; energy tolerance ±0.005 per spin. These are finite-time energy checks, not exact-distribution tests.','', '| L | T | Total MCS | Burn-in | All-up minus random energy ± 95% half-width | Original status |','|---:|---:|---:|---:|---:|---|']
    for r in p1:
        d=r['difference'];lines.append(f"| {r['L']} | {r['T']:g} | {r['sweeps']} | {r['burn']} | {d['mean']:+.6f} ± {d['half95']:.6f} | {r['status']} |")
    (ROOT/'part1_existing/table.md').write_text('\n'.join(lines)+'\n')
    p2=load('part2_exact/summary.json')
    lines=['# Exact Boltzmann comparisons','', 'MC estimates are mean ± approximate pointwise 95% Student-t half-width across 16 independent runs. Δ = MC − exact. The exact value has no sampling error. S = interval entirely inside the declared tolerance; I = inconclusive at that precision. Energy tolerance: 0.004; absolute-magnetization tolerance: 0.001. These are separate observables with separate tolerances.','', '| L | T | Burn / retained MCS | Exact e | MC e ± 95% | Δe | Exact ⟨abs(m)⟩ | MC ⟨abs(m)⟩ ± 95% | Δ⟨abs(m)⟩ | Direct e / abs(m) | All diagnostics |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|']
    for r in p2['final']:
        e=r['observables']['energy']['mc_minus_exact'];m=r['observables']['abs_m']['mc_minus_exact']
        s=lambda v:'S' if v['status']=='supported_at_tolerance' else ('I' if v['status']=='inconclusive' else 'D')
        lines.append(f"| {r['L']} | {r['T']:g} | {r['burn']} / {r['measurements']} | {e['reference']:.6f} | {e['mean']:.6f} ± {e['half95']:.6f} | {e['difference']:+.6f} | {m['reference']:.6f} | {m['mean']:.6f} ± {m['half95']:.6f} | {m['difference']:+.6f} | {s(e)} / {s(m)} | {'S' if r['supported'] else 'I'} |")
    lines+=['', 'Only the two T=1.2 cases satisfy every residual and window-sensitivity criterion. Direct residual precision is supported for energy in 7/8 cases and absolute magnetization in 4/8; both direct criteria in 4/8. At L=3, T=3.2, both nominal 95% residual intervals exclude zero (energy below exact, magnetization above exact). This unsuccessful comparison is retained; neither interval lies wholly outside its practical tolerance. Intervals are pointwise, not simultaneous, and adaptive stage selection does not preserve a simple unconditional 95% guarantee.','', 'See `summary.json` for every pilot, extension, interval endpoint, seed-level mean and energy-level count. Overlap of error bars is not used as an agreement criterion.']
    (ROOT/'part2_exact/table.md').write_text('\n'.join(lines)+'\n')
    d=load('driving/summary.json')
    lines=['# Driven reliability and period scan','', 'L=40, T=2, J=1, h0=0.5. Eight independent runs per initial mode. ± denotes pointwise approximate 95% run-mean intervals. All quantities per spin; work is signed field work.','', '| P | Initial mode | Discarded / retained cycles | Mean W ± 95% | Mean abs(Q) ± 95% | Targeted checks |','|---:|---|---:|---:|---:|---|']
    for r in d['targeted_final']:
        for mode,g in r['groups'].items():
            w=g['observables']['W']['mean'];q=g['observables']['abs_Q']['mean']
            lines.append(f"| {r['P']} | {mode} | {r['burn']} / {r['cycles']-r['burn']} | {w['mean']:.6f} ± {w['half95']:.6f} | {q['mean']:.6f} ± {q['half95']:.6f} | {'supported' if r['supported'] else 'inconclusive'} |")
    lines+=['','## Common pilot scan','', 'The period comparison uses the same 20 discarded + 60 retained cycles at every P; P=10 extended results above are deliberately not substituted into this scan. Only P=10,125,300 also received an all-up comparison. Other statuses cover within-random-start window checks only.','', '| P | Signed W ± 95% | Legacy absolute area ± 95% | Mean abs(Q) ± 95% | Pilot checks |','|---:|---:|---:|---:|---|']
    for r in d['pilot_period_scan']:
        g=r['groups']['random'];vals=[g['observables']['W']['mean'],g['legacy_abs_area'],g['observables']['abs_Q']['mean']]
        lines.append('| '+str(r['P'])+' | '+' | '.join(f"{v['mean']:.6f} ± {v['half95']:.6f}" for v in vals)+f" | {'supported (tested checks only)' if r['supported'] else 'inconclusive'} |")
    lines+=['', 'Both definitions peak at P=125 on the sampled grid. Paired differences use common seed identities across periods:','', '| Contrast | Signed work difference ± 95% |','|---|---:|']
    for p,v in d['P125_minus_other_periods'].items():lines.append(f"| W(125) − W({p}) | {v['mean']:.6f} ± {v['half95']:.6f} |")
    (ROOT/'driving/table.md').write_text('\n'.join(lines)+'\n')
    lines=['# Unresolved comparisons','', 'The following list preserves every non-supported criterion from the recorded stages. Repeated pilot and extension entries are intentional. An inconclusive criterion is not an algorithm failure. Nominal zero-exclusion and practical precision are different statements.','', '## Part 2: all stages','']
    for r in p2['stages']:
        for obs,diags in r['observables'].items():
            for name,v in diags.items():
                if v['status']!='supported_at_tolerance':lines.append(f"- L={r['L']}, T={r['T']:g}, burn={r['burn']}, retained={r['measurements']}: {obs}/{name}: {v['status']}; difference {v['difference']:+.7f}, interval [{v['low95']:+.7f}, {v['high95']:+.7f}], tolerance ±{v['tolerance']:g}.")
    lines+=['','## Driving: all stages','']
    for r in d['stages']:
        for mode,g in r['groups'].items():
            for obs,diags in g['observables'].items():
                for name,v in diags.items():
                    if name!='mean' and v['status']!='supported_at_tolerance':lines.append(f"- P={r['P']}, cycles={r['cycles']}, {mode}, {obs}/{name}: {v['status']}; difference {v['difference']:+.7f}, interval [{v['low95']:+.7f}, {v['high95']:+.7f}], tolerance ±{v['tolerance']:g}.")
        for obs,v in r['initial_state_difference'].items():
            if v['status']!='supported_at_tolerance':lines.append(f"- P={r['P']}, cycles={r['cycles']}, all-up minus random, {obs}: {v['status']}; difference {v['difference']:+.7f}, interval [{v['low95']:+.7f}, {v['high95']:+.7f}], tolerance ±{v['tolerance']:g}.")
    lines+=['', '## Boundaries of the conclusions','', '- Part 1: T=2.27 at all three sizes, and L=80 at T=1.2, remain inconclusive.', '- Part 3: only four existing temperatures, no new fine sampling around Tc and no thermodynamic-limit extrapolation; energy stability alone does not validate magnetization.', '- Driven P=10 remains preliminary after its one capped extension. P=20,50,75 pilot window checks are also inconclusive. Other non-target periods were not tested across initial states.', '- Rare unobserved energy levels have unknown sampling uncertainty; their zero counts do not imply zero true probability.', '- Student-t intervals rely on approximate distributions of independent-run summaries. Eight or sixteen runs cannot rule out unvisited long-lived states; intervals are unadjusted for multiple checks and adaptive extension.', '- No driven temperature/size sweep, heat accounting, calibrated physical-time mapping, or dynamic-phase-transition claim is established here.']
    (ROOT/'UNRESOLVED.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
