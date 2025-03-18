# imports
import matplotlib
matplotlib.use('Agg')
import os
import numpy as np
import pandas as pd
import fastf1 as ff1
from fastf1 import api
from fastf1 import utils
from fastf1 import plotting
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

# enables cache, allows storage of race data locally
ff1.Cache.enable_cache('formula/cache')

# patches matplotlib for time delta support
ff1.plotting.setup_mpl(mpl_timedelta_support = True, color_scheme = 'fastf1')

def plot_function(race, input_data):
    # Clear any existing plots
    plt.close('all')
    
    # Create a new figure explicitly
    fig, ax = plt.subplots()  # or whatever subplot configuration you need
    
    # Your plotting code...
    
    # Save and close
    plt.savefig(img_path, dpi=200)
    plt.close(fig)
    
# gets race data from fastf1 based on input data parameter
# runs appropriate plot function based on user input
def get_race_data(input_data):
    #['2022', 'Austria', 'FP1', 'VER', 'VER', 'Lap Time']
    race = ff1.get_session(int(input_data[0]), input_data[1], input_data[2])
    race.load()

    if input_data[5] == 'Lap Time':
        plot_laptime(race, input_data)
    elif input_data[5] == 'Fastest Lap':
        plot_fastest_lap(race, input_data)
    elif input_data[5] == 'Fastest Sectors':
        plot_fastest_sectors(race, input_data)
    elif input_data[5] == 'Full Telemetry':
        plot_full_telemetry(race, input_data)

# takes in speed/distance data for both drivers and determines which is faster
# returns dataframe of which driver was the fastest in each sector
def get_sectors(average_speed, input_data):
    sectors_combined = average_speed.groupby(['Driver', 'Minisector'])['Speed'].mean().reset_index()
    final = pd.DataFrame({
        'Driver': [],
        'Minisector': [],
        'Speed': []
    })

    d1 = sectors_combined.loc[sectors_combined['Driver'] == input_data[3].split()[0]]
    d2 = sectors_combined.loc[sectors_combined['Driver'] == input_data[4].split()[0]]

    for i in range(0, len(d1)): #issue, sometimes length of d1 is not 25
        d1_sector = d1.iloc[[i]].values.tolist()
        d1_speed = d1_sector[0][2]
        d2_sector = d2.iloc[[i]].values.tolist()
        d2_speed = d2_sector[0][2]
        if d1_speed > d2_speed:
            final.loc[len(final)] = d1_sector[0]
        else:
            final.loc[len(final)] = d2_sector[0]

    return final

# plots a laptime/distance comparison for both specified drivers
# returns a saved version of the generated plot
def plot_laptime(race, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    laps_d1 = race.laps.pick_driver(d1)
    laps_d2 = race.laps.pick_driver(d2)

    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])

    fig, ax = plt.subplots()
    ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'], color = color1, label = input_data[3])
    ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'], color = color2, label = input_data[4])
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    ax.legend()
    plt.suptitle(f"Lap Time Comparison \n" f"{race.event.year} {race.event['EventName']} {input_data[2]}")

    img_path = os.getcwd() + (f'/formula/plot/{input_data[5]}.png')
    plt.savefig(img_path, dpi = 200)

# speed comaprison by distance for the fastest lap of both drivers
# returns a saved version of the generated plot
def plot_fastest_lap(race, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    fastest_d1 = race.laps.pick_driver(d1).pick_fastest()
    fastest_d2 = race.laps.pick_driver(d2).pick_fastest()

    tel_d1 = fastest_d1.get_car_data().add_distance()
    tel_d2 = fastest_d2.get_car_data().add_distance()

    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])

    fig, ax = plt.subplots()
    ax.plot(tel_d1['Distance'], tel_d1['Speed'], color = color1, label = input_data[3])
    ax.plot(tel_d2['Distance'], tel_d2['Speed'], color = color2, label = input_data[4])
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.legend()
    plt.suptitle(f"Fastest Lap Comparison \n" f"{race.event.year} {race.event['EventName']} {input_data[2]}")

    img_path = os.getcwd() + (f'/formula/plot/{input_data[5]}.png')
    plt.savefig(img_path, dpi = 700)


# compares the sector speeds for each driver, and generates a map of the circuit, with color coded sectors for the fastest driver.
# returns a saved version of the generated plot
def plot_fastest_sectors(race, input_data):
    plt.clf()
    laps = race.laps
    drivers = [input_data[3].split()[0], input_data[4].split()[0]]
    telemetry_list = []
    
    # Make sure we have a valid lap number (modify this part)
    try:
        # Try to get the lap number from input_data[6]
        lap_number = int(input_data[6])
    except (IndexError, ValueError):
        # If there's an issue, use the first lap as default
        lap_number = 1
        
    # List of each driver's telemetry data across laps
    for driver in drivers:
        driver_laps = laps.pick_driver(driver)
        for lap in driver_laps.iterlaps():
            driver_telemtry = lap[1].get_telemetry().add_distance()
            driver_telemtry['Driver'] = driver
            driver_telemtry['Lap'] = lap[1]['LapNumber']
            telemetry_list.append(driver_telemtry)
    
    # Concatenate all telemetry dataframes
    telemetry = pd.concat(telemetry_list, ignore_index=True)
    
    # Keep only important columns
    telemetry = telemetry[['Lap', 'Distance', 'Driver', 'Speed', 'X', 'Y']]
    
    # Create minisectors
    total_minisectors = 25
    telemetry['Minisector'] = pd.cut(telemetry['Distance'], total_minisectors, labels=False) + 1
    
    average_speed = telemetry.groupby(['Lap', 'Minisector', 'Driver'])['Speed'].mean().reset_index()
    
    # Get fastest driver in each sector
    best_sectors = get_sectors(average_speed, input_data)
    best_sectors = best_sectors[['Driver', 'Minisector']].rename(columns={'Driver': 'fastest_driver'})
    
    # Merge telemetry with fastest sector info and sort by distance
    telemetry = telemetry.merge(best_sectors, on=['Minisector'])
    telemetry = telemetry.sort_values(by=['Distance'])
    
    telemetry.loc[telemetry['fastest_driver'] == input_data[3].split()[0], 'fastest_driver_int'] = 1
    telemetry.loc[telemetry['fastest_driver'] == input_data[4].split()[0], 'fastest_driver_int'] = 2
    
    # Extract X, Y data for a single lap
    single_lap = telemetry.loc[telemetry['Lap'] == lap_number]
    lap_x = single_lap['X'].values
    lap_y = single_lap['Y'].values

    points = np.array([lap_x, lap_y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    which_driver = single_lap['fastest_driver_int'].to_numpy().astype(float)

    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])
    color1 = matplotlib.colors.to_rgb(color1)
    color2 = matplotlib.colors.to_rgb(color2)
    colors = [color1, color2]
    cmap = matplotlib.colors.ListedColormap(colors)

    lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N), cmap=cmap)
    lc_comp.set_array(which_driver)
    lc_comp.set_linewidth(2)

    plt.rcParams['figure.figsize'] = [6.25, 4.70]
    plt.suptitle(f"Average Fastest Sectors Lap {input_data[6]}\n"
                 f"{race.event.year} {race.event['EventName']} {input_data[2]}")
    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    legend_lines = [Line2D([0], [0], color=color1, lw=1),
                    Line2D([0], [0], color=color2, lw=1)]
    plt.legend(legend_lines, [input_data[3], input_data[4]])

    img_path = os.getcwd() + (f'/formula/plot/{input_data[5]}.png')
    plt.savefig(img_path, dpi=200)

# plots a speed, throttle, brake, rpm, gear, and drs comparison for both drivers
# returns a saved version of the generated plot
def plot_laptime(race, input_data):
    try:
        plt.clf()
        d1 = input_data[3].split()[0]
        d2 = input_data[4].split()[0]

        laps_d1 = race.laps.pick_driver(d1)
        laps_d2 = race.laps.pick_driver(d2)

        # Check if we have valid laps data
        if laps_d1.empty or laps_d2.empty:
            plt.figure()
            plt.text(0.5, 0.5, f"No lap data available for {d1} or {d2}", 
                     horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
        else:
            color1 = ff1.plotting.driver_color(input_data[3])
            color2 = ff1.plotting.driver_color(input_data[4])

            fig, ax = plt.subplots()
            ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'], color=color1, label=input_data[3])
            ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'], color=color2, label=input_data[4])
            ax.set_xlabel('Lap Number')
            ax.set_ylabel('Lap Time')
            ax.legend()
            plt.suptitle(f"Lap Time Comparison \n" f"{race.event.year} {race.event['EventName']} {input_data[2]}")

        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(os.getcwd() + '/formula/plot/'), exist_ok=True)
        
        img_path = os.getcwd() + (f'/formula/plot/{input_data[5]}.png')
        plt.savefig(img_path, dpi=200)
        
        return True
    except Exception as e:
        print(f"Error in plot_laptime: {str(e)}")
        plt.figure()
        plt.text(0.5, 0.5, f"Error generating plot: {str(e)}", 
                 horizontalalignment='center', verticalalignment='center')
        plt.axis('off')
        
        img_path = os.getcwd() + (f'/formula/plot/{input_data[5]}.png')
        plt.savefig(img_path, dpi=200)
        
        return False
def plot_full_telemetry(race, input_data):
    """
    Plots comprehensive telemetry data comparing two drivers' fastest laps.
    Displays speed, throttle, brake, RPM, gear, and delta time.
    
    Parameters:
    race (FastF1 Session): The loaded race session
    input_data (list): List containing input parameters [year, location, session, driver1, driver2, analysis_type, lap]
    
    Returns:
    None: Saves the plot to the specified location
    """
    import os
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from fastf1 import utils
    import fastf1 as ff1
    
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    try:
        # Get fastest laps for both drivers
        fastest_d1 = race.laps.pick_driver(d1).pick_fastest()
        fastest_d2 = race.laps.pick_driver(d2).pick_fastest()
        
        # Get telemetry data with distance
        tel_d1 = fastest_d1.get_car_data().add_distance()
        tel_d2 = fastest_d2.get_car_data().add_distance()
        
        # Ensure brake data is properly formatted (convert to binary integers)
        tel_d1['Brake'] = tel_d1['Brake'].astype(int)
        tel_d2['Brake'] = tel_d2['Brake'].astype(int)
        
        # Calculate delta time between the two drivers
        delta_time, ref_tel, compare_tel = utils.delta_time(fastest_d1, fastest_d2)
        
        # Combine telemetry data for plotting
        telem_data_combined = [tel_d1, tel_d2]
        
        # Get driver colors
        colors = [ff1.plotting.driver_color(input_data[3]), ff1.plotting.driver_color(input_data[4])]
        
        # Create figure with 6 subplots
        fig, ax = plt.subplots(6, 1, figsize=(12, 10), sharex=True)
        plt.subplots_adjust(hspace=0.3)
        
        # Plot data for both drivers
        for telem, color in zip(telem_data_combined, colors):
            # Delta time plot
            ax[0].axhline(0, color='White', linewidth=0.5)
            ax[0].plot(ref_tel['Distance'], delta_time, color=color, linewidth=1.5)
            
            # Speed plot 
            ax[1].plot(telem['Distance'], telem['Speed'], color=color, linewidth=1)
            
            # Throttle plot
            ax[2].plot(telem['Distance'], telem['Throttle'], color=color, linewidth=1)
            
            # Brake plot
            ax[3].plot(telem['Distance'], telem['Brake'] * 100, color=color, linewidth=1)  # *100 to make it visible
            
            # RPM plot
            ax[4].plot(telem['Distance'], telem['RPM'], color=color, linewidth=1)
            
            # Gear plot
            ax[5].plot(telem['Distance'], telem['nGear'], color=color, linewidth=1)
        
        # Add labels to each subplot
        ax[0].set_ylabel('Delta (s)')
        ax[1].set_ylabel('Speed (km/h)')
        ax[2].set_ylabel('Throttle (%)')
        ax[3].set_ylabel('Brake')
        ax[4].set_ylabel('RPM')
        ax[5].set_ylabel('Gear')
        ax[5].set_xlabel('Distance (m)')
        
        # Set y-axis limits for percentage plots
        ax[2].set_ylim(0, 100)
        ax[3].set_ylim(0, 100)
        
        # Set title
        plt.suptitle(f"Fastest Lap Telemetry - {input_data[3]} vs {input_data[4]}\n{race.event.year} {race.event['EventName']} {input_data[2]}", fontsize=16)
        
        # Add legend
        legend_lines = [Line2D([0], [0], color=colors[0], lw=2),
                        Line2D([0], [0], color=colors[1], lw=2)]
        
        ax[0].legend(legend_lines, [input_data[3], input_data[4]], loc='upper right')
        
        # Create directory if it doesn't exist
        plot_dir = os.path.join(os.getcwd(), 'formula', 'plot')
        os.makedirs(plot_dir, exist_ok=True)
        
        # Save the figure
        img_path = os.path.join(plot_dir, f"{input_data[5]}.png")
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout with room for title
        plt.savefig(img_path, dpi=200)
        plt.close()
        
    except Exception as e:
        print(f"Error in plot_full_telemetry: {str(e)}")
        
        # Create a simple error plot
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error generating telemetry plot:\n{str(e)}",
                 horizontalalignment='center', verticalalignment='center', fontsize=12)
        plt.axis('off')
        
        # Save the error figure
        plot_dir = os.path.join(os.getcwd(), 'formula', 'plot')
        os.makedirs(plot_dir, exist_ok=True)
        img_path = os.path.join(plot_dir, f"{input_data[5]}.png")
        plt.savefig(img_path, dpi=200)
        plt.close()