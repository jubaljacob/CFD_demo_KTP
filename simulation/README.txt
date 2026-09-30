OPENFOAM SCIENTIFIC SOURCE BUNDLE

This archive includes scientific model files and experiment inputs used during the
project. The live site still serves only its compact static viewer; CFD runs on
your own Linux workstation. No hosted agent or CFD service is enabled.

WHAT IS INCLUDED

openfoam/day0/cavity                 Initial lid-driven cavity exercise.
openfoam/day1/                       Poiseuille and 2D chamber case inputs.
openfoam/nist3d/geometry/             Four-inlet labelled STL and VTK surfaces.
geometry/nist-3d/                    Dimensions, assumptions and drawing.
physics/nist-3d/                     Operating point, properties and screening.
references/nist-reactor/             Small nitrogen property table, not papers.
openfoam/nist3d/pilot-smooth/         Four-inlet meshing dictionaries.
openfoam/nist3d/mesh-fine/            Reference refined meshing dictionaries.
openfoam/nist3d/flow-*/               Carrier-flow case settings.
openfoam/nist3d/tracer-*/             Historical tracer case settings.
openfoam/experiments/6117e9b5ca3fd077/ Five-inlet surfaces and mesh settings.
openfoam/experiments/52ebf42498b9d075/ Completed five-inlet carrier and matched
                                    four/five-inlet tracer study inputs.
openfoam/experiments/8f9e0a81f173355e/ One/four-correction startup study inputs.
simulation/review/                  Historical strict mesh findings.
simulation/source-manifest.json     Original and published file fingerprints.

The source archive preserves the recorded dictionaries. Progress notes inside
historical metadata may describe an earlier stage. The published dashboard gives
the final measured outcomes. Where present, local absolute project paths have
been replaced by repository-relative paths; the manifest identifies those files.

Generated volume meshes, decomposed processor folders, compiled dynamic-code
libraries and large solution time directories are excluded. Tracer 0/U and 0/phi
are frozen carrier results, so these are also excluded and copied from a fresh
carrier calculation when preparing a reproduction. The STL/VTK files are surface
models, not the complete volume mesh or a proprietary/native CAD assembly.

The baseline uses four inlets at 75 sccm each (300 total); the variant uses five
at 75 sccm each (375 total). Gas temperature is 383.15 K and absolute operating
pressure is 13332 Pa. Kinematic pressure p is a gauge field, not absolute pressure.
T is a dimensionless passive nitrogen label, not temperature or deposition.

REPRODUCE THE MAIN 3D STUDY

Requirements: Linux, Docker, Python 3, free disk space for several GB of outputs,
and sufficient memory. The helper caps each container at 8 CPUs and 12 GiB RAM.
The volume mesh is generated in serial; optional parallel flow commands follow.
Original timings are not promised on other machines. Commands below assume the
repository root is the current working directory.

1. Prepare a fresh four-inlet mesh case. This copies inputs only.

   python3 simulation/prepare_case.py four mesh

2. Build the background mesh, extract features, fit the reactor mesh, then check.
   Docker downloads the pinned OpenCFD v2512 image on its first use if necessary.

   bash simulation/foam.sh simulation-runs/four/mesh blockMesh
   bash simulation/foam.sh simulation-runs/four/mesh surfaceFeatureExtract
   bash simulation/foam.sh simulation-runs/four/mesh snappyHexMesh -overwrite
   bash simulation/foam.sh simulation-runs/four/mesh checkMesh -allGeometry -allTopology
   bash simulation/foam.sh simulation-runs/four/mesh checkMesh -meshQuality

   Inspect all findings before continuing. The original study retained strict
   concavity warnings; its conditional review is not approval of a new mesh.
   These helpers do not automatically approve results or suppress failed checks.

3. Prepare the flow case from the new mesh, then calculate the carrier velocity.

   python3 simulation/prepare_case.py four flow
   bash simulation/foam.sh simulation-runs/four/flow simpleFoam

   The stored settings run to iteration 600, not 600 physical seconds. Inspect
   completion, residual history, flux balance, outlet reversal, pressure changes
   and velocity settling before using the flow in a tracer run.

   Alternatively, replace the simpleFoam command with the original eight-way
   decomposition sequence (do not run both on the same fresh case):

   bash simulation/foam.sh simulation-runs/four/flow decomposePar
   bash simulation/foam.sh simulation-runs/four/flow mpirun -np 8 simpleFoam -parallel
   bash simulation/foam.sh simulation-runs/four/flow reconstructPar

4. Prepare the tracer case. The helper copies the reconstructed 600/U and 600/phi
   from this new carrier case; it refuses to continue if either field is missing.

   python3 simulation/prepare_case.py four tracer
   bash simulation/foam.sh simulation-runs/four/tracer scalarTransportFoam

   The matched tracer templates use a 0.05-second step, 40-second history and four
   non-orthogonal corrections. Inspect concentration bounds, full probe history
   and conservative budget before interpreting arrival times.

5. Repeat steps 1-4 with five instead of four for the five-inlet configuration.
   Use four-fine for the corrected fine-reference configuration. Prepare each
   stage only once: existing reproduction directories are never overwritten.

6. Open a prepared case's reactor.foam file in a host ParaView installation.
   The container supplies OpenFOAM; it need not contain the ParaView GUI.

   paraview simulation-runs/four/tracer/reactor.foam

GEOMETRY REGENERATION AND PROPERTY CALCULATIONS

The archived surfaces can be used directly; no Python numerical packages are
required just to prepare a case and run OpenFOAM. To regenerate geometry:

   python3 -m venv .venv-simulation
   . .venv-simulation/bin/activate
   pip install -r simulation/requirements.txt
   python simulation/build_geometry.py four --output simulation-runs/four-surface
   python simulation/build_geometry.py five --output simulation-runs/five-surface

These commands build and check closed labelled surfaces. Surface tessellation can
vary with library versions; use the archived STL for the closest reproduction of
the published mesh inputs. Surface topology checks are not CFD validation.

   python3 scripts/check_nist_operating_point.py

This recalculates unit conversions and regime estimates from the included NIST
property table and operating-point input. It rewrites the derived regime-checks
file; inspect the diff if using a different Python/platform version.

EARLIER EXERCISES

Day 0 and day 1 inputs document the learning progression; the helper above targets
the 3D study. Copy an earlier case to a fresh directory before running it. Generate
its volume mesh from its blockMeshDict. For tracer-only cases, first regenerate
the matching carrier mesh, solve the matching carrier case and copy its final U
and phi into tracer/0. These dependencies are not supplied as frozen large fields.
Historical fine-tracer failures are retained for inspection, not recommended as
the production setup. Use the matched-study templates for the final comparison.

PUBLICATION VALIDATION

The source files have been audited and fingerprinted. Geometry regeneration,
case preparation and OpenFOAM dictionary parsing are checked before publication.
Publishing these files does not mean the full 3D solver study was rerun from a
fresh clone, nor that reproduced fields will be bit-for-bit identical. Resolution
sensitivity and physical validation limitations in the main README still apply.
