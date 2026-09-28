"""Record the FreeCAD FEA results and compare them with the beam estimate."""

import pandas as pd

FORCE_N = 1000

fea = pd.DataFrame({
    'rib_count': [3, 5],
    'rib_thickness_mm': [6, 4],
    'fea_displacement_um': [1.67, 1.72],
    'fea_max_stress_MPa': [106.46, 98.21],
})

fea['fea_stiffness_kN_per_mm'] = round(
    FORCE_N / (fea['fea_displacement_um'] / 1000) / 1000, 1)

study = pd.read_csv('variant_results_with_stiffness.csv') #reads the result from the 15 variants and the estimated stiffness from add_stiffness.py

merged = fea.merge(  #joins the FEA results with the estimated stiffness from add_stiffness.py, based on rib count and thickness
    study[['rib_count', 'rib_thickness_mm', 'mass_g', 'stiffness_kN_per_mm']],
    on=['rib_count', 'rib_thickness_mm'])

merged = merged.rename(
    columns={'stiffness_kN_per_mm': 'estimated_stiffness_kN_per_mm'})

merged['estimate_error_pct'] = round(
    (merged['estimated_stiffness_kN_per_mm'] - merged['fea_stiffness_kN_per_mm'])
    / merged['fea_stiffness_kN_per_mm'] * 100, 1)

merged.to_csv('fea_validation.csv', index=False)

print(merged.to_string(index=False))