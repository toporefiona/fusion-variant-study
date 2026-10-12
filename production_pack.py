"""Production pack: build the chosen design and export the files a manufacturer needs."""
import csv, json, math, os, traceback
import adsk.core, adsk.fusion

app = adsk.core.Application.get()  #connects to the running fusion
ui = app.userInterface

FOLDER = r'D:\Python\fusion-variant-study' #builds the path to a folder

 
def mm(params, name): #a helper function to convert a parameter to mm
    return params.itemByName(name).value * 10 #finds the value of a parameter and converts it to mm


def run(_context: str):  #the main function that Fusion calls when the script is run
    try:
        with open(os.path.join(FOLDER, 'chosen_design.json')) as f: #opens the chosen design file and reads the parameters
            choice = json.load(f) #turns the json file into a python dictionary
        count = int(choice['rib_count']) #reads as a whole number
        thick = float(choice['rib_thickness_mm']) #reads as a decimal   

        design = adsk.fusion.Design.cast(app.activeProduct) #gets the open design in Fusion
        params = design.userParameters
        params.itemByName('rib_count').expression = str(count) #sets the rib count parameter to the chosen value
        params.itemByName('rib_thickness').expression = f'{thick} mm' #sets the rib thickness parameter to the chosen value
        adsk.doEvents() #lets Fusion update the design with the new parameters

        name = f'ribs{count}_t{thick:g}' #creates a name for the output folder based on the chosen parameters
        out = os.path.join(FOLDER, 'production', name) #gives the path to the output folder
        os.makedirs(out, exist_ok=True) #creates the output folder if it doesn't exist

        exporter = design.exportManager #gets fusions export tools
        step = exporter.createSTEPExportOptions(os.path.join(out, name + '.step')) #prepares to export a STEP file of the design to the output folder
        exporter.execute(step) #runs the export command to create the STEP file

        radius = mm(params, 'hole_radius') #gets the hole radius parameter and converts it to mm
        with open(os.path.join(out, 'holes.csv'), 'w', newline='') as f: #opens a new csv file in the output folder to write the hole data
            writer = csv.writer(f) #creates a csv writer object to write to the file
            writer.writerow(['hole', 'z_mm', 'y_mm', 'diameter_mm',
                             'cbore_diameter_mm', 'cbore_depth_mm']) #writes the header row to the csv file
            for i in range(count):
                angle = math.radians(180 / count + i * 360 / count)
                writer.writerow([i + 1,
                                 round(radius * math.cos(angle), 2),
                                 round(radius * math.sin(angle), 2),
                                 mm(params, 'hole_diameter'),
                                 mm(params, 'cbore_diameter'),
                                 mm(params, 'cbore_depth')])
 
        props = design.rootComponent.physicalProperties #gets the physical properties of the design, including mass
        with open(os.path.join(out, 'summary.csv'), 'w', newline='') as f: #opens a new csv file in the output folder to write the summary data
            writer = csv.writer(f)
            writer.writerow(['property', 'value'])
            writer.writerow(['rib_count', count])
            writer.writerow(['rib_thickness_mm', thick])
            writer.writerow(['base_diameter_mm', mm(params, 'base_diameter')])
            writer.writerow(['rib_height_mm', mm(params, 'rib_height')])
            writer.writerow(['mass_g', round(props.mass * 1000, 1)])

        ui.messageBox(f'Production pack saved to\n{out}') #shows a message box to the user indicating that the production pack has been saved successfully
    except:
        ui.messageBox(f'Failed:\n{traceback.format_exc()}')