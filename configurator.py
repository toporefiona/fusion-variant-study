"""Configurator: pick the lightest buildable design that meets a stiffness requirement."""
import pandas as pd

RESULTS_FILE = 'variant_results_with_stiffness.csv'
STIFFNESS_COL = 'stiffness_kN_per_mm'
CLEARANCE_COL = 'hole_clearance_mm'


def configure(min_stiffness, min_clearance): #this function does the deciding of which design is the best based on the stiffness requirement
    df = pd.read_csv(RESULTS_FILE) #loads the results file into a pandas dataframe 
    buildable = df[df[CLEARANCE_COL] >= min_clearance] #filters for buildable designs
    meets = buildable[buildable[STIFFNESS_COL] >= min_stiffness] #filters for designs that meet the stiffness requirement
    report = {
        'total': len(df), #total number of designs in the results file  
        'not_buildable': len(df) - len(buildable), #number of designs that are not buildable
        'too_flexible': len(buildable) - len(meets), #number of buildable designs that do not meet the stiffness requirement
        'max_possible': buildable[STIFFNESS_COL].max(), #maximum stiffness of the buildable designs
    }
    if meets.empty:  #checks wether no designs meet the stiffness requirement
        return None, report
    best = meets.sort_values('mass_g').iloc[0] #sorts the designs that meet the stiffness requirement by mass and selects the lightest one, iloc[0] selects the first row of the sorted dataframe
    return best, report


def main(): #this function runs the configurator and talks to the user
    min_stiffness = float(input('Required stiffness (kN/mm): ')) #prompts the user for the required stiffness
    text = input('Minimum bolt hole clearance (mm), press Enter for 2: ')
    min_clearance = float(text) if text else 2.0
    best, report = configure(min_stiffness, min_clearance)

    print(f"\nChecked {report['total']} designs")
    print(f"  {report['not_buildable']} rejected: bolt hole clearance below {min_clearance} mm")
    print(f"  {report['too_flexible']} rejected: below {min_stiffness:.0f} kN/mm")

    if best is None:
        print(f"\nNo buildable design is stiff enough. "
              f"The stiffest buildable design gives {report['max_possible']:.0f} kN/mm.")
        return

    print('\nRecommended design')
    print(f"  Ribs: {int(best['rib_count'])}")
    print(f"  Rib thickness: {best['rib_thickness_mm']:.0f} mm")
    print(f"  Clearance: {best[CLEARANCE_COL]:.1f} mm")
    print(f"  Mass: {best['mass_g']:.1f} g")
    print(f"  Stiffness: {best[STIFFNESS_COL]:.0f} kN/mm")


if __name__ == '__main__': #checks if the script is being run directly
    main() #calls the main function if the script is run directly