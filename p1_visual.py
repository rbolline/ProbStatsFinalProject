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



