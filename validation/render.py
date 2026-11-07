"""Redraw every new final figure from cached results. Never run Monte Carlo."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from part3_reference.reuse_part1 import yang_magnetization

ROOT=Path(__file__).resolve().parent


def render_all(root=ROOT):
    root=Path(root)
    out=root/'figures';out.mkdir(exist_ok=True)
    outputs=[]
    def save(fig,name):
        fig.savefig(out/name,dpi=180,bbox_inches='tight')
        fig.savefig((out/name).with_suffix('.pdf'),bbox_inches='tight')
        outputs.append(out/name);plt.close(fig)
    exact=json.loads((root/'part2_exact/exact.json').read_text())
    benchmark=json.loads((root/'part2_exact/summary.json').read_text())['final']
    colors={3:'tab:blue',4:'tab:orange'}
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for L in (3,4):
        rows=sorted([r for r in benchmark if r['L']==L],key=lambda r:r['T'])
        ts=[r['T'] for r in rows]
        for col,name in enumerate(('energy','abs_m')):
            vals=[r['observables'][name]['mc_minus_exact'] for r in rows]
            axes[0,col].plot(ts,[v['reference'] for v in vals],'-',color=colors[L],label=f'Exact L={L}')
            axes[0,col].errorbar(ts,[v['mean'] for v in vals],yerr=[v['half95'] for v in vals],
                fmt='o',mfc='white',color=colors[L],capsize=4,label=f'MC L={L}')
            axes[1,col].errorbar(ts,[v['difference'] for v in vals],yerr=[v['half95'] for v in vals],
                fmt='o-',color=colors[L],capsize=4,label=f'L={L}')
    for col,(label,tol) in enumerate((('Energy per spin',.004),('Mean absolute magnetization',.001))):
        axes[0,col].set_ylabel(label)
        axes[0,col].legend(fontsize=8)
        axes[1,col].axhspan(-tol,tol,color='seagreen',alpha=.1,label='Predeclared precision target')
        axes[1,col].axhline(0,color='gray',ls='--',lw=.8)
        axes[1,col].set_ylabel('MC minus exact')
        axes[1,col].legend(fontsize=8)
    for ax in axes.flat:
        ax.set_xlabel('Temperature T');ax.grid(alpha=.2)
    fig.suptitle('Small-lattice Boltzmann benchmark | error bars: pointwise approximate 95% intervals')
    fig.tight_layout(rect=(0,0,1,.96));save(fig,'part2_exact_means.png')

    fig,axes=plt.subplots(1,2,figsize=(11,4.3))
    for ax,L in zip(axes,(3,4)):
        r=next(r for r in benchmark if r['L']==L and r['T']==2.)
        d=r['distribution'];levels=np.array(d['levels'])
        ax.plot(levels,d['exact_probabilities'],'ko-',ms=4,label='Exact, includes degeneracy')
        errors=[v if v is not None else 0 for v in d['half95']]
        ax.errorbar(levels,d['mc_probabilities'],yerr=errors,fmt='s',mfc='white',
                    color=colors[L],capsize=4,label='MC ± pointwise 95% interval')
        ax.set(title=f'L={L}, T=2 | TV distance={d["total_variation"]:.4g}',
               xlabel='Total energy H',ylabel='Probability')
        ax.xaxis.set_major_locator(MaxNLocator(nbins=7,integer=True));ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Energy distributions: unobserved rare levels do not establish zero probability')
    fig.tight_layout(rect=(0,0,1,.94));save(fig,'part2_energy_distribution_T2.png')

    reused=json.loads((root/'part3_reference/summary.json').read_text())['results']
    fig,ax=plt.subplots(figsize=(9,5.4))
    grid=np.linspace(1.1,3.4,700)
    ax.plot(grid,yang_magnetization(grid),'k-',lw=1.8,label='Onsager–Yang, thermodynamic limit')
    Tc=2/np.log(1+np.sqrt(2));ax.axvline(Tc,color='gray',ls='--',lw=1)
    color3={20:'tab:blue',40:'tab:orange',80:'tab:green'}
    for r in reused:
        for mode,marker,shift in [('up','o',-.012),('random','^',.012)]:
            v=r['groups'][mode]['abs_m']
            hollow=r['original_part1_energy_status']!='supported'
            ax.errorbar(r['T']+shift,v['mean'],yerr=v['half95'],fmt=marker,ms=5,
                mfc='white' if hollow else color3[r['L']],color=color3[r['L']],capsize=3)
    handles=[Line2D([0],[0],color='black',label='Thermodynamic-limit reference')]
    handles += [Line2D([0],[0],color=c,label=f'L={L}') for L,c in color3.items()]
    handles += [Line2D([0],[0],color='gray',marker='o',ls='',label='All-up initial state'),
                Line2D([0],[0],color='gray',marker='^',ls='',label='Random initial state'),
                Line2D([0],[0],color='gray',marker='o',mfc='white',ls='',label='Hollow: Part 1 energy inconclusive')]
    ax.legend(handles=handles,fontsize=8,loc='lower left')
    upper=max(r['groups'][mode]['abs_m']['mean']+r['groups'][mode]['abs_m']['half95']
              for r in reused for mode in ('up','random'))
    ax.set(xlabel='Temperature T (small horizontal offsets for visibility)',ylabel='Mean |m|',ylim=(-.035,max(1.055,upper+.025)),
           title='Finite-size magnetization reference | reused Part 1 trajectories; no new simulations')
    ax.grid(alpha=.2);fig.tight_layout();save(fig,'part3_onsager_yang_reference.png')

    drive=json.loads((root/'driving/summary.json').read_text())
    pilots=drive['pilot_period_scan'];periods=[r['P'] for r in pilots]
    fig,axes=plt.subplots(1,2,figsize=(11,4.6))
    for label,key,color in [('Signed field work','W','tab:blue'),('Legacy mean absolute loop integral','legacy','tab:orange')]:
        vals=[r['groups']['random']['observables']['W']['mean'] if key=='W'
              else r['groups']['random']['legacy_abs_area'] for r in pilots]
        axes[0].errorbar(periods,[v['mean'] for v in vals],yerr=[v['half95'] for v in vals],
            fmt='o-',capsize=3,color=color,label=label)
    q=[r['groups']['random']['observables']['abs_Q']['mean'] for r in pilots]
    axes[1].errorbar(periods,[v['mean'] for v in q],yerr=[v['half95'] for v in q],fmt='o-',capsize=3)
    axes[0].set_ylabel('Work / loop integral per spin');axes[0].legend(fontsize=8)
    axes[1].set_ylabel('Mean |Q_cycle|')
    for ax in axes:
        ax.set_xlabel('Driving period P (MCS)');ax.grid(alpha=.2)
        ax.axvline(125,color='gray',ls='--',lw=.8)
    fig.suptitle('Common pilot: L=40, T=2, h0=0.5 | 8 random-start runs, 20 discarded + 60 retained cycles')
    fig.tight_layout(rect=(0,0,1,.93));save(fig,'driving_period_scan.png')

    fig,axes=plt.subplots(3,2,figsize=(12,10))
    for row,r in enumerate(drive['targeted_final']):
        for mode,color in [('all_up','tab:blue'),('random','tab:orange')]:
            d=np.load(root/'driving/data'/r['groups'][mode]['file'])
            for col,key in enumerate(('W','Q')):
                ax=axes[row,col];x=np.arange(1,d[key].shape[1]+1)
                for vals in d[key]:ax.plot(x,vals,color=color,alpha=.2,lw=.65)
                ax.plot(x,d[key].mean(axis=0),color=color,lw=1.5,label=mode)
        for col,key in enumerate(('W','Q')):
            axes[row,col].axvline(r['burn'],color='gray',ls='--',lw=.8)
            axes[row,col].set(title=f'P={r["P"]}: {"supported" if r["supported"] else "inconclusive"}',
                 xlabel='Completed driving cycles',ylabel='Signed work W' if key=='W' else 'Signed Q')
            axes[row,col].grid(alpha=.2)
            if row==0:axes[row,col].legend(fontsize=8)
    fig.suptitle('Periodic-state diagnostics | thin: individual runs; thick: ensemble mean')
    fig.tight_layout(rect=(0,0,1,.96));save(fig,'driving_cycle_diagnostics.png')
    return outputs

if __name__=='__main__':
    for path in render_all():print(path.relative_to(ROOT))
