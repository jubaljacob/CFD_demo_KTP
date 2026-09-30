"""Check published fingerprints, case dependencies and experiment invariants."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from prepare_case import CONFIGS, MESH_FILES, ROOT, prepare

class ScientificSourceTests(unittest.TestCase):
    def test_source_fingerprints_and_scope(self):
        manifest=json.loads((ROOT/'simulation/source-manifest.json').read_text())
        for record in manifest['files']:
            path=ROOT/record['published']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['published_sha256'],str(path))
            self.assertNotIn(path.suffix.lower(),['.md','.pdf','.pyc'])
            self.assertLess(path.stat().st_size,5_000_000)
            if path.suffix!='.png':self.assertNotIn('/home/',path.read_text())

    def test_main_comparison_preserves_supply_and_probe_settings(self):
        flows=[]
        for name,count in [('four',4),('five',5)]:
            c=CONFIGS[name]
            u=(ROOT/c['flow']/'0/U').read_text()
            rates=list(map(float,re.findall(r'volumetricFlowRate\s+([^;]+);',u)))
            self.assertEqual(len(rates),count)
            self.assertEqual(len(set(rates)),1)
            flows.append(sum(rates))
            mesh=(ROOT/c['mesh']/'system/snappyHexMeshDict').read_text()
            field=(ROOT/c['tracer']/'0/T').read_text()
            for i in range(1,count+1):
                self.assertIn(f'inlet{i}',mesh)
                self.assertIn(f'inlet{i}',field)
            self.assertRegex(field,r'internalField\s+uniform\s+0;')
        self.assertAlmostEqual(flows[1]/flows[0],1.25,places=12)
        a=(ROOT/CONFIGS['four']['tracer']/'system/controlDict').read_text()
        b=(ROOT/CONFIGS['five']['tracer']/'system/controlDict').read_text()
        self.assertEqual(a,b,'Matched comparison must retain identical sampling and time settings')

    def test_preparation_refuses_missing_dependencies_and_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for c in CONFIGS.values():
                for value in c.values():
                    if not (root/value).exists():shutil.copytree(ROOT/value,root/value)
            with self.assertRaisesRegex(ValueError,'Missing'):
                prepare('four','tracer',root)
            self.assertFalse((root/'simulation-runs/four/tracer').exists())
            for name in CONFIGS:
                mesh=prepare(name,'mesh',root)
                self.assertTrue((mesh/'constant/triSurface/reactor.stl').is_file())
                with self.assertRaisesRegex(ValueError,'overwrite'):prepare(name,'mesh',root)
                poly=mesh/'constant/polyMesh';poly.mkdir()
                # Sentinel files verify copying/dependency guards, not numerical correctness.
                for field in MESH_FILES:(poly/field).write_text('test mesh '+field)
                flow=prepare(name,'flow',root)
                self.assertEqual((flow/'constant/polyMesh/points').read_bytes(),(poly/'points').read_bytes())
                with self.assertRaisesRegex(ValueError,'Missing'):prepare(name,'tracer',root)
                (flow/'600').mkdir()
                for field in ['U','phi']:(flow/'600'/field).write_text('test carrier '+field)
                tracer=prepare(name,'tracer',root)
                for field in ['U','phi']:self.assertEqual((tracer/'0'/field).read_bytes(),(flow/'600'/field).read_bytes())

if __name__=='__main__':unittest.main()
