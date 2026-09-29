"""Estimate lateral stiffness, check buildability, and plot stiffness against mass."""

import numpy as np
import pandas as pd
import plotly.express as px

# Fixed geometry and material (from the Fusion parameters)
E = 200_000            # Young's modulus of steel, N/mm²
RIB_HEIGHT = 20        # mm
BASE_DIAMETER = 82     # mm
HUB_DIAMETER = 26      # mm
SLOT_WIDTH = 10        # mm
HOLE_RADIUS = 33       # mm, centre of part to centre of each bolt hole
CBORE_RADIUS = 5       # mm, counterbore diameter 10 / 2
MIN_WALL = 2           # mm, minimum material between counterbore and rib

WALL_LENGTH = (BASE_DIAMETER - HUB_DIAMETER) / 2


def lateral_stiffness(rib_count, wall_thickness):
    """Cantilever estimate of sideways stiffness, in kN/mm."""
    t, b, h = wall_thickness, WALL_LENGTH, RIB_HEIGHT
    i_strong = t * b**3 / 12
    i_weak = b * t**3 / 12

    total = 0
    for i in range(rib_count):
        angle = 2 * np.pi * i / rib_count
        i_eff = i_strong * np.cos(angle)**2 + i_weak * np.sin(angle)**2
        total += 2 * (3 * E * i_eff / h**3)

    return total / 1000


def hole_clearance(rib_count, wall_thickness):
    """Material between each counterbore and the nearest rib wall, in mm."""
    to_rib_centreline = HOLE_RADIUS * np.sin(np.pi / rib_count)
    half_rib_width = SLOT_WIDTH / 2 + wall_thickness
    return to_rib_centreline - half_rib_width - CBORE_RADIUS


df = pd.read_csv('variant_results.csv')

df['stiffness_kN_per_mm'] = [
    round(lateral_stiffness(n, t), 1)
    for n, t in zip(df['rib_count'], df['rib_thickness_mm'])
]
df['stiffness_per_gram'] = round(df['stiffness_kN_per_mm'] / df['mass_g'], 3)

df['hole_clearance_mm'] = [
    round(hole_clearance(n, t), 2)
    for n, t in zip(df['rib_count'], df['rib_thickness_mm'])
]
df['feasible'] = df['hole_clearance_mm'] >= MIN_WALL

# Pareto front, among buildable designs only
df = df.sort_values('mass_g')
best_so_far = -1
pareto = []
for s, ok in zip(df['stiffness_kN_per_mm'], df['feasible']):
    on_front = ok and s > best_so_far
    pareto.append(on_front)
    if on_front:
        best_so_far = s
df['pareto'] = pareto

df.to_csv('variant_results_with_stiffness.csv', index=False)

df['rib_count'] = df['rib_count'].astype(str)
df['label'] = df['rib_count'] + ' ribs, ' + df['rib_thickness_mm'].astype(str) + ' mm'

fig = px.scatter(
    df, x='mass_g', y='stiffness_kN_per_mm', color='rib_count',
    symbol='pareto', hover_name='label',
    title='Stiffness against mass',
    labels={'mass_g': 'Mass (g)', 'stiffness_kN_per_mm': 'Sideways stiffness (kN/mm)',
            'rib_count': 'Ribs', 'pareto': 'Pareto front'},
)
front = df[df['pareto']]
fig.add_scatter(x=front['mass_g'], y=front['stiffness_kN_per_mm'],
                mode='lines', name='Pareto front', line=dict(dash='dash'))
fig.write_html('stiffness_vs_mass.html')
fig.show()

print(df[['label', 'mass_g', 'stiffness_kN_per_mm', 'hole_clearance_mm',
          'feasible', 'pareto']].to_string(index=False))