import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
import sys

# Add the directory containing the script.py to Python's path
sys.path.append(os.getcwd())

# Import the get_race_data function directly
# Option 1: If you renamed paste.txt to script.py
try:
    from script import get_race_data
except ImportError:
    # Option 2: If your file is still paste.txt, create a function to call it
    def get_race_data(input_data):
        # Import the script contents at runtime
        with open('paste.txt', 'r') as f:
            script_code = f.read()
        
        # Add the function to the globals
        script_globals = globals().copy()
        exec(script_code, script_globals)
        
        # Call the get_race_data function from the script
        return script_globals['get_race_data'](input_data)

app = Flask(__name__)
app.secret_key = "formula1_telemetry_app"  # For flash messages

# Set up paths
CWD = os.getcwd()
DATA_PATH = os.path.join(CWD, 'formula', 'data')
PLOT_PATH = os.path.join(CWD, 'formula', 'plot')

# Create directories if they don't exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(PLOT_PATH, exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'plot'), exist_ok=True)

# Load CSV data
try:
    events = pd.read_csv(os.path.join(DATA_PATH, 'events.csv'))
    drivers = pd.read_csv(os.path.join(DATA_PATH, 'drivers.csv'))
    race_laps = pd.read_csv(os.path.join(DATA_PATH, 'laps.csv'))
except FileNotFoundError as e:
    print(f"Error loading CSV files: {e}")
    # Create empty DataFrames if files don't exist
    events = pd.DataFrame()
    drivers = pd.DataFrame()
    race_laps = pd.DataFrame()

# Prepare static options
years = ['Select Year']
if not events.empty:
    years += list(events.columns[1:])

sessions = ['Race', 'Qualifying', 'FP1', 'FP2', 'FP3']
analysis_options = ['Lap Time', 'Fastest Lap', 'Fastest Sectors', 'Full Telemetry']

# Prepopulate dropdowns using a default year (if available)
default_year = years[1] if len(years) > 1 else None
if default_year and not events.empty:
    grand_prix_options = events[default_year].dropna().tolist()
    driver_options = drivers[default_year].dropna().tolist()
else:
    grand_prix_options = []
    driver_options = []

@app.route("/", methods=['GET', 'POST'])
def index():
    image_file = None
    lap_options = None
    error = None
    
    if request.method == 'POST':
        # Retrieve form data
        year = request.form.get('year')
        grand_prix = request.form.get('grand_prix')
        session_type = request.form.get('session')
        driver1 = request.form.get('driver1')
        driver2 = request.form.get('driver2')
        analysis = request.form.get('analysis')
        lap_number = request.form.get('lap_number') or "1"  # Default to lap 1 if not provided
        
        # Basic validation
        if year == 'Select Year' or not grand_prix or not driver1 or not driver2:
            error = "Please fill out all required fields"
            return render_template("index.html", years=years, sessions=sessions,
                               analysis_options=analysis_options, driver_options=driver_options,
                               grand_prix_options=grand_prix_options, error=error,
                               lap_options=lap_options)
        
        # Prepare data for analysis
        input_data = [year, grand_prix, session_type, driver1, driver2, analysis, lap_number]
        
        try:
            # Call the analysis function (this will generate a plot)
            get_race_data(input_data)
            
            # Determine image filename
            image_file = f"{analysis}.png"
            
            # Copy the plot image to the static folder for serving
            src_img = os.path.join(PLOT_PATH, image_file)
            dst_img = os.path.join(app.static_folder, 'plot', image_file)
            
            if os.path.exists(src_img):
                from shutil import copyfile
                copyfile(src_img, dst_img)
            else:
                error = f"Plot generation failed. Image file not found: {src_img}"
                image_file = None
                
        except Exception as e:
            error = f"Error during analysis: {str(e)}"
            image_file = None
        
        # Update lap options based on the grand prix selection
        if grand_prix and grand_prix != "" and not race_laps.empty:
            total_laps = race_laps.loc[race_laps['event'] == grand_prix, 'laps'].values
            if total_laps.size:
                lap_options = ['Select Lap'] + list(map(str, range(1, int(total_laps[0]) + 1)))
    
    # For GET requests, pre-populate lap options if possible
    elif request.args.get('grand_prix') and not race_laps.empty:
        grand_prix = request.args.get('grand_prix')
        total_laps = race_laps.loc[race_laps['event'] == grand_prix, 'laps'].values
        if total_laps.size:
            lap_options = ['Select Lap'] + list(map(str, range(1, int(total_laps[0]) + 1)))
    
    return render_template("index.html", 
                           years=years, 
                           sessions=sessions,
                           analysis_options=analysis_options, 
                           driver_options=driver_options,
                           grand_prix_options=grand_prix_options, 
                           image_file=image_file,
                           lap_options=lap_options,
                           error=error)

@app.route('/update_options', methods=['POST'])
def update_options():
    """AJAX endpoint to update dropdowns based on selections"""
    selected_year = request.form.get('year')
    
    if selected_year and selected_year != 'Select Year' and not events.empty:
        # Get grand prix options for the selected year
        grand_prix_options = events[selected_year].dropna().tolist()
        
        # Get driver options for the selected year
        driver_options = drivers[selected_year].dropna().tolist()
        
        return {
            'grand_prix_options': grand_prix_options,
            'driver_options': driver_options
        }
    
    return {'error': 'Invalid year selection'}

if __name__ == '__main__':
    app.run(debug=True)