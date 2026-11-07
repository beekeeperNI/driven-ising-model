"""Load the repository's original simulator, then the existing Part 1 observer.

The observation extension contains NO Metropolis sweep. It reuses the exact
original _metropolis_sweep_fast object in the same function-global namespace.
"""
import ast
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE.parents[1] / 'notebooks' / 'Simulator.ipynb'
FROZEN = (HERE / 'original_first_cell.py').read_text()
SOURCE = (''.join(json.loads(NOTEBOOK.read_text())['cells'][0]['source'])
          if NOTEBOOK.exists() else FROZEN)
if ast.dump(ast.parse(SOURCE)) != ast.dump(ast.parse(FROZEN)):
    raise RuntimeError('Simulator source changed since the audited snapshot; re-audit before running.')

original_namespace = {}
exec(compile(SOURCE, str(NOTEBOOK), 'exec'), original_namespace)
observed_namespace = {}
exec(compile(SOURCE, str(NOTEBOOK), 'exec'), observed_namespace)
original_sweep = observed_namespace['_metropolis_sweep_fast']
extension = (HERE / 'observation_extension.py').read_text()
assert {n.name for n in ast.parse(extension).body if isinstance(n, ast.FunctionDef)} == {
    'energy_per_spin', '_simulation_core', 'simulator'}
exec(compile(extension, str(HERE / 'observation_extension.py'), 'exec'), observed_namespace)
assert observed_namespace['_metropolis_sweep_fast'] is original_sweep
simulator = observed_namespace['simulator']

