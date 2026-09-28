"""Estimate lateral stiffness for each variant and plot it against mass."""

import numpy as np
import pandas as pd
import plotly.express as px

# Fixed geometry and material (from the Fusion parameters)
E = 200_000            # Young's modulus of steel, N/mm²
RIB_HEIGHT = 20        # mm
BASE_DIAMETER = 62     # mm
HUB_DIAMETER = 26      # mm
WALL_LENGTH = (BASE_DIAMETER - HUB_DIAMETER) / 2   # radial length of each wall, mm


def lateral_stiffness(rib_count, wall_thickness):
    """Cantilever estimate of sideways stiffness, in kN/mm."""
    t, b, h = wall_thickness, WALL_LENGTH, RIB_HEIGHT
    i_strong = t * b**3 / 12     # wall pushed along its length
    i_weak = b * t**3 / 12       # wall pushed across its thickness

    total = 0
    for i in range(rib_count):
        angle = 2 * np.pi * i / rib_count
        # How much of each wall's strength lines up with a sideways load
        i_eff = i_strong * np.cos(angle)**2 + i_weak * np.sin(angle)**2
        total += 2 * (3 * E * i_eff / h**3)   # two walls per rib

    return total / 1000   # N/mm to kN/mm


df = pd.read_csv('variant_results.csv')
df['stiffness_kN_per_mm'] = [
    round(lateral_stiffness(n, t), 1)
    for n, t in zip(df['rib_count'], df['rib_thickness_mm'])
]
df['stiffness_per_gram'] = round(df['stiffness_kN_per_mm'] / df['mass_g'], 3)

# Pareto front: designs where nothing else is both lighter and stiffer
df = df.sort_values('mass_g')
best_so_far = -1  #keeps tracl  of the highest stiffness,  strats at below zero so the first design always beats it
pareto = [] #an empty list to hold true or false for each design
for s in df['stiffness_kN_per_mm']:
    pareto.append(s > best_so_far)
    best_so_far = max(best_so_far, s)
df['pareto'] = pareto

df.to_csv('variant_results_with_stiffness.csv', index=False)

df['rib_count'] = df['rib_count'].astype(str) #turns the rib count into text
df['label'] = df['rib_count'] + ' ribs, ' + df['rib_thickness_mm'].astype(str) + ' mm'

fig = px.scatter(
    df, x='mass_g', y='stiffness_kN_per_mm', color='rib_count',
    symbol='pareto', hover_name='label',
    title='Stiffness against mass (circles on the Pareto front are the efficient designs)',
    labels={'mass_g': 'Mass (g)', 'stiffness_kN_per_mm': 'Sideways stiffness (kN/mm)',
            'rib_count': 'Ribs', 'pareto': 'Pareto front'},
)
front = df[df['pareto']]
fig.add_scatter(x=front['mass_g'], y=front['stiffness_kN_per_mm'],    #Draws a dashed line connecting the Pareto designs, so the front is easy to see.
                mode='lines', name='Pareto front', line=dict(dash='dash'))
fig.write_html('stiffness_vs_mass.html')    #saves the file as html and opens in browser
fig.show()

print(df[['label', 'mass_g', 'stiffness_kN_per_mm', 'stiffness_per_gram', 'pareto']]
      .to_string(index=False))