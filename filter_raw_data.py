import numpy as np
import pandas as pd
import tqdm
from ghcn import load_daily
from glob import glob

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

    # Extract only specific metrics - create a filter for doing so
    metric_names = ["TMIN", "TMAX", "PRCP", "SNOW"]

    filter_ = np.zeros(df.shape[0]).astype(bool)
    for metric in metric_names:
        filter_ = np.logical_or(filter_, df["element"] == metric)
        
    temperatures = df[filter_]

    # Delete unnecessary columns
    temperatures = temperatures.drop(columns=["measurement", "quality", "source"])

    data_all.append(temperatures)

    del filename, station_name, latitude, df, filter_, temperatures
print("Reading files... DONE")

# Combine all the dataframes
data_all = pd.concat(data_all)

# Delete missing data
data_all = data_all[data_all["value"] != -9999]
print("Dataframe shape:", data_all.shape)

# Save data to CSV
data_all.to_csv("filtered_data.csv", index=False)