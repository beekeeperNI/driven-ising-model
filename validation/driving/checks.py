"""Bounded driving checks and a compact, consistently defined period scan."""
from pathlib import Path
import sys
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from common.observed import simulator
from common.statistics import interval,welch_difference
HERE=Path(__file__).resolve().parent

CONFIG=dict(L=40,T=2.,J=1.,h0=.5,periods=[10,20,50,75,100,125,150,200,300],
    diagnostic_periods=[10,125,300],runs=8,pilot_cycles=80,pilot_burn=20,
    maximum_cycles=200,maximum_burn=50,work_tolerance=.02,abs_Q_tolerance=.02,
    rationale='Exploratory resolution targets: 0.02 J/spin/cycle for work and two percentage points for |Q|. Not universal validation thresholds.',
    seed_base=440000,
    extension_rule='Only the three diagnostic periods, once, if any pilot diagnostic exceeds its precision target.')


def cycle_observables(h,m,period):
    h=np.asarray(h,dtype=float); m=np.asarray(m,dtype=float)
    if h.shape != m.shape or h.ndim!=1 or len(h)%period:
        raise ValueError('Need equal one-dimensional arrays of complete, aligned cycles.')
    hs=h.reshape(-1,period); ms=m.reshape(-1,period)
    # Work from the field jump AFTER the recorded magnetization. The final
    # trajectory boundary closes to h(0); intermediate boundaries use next-cycle h.
    dh=(np.roll(h,-1)-h).reshape(-1,period)
    W=-np.sum(ms*dh,axis=1)
    Q=ms.mean(axis=1)
    # Preserve the OLD closed per-cycle trapezoidal geometry, including its use
    # of the same cycle's first magnetization at closure. It is not field work.
    legacy=np.abs(np.sum(.5*(ms+np.roll(ms,-1,axis=1))*
                         (np.roll(hs,-1,axis=1)-hs),axis=1))
    return dict(W=W,Q=Q,abs_Q=np.abs(Q),legacy_abs_area=legacy)


def run(P,mode,cycles,previous=None):
    path=HERE/'data'/f'P{P}_{mode}_cycles{cycles}.npz'
    if path.exists():raise FileExistsError(path)
    seeds=CONFIG['seed_base']+(1000 if mode=='all_up' else 0)+np.arange(CONFIG['runs'])
    N=CONFIG['L']**2
    M=np.empty((len(seeds),P*cycles),dtype=np.int16)
    series={key:np.empty((len(seeds),cycles)) for key in ('W','Q','abs_Q','legacy_abs_area')}
    for r,seed in enumerate(seeds):
        lat=np.ones((CONFIG['L'],CONFIG['L']),dtype=np.int8) if mode=='all_up' else None
        h,m=simulator(L=CONFIG['L'],T=CONFIG['T'],J=CONFIG['J'],h0=CONFIG['h0'],
                      period=P,n=cycles,lattice=lat,seed=int(seed))
        M[r]=np.rint(m*N).astype(np.int16)
        assert np.allclose(m,M[r]/N,atol=1e-14)
        for key,val in cycle_observables(h,m,P).items():series[key][r]=val
    if previous:
        old=np.load(previous)
        assert np.array_equal(M[:,:old['M'].shape[1]],old['M'])
        for key in series:
            assert np.allclose(series[key][:,:old[key].shape[1]],old[key],atol=1e-12)
    np.savez_compressed(path,M=M,h=h,seeds=seeds,**series,L=CONFIG['L'],T=CONFIG['T'],
                        J=CONFIG['J'],h0=CONFIG['h0'],period=P,cycles=cycles,mode=mode)
    return path


def summarize(P,paths,burn,previous=None):
    out=dict(P=P,cycles=int(np.load(paths['random'])['cycles']),burn=burn,
             groups={},initial_state_difference={})
    all_checks=[]
    for mode,path in paths.items():
        data=np.load(path)
        group=dict(file=path.name,observables={})
        for key,tol in [('W',CONFIG['work_tolerance']),('abs_Q',CONFIG['abs_Q_tolerance'])]:
            x=data[key][:,burn:]; n=x.shape[1]; means=x.mean(axis=1)
            later=burn+(20 if out['cycles']==CONFIG['pilot_cycles'] else 50)
            diag=dict(mean=interval(means),
                burn_change=interval(data[key][:,later:].mean(axis=1)-means,0,tol),
                measurement_length_change=interval(means-x[:,:n//2].mean(axis=1),0,tol),
                late_drift=interval(x[:,n//2:].mean(axis=1)-x[:,:n//2].mean(axis=1),0,tol))
            if previous:
                old=np.load(previous[mode])
                oldmeans=old[key][:,CONFIG['pilot_burn']:].mean(axis=1)
                diag['extension_change']=interval(means-oldmeans,0,tol)
            all_checks.extend(v for k,v in diag.items() if k!='mean')
            group['observables'][key]=diag
        group['signed_Q']=interval(data['Q'][:,burn:].mean(axis=1))
        group['legacy_abs_area']=interval(data['legacy_abs_area'][:,burn:].mean(axis=1))
        out['groups'][mode]=group
    if 'all_up' in paths:
        for key,tol in [('W',CONFIG['work_tolerance']),('abs_Q',CONFIG['abs_Q_tolerance'])]:
            a=out['groups']['all_up']['observables'][key]['mean']['run_values']
            b=out['groups']['random']['observables'][key]['mean']['run_values']
            contrast=welch_difference(a,b,tol)
            out['initial_state_difference'][key]=contrast
            all_checks.append(contrast)
    out['supported']=all(x['status']=='supported_at_tolerance' for x in all_checks)
    return out


def main():
    (HERE/'data').mkdir(exist_ok=True)
    (HERE/'config.json').write_text(json.dumps(CONFIG,indent=2))
    pilots=[]; finals=[]; stages=[]
    for P in CONFIG['periods']:
        paths={'random':run(P,'random',CONFIG['pilot_cycles'])}
        if P in CONFIG['diagnostic_periods']:
            paths['all_up']=run(P,'all_up',CONFIG['pilot_cycles'])
        pilot=summarize(P,paths,CONFIG['pilot_burn'])
        pilots.append(pilot); stages.append(pilot)
        print(f'Driving pilot P={P}: supported={pilot["supported"]}',flush=True)
        if P in CONFIG['diagnostic_periods']:
            final=pilot
            if not pilot['supported']:
                extended={mode:run(P,mode,CONFIG['maximum_cycles'],path) for mode,path in paths.items()}
                final=summarize(P,extended,CONFIG['maximum_burn'],paths)
                stages.append(final)
                print(f'  bounded extension: supported={final["supported"]}',flush=True)
            finals.append(final)
    # Compare the period dependence ONLY using the common 80-cycle pilot protocol.
    values={r['P']:np.array(r['groups']['random']['observables']['W']['mean']['run_values']) for r in pilots}
    legacy={r['P']:r['groups']['random']['legacy_abs_area']['mean'] for r in pilots}
    peak=max(values,key=lambda p:values[p].mean())
    peak_old=max(legacy,key=legacy.get)
    comparisons={str(p):interval(values[125]-values[p]) for p in (10,75,100,150,200,300)}
    # Same seeds across periods => pair each seed before computing uncertainties.
    result=dict(pilot_period_scan=pilots,targeted_final=finals,stages=stages,
        peak_signed_work_on_tested_grid=peak,peak_legacy_absolute_area_on_tested_grid=peak_old,
        P125_minus_other_periods=comparisons,
        peak_minus_endpoints={str(p):interval(values[peak]-values[p]) for p in (10,300)})
    (HERE/'summary.json').write_text(json.dumps(result,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,help='Separate output directory for a new run; never overwrites raw data.')
    args=parser.parse_args()
    if args.output:
        HERE=args.output.resolve()
        HERE.mkdir(parents=True,exist_ok=True)
    main()

