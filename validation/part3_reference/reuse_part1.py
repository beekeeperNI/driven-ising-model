"""Derive magnetization summaries from existing Part 1 arrays; never simulate."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from common.statistics import interval,welch_difference
HERE=Path(__file__).resolve().parent


def yang_magnetization(T):
    T=np.asarray(T,dtype=float)
    Tc=2/np.log(1+np.sqrt(2))
    result=np.zeros_like(T)
    below=T<Tc
    result[below]=np.maximum(0,1-np.sinh(2/T[below])**(-4))**(1/8)
    return result


def main(source):
    target=HERE/'summary.json'
    if target.exists():raise FileExistsError(target)
    source=Path(source)
    part1=json.loads((source/'summary.json').read_text())
    assert len(part1['records'])==12 and sum(r['supported'] for r in part1['records'])==8
    groups=[]; manifests=[]; run_means=[]; late_drifts=[]
    for row in part1['records']:
        path=source/Path(row['path']).name
        data=np.load(path)
        B=row['burn']
        record=dict(L=row['L'],T=row['T'],sweeps=row['sweeps'],burn=B,
             original_part1_energy_status=row['status'],source_file=path.name,
             thermodynamic_limit_reference=float(yang_magnetization(row['T'])),groups={})
        one=[];drifts=[]
        for mode in ('up','random'):
            a=np.abs(data['m_'+mode][:,B:])
            means=a.mean(axis=1)
            mid=a.shape[1]//2
            drift=a[:,mid:].mean(axis=1)-a[:,:mid].mean(axis=1)
            record['groups'][mode]=dict(abs_m=interval(means),late_drift=interval(drift),
                                       seeds=data['seeds_'+mode].tolist())
            one.append(means);drifts.append(drift)
        # Descriptive contrast only; do not inherit Part 1's ENERGY tolerance.
        contrast=welch_difference(one[0],one[1],1.0)
        del contrast['status'];del contrast['tolerance']
        record['initial_state_abs_m_difference']=contrast
        groups.append(record);run_means.append(one);late_drifts.append(drifts)
        manifests.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              bytes=path.stat().st_size))
    np.savez_compressed(HERE/'cached_run_statistics.npz',run_means=np.array(run_means),
                        late_drifts=np.array(late_drifts),
                        sizes=[r['L'] for r in groups],temperatures=[r['T'] for r in groups])
    target.write_text(json.dumps(dict(results=groups,new_equilibrium_simulations=0,
        interpretation='Finite-lattice |m| is compared with a thermodynamic-limit reference, NOT tested for equality. Hollow plot markers denote the existing Part 1 energy-inconclusive cases, not new algorithm failures.'),indent=2))
    (HERE/'source_data_manifest.json').write_text(json.dumps(manifests,indent=2))
    print('Reused 12 existing parameter points; no new large-lattice equilibrium simulation.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--part1-data',required=True)
    main(p.parse_args().part1_data)
