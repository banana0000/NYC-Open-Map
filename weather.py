import dash 
from dash import html, dcc, Input, Output, register_page
import dash_bootstrap_components as dbc
import requests
import plotly.graph_objects as go

register_page(__name__, path="/weather")  # Registering the page

API_KEY = ''

# Function to fetch weather data
def fetch_weather_data(city):
    URL = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    FORECAST_URL = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    
    response = requests.get(URL)
    forecast_response = requests.get(FORECAST_URL)

    data = response.json()
    forecast_data = forecast_response.json()
    
    if response.status_code == 200:
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        icon = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon}.png"
    else:
        temperature, weather_description, wind_speed, humidity, pressure, icon_url = ["N/A"] * 6

    # Forecast data (5 points for 5 days)
    forecast_temps = [forecast['main']['temp'] for forecast in forecast_data['list'][::8]]  # Get one data point per day (every 8th item)
    forecast_times = [forecast['dt_txt'] for forecast in forecast_data['list'][::8]]  # Extract the time of the forecast

    return temperature, weather_description, wind_speed, humidity, pressure, icon_url, forecast_temps, forecast_times

# Layout for the page
layout = dbc.Container(
    [   html.H1("Weather and forecast in New York City", className="text-center text-primary mb-4"),
        html.Br(),

        # Select a component label, aligned left
        html.H5("Select a component", className="text-light", style={"textAlign": "left"}),

        # Dropdown for selecting visible metrics, with reduced size and centered
        dbc.Row(
            dbc.Col(
                dbc.Select(
                    id='metric-dropdown',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Temperature', 'value': 'temperature'},
                        {'label': 'Condition', 'value': 'condition'},
                        {'label': 'Wind Speed', 'value': 'wind'},
                        {'label': 'Humidity', 'value': 'humidity'},
                        {'label': 'Pressure', 'value': 'pressure'}
                    ],
                    value='all',
                    style={
                        'backgroundColor': 'black',
                        'color': 'white',
                        'border': '1px solid white',
                        'borderRadius': '5px',
                        'padding': '10px',
                        'fontSize': '16px',
                        'boxShadow': '0px 4px 6px rgba(255, 255, 255, 0.2)',
                        'cursor': 'pointer',
                        'width': '50%'  # Reduced the width to 50%
                    },
                    className="text-center"
                ), width=4, className="text-center"
            )
        ),

        html.Br(),

        # Weather Details
        dbc.Row(
            dbc.Col(
                [
                    dbc.Card(
                        dbc.CardBody([html.H4("Temperature"), html.P(id='current-temperature')]),
                        color="dark", inverse=True, className="mb-3 text-center", id="temp-card"
                    ),
                    dbc.Card(
                        dbc.CardBody([html.H4("Condition"), html.P(id='current-condition')]),
                        color="dark", inverse=True, className="mb-3 text-center", id="condition-card"
                    ),
                    dbc.Card(
                        dbc.CardBody([html.H4("Wind Speed"), html.P(id='current-wind')]),
                        color="dark", inverse=True, className="mb-3 text-center", id="wind-card"
                    ),
                    dbc.Card(
                        dbc.CardBody([html.H4("Humidity"), html.P(id='current-humidity')]),
                        color="dark", inverse=True, className="mb-3 text-center", id="humidity-card"
                    ),
                    dbc.Card(
                        dbc.CardBody([html.H4("Pressure"), html.P(id='current-pressure')]),
                        color="dark", inverse=True, className="mb-3 text-center", id="pressure-card"
                    ),
                    dbc.Card(
                        dbc.CardBody([html.Img(id='weather-icon', style={"maxWidth": "50px"})]),
                        color="dark", className="mb-3 text-center"
                    ),
                ], width=4
            ),
            className="justify-content-center"
        ),

        # Forecast Line Chart
        dbc.Row(
            dbc.Col(dcc.Graph(id='forecast-graph'), width=12)
        ),
    ],
    fluid=True,
    style={"backgroundColor": "black", "minHeight": "100vh", "padding": "20px"}
)

# Callback to update weather data based on selected metric
@dash.callback(
    [
        Output('current-temperature', 'children'),
        Output('current-condition', 'children'),
        Output('current-wind', 'children'),
        Output('current-humidity', 'children'),
        Output('current-pressure', 'children'),
        Output('weather-icon', 'src'),
        Output('forecast-graph', 'figure'),
        Output('temp-card', 'style'),
        Output('condition-card', 'style'),
        Output('wind-card', 'style'),
        Output('humidity-card', 'style'),
        Output('pressure-card', 'style'),
    ],
    [Input('metric-dropdown', 'value')]
)
def update_weather(selected_metric):
    city = "New York"  # Always show New York
    temperature, weather_description, wind_speed, humidity, pressure, icon_url, forecast_temps, forecast_times = fetch_weather_data(city)

    # Create Forecast Line Chart
    forecast_fig = go.Figure(
        data=[go.Scatter(
            x=forecast_times,
            y=forecast_temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='lightblue', width=3),
            marker=dict(size=6),
            text=forecast_temps,
            textposition='top center',
        )],
        layout=go.Layout(
            title="5-Day Weather Forecast",
            xaxis=dict(title="Time", tickangle=-45),
            yaxis=dict(title="Temperature (°C)"),
            template="plotly_dark",
            showlegend=False
        )
    )

    # Hide or show cards based on dropdown selection
    hidden_style = {"display": "none"}
    visible_style = {}

    temp_style = visible_style if selected_metric in ['all', 'temperature'] else hidden_style
    condition_style = visible_style if selected_metric in ['all', 'condition'] else hidden_style
    wind_style = visible_style if selected_metric in ['all', 'wind'] else hidden_style
    humidity_style = visible_style if selected_metric in ['all', 'humidity'] else hidden_style
    pressure_style = visible_style if selected_metric in ['all', 'pressure'] else hidden_style

    return (
        f"{temperature}°C", weather_description, f"{wind_speed} m/s",
        f"{humidity}%", f"{pressure} hPa", icon_url, forecast_fig,
        temp_style, condition_style, wind_style, humidity_style, pressure_style
    )
