import fastf1
from flask import Flask, render_template, request, jsonify
import os
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json

# Initialize Flask app
app = Flask(__name__)

# Define cache directory
cache_path = os.path.join(os.getcwd(), 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
fastf1.Cache.enable_cache(cache_path)

@app.route('/')
def index():
    # Example: available seasons and tracks
    seasons = list(range(2020, 2025))
    tracks = [
        'Bahrain Grand Prix', 'Emilia Romagna Grand Prix', 'Spanish Grand Prix', 'Monaco Grand Prix',
        'Azerbaijan Grand Prix', 'French Grand Prix', 'British Grand Prix', 'Hungarian Grand Prix',
        'Belgian Grand Prix', 'Dutch Grand Prix', 'Italian Grand Prix', 'United States Grand Prix',
        'Brazilian Grand Prix', 'Saudi Arabian Grand Prix', 'Abu Dhabi Grand Prix'
    ]
    drivers = ['VER', 'LEC', 'HAM', 'PER', 'RIC', 'NOR', 'SAI', 'RUS', 'ALO']
    return render_template('index.html', seasons=seasons, tracks=tracks, drivers=drivers)

@app.route('/get_lap_times', methods=['POST'])
def get_lap_times():
    season = int(request.form['season'])
    track = request.form['track']
    driver = request.form['driver']

    event = fastf1.get_event(season, track)
    session = event.get_session('R')  # 'R' for Race session
    session.load()

    laps = session.laps.pick_driver(driver)

    lap_numbers = laps['LapNumber'].tolist()
    lap_times = laps['LapTime'].dt.total_seconds().tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lap_numbers,
        y=lap_times,
        mode='lines+markers',
        name=f"{driver}'s Lap Times",
        hovertemplate='Lap: %{x}<br>Time: %{y} seconds<extra></extra>'
    ))

    fig.update_layout(
        title=f"Lap Time Chart for {driver} - {track} {season}",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        template="plotly_dark"
    )

    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)

    return jsonify({'graph_json': graph_json})


if __name__ == '__main__':
    app.run(debug=True)
