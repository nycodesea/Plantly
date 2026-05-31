import pandas as pd
import numpy as np


# Information Card
def build_info_card(past_7days_df, today_hourly_df, now):
    rain_5days = past_7days_df["precipitation_sum"].tail(5).sum()
    df_12h = today_hourly_df[
        (today_hourly_df["date"] >= now)
        & (today_hourly_df["date"] <= now + pd.Timedelta(hours=12))
    ]
    if df_12h.empty:
        temp_max_12h = np.nan
    else:
        temp_max_12h = df_12h["temperature_2m"].max()

    if df_12h.empty:
        temp_min_12h = np.nan
    else:
        temp_min_12h = df_12h["temperature_2m"].min()

    current_row = today_hourly_df[
        (today_hourly_df["date"] <= now)
        & (today_hourly_df["date"] > now - pd.Timedelta(minutes=30))
    ].tail(1)

    is_raining_now = not current_row.empty and current_row["precipitation"].iloc[0] > 0
    rain_future = today_hourly_df[
        (today_hourly_df["date"] > now) & (today_hourly_df["precipitation"] > 0)
    ]

    if is_raining_now:
        rain_start_time = "now"
    elif not rain_future.empty:
        rain_start_time = rain_future["date"].iloc[0]
    else:
        rain_start_time = "not rain"

    def format_time(x):
        if x in ["now", "not rain"]:
            return x
        dt = pd.to_datetime(x)
        return f"{dt.month}/{dt.day} {dt.hour}:{dt.minute:02d}"

    rain_start_time = format_time(rain_start_time)
    return rain_5days, temp_max_12h, temp_min_12h, rain_start_time


# insight Card
def build_insight_card(
    rain_start_time, rain_5days, temp_max_12h, daily_dataframe, today
):
    # insight Water
    insight_water_title = "💧 Watering : "
    insight_water_text = (
        f"The total precipitation over the last 5 days is {rain_5days:.0f}mm."
        f"Over the next 12 hours, the temperature is expected to reach up to {temp_max_12h:.0f}℃."
    )

    if rain_start_time == "not rain" and rain_5days < 10:
        insight_water_title = "💧 Watering Recommended : "
        insight_water_text = (
            "No rain forecast for a while, and the soil is prone to drying out."
        )

    elif rain_start_time != "not rain":
        insight_water_title = "🌧️ No Need to Water : "
        insight_water_text = "Rain is forecast, so watering can be skipped for now."

    else:
        insight_water_title = "🌱 Good Conditions : "
        insight_water_text = "No extreme drought or rainfall expected."
    # insight Solar-ray
    today_uv = daily_dataframe.loc[
        daily_dataframe["date"].dt.normalize() == today,
        "uv_index_max",
    ].iloc[0]

    insight_solar_title = ""
    insight_solar_text = f""

    if today_uv >= 8:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "Danger⚡"
    elif today_uv > 5:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "Careful⚠️"
    else:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "👌"

    # insight some peaky scores

    return (
        insight_water_title,
        insight_water_text,
        insight_solar_title,
        insight_solar_text,
    )
