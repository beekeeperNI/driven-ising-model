"""Export original notebook animations and widget playback as separate GIFs.

No simulation algorithm is reimplemented. Execute only the archived original
cells needed by each demo; the original notebook is never modified.
"""
from pathlib import Path
import argparse,ast,base64,hashlib,io,json,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/demos/notebook'
SOURCES=OUT/'source_cells.json'

def execute(source,ns):
    exec(compile(source,'original_notebook_cell','exec'),ns)

def namespace(cells):
    ns={};execute(cells['0'],ns);return ns

def original_functions(source,ns):
    tree=ast.parse(source)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'original_function','exec'),ns)

def save_images(images,path,duration):
    frames=[im.convert('RGB').quantize(colors=256) for im in images]
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False,disposal=2)

def record(path,origin,**kwargs):
    with Image.open(path) as im:
        durations=[]
        for i in range(im.n_frames):im.seek(i);im.load();durations.append(im.info.get('duration',0))
        poster_frame=im.n_frames-1 if path.stem.startswith('multi_cycle_') else im.n_frames//2
        im.seek(poster_frame)
        (path.parent/'previews').mkdir(exist_ok=True)
        im.convert('RGB').save(path.parent/'previews'/f'{path.stem}.png')
        result=dict(file=path.name,origin=origin,frames=im.n_frames,width=im.width,height=im.height,
                    playback_ms=sum(durations),loop=im.info.get('loop'),bytes=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),**kwargs)
    print(f"Exported {path.name}: {result['frames']} frames, {result['bytes']} bytes",flush=True)
    return result

def main(notebook=None):
    archive=json.loads(SOURCES.read_text());cells=archive['cells'];records=[]
    # A GitHub checkout still uses the very same first-cell simulation source.
    repo_nb=ROOT/'notebooks/Simulator.ipynb'
    if repo_nb.exists():
        core=''.join(json.loads(repo_nb.read_text())['cells'][0]['source'])
        assert ast.dump(ast.parse(core))==ast.dump(ast.parse(cells['0']))
    path=OUT/'temperature_field_response.gif'
    if notebook:
        nb=json.loads(Path(notebook).read_text())
        assert hashlib.sha256(Path(notebook).read_bytes()).hexdigest()==archive['notebook_sha256'], 'Use the archived source notebook version.'
        html=''.join(nb['cells'][3]['outputs'][0]['data']['text/html'])
        matched=re.findall(r'frames\[(\d+)\]\s*=\s*"data:image/png;base64,([\s\S]*?)"',html)
        assert [int(i) for i,b in matched]==list(range(61))
        images=[Image.open(io.BytesIO(base64.b64decode(re.sub(r'[\\\s]','',b)))).convert('RGB') for i,b in matched]
        save_images(images,path,120)
    elif not path.exists():
        raise FileNotFoundError('Temperature animation requires the original saved HTML output; pass --notebook. It is not regenerated with a new seed.')
    records.append(record(path,'Original saved HTML frames; no new simulation',L=40,temperatures=[1.5,2.,3.],field_before=0,field_after=-.5,switch_MCS=45,total_MCS=180,snapshot_interval=3,seed='not recorded in original temperature demo'))

    ns=namespace(cells);execute(cells['1'],ns)
    source='\n'.join(s for s in cells['2'].splitlines() if not s.startswith('%'))
    cutoff=source.index('# Interactive Controls')
    execute(source[:cutoff],ns);original_functions(source,ns)
    ani=FuncAnimation(ns['fig'],ns['update_frame'],frames=range(1,ns['N']+1),interval=100,blit=False)
    path=OUT/'spin_configuration_dynamics.gif';ani.save(path,writer=PillowWriter(fps=10),dpi=75);plt.close('all')
    records.append(record(path,'Original snapshot widget re-rendered; original core/observer equality assertions passed',L=40,T=2.,h0=.5,period=125,cycles=3,seed=42,source_cells=[1,2]))

    ns=namespace(cells)
    source=cells['4'][:cells['4'].index('# 7. Period Selector')]
    # Original factory returns HTML. Capture its FuncAnimation instead of encoding HTML.
    source=source.replace("return HTML(\n        ani.to_jshtml(\n            fps=8,\n            default_mode='loop'\n        )\n    )",'return ani')
    assert 'return ani' in source
    execute(source,ns)
    for P in ns['periods_multi_demo']:
        ani=ns['build_multi_cycle_animation'](P);path=OUT/f'multi_cycle_hysteresis_P{P}.gif'
        ani.save(path,writer=PillowWriter(fps=8),dpi=85);plt.close('all')
        records.append(record(path,'Original multi-cycle factory; only HTML return changed to GIF export',L=40,T=2.,h0=.5,period=P,warmup_cycles=15,shown_cycles=3,seed=101,source_cells=[4]))

    ns=namespace(cells);execute(cells['7'],ns)
    execute(cells['8'][:cells['8'].index('# 2. Create Interactive Controls')],ns)
    images=[Image.open(io.BytesIO(ns['rendered_sweep_images'][P])).convert('RGB') for P in ns['periods_sweep_demo']]
    path=OUT/'period_sweep_explorer.gif';save_images(images,path,1200)
    records.append(record(path,'Original period-selector images, played in period order',L=40,T=2.,h0=.5,periods=[int(p) for p in ns['periods_sweep_demo']],seeds=[101,202,303],cycles=24,burn_cycles=12,source_cells=[7,8],observable='absolute trapezoidal integral of phase-averaged loop; original explorer definition'))

    ns=namespace(cells);execute(cells['20'],ns)
    execute(cells['21'][:cells['21'].index('# 7. Temperature Checkboxes')],ns)
    images=[Image.open(io.BytesIO(ns['render_TP_figure'](P,ns['temperatures']))).convert('RGB') for P in ns['periods']]
    path=OUT/'multi_temperature_period_explorer.gif';save_images(images,path,450)
    records.append(record(path,'Original temperature/period explorer, all temperature checkboxes selected',L=40,h0=.5,periods=ns['periods'],temperatures=ns['temperatures'],seed=101,cycles=20,burn_cycles=10,source_cells=[20,21],observable='signed post-sweep field work, original explorer definition'))
    (OUT/'manifest.json').write_text(json.dumps(dict(source_notebook_sha256=archive['notebook_sha256'],note='Illustrative exports, not additional validation. Widget controls become fixed GIF playback. GIF frame delays are quantized to 10 ms.',gifs=records),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--notebook',type=Path,help='Original notebook with saved temperature animation HTML (needed for extraction).');args=p.parse_args();main(args.notebook)
