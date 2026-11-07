"""Independent configuration enumeration + original simulator comparison."""
from pathlib import Path
import sys
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.observed import simulator
from common.statistics import interval

HERE = Path(__file__).resolve().parent
CONFIG = dict(sizes=[3,4], temperatures=[1.2,2.0,2.27,3.2], J=1., h=0., kB=1.,
    runs=16, pilot_burn=5000, pilot_measurements=20000,
    maximum_burn=10000, maximum_measurements=80000,
    energy_tolerance=.004, abs_m_tolerance=.001,
    tolerance_rationale='One part in 1000 of conventional bounding spans: e in [-2,2], abs(m) in [0,1]. These are not necessarily attained finite-L ranges (especially at odd L). Exploratory precision targets, not physical constants.',
    initial_state='random', seed_base=220000,
    extension_rule='One extension only if any residual, burn-window, length-window, or late-drift interval exceeds its precision target. Keep every stage.')


def bond_pairs(L):
    """Undirected graph from pairwise coordinate distance, independent of sweep code."""
    if L < 3:
        raise ValueError('This graph benchmark deliberately excludes the L=2 parallel-bond convention.')
    coords = [(i,j) for i in range(L) for j in range(L)]
    edges = []
    for u, (x,y) in enumerate(coords):
        for v in range(u+1, len(coords)):
            a,b = coords[v]
            dx,dy = min(abs(x-a),L-abs(x-a)), min(abs(y-b),L-abs(y-b))
            if dx+dy == 1:
                edges.append((u,v))
    assert len(edges)==2*L*L
    return np.asarray(edges,dtype=np.int16)


def independent_H(spins, L, J=1., h=0.):
    s=np.asarray(spins,dtype=np.int16).reshape(-1)
    edges=bond_pairs(L)
    return float(-J*np.sum(s[edges[:,0]]*s[edges[:,1]])-h*np.sum(s))


def enumerate_states(L):
    N=L*L
    ids=np.arange(1<<N,dtype=np.uint32)
    spins=(2*((ids[:,None] >> np.arange(N,dtype=np.uint32))&1).astype(np.int8)-1)
    edges=bond_pairs(L)
    energy=-np.sum(spins[:,edges[:,0]]*spins[:,edges[:,1]],axis=1,dtype=np.int16)
    magnetization=spins.sum(axis=1,dtype=np.int16)
    levels,inverse,degeneracy=np.unique(energy,return_inverse=True,return_counts=True)
    assert len(energy)==(1<<N) and degeneracy.sum()==(1<<N)
    assert energy[0]==energy[-1]==-2*N and degeneracy[levels==-2*N][0]==2
    assert np.isclose(energy.mean(),0)  # uniform configuration ensemble, beta=0
    assert np.array_equal(energy,energy[::-1]) and np.array_equal(magnetization,-magnetization[::-1])
    if L%2==0:
        assert levels[-1]==2*N and degeneracy[-1]==2
    return dict(configuration_ids=ids, H=energy, M=magnetization, levels=levels,
                level_index=inverse, degeneracy=degeneracy, L=L)


def boltzmann(enumeration, T):
    H=enumeration['H'].astype(float)
    M=enumeration['M'].astype(float)
    N=int(enumeration['L'])**2
    shifted=np.exp(-(H-H.min())/T)
    normalizer=shifted.sum()
    probability=shifted/normalizer
    logZ=float(-H.min()/T+np.log(normalizer))
    p_levels=np.bincount(enumeration['level_index'],weights=probability,
                         minlength=len(enumeration['levels']))
    by_degeneracy=enumeration['degeneracy']*np.exp(-(enumeration['levels']-H.min())/T)/normalizer
    assert np.isclose(probability.sum(),1,atol=1e-13)
    assert np.isclose(p_levels.sum(),1,atol=1e-13)
    assert np.allclose(p_levels,by_degeneracy,atol=2e-13)
    return dict(L=int(enumeration['L']),T=T,logZ=logZ,Z=float(np.exp(logZ)),
        mean_e=float(probability@(H/N)),mean_abs_m=float(probability@(np.abs(M)/N)),
        levels=enumeration['levels'].tolist(),degeneracy=enumeration['degeneracy'].tolist(),
        probabilities=p_levels.tolist(),configurations=len(H))


def run_mc(L,T,idx,burn,measurements,previous_path=None):
    S=burn+measurements
    path=HERE/'data'/f'mc_L{L}_T{T:g}_S{S}.npz'
    if path.exists():
        raise FileExistsError(f'Refusing to silently overwrite raw data: {path}')
    seeds=CONFIG['seed_base']+100*idx+np.arange(CONFIG['runs'])
    energies=np.empty((len(seeds),S),dtype=np.int16)
    mags=np.empty_like(energies)
    for r,seed in enumerate(seeds):
        h,m,e=simulator(L=L,T=T,J=1.,h0=0.,period=1,n=S,lattice=None,
                        seed=int(seed),record_energy=True)
        energies[r]=np.rint(e*L*L).astype(np.int16)
        mags[r]=np.rint(m*L*L).astype(np.int16)
        assert np.all(h==0) and np.allclose(e,energies[r]/(L*L),atol=1e-14)
        assert np.allclose(m,mags[r]/(L*L),atol=1e-14)
    if previous_path:
        old=np.load(previous_path)
        q=old['H'].shape[1]
        assert np.array_equal(energies[:,:q],old['H']) and np.array_equal(mags[:,:q],old['M'])
    np.savez_compressed(path,H=energies,M=mags,seeds=seeds,L=L,T=T,J=1.,h=0.,
                        burn=burn,measurements=measurements)
    return path


def analyze(path,exact,previous_path=None):
    data=np.load(path)
    L=int(data['L']); B=int(data['burn']); S=data['H'].shape[1]; n=S-B
    out=dict(L=L,T=float(data['T']),burn=B,measurements=n,raw_file=path.name,observables={})
    for name,values,truth,tol in (
        ('energy',data['H']/(L*L),exact['mean_e'],CONFIG['energy_tolerance']),
        ('abs_m',np.abs(data['M'])/(L*L),exact['mean_abs_m'],CONFIG['abs_m_tolerance'])):
        tail=values[:,B:]
        means=tail.mean(axis=1)
        # Increase burn by 5000 while keeping the endpoint; report the shorter retained length.
        later_burn=B+5000
        diagnostics={
            'mc_minus_exact':interval(means,truth,tol),
            'burn_change':interval(values[:,later_burn:].mean(axis=1)-means,0,tol),
            'measurement_length_change':interval(means-tail[:,:n//2].mean(axis=1),0,tol),
            'late_drift':interval(tail[:,n//2:].mean(axis=1)-tail[:,:n//2].mean(axis=1),0,tol)}
        if previous_path:
            prev=np.load(previous_path)
            old_values=prev['H']/(L*L) if name=='energy' else np.abs(prev['M'])/(L*L)
            diagnostics['extension_change']=interval(means-old_values[:,int(prev['burn']):].mean(axis=1),0,tol)
        out['observables'][name]=diagnostics
    out['supported']=all(v['status']=='supported_at_tolerance'
        for d in out['observables'].values() for v in d.values())
    levels=np.array(exact['levels'])
    retained=data['H'][:,B:]
    assert np.isin(retained,levels).all()
    counts=np.array([[np.count_nonzero(row==level) for level in levels] for row in retained])
    freq=counts/n
    prob=freq.mean(axis=0)
    p_exact=np.array(exact['probabilities'])
    out['distribution']=dict(levels=levels.tolist(),counts_by_run=counts.tolist(),
        exact_probabilities=p_exact.tolist(),mc_probabilities=prob.tolist(),
        half95=[interval(freq[:,j])['half95'] if counts[:,j].sum()>0 else None for j in range(len(levels))],
        unobserved_levels=levels[counts.sum(axis=0)==0].tolist(),
        exact_mass_on_unobserved_levels=float(p_exact[counts.sum(axis=0)==0].sum()),
        total_variation=float(.5*np.abs(prob-p_exact).sum()))
    return out


def main():
    (HERE/'data').mkdir(exist_ok=True)
    (HERE/'config.json').write_text(json.dumps(CONFIG,indent=2))
    exacts=[]; stages=[]; finals=[]
    for li,L in enumerate(CONFIG['sizes']):
        enum=enumerate_states(L)
        ep=HERE/'data'/f'exact_configurations_L{L}.npz'
        if ep.exists(): raise FileExistsError(ep)
        np.savez_compressed(ep,**enum)
        for ti,T in enumerate(CONFIG['temperatures']):
            exact=boltzmann(enum,T); exacts.append(exact)
            idx=li*4+ti
            p=run_mc(L,T,idx,CONFIG['pilot_burn'],CONFIG['pilot_measurements'])
            result=analyze(p,exact); stages.append(result)
            print(f'Exact pilot L={L}, T={T}: supported={result["supported"]}',flush=True)
            if not result['supported']:
                longer=run_mc(L,T,idx,CONFIG['maximum_burn'],CONFIG['maximum_measurements'],p)
                result=analyze(longer,exact,p); stages.append(result)
                print(f'  finite-budget extension: supported={result["supported"]}',flush=True)
            finals.append(result)
    (HERE/'exact.json').write_text(json.dumps(exacts,indent=2))
    (HERE/'summary.json').write_text(json.dumps(dict(final=finals,stages=stages),indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,help='Separate output directory for a new run; never overwrites raw data.')
    args=parser.parse_args()
    if args.output:
        HERE=args.output.resolve()
        HERE.mkdir(parents=True,exist_ok=True)
    main()
