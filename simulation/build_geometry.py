"""Regenerate labelled four/five inlet surfaces in an isolated output directory."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def build(configuration,output):
    spec=importlib.util.spec_from_file_location('surface_builder',ROOT/'scripts/build_nist_surface.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if output.exists():raise ValueError('Output already exists; choose a fresh directory.')
    module.OUT=output
    module.SPEC=(ROOT/'geometry/nist-3d/geometry-spec.json' if configuration=='four' else ROOT/'openfoam/experiments/6117e9b5ca3fd077/geometry/geometry-spec.json')
    module.G=json.loads(module.SPEC.read_text())
    expected=json.loads((ROOT/'physics/nist-3d/regime-checks.json').read_text())['analytic_gas_volume_m3']
    if configuration=='five':expected+=math.pi*(module.G['inlets']['radius']*1e-3)**2*(module.G['inlets']['z_boundary']-module.G['inlets']['z_chamber'])*1e-3
    module.build()
    points=np.asarray(module.POINTS)*1e-3;faces=np.asarray(module.FACES)
    report,normals=module.validate(points,faces,expected_volume=expected)
    module.export(points,faces,normals)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration',choices=['four','five'])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=build(args.configuration,args.output.resolve())
    print(json.dumps({k:result[k] for k in ['vertices','triangles','edges_without_exactly_two_faces','inconsistently_oriented_edges','volume_error_percent']},indent=2))
