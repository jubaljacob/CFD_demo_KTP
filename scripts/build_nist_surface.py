"""Build a labelled, closed gas boundary for the reviewed NIST-inspired geometry.

Units in the geometry spec are mm; all exported geometry is in metres.
Requires the existing numpy/matplotlib environment; no CAD dependencies.
"""
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/ktp-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "openfoam/nist3d/geometry"
SPEC = ROOT / "geometry/nist-3d/geometry-spec.json"
G = json.loads(SPEC.read_text())
N_MAIN, N_TUBE = 192, 64
POINTS, FACES, LABELS = [], [], []
LOOKUP = {}


def vertex(p):
    key = tuple(round(float(x), 10) for x in p)  # mm, shared topology
    if key not in LOOKUP:
        LOOKUP[key] = len(POINTS)
        POINTS.append(key)
    return LOOKUP[key]


def triangle(ids, label, direction=None):
    ids = list(ids)
    a, b, c = np.asarray([POINTS[i] for i in ids])
    normal = np.cross(b - a, c - a)
    if direction is not None and np.dot(normal, direction) < 0:
        ids[1], ids[2] = ids[2], ids[1]
    FACES.append(ids)
    LABELS.append(label)


def ring(r, z, n=N_MAIN, xy=(0, 0)):
    return [vertex((xy[0] + r * math.cos(2 * math.pi * i / n),
                    xy[1] + r * math.sin(2 * math.pi * i / n), z))
            for i in range(n)]


def loft(rbottom, zbottom, rtop, ztop, label, n=N_MAIN, xy=(0, 0), inward=False):
    assert ztop > zbottom
    # A straight generator needs only its end rings. Extra coplanar strips do
    # not improve geometric fidelity and create avoidable intersection ambiguity.
    # This surface tessellation is independent of the later volume-cell size.
    count = 1
    loops = [ring(rbottom + (rtop - rbottom) * i / count,
                  zbottom + (ztop - zbottom) * i / count, n, xy)
             for i in range(count + 1)]
    for lower, upper in zip(loops[:-1], loops[1:]):
        for i in range(n):
            j = (i + 1) % n
            for face in [(lower[i], lower[j], upper[j]), (lower[i], upper[j], upper[i])]:
                triangle(face[::-1] if inward else face, label)


def annulus(inner, outer, z, label, sign):
    a, b = ring(inner, z), ring(outer, z)
    for i in range(N_MAIN):
        j = (i + 1) % N_MAIN
        triangle((a[i], b[i], b[j]), label, (0, 0, sign))
        triangle((a[i], b[j], a[j]), label, (0, 0, sign))


def disk(r, z, label, sign, n=N_MAIN, xy=(0, 0)):
    loop, centre = ring(r, z, n, xy), vertex((*xy, z))
    for i in range(n):
        triangle((centre, loop[i], loop[(i + 1) % n]), label, (0, 0, sign))


def perforated_disk(outer, z, holes, label, sign):
    # Delaunay triangles wholly inside circular holes are removed. The subsequent
    # edge-incidence check is essential: it detects any unpreserved hole edge.
    ids = ring(outer, z)
    for xy, r, n in holes:
        ids.extend(ring(r, z, n, xy))
    points = np.array([POINTS[i][:2] for i in ids])
    triangulation = mtri.Triangulation(points[:, 0], points[:, 1])
    for local in triangulation.triangles:
        centre = points[local].mean(axis=0)
        if any(np.linalg.norm(centre - np.array(xy)) < r * math.cos(math.pi / n)
               for xy, r, n in holes):
            continue
        triangle([ids[i] for i in local], label, (0, 0, sign))


def build():
    if G["units"] != "mm":
        raise ValueError("Expected geometry dimensions in mm")
    cone, body, junction = G["cone"], G["body"], G["junction"]
    loft(cone["radius_bottom"], cone["z_bottom"], cone["radius_top"], cone["z_top"], "walls")
    assert junction["radius"] == body["radius"] and junction["z_bottom"] == body["z_top"]
    # Preserve both lengths but omit the coplanar seam in this continuous bore.
    loft(body["radius"], body["z_bottom"], body["radius"], junction["z_top"], "walls")
    ins, outs, wafer = G["inlets"], G["outlets"], G["wafer"]
    perforated_disk(cone["radius_top"], ins["z_chamber"],
                    [(xy, ins["radius"], N_TUBE) for xy in ins["centres_xy"]], "walls", 1)
    for name, xy in zip(ins["names"], ins["centres_xy"]):
        loft(ins["radius"], ins["z_chamber"], ins["radius"], ins["z_boundary"],
             "walls", N_TUBE, xy)
        disk(ins["radius"], ins["z_boundary"], name, 1, N_TUBE, xy)
    support = G["support_sections"]
    disk(wafer["radius"], wafer["z"], "wafer", -1)
    annulus(wafer["radius"], support[0]["radius"], wafer["z"], "support", -1)
    spans = []
    for section in support:
        if spans and spans[-1]["radius"] == section["radius"] and spans[-1]["z_bottom"] == section["z_top"]:
            spans[-1]["z_bottom"] = section["z_bottom"]
        else:
            spans.append(dict(section))
    for section in spans:
        loft(section["radius"], section["z_bottom"], section["radius"], section["z_top"],
             "support", inward=True)
    for upper, lower in zip(support[:-1], support[1:]):
        if upper["z_bottom"] != lower["z_top"]:
            raise ValueError("Support sections must touch without overlap")
        ru, rl = upper["radius"], lower["radius"]
        if ru != rl:
            annulus(min(ru, rl), max(ru, rl), upper["z_bottom"], "support", -1 if rl > ru else 1)
    perforated_disk(body["radius"], outs["z_chamber"],
                    [((0, 0), support[-1]["radius"], N_MAIN)] +
                    [(xy, outs["radius"], N_TUBE) for xy in outs["centres_xy"]], "walls", -1)
    for name, xy in zip(outs["names"], outs["centres_xy"]):
        loft(outs["radius"], outs["z_boundary"], outs["radius"], outs["z_chamber"],
             "walls", N_TUBE, xy)
        disk(outs["radius"], outs["z_boundary"], name, -1, N_TUBE, xy)


def validate(points, faces, expected_volume=None):
    edge_faces = defaultdict(list)
    oriented = Counter()
    for fi, face in enumerate(faces):
        for a, b in zip(face, np.roll(face, -1)):
            edge_faces[tuple(sorted((int(a), int(b))))].append(fi)
            oriented[(int(a), int(b))] += 1
    bad_edges = [e for e, fs in edge_faces.items() if len(fs) != 2]
    bad_orientation = [e for e in edge_faces if oriented[e] != 1 or oriented[e[::-1]] != 1]
    tri = points[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = np.linalg.norm(normals, axis=1) / 2
    volume = np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6
    neighbours = defaultdict(list)
    for linked in edge_faces.values():
        if len(linked) == 2:
            a, b = linked
            neighbours[a].append(b)
            neighbours[b].append(a)
    unseen = set(range(len(faces)))
    components = 0
    while unseen:
        components += 1
        pending = [unseen.pop()]
        while pending:
            for j in neighbours[pending.pop()]:
                if j in unseen:
                    unseen.remove(j)
                    pending.append(j)
    duplicates = len(faces) - len({tuple(sorted(f)) for f in faces})
    if expected_volume is None:
        expected_volume = json.loads((ROOT / "physics/nist-3d/regime-checks.json").read_text())["analytic_gas_volume_m3"]
    patches = {}
    for label in sorted(set(LABELS)):
        mask = np.array(LABELS) == label
        record = {"triangles": int(mask.sum()), "area_m2": float(areas[mask].sum()),
                  "oriented_area_vector_m2": (normals[mask].sum(axis=0) / 2).tolist()}
        radius = G["wafer"]["radius"] if label == "wafer" else G["inlets"]["radius"] if label.startswith("inlet") else G["outlets"]["radius"] if label.startswith("outlet") else None
        if radius:
            analytic = math.pi * (radius * 1e-3)**2
            record.update(analytic_area_m2=analytic, area_error_percent=100 * (record["area_m2"] / analytic - 1))
        patches[label] = record
    report = {
        "status": "Python topology checks only; consult OpenFOAM surfaceCheck for self-intersection check",
        "units": "metres", "vertices": len(points), "triangles": len(faces),
        "boundary_connected_components": components,
        "edges_without_exactly_two_faces": len(bad_edges), "inconsistently_oriented_edges": len(bad_orientation),
        "duplicate_triangles": duplicates, "zero_area_triangles": int((areas <= 1e-20).sum()),
        "signed_gas_volume_m3": float(volume), "analytic_gas_volume_m3": expected_volume,
        "volume_error_percent": 100 * (volume / expected_volume - 1),
        "bounding_box_m": [points.min(axis=0).tolist(), points.max(axis=0).tolist()],
        "patches": patches,
        "circle_segments": {"main": N_MAIN, "tubes": N_TUBE},
        "spec_sha256": hashlib.sha256(SPEC.read_bytes()).hexdigest(),
        "assumptions": "Reviewed geometry rev1; no new physical dimensions. Circular surfaces approximated by polygons.",
        "acceptance": "Closed oriented connected surface; positive volume; area and volume polygon errors below 0.2%. This is geometric consistency, not CFD validation."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "surface-checks.json").write_text(json.dumps(report, indent=2) + "\n")
    if bad_edges or bad_orientation or duplicates or components != 1 or (areas <= 1e-20).any() or volume <= 0:
        raise ValueError(f"Surface failed topology: see {OUT / 'surface-checks.json'}; example edges {bad_edges[:5]}")
    if abs(report["volume_error_percent"]) > .2 or any(abs(p.get("area_error_percent", 0)) > .2 for p in patches.values()):
        raise ValueError("Surface polygon approximation exceeds geometry tolerance")
    return report, normals


def export(points, faces, normals):
    with (OUT / "reactor.stl").open("w") as f:
        for label in sorted(set(LABELS)):
            f.write(f"solid {label}\n")
            for i, face in enumerate(faces):
                if LABELS[i] != label:
                    continue
                normal = normals[i] / np.linalg.norm(normals[i])
                f.write("facet normal " + " ".join(f"{v:.12g}" for v in normal) + "\nouter loop\n")
                for point in points[face]:
                    f.write("vertex " + " ".join(f"{v:.12g}" for v in point) + "\n")
                f.write("endloop\nendfacet\n")
            f.write(f"endsolid {label}\n")
    labels = sorted(set(LABELS))
    (OUT / "region-labels.json").write_text(json.dumps(dict(enumerate(labels)), indent=2) + "\n")
    with (OUT / "reactor.vtk").open("w") as f:
        f.write("# vtk DataFile Version 3.0\nNIST-inspired gas boundary, metres\nASCII\nDATASET POLYDATA\n")
        f.write(f"POINTS {len(points)} double\n")
        for p in points:
            f.write(" ".join(f"{v:.12g}" for v in p) + "\n")
        f.write(f"POLYGONS {len(faces)} {len(faces)*4}\n")
        for face in faces:
            f.write("3 " + " ".join(map(str, face)) + "\n")
        f.write(f"CELL_DATA {len(faces)}\nSCALARS region_id int 1\nLOOKUP_TABLE default\n")
        f.write("\n".join(str(labels.index(label)) for label in LABELS) + "\n")


def clip_above_z(triangle, zmin):
    """Clip display polygons only; exported geometry is never cut away."""
    polygon = []
    for a, b in zip(triangle, np.roll(triangle, -1, axis=0)):
        a_in, b_in = a[2] >= zmin, b[2] >= zmin
        if a_in:
            polygon.append(a)
        if a_in != b_in:
            polygon.append(a + (b - a) * ((zmin - a[2]) / (b[2] - a[2])))
    return polygon


def preview(points, faces):
    tri = points[faces] * 1000
    labels = np.array(LABELS)
    palette = {"walls": "#a7c3d8", "support": "#b69e85", "wafer": "#166db5"}
    fig = plt.figure(figsize=(12, 9), layout="constrained")
    for k, (title, zoom) in enumerate([("Whole gas boundary — front wall cut away", False), ("Inlets and raised wafer — detail", True)], start=1):
        ax = fig.add_subplot(1, 2, k, projection="3d")
        shown, colours = [], []
        for label in sorted(set(labels)):
            mask = labels == label
            if label == "walls":
                mask &= tri[:, :, 1].mean(axis=1) >= 0
            if zoom:
                mask &= tri[:, :, 2].max(axis=1) >= -200
            colour = palette.get(label, "#da563c" if label.startswith("inlet") else "#eb9a24")
            for face in tri[mask]:
                polygon = clip_above_z(face, -210) if zoom else face
                if len(polygon) >= 3:
                    shown.append(polygon)
                    colours.append(to_rgba(colour, .35 if label == "walls" else 1))
        # One collection lets matplotlib depth-sort individual triangles across
        # regions, instead of hiding the wafer behind the entire support object.
        ax.add_collection3d(Poly3DCollection(shown, facecolors=colours, edgecolor="none", antialiased=False))
        ax.set(xlim=(-60, 60), ylim=(-60, 60), zlim=(-210 if zoom else -550, 20),
               xlabel="x (mm)", ylabel="y (mm)", zlabel="z (mm)", title=title)
        ax.set_box_aspect((120, 120, 230 if zoom else 570))
        ax.view_init(elev=25 if zoom else 15, azim=-65)
        ax.tick_params(labelsize=8)
    fig.suptitle("NIST-inspired reactor: labelled surface geometry\nGeometry only — no flow solution", fontsize=15)
    fig.legend(handles=[Patch(color=c, label=l) for l, c in
                        [("Chamber / tube walls (cut away)", "#a7c3d8"), ("Solid support", "#b69e85"),
                         ("50 mm wafer", "#166db5"), ("4 inlet caps", "#da563c"), ("2 outlet caps", "#eb9a24")]],
               loc="lower center", ncol=3, fontsize=9)
    fig.savefig(OUT / "surface-preview.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    build()
    points = np.asarray(POINTS) * 1e-3
    faces = np.asarray(FACES)
    report, normals = validate(points, faces)
    export(points, faces, normals)
    preview(points, faces)
    print(json.dumps({key: report[key] for key in ["vertices", "triangles", "boundary_connected_components", "edges_without_exactly_two_faces", "inconsistently_oriented_edges", "volume_error_percent"]}, indent=2))
    print(f"Created geometry and checks in {OUT}")
