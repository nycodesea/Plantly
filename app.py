import requests
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd

app = Dash(__name__)

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 35,
    "longitude": 139,
    "hourly": "temperature_2m,relative_humidity_2m",
}

data = requests.get(url, params=params).json()
print(data)
times = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]
humidity = data["hourly"]["relative_humidity_2m"]

df = pd.DataFrame({"time": times, "temperature": temperatures, "humidity": humidity})
fig = px.line(
    df,
    x="time",
    y=["temperature", "humidity"],
    title="Temperature and Humidity Over Time",
)
app.layout = html.Div([html.H1("Plant Dashboard"), dcc.Graph(figure=fig)])


app.run(debug=True)
