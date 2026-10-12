# Parametric Rib Study: Automated Design Exploration in Fusion 360

<p align="center">
  <img src="images/15_variants.gif" width="700" alt="The 15 variants rebuilding automatically">
</p>
<p align="center"><em>All 15 variants generated automatically by the Python script.</em></p>

A small generative design pipeline. A parametric mounting hub is driven from Python through the Fusion 360 API, 15 design variants are generated automatically, each is checked for buildability, and each is evaluated for mass and sideways stiffness. A quick stiffness estimate is then checked against finite element analysis in FreeCAD.

## The question

The part is a hub bolted down through its base, with a shaft through the central bore. When the shaft is pushed sideways, the ribs stop the hub from bending over.

**For a given mass, how should the ribs be arranged to make the hub as stiff as possible? Fewer thick ribs, or more thin ones?**

## Pipeline

1. **Parametric model (Fusion 360).** Every key dimension is a named User Parameter, so changing one value rebuilds the whole part.
2. **Variant generation (Python, Fusion API).** A script loops through every combination of rib count and wall thickness, rebuilds the model, checks every feature rebuilt successfully, and records mass, volume and surface area to CSV.
3. **Buildability check (Python).** Each design is checked for enough material between the bolt counterbores and the rib walls.
4. **Stiffness estimate (Python).** Each rib wall is treated as a cantilever beam, with its contribution weighted by its orientation to the load.
5. **Trade off analysis (pandas, Plotly).** Stiffness is plotted against mass, and the Pareto front is identified among buildable designs.
6. **FEA validation (FreeCAD, CalculiX).** Two designs of near identical mass are simulated to test the estimate.

## The parametric model

The base geometry follows a Fusion 360 tutorial part. The work in this project is in making it robustly parametric and building the study around it.

The tutorial version could not change its rib count, because the ribs were drawn and trimmed as sketch lines. I rebuilt it so that a single rib is a solid feature, and the slots and bolt holes are patterned features, all driven by `rib_count`. The bolt holes are positioned at an angle of `180 deg / rib_count`, so they stay centred between the ribs for any rib count.

<p align="center">
  <img src="images/parametric-rib-study.gif" width="700" alt="Building the parametric model step by step">
</p>
<p align="center"><em>The model built step by step: base, hub, one rib, then patterned slots and holes driven by rib_count.</em></p>

| Parameter | Baseline | Role |
|---|---|---|
| `rib_count` | 3 | Number of ribs, slots and bolt holes |
| `rib_thickness` | 5 mm | Thickness of each rib wall |
| `slot_width` | 10 mm | Gap between the two walls of a rib |
| `rib_height` | 20 mm | Height of ribs and hub above the base |
| `base_diameter` | 82 mm | Outer diameter of the base |
| `hub_diameter` | 26 mm | Diameter of the central hub |
| `hole_radius` | 33 mm | Distance from the centre to each bolt hole |

Rib width is `slot_width + 2 * rib_thickness`, and the slot depth is linked to `rib_height`.

<p align="center">
  <img src="images/Baseline.png" width="700" alt="Baseline design">
</p>
<p align="center"><em>The baseline design: 3 ribs, 5 mm walls.</em></p>

Fillets and chamfers were excluded from the study. Their edges change with rib count (with three ribs a thin strip of hub separates adjacent walls, with four or more the walls meet directly), so they cannot follow the pattern reliably. Their effect on mass is negligible.

## Design constraints

The first version of the study used a 62 mm base with holes 21.55 mm from the centre. Checking the results showed that 7 of the 15 designs could not be built: with more or thicker ribs, the counterbores cut into the rib walls.

I added a buildability rule, requiring at least 2 mm of material between each counterbore and the nearest rib wall:

```
clearance = hole_radius × sin(180° / rib_count) − (slot_width / 2 + rib_thickness) − counterbore_radius
```

I then enlarged the base to 82 mm and moved the holes out to 33 mm, so that every design in the study passes. The tightest case, 5 ribs with 7 mm walls, has 2.4 mm of clearance. The check stays in the analysis, so any future change to the ranges is caught automatically.

## Variant study

15 variants: `rib_count` of 3, 4 and 5, and `rib_thickness` of 3 to 7 mm. All 15 rebuilt without errors and all 15 are buildable. Masses range from 412 g to 624 g (steel).

<p align="center">
  <img src="images/mass-against-rib-thickness.png" width="700" alt="Mass against rib thickness">
</p>

Mass rises linearly with wall thickness. Each extra rib adds less mass than the one before (at 7 mm, going from 3 to 4 ribs adds about 54 g, but 4 to 5 adds about 39 g), because ribs overlap more near the hub as they crowd together, and overlapping material only counts once.

<p align="center">
  <img src="images/design-space.png" width="700" alt="3D design space: rib count, wall thickness and mass">
</p>

Each dot is one generated design, positioned by its rib count, wall thickness and mass.

## Stiffness against mass

<p align="center">
  <img src="images/stiffness-against-mass.png" width="700" alt="Stiffness against mass">
</p>

Fourteen of the fifteen designs sit on the Pareto front, meaning no other design is both lighter and stiffer. The one exception is **4 ribs at 6 mm**, which is beaten by **5 ribs at 5 mm**: 1.8 g lighter and, on the estimate, about 3% stiffer. This is the one clear claim the estimate makes, so it is the one I tested with FEA.

## FEA validation

Both designs were simulated in FreeCAD with CalculiX under identical conditions: base fixed, 1000 N applied sideways across the bore wall, steel, 2 mm mesh.

| Design | Mass | Estimated stiffness | FEA stiffness | Estimate error | FEA max stress |
|---|---|---|---|---|---|
| 5 ribs, 5 mm | 547.9 g | 3,539 kN/mm | 3,493 kN/mm | +1.3% | 3.31 MPa |
| 4 ribs, 6 mm | 549.8 g | 3,444 kN/mm | 3,379 kN/mm | +1.9% | 3.30 MPa |

<p align="center">
  <img src="images/fea_ribs5_t5.png" height="320" alt="FEA displacement, 5 ribs 5 mm">
  <img src="images/fea_ribs4_t6.png" height="320" alt="FEA displacement, 4 ribs 6 mm">
</p>
<p align="center"><em>Displacement under a 1000 N sideways load, on the same colour scale. Left: 5 ribs, 5 mm. Right: 4 ribs, 6 mm.</em></p>

## Findings

1. **More, thinner ribs give more stiffness per gram.** FEA confirms the 5 rib, 5 mm design is 3.4% stiffer than the 4 rib, 6 mm design while being slightly lighter, matching the estimate's ranking.
2. **The beam estimate was accurate to within 2%** for this geometry, which makes it a reliable way to screen many variants quickly.
3. **Peak stress is almost identical and very low** (about 3.3 MPa at 1000 N), so strength does not govern this design. Stiffness per gram does.
4. **Buildability changed the design.** A third of the original variants could not be manufactured, which forced a larger base and a wider hole pattern.

## From requirement to production files

The study answers "which design is best?". The next step was to automate the whole route from a requirement to the files a manufacturer needs, with no manual step in between.

1. **`configurator.py`** takes a stiffness requirement and a minimum bolt hole clearance, the manufacturer's own rule. It removes designs that break the rule, removes designs that are not stiff enough, and returns the lightest one left. It saves the choice to `chosen_design.json`.
2. **`production_pack.py`**, a Fusion 360 script, reads that choice, rebuilds the design in Fusion and exports a production pack: a STEP file, a sheet of bolt hole coordinates, and a summary of dimensions and mass.

| Requirement | Clearance rule | Rejected by rule | Rejected as too flexible | Chosen design |
|---|---|---|---|---|
| 3000 kN/mm | 2 mm | 0 | 9 | 3 ribs, 7 mm, 531.2 g |
| 3000 kN/mm | 5 mm | 3 | 9 | 3 ribs, 7 mm, 531.2 g |

The stricter clearance rule removes the three 5 rib designs, where the ribs sit closest to the bolt holes. The chosen design is unaffected because it has 11.6 mm of clearance.

**Checking the output.** The hole coordinates are calculated from the parameters, not measured. I checked them against the model with Fusion's Measure tool: hole 2 measured at Z = −33.00 mm, Y = 0.00 mm, matching the sheet exactly.

## Machining simulation

<p align="center"><img src="images/simulation.gif" width="700"></p>

The chosen design was programmed for CNC milling in Fusion 360's Manufacture workspace, cut from an 84 mm round bar:

| Operation | Tool | Purpose |
|---|---|---|
| 2D Adaptive Roughing | 6 mm flat end mill | Clears between the ribs and inside the slots |
| 2D Contour | 16 mm flat end mill | Cuts the outside profile in 5 mm layers |
| Bore | 6 mm flat end mill | Cuts the counterbores |
| Drill | Drill | Drills the bolt holes |
| Bore | 16 mm flat end mill | Cuts the centre hole |

Fusion's verification reports **0 collisions**. Getting there took several fixes, and each one taught me something about designing for manufacture:

- **Holes in a selected floor are treated as islands.** The first roughing pass left a column of metal above each bolt hole. Selecting the floor boundaries as open chains closed by the stock fixed it.
- **A round cutter cannot make a sharp inside corner.** The tool leaves material equal to its radius in every inside corner, so the design now has 3.5 mm corner fillets, larger than the 3 mm tool radius. This is a manufacturing rule I would add to the configurator next, alongside the bolt hole clearance.
- **Tool reach matters.** The 6 mm cutter's 20 mm cutting length only just covers the rib height, so the deep cuts use a 16 mm tool.

### How this maps to offsite manufacturing

| This project | Offsite manufacturing |
|---|---|
| Design parameters | The building design |
| Clearance rule | The factory's product rules |
| Configurator | Automatic project set up |
| Production pack | Production drawings and machine files |

## Lessons

- **Check buildability, not just performance.** The original study looked complete until the geometry was checked for clashes. Adding the rule turned it into a real design constraint rather than an afterthought.
- **How the load is applied can matter more than the model.** My first simulations applied the force to the rim edge of the bore rather than its wall. That concentrated the load on a line and produced displacements around six times too large and stresses around thirty times too high, which made the estimate look 20 to 30% wrong. Applying the load correctly brought the error under 2%.

## Limitations

- **The estimate's accuracy may be partly coincidental.** It ignores shear, which makes it too stiff, and ignores how the hub and base support the ribs, which makes it too soft. These may partly cancel for this geometry, so it should be rechecked before trusting it for very different proportions.
- **Only two designs were simulated.** The FEA checks the key ranking, not the whole design space.
- **Maximum stress is approximate**, because sharp internal corners (fillets excluded) make it mesh dependent.

## Next steps

- Automate the FEA through FreeCAD's Python API, so every variant gets simulated stiffness rather than an estimate.
- Train a surrogate model on the simulated results to predict stiffness from the parameters.
- Add further parameters, such as rib height or hole position, to explore a larger design space.

## Files

```
variant_test.py                        Fusion script: change rib_count and read mass
variant_study.py                       Fusion script: generate all 15 variants to CSV
plot_results.py                        Mass charts
add_stiffness.py                       Buildability check, stiffness estimate, Pareto front
fea_validation.py                      Compares the estimate with FEA
variant_results.csv                    Raw results from Fusion
variant_results_with_stiffness.csv     Results with stiffness and buildability
fea_validation.csv                     Estimate against FEA
ribs5_t5.step, ribs5_t5.FCStd          FEA model, 5 ribs 5 mm
ribs4_t6.step, ribs4_t6.FCStd          FEA model, 4 ribs 6 mm
images/                                Charts, screenshots and animations
configurator.py                        Picks the lightest design that meets a stiffness requirement and a clearance rule
production_pack.py                     Fusion script that rebuilds the chosen design and exports the production pack
production/                            Generated production packs, one folder per design
```

## How to run

1. **Variant study:** open the parametric design in Fusion 360 and run `variant_study.py` from Utilities, Add-Ins, Scripts and Add-Ins. Results are saved to `variant_results.csv`.
2. **Analysis:** install the dependencies with `pip install pandas plotly numpy`, then run `plot_results.py`, `add_stiffness.py` and `fea_validation.py` in that order.
3. **FEA:** open the `.FCStd` files in FreeCAD 1.x with the FEM workbench.
4. **Configurator:** run `python configurator.py` and enter a stiffness requirement and a minimum clearance. The choice is saved to `chosen_design.json`.
5. **Production pack:** open the parametric design in Fusion 360 and run `production_pack.py`. Set the `FOLDER` line to your own project folder first.

## Tools

Fusion 360 and its Python API, Python (pandas, NumPy, Plotly), FreeCAD FEM with CalculiX and Gmsh, Git.

*Fiona Topore*