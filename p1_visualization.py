import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ghcn import load_daily
from glob import glob
import tqdm
import time
import collections

# Data files
files = sorted(glob('ghcnd_small/*.dly'))

# Load data about stations (we only the station ID and latitude)
# that are in the northern hemisphere (a.k.a. latitude > 0)
north_stations = pd.read_fwf("ghcnd-stations.txt", header=None, usecols=[0, 1])
north_stations.columns = ["station_id", "latitude"]
north_stations = north_stations[north_stations["latitude"] > 0]
north_stations.set_index("station_id", inplace=True)




# We only care about stations in the northern hemisphere (latitude > 0)
# So go through the list of files, and only load files corresponding to
# stations in the northern hemisphere.
data_all = []
for filename in tqdm.tqdm(files):
    # Get the station name from the filename
    station_name = filename.split(sep='/')[-1][:-4]
    # Get the latitude of the station if it's in the dictionary (if not, it's -1)
    try:
        latitude = north_stations['latitude'][station_name]
    except:
        latitude = -1
    # Only load this file if the station is in the northern hemisphere (a.k.a. having latitude > 0)
    if latitude < 0:
        continue
    
    # All the data for one station
    df = pd.DataFrame.from_records(load_daily(filename))

    # Extract the temperature data
    filter_ = np.logical_or(np.logical_or(np.logical_or(
                                        df["element"] == "TMIN",
                                        df["element"] == "TMAX"), 
                                        df["element"] == "PRCP"), 
                                        df["element"] == "SNOW")
    
    temperatures = df[filter_]

    # Delete unnecessary columns
    temperatures = temperatures.drop(columns=["measurement", "quality", "source"])

    data_all.append(temperatures)

    del filename, station_name, latitude, df, filter_, temperatures
print("Reading files... DONE")

# Combine all the dataframes
data_all = pd.concat(data_all)
print("Dataframe shape:", data_all.shape)

# Delete missing data
data_all = data_all[data_all["value"] != -9999]
print(data_all.groupby(by=["station_id"]).mean())

# For each station and for each day, compute the midpoint temperature by
# averaging the min and max temperatures
print("Computing midpoint temperature...")
mid_temps = data_all.where(np.logical_or(data_all["element"] == "TMIN",
                            data_all["element"] == "TMAX")).groupby(by=["station_id", "year", "month", "day"]).mean().reset_index()
print(mid_temps)
# For each station and for each year, compute the average temperature across that year
avg_yearly_temps_per_station = mid_temps.groupby(by=["station_id", "year"]).mean()["value"].reset_index()

# For each year, compute the average temperature across stations
avg_yearly_temps = mid_temps.groupby(by=["year"]).mean()["value"].reset_index()

# All temperatures are in tenths of degree Celsius, so divide by 10 to get
# actual temperatures
avg_yearly_temps["value"] /= 10

print("Computing yearly precipitation...")
# Extract the precipitation data
prcp = data_all.where(data_all['element'] == 'PRCP').dropna()
# Delete missing data, and unnecessary columns
prcp = prcp[prcp["value"] != -9999]

# For each station and for each year, compute the average temperature across that year
avg_yearly_prcp_per_station = prcp.groupby(by=["station_id", "year"]).mean()["value"].reset_index()

# For each year, compute the average temperature across stations
avg_yearly_prcp = avg_yearly_prcp_per_station.groupby(by=["year"]).mean()["value"].reset_index()

print("Computing yearly snowfall...")
snow = data_all.where(data_all['element'] == 'SNOW').dropna()
# Delete missing data, and unnecessary columns
snow = snow[snow["value"] != -9999]

# For each station and for each year, compute the average temperature across that year
avg_yearly_snow_per_station = snow.groupby(by=["station_id", "year"]).mean()["value"].reset_index()

# For each year, compute the average temperature across stations
avg_yearly_snow = avg_yearly_snow_per_station.groupby(by=["year"]).mean()["value"].reset_index()


# Plot the result
plt.plot(avg_yearly_temps["year"], avg_yearly_temps["value"])
plt.show()
plt.savefig("avg_yearly_temps.png")


plt.plot(avg_yearly_prcp["year"], avg_yearly_prcp["value"])
plt.show()
plt.savefig("avg_yearly_prcp.png")


plt.plot(avg_yearly_snow["year"], avg_yearly_snow["value"])
plt.show()
plt.savefig("avg_yearly_snow.png")



