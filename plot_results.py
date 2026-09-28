"""Plot the Fusion variant study results."""

import pandas as pd
import plotly.express as px

df = pd.read_csv('variant_results.csv')
df['rib_count'] = df['rib_count'].astype(str)  # treat as categories, not a scale

# Chart 1: mass against rib thickness, one line per rib count
fig = px.line(
    df, x='rib_thickness_mm', y='mass_g', color='rib_count', markers=True,
    title='Mass against rib thickness',
    labels={'rib_thickness_mm': 'Rib thickness (mm)', 'mass_g': 'Mass (g)',
            'rib_count': 'Ribs'},
)
fig.write_html('mass_vs_thickness.html')
fig.show()

# Chart 2: the 3D design space, one dot per variant
fig3d = px.scatter_3d(
    df, x='rib_count', y='rib_thickness_mm', z='mass_g', color='mass_g',
    title='Design space',
    labels={'rib_thickness_mm': 'Rib thickness (mm)', 'mass_g': 'Mass (g)',
            'rib_count': 'Ribs'},
)
fig3d.write_html('design_space_3d.html')
fig3d.show()