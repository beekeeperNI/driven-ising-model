"""Rebuild illustrative assets with the repository's original Metropolis core.

This is a reproduction/packaging utility, not a validation of the code's physics.
Outputs are exploratory and must not be interpreted as converged results.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
notebook = json.loads((ROOT / "notebooks/Simulator.ipynb").read_text())
namespace = {}
exec("".join(notebook["cells"][0]["source"]), namespace)
simulator = namespace["simulator"]
sweep = namespace["_metropolis_sweep_fast"]
OUT = ROOT / "assets"
for part in ["demos", "results", "validation"]:
    (OUT / part).mkdir(parents=True, exist_ok=True)

@njit
def seed_rng(seed):
    np.random.seed(seed)

@njit
def energy_per_spin(lattice):
    L = lattice.shape[0]
    E = 0.0
    for i in range(L):
        for j in range(L):
            E -= lattice[i, j] * (
                lattice[(i + 1) % L, j] + lattice[i, (j + 1) % L]
            )
    return E / (L * L)

def cycle_segments(h, m, P, discard):
    for k in range(discard, len(m)//P):
        sl = slice(k * P, (k + 1) * P)
        yield h[sl], m[sl]

def cycle_area(h, m):
    hh = np.r_[h, h[0]]
    mm = np.r_[m, m[0]]
    return float(abs(np.sum((mm[:-1] + mm[1:]) * 0.5 * np.diff(hh))))

def cycle_work(h, m):
    return float(-np.sum(m * (np.roll(h, -1) - h)))

def animate_hysteresis(P):
    L, T, h0, warm, show = 40, 2.0, 0.5, 15, 3
    h, m = simulator(L=L, T=T, h0=h0, period=P, n=warm+show, seed=101)
    start = warm*P
    hh, mm = h[start:], m[start:]
    t = np.arange(start, len(h))
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(t, hh, color="gray", alpha=.7, label="h(t)")
    ax[0].set(xlabel="MCS", ylabel="h / m", title=f"Three driven cycles, P={P}")
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].legend(loc="upper right")
    lm, = ax[0].plot([], [], color="tab:blue", label="m(t)")
    ax[1].set(xlabel="h", ylabel="m", xlim=(-.6,.6), ylim=(-1.05,1.05),
              title="Magnetization-field response")
    loop, = ax[1].plot([], [], color="tab:orange", linewidth=2)
    dot, = ax[1].plot([], [], "o", color="tab:red")
    frames = np.unique(np.linspace(1, len(hh), 30).astype(int))
    def update(q):
        lm.set_data(t[:q], mm[:q])
        loop.set_data(hh[:q], mm[:q])
        dot.set_data([hh[q-1]], [mm[q-1]])
        return lm, loop, dot
    anim = FuncAnimation(fig, update, frames=frames, interval=120, blit=False)
    anim.save(OUT/"demos"/f"hysteresis_P{P}.gif",
              writer=PillowWriter(fps=8), dpi=70)
    plt.close(fig)

def animate_step():
    L, h0, steps = 40, .5, 180
    temps = [1.5, 2.0, 2.5]
    signals = []
    for j, T in enumerate(temps):
        rng = np.random.default_rng(400+j)
        lat = rng.choice(np.array([-1,1],dtype=np.int8), size=(L,L))
        spin_sum = int(lat.sum())
        seed_rng(500+j)
        readings = []
        for t in range(steps):
            field = -h0 if t < steps//2 else h0
            spin_sum = sweep(lat, T, field, 1.0, spin_sum)
            readings.append(spin_sum/(L*L))
        signals.append(np.array(readings))
    fig, ax = plt.subplots(figsize=(8,4))
    t = np.arange(steps)
    ax.axvline(steps//2, linestyle="--", color="gray",label="Field step")
    ax.set(xlabel="MCS",ylabel="m(t)",title="Response to a field step (not sinusoidal driving)",
           xlim=(0,steps),ylim=(-1.05,1.05))
    artists = [ax.plot([],[],label=f"T={T}")[0] for T in temps]
    ax.legend(loc="lower right")
    frames = np.unique(np.linspace(1,steps,26).astype(int))
    def update(q):
        for a,y in zip(artists,signals): a.set_data(t[:q],y[:q])
        return artists
    anim = FuncAnimation(fig,update,frames=frames,interval=100)
    anim.save(OUT/"demos"/"temperature_field_response.gif",
              writer=PillowWriter(fps=8),dpi=75)
    plt.close(fig)

def results():
    periods = [10,25,50,75,100,125,150,200,300,450]
    h0, L, n, discard = .5,40,24,8
    means, sems = [],[]
    for P in periods:
        trial=[]
        for seed in [101,202,303]:
            h,m=simulator(L=L,T=2,h0=h0,period=P,n=n,seed=seed)
            trial.append(np.mean([cycle_area(a,b)
                          for a,b in cycle_segments(h,m,P,discard)]))
        means.append(np.mean(trial))
        sems.append(np.std(trial,ddof=1)/np.sqrt(len(trial)))
    fig,ax=plt.subplots(figsize=(7,4))
    ax.errorbar(periods,means,yerr=sems,fmt="o-",capsize=3)
    ax.set(xlabel="Driving period P (MCS)",ylabel="Mean absolute loop integral",
           title="Exploratory period scan, L=40, T=2, h0=0.5")
    fig.tight_layout()
    fig.savefig(OUT/"results"/"period_area_scan_preliminary.png",dpi=145)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(7,4))
    for P in [10,125,300]:
        h,m=simulator(L=40,T=2,h0=.5,period=P,n=20,seed=101)
        ax.plot(h[-P:],m[-P:],label=f"P={P}")
    ax.set(xlabel="h(t)",ylabel="m(t)",title="Selected final-cycle loops (exploratory)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT/"results"/"selected_hysteresis_loops_preliminary.png",dpi=145)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(7,4))
    for k,T in enumerate([1.5,1.8,2.0,2.3]):
        values=[]
        for P in periods:
            trials=[]
            for seed in [101,202]:
                h,m=simulator(L=40,T=T,h0=.5,period=P,n=18,seed=seed+k*1000)
                trials.append(np.mean([cycle_area(a,b)
                              for a,b in cycle_segments(h,m,P,6)]))
            values.append(np.mean(trials))
        ax.plot(periods,values,"o-",label=f"T={T}")
    ax.set(xlabel="Driving period P (MCS)",ylabel="Mean absolute loop integral",
           title="Exploratory temperature-period scan")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT/"results"/"temperature_period_scan_preliminary.png",dpi=145)
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for L in [20,40,80]:
        ws,qs=[],[]
        for P in [50,125,300]:
            work_runs=[];q_runs=[]
            for seed in [101,202,303]:
                h,m=simulator(L=L,T=2,h0=.5,period=P,n=18,seed=seed)
                seg=list(cycle_segments(h,m,P,6))
                work_runs.append(np.mean([cycle_work(a,b) for a,b in seg]))
                q_runs.append(np.mean([abs(b.mean()) for a,b in seg]))
            ws.append(np.mean(work_runs));qs.append(np.mean(q_runs))
        axes[0].plot([50,125,300],ws,"o-",label=f"L={L}")
        axes[1].plot([50,125,300],qs,"o-",label=f"L={L}")
    axes[0].set(xlabel="P (MCS)",ylabel="Signed work per spin")
    axes[1].set(xlabel="P (MCS)",ylabel="Mean absolute cycle magnetization")
    for ax in axes:ax.legend()
    fig.suptitle("Exploratory lattice-size comparison (L=20, 40, 80)")
    fig.tight_layout()
    fig.savefig(OUT/"results"/"finite_size_scan_preliminary.png",dpi=145)
    plt.close(fig)

def validation():
    L, T, steps, burn, n_runs=40,2.0,10000,5000,8
    all_data={}
    for mode in ("all-up","random"):
        records=[]
        for run in range(n_runs):
            seed=1001+run+(8 if mode=="random" else 0)
            rng=np.random.default_rng(seed)
            lat=(np.ones((L,L),dtype=np.int8) if mode=="all-up" else
                 rng.choice(np.array([-1,1],dtype=np.int8),size=(L,L)))
            spin_sum=int(lat.sum())
            seed_rng(seed)
            vals=np.empty(steps+1)
            vals[0]=energy_per_spin(lat)
            for t in range(1,steps+1):
                spin_sum=sweep(lat,T,0.0,1.0,spin_sum)
                vals[t]=energy_per_spin(lat)
            records.append(vals)
        all_data[mode]=np.array(records)
    np.savez_compressed(ROOT/"results"/"validation_L40_T2_energy.npz",
                        all_up=all_data["all-up"],random=all_data["random"])
    x=np.arange(steps+1)
    fig,ax=plt.subplots(figsize=(9,4))
    for mode in all_data:
        ax.plot(x,all_data[mode][0],alpha=.55,lw=.65,label=mode)
    ax.axvline(burn,linestyle="--",color="gray",label="burn cutoff")
    ax.set(xlabel="Completed MCS",ylabel="Energy per spin",title="Raw energy: first run")
    ax.legend();fig.tight_layout()
    fig.savefig(OUT/"validation"/"01_raw_energy_L40_T2.png",dpi=145);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,4))
    for mode in all_data:
        blocks=all_data[mode][:,1:].reshape(n_runs,40,250).mean(axis=2)
        avg=blocks.mean(axis=0);sem=blocks.std(axis=0,ddof=1)/np.sqrt(n_runs)
        times=np.arange(40)*250+125
        ax.plot(times,avg,label=mode)
        ax.fill_between(times,avg-sem,avg+sem,alpha=.18)
    ax.axvline(burn,linestyle="--",color="gray")
    ax.set(xlabel="Completed MCS",ylabel="Block ensemble mean ± 1 SEM",
           title="Relaxation: 250-MCS block means across 8 runs")
    ax.legend();fig.tight_layout()
    fig.savefig(OUT/"validation"/"02_block_relaxation_L40_T2.png",dpi=145);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7,4))
    for idx,mode in enumerate(all_data):
        values=all_data[mode][:,burn+1:].mean(axis=1)
        ax.scatter(np.full(n_runs,idx)+np.linspace(-.09,.09,n_runs),
                   values,alpha=.75,label=mode)
        avg=values.mean();sem=values.std(ddof=1)/np.sqrt(n_runs)
        ax.errorbar(idx,avg,yerr=sem,fmt="D",color="black",capsize=5)
    ax.set_xticks([0,1],["all-up","random"])
    ax.set(ylabel="Mean energy per spin",title="Retained mean energy: MCS 5001–10000")
    fig.tight_layout()
    fig.savefig(OUT/"validation"/"03_retained_energy_L40_T2.png",dpi=145);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7,4))
    for idx,mode in enumerate(all_data):
        data=all_data[mode]
        first=data[:,5001:7501].mean(axis=1)
        second=data[:,7501:10001].mean(axis=1)
        differences=second-first
        avg=differences.mean();sem=differences.std(ddof=1)/np.sqrt(n_runs)
        ax.errorbar(idx,avg,yerr=sem,fmt="o",capsize=5,label=mode)
    ax.axhline(0,linestyle="--",color="gray")
    ax.set_xticks([0,1],["all-up","random"])
    ax.set(ylabel="Second-half minus first-half mean",
           title="Late drift diagnostic")
    ax.legend();fig.tight_layout()
    fig.savefig(OUT/"validation"/"04_late_drift_L40_T2.png",dpi=145);plt.close(fig)

if __name__ == "__main__":
    (ROOT/"results").mkdir(exist_ok=True)
    animate_hysteresis(50)
    animate_hysteresis(125)
    animate_step()
    results()
    validation()
    print("Generated GIFs, exploratory figures, validation figures and raw energy data.")
