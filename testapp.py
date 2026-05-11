import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "weather_code",
        "rain_sum",
        "showers_sum",
        "sunrise",
        "sunset",
        "daylight_duration",
        "sunshine_duration",
        "uv_index_max",
        "wind_speed_10m_max",
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "precipitation",
        "rain",
        "showers",
        "wind_speed_10m",
        "weather_code",
        "cloud_cover",
        "evapotranspiration",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
    ],
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "is_day",
        "weather_code",
        "cloud_cover",
        "precipitation",
        "rain",
        "showers",
        "wind_speed_10m",
    ],
    "timezone": "Asia/Tokyo",
    "past_days": 7,
    "wind_speed_unit": "ms",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_is_day = current.Variables(2).Value()
current_weather_code = current.Variables(3).Value()
current_cloud_cover = current.Variables(4).Value()
current_precipitation = current.Variables(5).Value()
current_rain = current.Variables(6).Value()
current_showers = current.Variables(7).Value()
current_wind_speed_10m = current.Variables(8).Value()

print(f"\nCurrent time: {current.Time()}")
print(f"Current temperature_2m: {current_temperature_2m}")
print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
print(f"Current is_day: {current_is_day}")
print(f"Current weather_code: {current_weather_code}")
print(f"Current cloud_cover: {current_cloud_cover}")
print(f"Current precipitation: {current_precipitation}")
print(f"Current rain: {current_rain}")
print(f"Current showers: {current_showers}")
print(f"Current wind_speed_10m: {current_wind_speed_10m}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
hourly_rain = hourly.Variables(4).ValuesAsNumpy()
hourly_showers = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(7).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(8).ValuesAsNumpy()
hourly_evapotranspiration = hourly.Variables(9).ValuesAsNumpy()
hourly_soil_temperature_0cm = hourly.Variables(10).ValuesAsNumpy()
hourly_soil_temperature_6cm = hourly.Variables(11).ValuesAsNumpy()
hourly_soil_moisture_0_to_1cm = hourly.Variables(12).ValuesAsNumpy()
hourly_soil_moisture_1_to_3cm = hourly.Variables(13).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    ).tz_convert("Asia/Tokyo")
}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["precipitation"] = hourly_precipitation
hourly_data["rain"] = hourly_rain
hourly_data["showers"] = hourly_showers
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["weather_code"] = hourly_weather_code
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["evapotranspiration"] = hourly_evapotranspiration
hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm

hourly_dataframe = pd.DataFrame(data=hourly_data)
print("\nHourly data\n", hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_weather_code = daily.Variables(2).ValuesAsNumpy()
daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
daily_sunrise = daily.Variables(5).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(6).ValuesInt64AsNumpy()
daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
daily_uv_index_max = daily.Variables(9).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(10).ValuesAsNumpy()

daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    ).tz_convert("Asia/Tokyo")
}

daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["weather_code"] = daily_weather_code
daily_data["rain_sum"] = daily_rain_sum
daily_data["showers_sum"] = daily_showers_sum
daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset
daily_data["daylight_duration"] = daily_daylight_duration
daily_data["sunshine_duration"] = daily_sunshine_duration
daily_data["uv_index_max"] = daily_uv_index_max
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max

daily_dataframe = pd.DataFrame(data=daily_data)
print("\nDaily data\n", daily_dataframe)
with open("record.txt", "w") as f:
    f.write(daily_dataframe.to_string())
    f.write("\n\n")
    f.write(hourly_dataframe.to_string())
