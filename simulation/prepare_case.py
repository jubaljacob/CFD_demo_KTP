"""Prepare fresh 3D reproduction cases from archived scientific dictionaries.

This copies inputs only. It does not run a solver or approve a regenerated mesh.
"""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    'four': {'mesh': 'openfoam/nist3d/pilot-smooth',
             'geometry': 'openfoam/nist3d/geometry',
             'flow': 'openfoam/nist3d/flow-pilot',
             'tracer': 'openfoam/experiments/52ebf42498b9d075/tracer-baseline'},
    'five': {'mesh': 'openfoam/experiments/6117e9b5ca3fd077/mesh',
             'geometry': 'openfoam/experiments/6117e9b5ca3fd077/geometry',
             'flow': 'openfoam/experiments/52ebf42498b9d075/flow',
             'tracer': 'openfoam/experiments/52ebf42498b9d075/tracer-variant'},
    'four-fine': {'mesh': 'openfoam/nist3d/mesh-fine',
                  'geometry': 'openfoam/nist3d/geometry',
                  'flow': 'openfoam/nist3d/flow-fine',
                  'tracer': 'openfoam/nist3d/tracer-fine-corrected'},
}
MESH_FILES = ('points','faces','owner','neighbour','boundary')

def prepare(configuration, stage, root=ROOT):
    config = CONFIGS[configuration]
    work = root/'simulation-runs'/configuration
    target = work/stage
    if target.exists():
        raise ValueError(f'Refusing to overwrite {target}; preserve or rename the previous run first.')
    source = root/config[stage]
    # Check prerequisites before creating any part of a case.
    carrier = work/'flow'
    mesh = work/('mesh' if stage=='flow' else 'flow')/'constant/polyMesh'
    if stage != 'mesh':
        required = [mesh/name for name in MESH_FILES]
        if stage == 'tracer':
            required += [carrier/'600'/name for name in ('U','phi')]
        missing = [str(p.relative_to(root)) for p in required if not p.is_file()]
        if missing:
            raise ValueError('Run and inspect the previous stage first. Missing: '+', '.join(missing))
    for folder in ('system','constant','0'):
        (target/folder).mkdir(parents=True,exist_ok=True)
        for p in (source/folder).glob('*'):
            if p.is_file():shutil.copy2(p,target/folder/p.name)
    if stage == 'mesh':
        surfaces=target/'constant/triSurface';surfaces.mkdir()
        shutil.copy2(root/config['geometry']/'reactor.stl',surfaces/'reactor.stl')
    else:
        shutil.copytree(mesh,target/'constant/polyMesh')
        if stage == 'tracer':
            for name in ('U','phi'):
                shutil.copy2(carrier/'600'/name,target/'0'/name)
    (target/'reactor.foam').touch()
    (target/'reproduction-inputs.json').write_text(json.dumps({
        'configuration':configuration,'stage':stage,'archived_template':config[stage],
        'notice':'Fresh reproduction setup only. Historical approvals/checks do not approve this new run.',
        'carrier_iteration':600 if stage=='tracer' else None,
    },indent=2)+'\n')
    return target

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration',choices=CONFIGS)
    parser.add_argument('stage',choices=['mesh','flow','tracer'])
    args=parser.parse_args()
    try:print(prepare(args.configuration,args.stage))
    except ValueError as error:parser.exit(1,str(error)+'\n')
