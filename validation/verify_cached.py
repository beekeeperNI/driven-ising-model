"""Check cached numerical evidence without rerunning any long simulation."""
from pathlib import Path
import hashlib,json
import numpy as np
from part2_exact.benchmark import analyze,boltzmann,enumerate_states
from driving.checks import cycle_observables,summarize
ROOT=Path(__file__).resolve().parent

def compare(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:compare(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):compare(x,y)
    elif isinstance(a,float):assert np.isclose(a,b,rtol=2e-12,atol=2e-13),(a,b)
    else:assert a==b,(a,b)

def main():
    load=lambda p:json.loads((ROOT/p).read_text())
    exact=load('part2_exact/exact.json')
    for L in (3,4):
        fresh=enumerate_states(L)
        saved=np.load(ROOT/f'part2_exact/data/exact_configurations_L{L}.npz')
        for key in fresh:assert np.array_equal(fresh[key],saved[key])
        for e in [x for x in exact if x['L']==L]:compare(boltzmann(fresh,e['T']),e)
    stages=load('part2_exact/summary.json')['stages'];previous={}
    for row in stages:
        key=row['L'],row['T'];path=ROOT/'part2_exact/data'/row['raw_file']
        if key in previous:
            a=np.load(previous[key]);b=np.load(path)
            for k in ('H','M'):assert np.array_equal(a[k],b[k][:,:a[k].shape[1]])
        truth=next(x for x in exact if (x['L'],x['T'])==key)
        compare(analyze(path,truth,previous.get(key)),row);previous[key]=path
    drive=load('driving/summary.json');previous={};files=set()
    for row in drive['stages']:
        paths={mode:ROOT/'driving/data'/g['file'] for mode,g in row['groups'].items()}
        for path in paths.values():
            d=np.load(path);files.add(path.name)
            assert d['M'].shape==(8,int(d['cycles'])*int(d['period']))
            for i,M in enumerate(d['M']):
                actual=cycle_observables(d['h'],M/int(d['L'])**2,int(d['period']))
                for k,v in actual.items():assert np.allclose(v,d[k][i],rtol=0,atol=1e-12)
        old=previous.get(row['P'])
        if old:
            for mode,path in paths.items():
                a=np.load(old[mode]);b=np.load(path)
                assert np.array_equal(a['M'],b['M'][:,:a['M'].shape[1]])
        compare(summarize(row['P'],paths,row['burn'],old),row);previous[row['P']]=paths
    p1=load('part1_existing/summary_original.json');assert len(p1['records'])==12
    assert sum(r['supported'] for r in p1['records'])==8
    expected=load('provenance.json')['part1_summary_sha256']
    assert hashlib.sha256((ROOT/'part1_existing/summary_original.json').read_bytes()).hexdigest()==expected
    p3=load('part3_reference/summary.json');assert p3['new_equilibrium_simulations']==0
    cache=np.load(ROOT/'part3_reference/cached_run_statistics.npz')
    for i,r in enumerate(p3['results']):
        for j,mode in enumerate(('up','random')):
            assert np.array_equal(cache['run_means'][i,j],r['groups'][mode]['abs_m']['run_values'])
    source=ROOT.parents[2]/'outputs/parameter_validation'
    checked=0
    if source.exists():
        assert hashlib.sha256((source/'summary.json').read_bytes()).hexdigest()==expected
        for row in load('part3_reference/source_data_manifest.json'):
            assert hashlib.sha256((source/row['file']).read_bytes()).hexdigest()==row['sha256'];checked+=1
    result=dict(exact_combinations_recomputed=len(exact),mc_stages_recomputed=len(stages),
        driving_files_recomputed=len(files),driving_stages_recomputed=len(drive['stages']),
        identical_extension_prefixes=True,part1_statuses_preserved=True,
        part3_source_hashes_verified_locally=checked,all_checks_passed=True)
    (ROOT/'cache_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
