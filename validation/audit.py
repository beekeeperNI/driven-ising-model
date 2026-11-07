"""Short independent physics checks and original-trajectory preservation tests."""
from pathlib import Path
import ast
import json
import hashlib
import numpy as np
from common.observed import SOURCE,original_namespace,observed_namespace,simulator
from part2_exact.benchmark import independent_H,enumerate_states,boltzmann
from driving.checks import cycle_observables
ROOT=Path(__file__).resolve().parent


def main():
    rng=np.random.default_rng(7711)
    # Evaluate the actual dE expression extracted from the original source.
    sweep=next(n for n in ast.parse(SOURCE).body if isinstance(n,ast.FunctionDef) and n.name=='_metropolis_sweep_fast')
    expr=next(n.value for n in ast.walk(sweep) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='dE' for t in n.targets))
    local=compile(ast.Expression(expr),'original_dE_expression','eval')
    tested=0
    for L in (3,4,7):
        for J,h in ((1.,0.),(.7,-.3)):
            for _ in range(3):
                lat=rng.choice(np.array([-1,1],dtype=np.int8),size=(L,L))
                for x in range(L):
                    for y in range(L):
                        flipped=lat.copy();flipped[x,y]*=-1
                        neighbors=int(lat[(x+1)%L,y])+int(lat[(x-1)%L,y])+int(lat[x,(y+1)%L])+int(lat[x,(y-1)%L])
                        dE=eval(local,{},dict(s=int(lat[x,y]),J=J,h=h,neighbors=neighbors))
                        assert np.isclose(dE,independent_H(flipped,L,J,h)-independent_H(lat,L,J,h))
                        tested+=1
    comparisons=0
    for L in (3,4):
        for T in (1.2,2.27,3.2):
            for h0 in (0.,.5):
                for mode in ('random','all-up'):
                    lat=None if mode=='random' else np.ones((L,L),dtype=np.int8)
                    kwargs=dict(L=L,T=T,h0=h0,period=13,n=3,lattice=lat,seed=991,J=1.)
                    h0s,m0=original_namespace['simulator'](**kwargs)
                    h1,m1=simulator(**kwargs)
                    h2,m2,e=simulator(**kwargs,record_energy=True)
                    assert np.array_equal(h0s,h1) and np.array_equal(h1,h2)
                    assert np.array_equal(m0,m1) and np.array_equal(m1,m2)
                    if lat is not None:assert np.all(lat==1)
                    comparisons+=1
    # Energy recording is also checked directly on a mutated core-owned lattice.
    lat=rng.choice(np.array([-1,1],dtype=np.int8),size=(4,4))
    e=np.empty(39)
    h,m=observed_namespace['_simulation_core'](lat,False,2.,.5,13,3,1.,991,e)
    assert np.isclose(e[-1],independent_H(lat,4,1.,h[-1])/16)
    enums=[]
    for L in (3,4):
        enum=enumerate_states(L)
        for T in (1.2,2.,2.27,3.2):boltzmann(enum,T)
        enums.append(dict(L=L,configurations=len(enum['H']),ground_energy=int(enum['H'].min()),
                          energy_levels=len(enum['levels'])))
    # Work closure for a constant configuration; Q must take abs BEFORE cycle averaging.
    h=np.tile(np.array([0.,.5,0.,-.5]),2)
    o=cycle_observables(h,np.r_[np.ones(4),-np.ones(4)],4)
    assert np.allclose(o['W'],0) and np.allclose(o['Q'],[1,-1])
    assert o['abs_Q'].mean()==1 and abs(o['Q'].mean())==0
    # The actual field jump work equals the field-only Hamiltonian difference.
    spin= np.ones((3,3),dtype=np.int8); spin[0,0]=-1
    assert np.isclose((independent_H(spin,3,1.,.3)-independent_H(spin,3,1.,-.1))/9,
                      -spin.mean()*(.3-(-.1)))
    source_nb=ROOT.parents[0]/'notebooks/Simulator.ipynb'
    reused={}
    if source_nb.exists():
        for i,c in enumerate(json.loads(source_nb.read_text())['cells']):
            if c['cell_type']!='code':continue
            tops=[n for n in ast.parse(''.join(c['source'])).body
                  if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
            for n in (node for top in tops for node in ast.walk(top)):
                if isinstance(n,(ast.Assign,ast.AnnAssign)):
                    targets=n.targets if isinstance(n,ast.Assign) else [n.target]
                    for target in targets:
                        if isinstance(target,ast.Name) and target.id in ('T','L','seeds','n_cycles','burn_in','periods'):
                            reused.setdefault(target.id,set()).add(i)
    report=dict(hamiltonian_flip_checks=tested,trajectory_comparisons=comparisons,
                trajectory_identical=True,enumeration_checks=enums,work_and_Q_checks=True,
                reused_notebook_names={k:sorted(v) for k,v in reused.items()},
                first_cell_sha256=hashlib.sha256(SOURCE.encode()).hexdigest(),
                protocol=dict(attempts_per_sweep='L^2 random-site selections with replacement',
                  boundaries='periodic',field_update='once before each sweep',
                  observations='magnetization and optional energy after sweep at h[t]',
                  seed='np.random.seed(seed) inside Numba core, before random initialization',
                  initialization='None => original initialize_lattice; provided lattice copied by wrapper',
                  global_scope_mitigation='Only first definition cell is executed; experiments pass explicit isolated configs.'))
    (ROOT/'audit_results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
