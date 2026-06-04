from datetime import date, timedelta
import sqlite3
from utils import get_now
import pandas as pd

DB_PATH = "weather.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS weather_history (
        date TEXT PRIMARY KEY,
        weather_code INTEGER,
        rain_sum REAL,
        showers_sum REAL,
        snowfall_sum REAL,
        precipitation_sum REAL,
        precipitation_hours REAL,
        precipitation_prob_max REAL,
        temp_max REAL,
        temp_min REAL,
        uv_max REAL,
        temp_mean REAL,
        shortwave_radiation_sum REAL,
        sunrise TEXT,
        sunset TEXT,
        daylight_duration REAL,
        sunshine_duration REAL,
        wind_speed_max REAL,
        et0_fao_evapotranspiration REAL,
        et0_fao_evapotranspiration_sum REAL
    )
    """)

    conn.commit()
    conn.close()


def save_daily_weather(
    date,
    weather_code,
    rain_sum,
    showers_sum,
    snowfall_sum,
    precipitation_sum,
    precipitation_hours,
    precipitation_prob_max,
    temp_max,
    temp_min,
    uv_max,
    temp_mean,
    shortwave_radiation_sum,
    sunrise,
    sunset,
    daylight_duration,
    sunshine_duration,
    wind_speed_max,
    et0_fao_evapotranspiration,
    et0_fao_evapotranspiration_sum,
):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT OR IGNORE INTO weather_history
            (date,weather_code, rain_sum, showers_sum, snowfall_sum, precipitation_sum,
            precipitation_hours, precipitation_prob_max, temp_max, temp_min, uv_max,
            temp_mean, shortwave_radiation_sum, sunrise, sunset, daylight_duration,
            sunshine_duration, wind_speed_max, et0_fao_evapotranspiration, et0_fao_evapotranspiration_sum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date,
            weather_code,
            rain_sum,
            showers_sum,
            snowfall_sum,
            precipitation_sum,
            precipitation_hours,
            precipitation_prob_max,
            temp_max,
            temp_min,
            uv_max,
            temp_mean,
            shortwave_radiation_sum,
            sunrise,
            sunset,
            daylight_duration,
            sunshine_duration,
            wind_speed_max,
            et0_fao_evapotranspiration,
            et0_fao_evapotranspiration_sum,
        ),
    )

    conn.commit()
    conn.close()


# def save_yesterday_weather(past_7days_df):
#     yesterday = date.today() - timedelta(days=1)
#     yesterday_df = past_7days_df[past_7days_df["date"].dt.date == yesterday.date()]
#     # Save the yesterday's weather data to the database
#     if not yesterday_df.empty:
#         row = yesterday_df.iloc[0]
#         save_daily_weather(
#             date=str(row["date"].date()),
#             temp_max=float(row["temperature_2m_max"]),
#             temp_min=float(row["temperature_2m_min"]),
#             precipitation_sum=float(row["precipitation_sum"]),
#             uv_max=float(row["uv_index_max"]),
#         )
#     else:
#         print("No weather data available for yesterday.")


# Save missing days (for 7days )
def save_missing_7days(past_7days_df):
    today = date.today()

    for i in range(1, 8):  # 1-7 days ago
        target_date = today - timedelta(days=i)

        df = past_7days_df[past_7days_df["date"].dt.date == target_date]

        if not df.empty:
            row = df.iloc[0]
            save_daily_weather(
                date=str(row["date"].date()),
                weather_code=int(row["weather_code"]),
                rain_sum=float(row["rain_sum"]),
                showers_sum=float(row["showers_sum"]),
                snowfall_sum=float(row["snowfall_sum"]),
                precipitation_sum=float(row["precipitation_sum"]),
                precipitation_hours=float(row["precipitation_hours"]),
                precipitation_prob_max=float(row["precipitation_probability_max"]),
                temp_max=float(row["temperature_2m_max"]),
                temp_min=float(row["temperature_2m_min"]),
                uv_max=float(row["uv_index_max"]),
                temp_mean=float(row["temperature_2m_mean"]),
                shortwave_radiation_sum=float(row["shortwave_radiation_sum"]),
                sunrise=str(row["sunrise"]),
                sunset=str(row["sunset"]),
                daylight_duration=float(row["daylight_duration"]),
                sunshine_duration=float(row["sunshine_duration"]),
                wind_speed_max=float(row["wind_speed_10m_max"]),
                et0_fao_evapotranspiration=float(row["et0_fao_evapotranspiration"]),
                et0_fao_evapotranspiration_sum=float(
                    row["et0_fao_evapotranspiration_sum"]
                ),
            )


def show_data():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM weather_history  ORDER BY date
        """)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # max width for each column
        col_widths = [
            max(len(str(row[i])) for row in rows + [columns])
            for i in range(len(columns))
        ]

        # header
        header = " | ".join(
            f"{col:<{width}}" for col, width in zip(columns, col_widths)
        )
        print(header)
        print("-" * len(header))

        # data rows
        for row in rows:
            print(
                " | ".join(
                    f"{str(item):<{width}}" for item, width in zip(row, col_widths)
                )
            )


if __name__ == "__main__":
    show_data()
