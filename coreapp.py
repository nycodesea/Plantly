# Plantly
import openmeteo_requests
import pandas as pd
from pandas import Timedelta
import requests_cache
from retry_requests import retry
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, no_update, ctx
import numpy as np
from plotly.subplots import make_subplots
from layout import create_layout
from graphs import (
    build_past7days_figure,
    build_future7days_figure,
    build_today_figure,
)
from config import (
    URL,
    TZ,
    WEATHER_GROUPS,
    WEATHER_ICONS,
    API_PARAMS,
    REFRESH_INTERVAL,
)
import weather
from utils import get_now
from cards import build_info_card, build_insight_card

weather_data = weather.load_weather_data()

past_7days_df = weather_data["past_7days_df"]
future_7days_df = weather_data["future_7days_df"]
daily_dataframe = weather_data["daily_dataframe"]
hourly_df = weather_data["hourly_df"]
today = weather_data["today"]


# make Graphs
fig_past = build_past7days_figure(past_7days_df)
fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df, today)
fig_today = build_today_figure(hourly_df)

# get time
time_info = get_now()
now = time_info["now"]
now_hour = time_info["hour"]
now_day = time_info["day"]

# Cards
# Information Card
rain_5days, temp_max_12h, temp_min_12h, rain_start_time = build_info_card(
    past_7days_df, hourly_df, now
)


# insight Card
insight_water_title, insight_water_text, insight_solar_title, insight_solar_text = (
    build_insight_card(
        rain_start_time, rain_5days, temp_max_12h, daily_dataframe, today
    )
)

# Dash
app = Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500&display=swap"
    ],
    title="Plantly",
)


# future graph (Top-right) hover
@app.callback(
    Output("future-tooltip", "show"),
    Output("future-tooltip", "bbox"),
    Output("future-tooltip", "children"),
    Input("future-temp-graph", "hoverData"),
    Input("future-rain-graph", "hoverData"),
)
def display_hover_card(temp_hover, rain_hover):
    trigger = ctx.triggered_id

    if trigger == "future-temp-graph":
        hoverData = temp_hover
    elif trigger == "future-rain-graph":
        hoverData = rain_hover
    else:
        hoverData = None

    if hoverData is None:
        return False, no_update, no_update

    point = hoverData["points"][0]
    bbox = point["bbox"]
    date = pd.to_datetime(point["x"]).date()

    matched = future_7days_df[future_7days_df["date"].dt.date == date]

    if matched.empty:
        return False, no_update, no_update

    row = matched.iloc[0]

    return (
        True,
        bbox,
        html.Div(
            [
                # Top
                html.Div(
                    f"{row['date'].strftime('%m/%d').replace('/0', '/').lstrip('0')}"
                    f"{row['weather_icon']}",
                    style={
                        "fontSize": "16px",
                        "paddingLeft": "4px",
                        "marginBottom": "8px",
                    },
                ),
                # Bottom
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    f"{row['temperature_2m_max']:.0f}℃",
                                    style={"color": "#d97366"},
                                ),
                                html.Div(
                                    f"{row['temperature_2m_min']:.1f}℃",
                                    style={"color": "#7aa38b"},
                                ),
                            ],
                            style={"width": "62px"},
                        ),
                        html.Div(f"☔"),
                        html.Div(
                            [
                                html.Div(f"{row['precipitation_sum']:.1f} mm"),
                                html.Div(
                                    f"{row['precipitation_probability_max']:.0f}%"
                                ),
                            ],
                            style={"color": "#6f8fb8"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        # "gap": "4px",
                        "fontSize": "12px",
                        "lineHeight": "1.4",
                    },
                ),
            ]
        ),
    )


# Current graph hover info-card
@app.callback(
    Output("today-tooltip", "show"),
    Output("today-tooltip", "bbox"),
    Output("today-tooltip", "children"),
    Input("today-graph", "hoverData"),
)
def display_today_hover(hoverData):
    time_info = get_now()
    now = time_info["now"]
    now_hour = time_info["hour"]
    now_day = time_info["day"]
    if not hoverData:
        return False, no_update, no_update

    point = hoverData["points"][0]

    bbox = point.get("bbox")

    if bbox is None:
        return False, no_update, no_update

    date = pd.to_datetime(point["x"])
    if date.tzinfo is None:
        date = date.tz_localize(TZ)
    else:
        date = date.tz_convert(TZ)
    global hourly_df
    matched = hourly_df[hourly_df["date"].dt.floor("h") == date.floor("h")]

    if matched.empty:
        return False, no_update, no_update

    row = matched.iloc[0]

    return (
        True,
        bbox,
        html.Div(
            [
                html.Div(
                    f"{row['date'].strftime('%H:%M')[1:] if row['date'].strftime('%H').startswith('0') else row['date'].strftime('%H:%M')} "
                    f"{row['weather_icon']}",
                    style={
                        "fontSize": "16px",
                        "marginBottom": "8px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            f"{row['temperature_2m']:.1f}℃",
                            style={
                                "color": "#6fa08a",
                                "fontSize": "18px",
                                "fontWeight": "500",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    f"☔",
                                    style={
                                        "marginRight": "6px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(f"{row['precipitation']:.1f} mm"),
                                        html.Div(
                                            f"{row['precipitation_probability']:.0f}%"
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "display": "flex",
                                "color": "#6f8fb8",
                                "fontSize": "12px",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "padding": "4px",
                "minWidth": "90px",
            },
        ),
    )


# Refresh Interval
@app.callback(
    Output("past-graph", "figure"),
    Output("future-temp-graph", "figure"),
    Output("future-rain-graph", "figure"),
    Output("today-graph", "figure"),
    Output("rain-5days-value", "children"),
    Output("temp-max-value", "children"),
    Output("temp-min-value", "children"),
    Output("rain-start-value", "children"),
    Output("insight-water", "children"),
    Output("insight-solar", "children"),
    Input("interval-component", "n_intervals"),
)
def update_data(n):
    global past_7days_df, future_7days_df, hourly_df, daily_dataframe, today
    weather_data = weather.load_weather_data()

    past_7days_df = weather_data["past_7days_df"]
    future_7days_df = weather_data["future_7days_df"]
    daily_dataframe = weather_data["daily_dataframe"]
    hourly_df = weather_data["hourly_df"]
    today = weather_data["today"]

    # get time
    time_info = get_now()
    now = time_info["now"]
    now_hour = time_info["hour"]
    now_day = time_info["day"]

    # graph rebuild
    fig_past = build_past7days_figure(past_7days_df)
    fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df, today)
    fig_today = build_today_figure(hourly_df)

    # info rebuild

    (
        rain_5days,
        temp_max_12h,
        temp_min_12h,
        rain_start_time,
    ) = build_info_card(
        past_7days_df,
        hourly_df,
        now,
    )

    # insight rebuild
    (
        insight_water_title,
        insight_water_text,
        insight_solar_title,
        insight_solar_text,
    ) = build_insight_card(
        rain_start_time,
        rain_5days,
        temp_max_12h,
        daily_dataframe,
        today,
    )

    return (
        fig_past,
        fig_future_temp,
        fig_future_rain,
        fig_today,
        f"{rain_5days:.0f} mm",
        f"{temp_max_12h:.1f} ℃",
        f"{temp_min_12h:.1f} ℃",
        rain_start_time,
        f"{insight_water_title}{insight_water_text}",
        f"{insight_solar_title}{insight_solar_text}",
    )


# Initial figures
fig_past = build_past7days_figure(past_7days_df)
fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df, today)
fig_today = build_today_figure(hourly_df)

time_info = get_now()
now = time_info["now"]
now_hour = time_info["hour"]
now_day = time_info["day"]
# Initial info card
(
    rain_5days,
    temp_max_12h,
    temp_min_12h,
    rain_start_time,
) = build_info_card(
    past_7days_df,
    hourly_df,
    now,
)

# Initial insight
(
    insight_water_title,
    insight_water_text,
    insight_solar_title,
    insight_solar_text,
) = build_insight_card(
    rain_start_time,
    rain_5days,
    temp_max_12h,
    daily_dataframe,
    today,
)


# Dash layout
app.layout = create_layout(
    fig_past,
    fig_future_temp,
    fig_future_rain,
    fig_today,
    rain_5days,
    temp_max_12h,
    temp_min_12h,
    rain_start_time,
)
# for Debug
app.run(debug=True)

# for Server
# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=8050)
