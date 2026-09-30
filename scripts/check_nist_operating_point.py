"""Reproduce the NIST-inspired pilot's unit conversions and regime screening.

Only standard-library dependencies. Inputs and outputs are rooted in this project.
This calculates estimates; it does not run or validate a CFD solution.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "physics/nist-3d"


def main():
    spec_path = OUT / "operating-point.json"
    s = json.loads(spec_path.read_text())
    geometry_path = ROOT / s["geometry_file"]
    g = json.loads(geometry_path.read_text())
    if g["units"] != "mm":
        raise ValueError("Geometry must use millimetres")
    property_path = ROOT / s["carrier_property_file"]
    with property_path.open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if len(rows) != 1:
        raise ValueError("Expected exactly one NIST fluid state")
    row = rows[0]
    temp, pressure = s["temperature_K"], s["pressure_absolute_Pa"]
    if not math.isclose(float(row["Temperature (K)"]), temp) or not math.isclose(float(row["Pressure (bar)"]) * 1e5, pressure):
        raise ValueError("NIST property state differs from selected operating point")
    rho = float(row["Density (kg/m3)"])
    mu = float(row["Viscosity (Pa*s)"])
    sound = float(row["Sound Spd. (m/s)"])
    gas_R = s["gas_constant_J_per_mol_K"] / s["molar_mass_kg_per_mol"]
    rho_std_ideal = s["standard_pressure_Pa"] / (gas_R * s["standard_temperature_K"])
    q_std = s["total_standard_flow_sccm"] * 1e-6 / 60
    mdot = rho_std_ideal * q_std
    q = mdot / rho
    nu = mu / rho
    ni, no = len(g["inlets"]["centres_xy"]), len(g["outlets"]["centres_xy"])
    ri, ro = g["inlets"]["radius"] * 1e-3, g["outlets"]["radius"] * 1e-3
    ai, ao = ni * math.pi * ri**2, no * math.pi * ro**2
    ui = q / ai
    # Viscosity-based mean free path convention; use geometric L, not particle L.
    mean_free_path = mu * math.sqrt(math.pi / (2 * rho * pressure))
    t = s["tracer"]
    if not t["temperature_fit_range_K"][0] <= temp <= t["temperature_fit_range_K"][1]:
        raise ValueError("Temperature is outside the sourced diffusion fit")
    d_at_ref_p = math.exp(t["A"] + t["B_K"] / temp + t["C"] * math.log(temp)) * 1e-4
    diffusion = d_at_ref_p * t["reference_pressure_Pa"] / pressure
    cone = g["cone"]
    h = (cone["z_top"] - cone["z_bottom"]) * 1e-3
    rt, rb = cone["radius_top"] * 1e-3, cone["radius_bottom"] * 1e-3
    cone_volume = math.pi * h * (rt**2 + rt * rb + rb**2) / 3

    def cylinder_volume(section):
        return math.pi * (section["radius"] * 1e-3)**2 * (section["z_top"] - section["z_bottom"]) * 1e-3

    volume = cone_volume + cylinder_volume(g["junction"]) + cylinder_volume(g["body"])
    volume -= sum(cylinder_volume(section) for section in g["support_sections"])
    volume += ai * abs(g["inlets"]["z_boundary"] - g["inlets"]["z_chamber"]) * 1e-3
    volume += ao * abs(g["outlets"]["z_boundary"] - g["outlets"]["z_chamber"]) * 1e-3
    if volume <= 0:
        raise ValueError("Nonpositive gas-volume estimate")
    radius = g["body"]["radius"] * 1e-3
    passages = []
    for section in g["support_sections"]:
        rs = section["radius"] * 1e-3
        gap = radius - rs
        if gap <= 0:
            raise ValueError("Support closes passage")
        u = q / (math.pi * (radius**2 - rs**2))
        passages.append({"section": section["name"], "radial_gap_m": gap,
                         "mean_axial_speed_estimate_m_per_s": u,
                         "Re_hydraulic_diameter": u * 2 * gap / nu,
                         "Kn_radial_gap": mean_free_path / gap})
    results = {
        "status": "pre-mesh estimates; carrier and tracer solution checks still pending",
        "rho_kg_per_m3": rho, "mu_Pa_s": mu, "nu_m2_per_s": nu,
        "sound_speed_m_per_s": sound,
        "rho_standard_ideal_kg_per_m3": rho_std_ideal,
        "rho_operating_ideal_kg_per_m3": pressure / (gas_R * temp),
        "standard_volume_flow_m3_per_s": q_std,
        "mass_flow_kg_per_s": mdot, "local_volume_flow_m3_per_s": q,
        "local_volume_flow_litre_per_min": q * 60000,
        "inlet_total_analytic_area_m2": ai,
        "volume_flow_per_inlet_m3_per_s": q / ni,
        "mass_flow_per_inlet_kg_per_s": mdot / ni,
        "inlet_mean_speed_m_per_s": ui,
        "inlet_Re_diameter": ui * 2 * ri / nu,
        "inlet_Mach": ui / sound,
        "mean_free_path_m": mean_free_path,
        "inlet_Kn_diameter": mean_free_path / (2 * ri),
        "mean_exhaust_speed_equal_split_estimate_m_per_s": q / ao,
        "support_passages": passages,
        "diffusion_at_reference_pressure_m2_per_s": d_at_ref_p,
        "label_diffusivity_m2_per_s": diffusion,
        "Schmidt_nu_over_D": nu / diffusion,
        "inlet_Peclet_Ud_over_D": ui * 2 * ri / diffusion,
        "analytic_gas_volume_m3": volume,
        "nominal_volume_over_flow_time_s": volume / q,
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [spec_path, geometry_path, property_path,
                                   ROOT / "references/nist-reactor/NIST.TN.2279.pdf"]},
        "formula_notes": [
            "sccm to m3/s: multiply by 1e-6/60; standard molar flow uses ideal gas convention.",
            "mdot = Qstandard*pstandard/(R_specific*Tstandard); Qlocal = mdot/rho_NIST.",
            "nu=mu/rho; Re=U*L/nu; Mach=U/sound; lambda=mu*sqrt(pi/(2*rho*p)); Kn=lambda/L.",
            "D from NIST full temperature fit in cm2/s, converted to m2/s and multiplied by 101325/p.",
            "Volume is analytic for the simplified envelope, including inlet/outlet tubes; compare with mesh volume.",
            "V/Q is a nominal turnover scale, not a prediction of wafer arrival time or complete replacement.",
            "Passage speeds assume net Q crossing each annulus; local jets and recirculation are unresolved."
        ]
    }
    limits = s["screening_limits"]
    results["screening"] = {
        "inlet_low_Mach": results["inlet_Mach"] < limits["inlet_Mach_below"],
        "geometric_continuum": max([results["inlet_Kn_diameter"]] + [x["Kn_radial_gap"] for x in passages]) < limits["geometric_Knudsen_below"],
        "laminar": "low inlet and passage Reynolds estimates support a laminar pilot; steadiness remains untested",
        "constant_density": "conditional on post-solve pressure variation and uniform-temperature assumption"
    }
    target = OUT / "regime-checks.json"
    target.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    print(json.dumps(results, indent=2, allow_nan=False))
    print(f"Saved: {target}")


if __name__ == "__main__":
    main()
