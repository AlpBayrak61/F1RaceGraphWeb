F1 Race Data Viewer

The F1 Race Data Viewer is an interactive web application designed for Formula 1 fans, analysts, and data enthusiasts. It allows users to explore race data for multiple seasons, tracks, and drivers, including lap times and telemetry data.
Features:

    Season, Track, and Driver Selection: Users can select a specific F1 season, track, and driver to view detailed race data.
    Lap Time Visualization: Displays the lap times of a selected driver over a race session, using an interactive Plotly chart.
    Telemetry Data: Visualizes telemetry data including speed, throttle, and brake pressure for the selected driver. Each telemetry type is presented in its own interactive graph.
    Track Map: Optionally, visualize the track layout with color-coded segments based on driver performance.

Technologies Used:

    Flask: Backend framework for handling form submissions and serving data.
    FastF1: Python package for accessing Formula 1 race data and telemetry.
    Plotly: Interactive charting library used for rendering lap time and telemetry graphs.
    Leaflet.js: JavaScript library for rendering track maps and visualizing driver performance on the track.

Setup Instructions:

    Clone this repository:

git clone https://github.com/yourusername/f1-race-data-viewer.git

Install dependencies:

pip install flask fastf1 plotly

Run the Flask application:

    python app.py

    Open your browser and navigate to http://127.0.0.1:5000/ to view the app.

How to Use:

    Select a season, track, and driver from the dropdown menus.
    Click "Show Lap Times" to visualize lap times and telemetry data for the selected inputs.
    The telemetry graphs show speed, throttle, and brake pressure over time, with each graph rendered interactively.

