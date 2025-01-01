import fastf1
from flask import Flask, render_template, request, jsonify
import os
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json

# Initialize Flask app
app = Flask(__name__)

# Define cache directory
cache_path = r'C:\path\to\cache'
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
fastf1.Cache.enable_cache(cache_path)

@app.route('/')
def index():
    # Example: available seasons and tracks (you could dynamically load this)
    seasons = [2024, 2023, 2022, 2021, 2020]
    tracks = ['Bahrain Grand Prix', 'Emilia Romagna Grand Prix', 'Spanish Grand Prix', 'Monaco Grand Prix',
        'Azerbaijan Grand Prix', 'French Grand Prix', 'Styrian Grand Prix', 'Austrian Grand Prix',
        'British Grand Prix', 'Hungarian Grand Prix', 'Belgian Grand Prix', 'Dutch Grand Prix',
        'Italian Grand Prix', 'Russian Grand Prix', 'Singapore Grand Prix', 'Japanese Grand Prix',
        'United States Grand Prix', 'Mexican Grand Prix', 'Brazilian Grand Prix', 'Saudi Arabian Grand Prix',
        'Abu Dhabi Grand Prix', 'Australian Grand Prix', 'Miami Grand Prix', 'Canadian Grand Prix',
        'Austrian Grand Prix', 'Portuguese Grand Prix', 'Turkish Grand Prix', 'Bahrain Grand Prix']
    drivers = ['VER', 'LEC', 'HAM', 'PER', 'RIC', 'NOR', 'SAI', 'RUS', 'ALO', 'TSU', 'DEV', 'ZHO', 'HUL',
        'MAG', 'LAT', 'MSC', 'SCH', 'GAS', 'RUS', 'SIR', 'STR', 'KVI', 'ERI']
    return render_template('index.html', seasons=seasons, tracks=tracks, drivers=drivers)

@app.route('/get_telemetry_data', methods=['POST'])
def get_telemetry_data():
    season = int(request.form['season'])
    track = request.form['track']
    driver = request.form['driver']
    
    session = fastf1.get_session(season, track, 'R')
    session.load()
    
    # Get telemetry data for the selected driver
    telemetry = session.laps.pick_drivers([driver]).get_telemetry()

    # Now we check which columns are available
    print(telemetry.columns)  # Print the available columns in the telemetry data

    # Ensure that telemetry has the necessary columns (Lap Number, Speed, Throttle, Brake)
    telemetry_data = {
        'lap_numbers': telemetry['LapNumber'].tolist() if 'LapNumber' in telemetry.columns else [],
        'speed': telemetry['Speed'].tolist() if 'Speed' in telemetry.columns else [],
        'throttle': telemetry['Throttle'].tolist() if 'Throttle' in telemetry.columns else [],
        'brake': telemetry['Brake'].tolist() if 'Brake' in telemetry.columns else [],
        'time': telemetry['Time'].dt.total_seconds().tolist() if 'Time' in telemetry.columns else []
    }

    # Send telemetry data as JSON to frontend
    return jsonify({'telemetry_data': telemetry_data})

@app.route('/get_lap_times', methods=['POST'])
def get_lap_times():
    season = int(request.form['season'])
    track = request.form['track']
    driver = request.form['driver']
    
    session = fastf1.get_session(season, track, 'R')
    session.load()
    
    laps = session.laps.pick_driver(driver)
    
    # Prepare data for the Plotly graph
    lap_numbers = laps['LapNumber'].tolist()
    lap_times = laps['LapTime'].dt.total_seconds().tolist()

    # Generate the plot (Plotly)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lap_numbers, 
        y=lap_times, 
        mode='lines+markers', 
        name=f"{driver}'s Lap Times",
        hovertemplate='Lap: %{x}<br>Time: %{y} seconds<extra></extra>'  # Hover information
    ))

    # Customize layout
    fig.update_layout(
        title=f"Lap Time Chart for {driver} - {track} {season}",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        template="plotly_dark"
    )

    # Convert the plot to JSON for rendering in the frontend
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)

    return jsonify({'graph_json': graph_json})

if __name__ == '__main__':
    app.run(debug=True)
