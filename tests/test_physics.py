"""Targeted checks against the authoritative notebook and independent identities."""
from pathlib import Path
import ast
import json
import unittest
import numpy as np
from src import ising
from src.observables import (hamiltonian, magnetization, dynamic_order,
    mean_absolute_dynamic_order, signed_field_work, absolute_hysteresis_integral)

ROOT = Path(__file__).resolve().parents[1]
CELLS = json.loads((ROOT / 'notebooks/Simulator.ipynb').read_text())['cells']
SOURCE = ''.join(CELLS[0]['source'])
ORIGINAL = {}
exec(compile(SOURCE, 'original_notebook_cell_0', 'exec'), ORIGINAL)


class DynamicsTests(unittest.TestCase):
    def test_original_function_bodies_preserved(self):
        def functions(source):
            return {n.name:ast.dump(n, include_attributes=False) for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef)}
        a,b=functions(SOURCE),functions((ROOT/'src/ising.py').read_text())
        for name,body in a.items():
            with self.subTest(function=name):self.assertEqual(body,b[name])

    def test_hamiltonian_and_actual_local_energy_expression(self):
        # Extract the ACTUAL original acceptance energy expression, rather than
        # duplicating an expression in a separate replacement update algorithm.
        sweep=next(n for n in ast.parse(SOURCE).body if isinstance(n,ast.FunctionDef) and n.name=='_metropolis_sweep_fast')
        expr=next(n.value for n in ast.walk(sweep) if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=='dE' for t in n.targets))
        code=compile(ast.Expression(expr),'original_delta_E','eval')
        rng=np.random.default_rng(5201)
        for L in (2,3,4,7):
            for J,h in ((1.,0.),(.7,-.3)):
                lat=rng.choice(np.array([-1,1],dtype=np.int8),size=(L,L))
                for x in range(L):
                    for y in range(L):
                        flip=lat.copy();flip[x,y]*=-1
                        n=sum(int(lat[i,j]) for i,j in [((x+1)%L,y),((x-1)%L,y),(x,(y+1)%L),(x,(y-1)%L)])
                        local=eval(code,{},dict(s=int(lat[x,y]),J=J,h=h,neighbors=n))
                        self.assertAlmostEqual(local,hamiltonian(flip,h,J)-hamiltonian(lat,h,J))

    def test_periodic_edges_and_known_states(self):
        for L in (2,3,4):
            for sign in (-1,1):
                lat=np.full((L,L),sign,dtype=np.int8)
                self.assertEqual(hamiltonian(lat,h=.2),-2*L*L-.2*sign*L*L)
                self.assertEqual(magnetization(lat),sign)
        # A corner flip must see both opposite-edge neighbors.
        lat=np.ones((3,3),dtype=np.int8);lat[2,0]=-1;lat[0,2]=-1
        before=hamiltonian(lat);lat[0,0]*=-1
        self.assertEqual(hamiltonian(lat)-before,0)
        checker=np.fromfunction(lambda i,j:1-2*((i+j)%2),(4,4)).astype(np.int8)
        self.assertEqual(hamiltonian(checker),32)

    def test_seeded_trajectories_against_original(self):
        # 36 cases: random/all-up/all-down, two L, three T, two field amplitudes.
        for L in (3,6):
            for T in (1.2,2.27,3.2):
                for h0 in (0.,.5):
                    for state in ('random','all-up','all-down'):
                        with self.subTest(L=L,T=T,h0=h0,state=state):
                            lat=ising.initial_lattice(L,state)
                            before=None if lat is None else lat.copy()
                            kw=dict(L=L,T=T,h0=h0,period=13,n=4,seed=1042,lattice=lat)
                            h0s,m0=ORIGINAL['simulator'](**kw);h1,m1=ising.simulator(**kw)
                            np.testing.assert_array_equal(h0s,h1);np.testing.assert_array_equal(m0,m1)
                            if lat is not None:np.testing.assert_array_equal(lat,before)
                            h2,m2=ising.simulator(**kw);np.testing.assert_array_equal(m1,m2)

    def test_supplied_lattice_final_state_and_field_timing(self):
        a=np.ones((5,5),dtype=np.int8);b=a.copy()
        h0,m0=ORIGINAL['_simulation_core'](a,False,2.,.5,11,3,1.,27)
        h1,m1=ising._simulation_core(b,False,2.,.5,11,3,1.,27)
        np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(m0,m1)
        np.testing.assert_allclose(h1,.5*np.sin(2*np.pi*np.arange(33)/11),atol=1e-14)
        self.assertEqual(m1[-1],b.mean())

    def test_zero_field_spin_inversion(self):
        args=dict(L=4,T=2.,h0=0.,period=7,n=4,seed=404)
        _,up=ising.simulator(**args,lattice=ising.initial_lattice(4,'all-up'))
        _,down=ising.simulator(**args,lattice=ising.initial_lattice(4,'all-down'))
        np.testing.assert_array_equal(up,-down)
        self.assertIsNone(ising.initial_lattice(4,'random'))

    def test_original_input_validation(self):
        for args in [dict(L=1),dict(T=0),dict(period=0),dict(n=0),
                     dict(L=3,lattice=np.ones((4,4))),dict(L=3,lattice=np.zeros((3,3)))]:
            with self.assertRaises(ValueError):ising.simulator(**args)
        with self.assertRaises(ValueError):ising.initial_lattice(4,'unknown')


class ObservableTests(unittest.TestCase):
    def test_abs_before_cycle_average(self):
        m=np.r_[np.ones(4),-np.ones(4)]
        np.testing.assert_array_equal(dynamic_order(m,4),[1,-1])
        self.assertEqual(mean_absolute_dynamic_order(m,4),1)
        self.assertEqual(abs(dynamic_order(m,4).mean()),0)

    def test_work_sign_and_trapezoid_are_distinct(self):
        h=np.array([0.,1.,0.,-1.]);m=np.array([1.,1.,-1.,-1.])
        # Post-sweep field work is zero; the trapezoidal loop has magnitude two.
        np.testing.assert_array_equal(signed_field_work(h,m,4),[0])
        np.testing.assert_array_equal(absolute_hysteresis_integral(h,m,4),[2])
        lag=np.array([-1.,0.,1.,0.])
        np.testing.assert_array_equal(signed_field_work(h,lag,4),[2])
        np.testing.assert_array_equal(signed_field_work(h,-lag,4),[-2])
        both_m=np.r_[lag,-lag];both_h=np.tile(h,2)
        self.assertEqual(signed_field_work(both_h,both_m,4).mean(),0)
        self.assertEqual(absolute_hysteresis_integral(both_h,both_m,4).mean(),2)
        self.assertEqual(absolute_hysteresis_integral(h,both_m.reshape(2,4).mean(axis=0),4)[0],0)

    def test_constant_magnetization_closed_work(self):
        h=np.tile([0.,.5,0.,-.5],3)
        np.testing.assert_allclose(signed_field_work(h,np.ones(12),4),0)
        np.testing.assert_allclose(absolute_hysteresis_integral(h,np.ones(12),4),0)
        # A field jump at fixed spins obeys delta H / N = -m delta h.
        lat=np.ones((3,3),dtype=np.int8);lat[0,0]=-1
        self.assertAlmostEqual((hamiltonian(lat,.3)-hamiltonian(lat,-.1))/9,-lat.mean()*.4)

    def test_against_original_observables(self):
        # Execute only original function definitions; do not launch scans.
        ns={'np':np}
        for idx in (5,24):
            for node in ast.parse(''.join(CELLS[idx]['source'])).body:
                if isinstance(node,ast.FunctionDef) and node.name in ('loop_area','observables_by_cycle'):
                    exec(compile(ast.Module(body=[node],type_ignores=[]),'notebook_observable','exec'),ns)
        h,m=ising.simulator(L=4,T=2.,h0=.5,period=17,n=4,seed=12)
        q,w,a=ns['observables_by_cycle'](h,m,17)
        np.testing.assert_array_equal(q,dynamic_order(m,17))
        np.testing.assert_array_equal(w,signed_field_work(h,m,17))
        np.testing.assert_array_equal(a,absolute_hysteresis_integral(h,m,17))
        for k in range(4):self.assertEqual(a[k],ns['loop_area'](h[k*17:(k+1)*17],m[k*17:(k+1)*17]))

    def test_incomplete_or_mismatched_cycles_rejected(self):
        for m,p in [([1,2,3],2),([],4),([1,np.nan],2),([[1,2]],2),([1,2],0),([1,2],True)]:
            with self.assertRaises(ValueError):dynamic_order(m,p)
        with self.assertRaises(ValueError):signed_field_work([0,1],[1,1,1,1],2)


if __name__=='__main__':unittest.main()
