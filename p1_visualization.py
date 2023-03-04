import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ghcn import load_daily
from glob import glob
import tqdm
import time
import collections

# Data files
start = time.time()
files = sorted(glob('ghcnd_tiny/*.dly'))

# Load data about stations (we only the station ID and latitude)
# that are in the northern hemisphere (a.k.a. latitude > 0)
north_stations = pd.read_fwf("ghcnd-stations.txt", header=None, usecols=[0, 1])
north_stations.columns = ["station_id", "latitude"]
north_stations = north_stations[north_stations["latitude"] > 0]
north_stations.set_index("station_id", inplace=True)

# Convert the dataframe to a dictionary for faster lookup
north_stations = north_stations["latitude"].to_dict()

# We only care about stations in the northern hemisphere (latitude > 0)
# So go through the list of files, and only load files corresponding to
# stations in the northern hemisphere.
dataframes = []
for filename in tqdm.tqdm(files):
    # Get the station name from the filename
    station_name = filename.split(sep='/')[1][:-4]
    
    # Get the latitude of the station if it's in the dictionary (if not, it's -1)
    latitude = north_stations.get(station_name, -1)
    
    # Only load this file if the station is in the northern hemisphere
    if latitude > 0:
        station_data = pd.DataFrame.from_records(load_daily(filename))
        dataframes.append(station_data)

# Combine all the dataframes
df = pd.concat(dataframes)
del dataframes
print("Loaded the data in", time.time() - start, "seconds")

# Extract the temperature data
filter_ = np.logical_or(df["element"] == "TMIN",
                        df["element"] == "TMAX")
temperatures = df[filter_]

# Delete missing data, and unnecessary columns
temperatures = temperatures[temperatures["value"] != -9999]
temperatures.drop(columns=["measurement", "quality", "source"], inplace=True)
print(temperatures.groupby(by=["station_id"]).mean())

# For each station and for each day, compute the midpoint temperature by
# averaging the min and max temperatures
mid_temps = temperatures.groupby(by=["station_id", "year", "month", "day"]).mean().reset_index()

# For each station and for each year, compute the average temperature across that year
avg_yearly_temps_per_station = mid_temps.groupby(by=["station_id", "year"]).mean()["value"].reset_index()

# For each year, compute the average temperature across stations
avg_yearly_temps = mid_temps.groupby(by=["year"]).mean()["value"].reset_index()

# All temperatures are in tenths of degree Celsius, so divide by 10 to get
# actual temperatures
avg_yearly_temps["value"] /= 10

# Plot the result
plt.plot(avg_yearly_temps["year"], avg_yearly_temps["value"])
plt.show()