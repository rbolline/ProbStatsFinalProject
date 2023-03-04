import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ghcn import load_daily
from glob import glob

# Data files
files = sorted(glob('ghcnd_tiny/*.dly'))

# Load data from each file
dataframes = map(lambda file: pd.DataFrame.from_records(load_daily(file)), files)
dataframes = list(dataframes)

# Combine all the dataframes
df = pd.concat(dataframes)
del dataframes

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