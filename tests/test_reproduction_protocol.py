"""The full experiment must remain tied to the recovered notebook settings."""
import ast
import json
from pathlib import Path
import unittest
from scripts.reproduce_period_scan import FULL

ROOT=Path(__file__).resolve().parents[1]


class RecoveredProtocolTests(unittest.TestCase):
    def test_full_configuration_matches_notebook_cell_5(self):
        source=''.join(json.loads((ROOT/'notebooks/Simulator.ipynb').read_text())['cells'][5]['source'])
        found={}
        for node in ast.parse(source).body:
            if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name):
                try:found[node.targets[0].id]=ast.literal_eval(node.value)
                except (ValueError,TypeError):pass
        for field,original in [('L','L'),('T','T'),('h0','h0'),('cycles','n_cycles'),('burn_cycles','burn_in')]:
            self.assertEqual(getattr(FULL,field),found[original])
        self.assertEqual(FULL.periods,tuple(found['periods']))
        self.assertEqual(FULL.seeds,tuple(found['seeds']))


if __name__=='__main__':unittest.main()
