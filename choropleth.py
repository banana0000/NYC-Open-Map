import dash_bootstrap_components as dbc
from dash import register_page, html, dcc, callback, Input, Output, no_update
import plotly.express as px
import pandas as pd
import json
from dash_bootstrap_templates import load_figure_template
import dash.dash_table as dt

# Register the page
register_page(
    __name__,
    path="/choropleth",
)

# Load GeoJSON and dataset
with open("data/new-york-zip-codes-_1604.geojson") as f:
    zip_geojson = json.load(f)

df = pd.read_csv('data/data_reduced.csv')
df["Postal Code"] = df["Postal Code"].astype(str)

# Apply darkly theme
load_figure_template("darkly")

def create_choropleth_map(dataframe, color, range_color, labels, map_style, colorscale):
    fig = px.choropleth_map(
        data_frame=dataframe,
        color=color,
        range_color=range_color,
        labels=labels,
        geojson=zip_geojson,
        opacity=0.9,
        zoom=10,
        featureidkey="properties.ZCTA5CE10",
        map_style=map_style,
        locations='Postal Code',
        center={"lat": 40.7128, "lon": -74.0060},
        height=650
    )
    return fig

# Page Layout
layout = html.Div([
    html.H1("New York City Building Data Visualization", style={"textAlign": "center", "margin": "30px"}),

    dbc.Row([
        dbc.Col([
            html.H5("Select Measurement", style={"color": "white", "textAlign": "center", "marginBottom": "5px"}),
            dbc.Select(
                id='measurments',
                options=[
                    {'label': 'ENERGY STAR Score', 'value': 'ENERGY STAR Score'},

                    {'label': 'Year Built', 'value': 'Year Built'}
                ],
                value='ENERGY STAR Score',
                style={
                    'backgroundColor': '#121212',
                    'color': 'white',
                    'border': '1px solid white',
                    'borderRadius': '5px',
                    'padding': '10px',
                    'fontSize': '16px',
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.2)',
                    'cursor': 'pointer'
                }
            )
        ], width=4, className='mb-4'),

        dbc.Col([
            html.H5("Select Map Style", style={"color": "white", "textAlign": "center", "marginBottom": "5px"}),
            dbc.Select(
                id='map-style',
                options=[
                    {'label': 'Light Mode', 'value': 'open-street-map'},
                    {'label': 'Dark Mode', 'value': 'carto-darkmatter'},
                    {'label': 'Satellite', 'value': 'satellite'}
                ],
                value='open-street-map',
                style={
                    'backgroundColor': '#121212',
                    'color': 'white',
                    'border': '1px solid white',
                    'borderRadius': '5px',
                    'padding': '10px',
                    'fontSize': '16px',
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.2)',
                    'cursor': 'pointer'
                }
            )
        ], width=3, className='mb-4'),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Current", style={"textAlign": "center", "backgroundColor": "black", "color": "white"}),
            dbc.CardBody(html.H2(id="kpi-value", style={"textAlign": "center", "fontSize": "24px"}))
        ], color="dark", inverse=True), width=3),
    ], className='align-items-center mb-3', justify="center"),

    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H2('Find and click any postalcode marker on the map', style={'textAlign': 'center', 'background-color': 'darkblue'}),
        ], width=12),
    ]),

    dbc.Spinner(
        id="loading-spinner",
        color="dark", spinner_style={"width": "3rem", "height": "3rem"},
        children=dcc.Graph(id='zip-map')
    ),

    html.Div(id='filler'),
])

# Callbacks
@callback(
    Output('kpi-value', 'children'),
    Input('measurments', 'value')
)
def update_kpi(measurment_chosen):
    df[measurment_chosen] = pd.to_numeric(df[measurment_chosen], errors='coerce')

    if measurment_chosen == 'ENERGY STAR Score':
        kpi_value = df[measurment_chosen].mean()
        return f"{kpi_value:.2f} (Avg Energy Score)"
    elif measurment_chosen == 'Indoor Water Use (All Water Sources) (kgal)':
        kpi_value = df[measurment_chosen].mean()
        return f"{kpi_value:.2f} kgal (Avg Water Use)"
    elif measurment_chosen == 'Year Built':
        kpi_value = df[measurment_chosen].mean()
        return f"{int(kpi_value)} (Avg Year Built)"
    return "N/A"

@callback(
    Output('zip-map', 'figure'),
    Input('measurments', 'value'),
    Input('map-style', 'value')
)
def make_graph(measurment_chosen, map_style):
    df[measurment_chosen] = pd.to_numeric(df[measurment_chosen], errors='coerce')
    df_filtered = df.groupby('Postal Code')[measurment_chosen].mean().reset_index()

    # Use 'Blues' colorscale for water-related data
    colorscale = 'Blues'

    if measurment_chosen == 'ENERGY STAR Score':
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[35, 85],
                                    labels={'ENERGY STAR Score': 'Energy Score'}, map_style=map_style, colorscale=colorscale)
    elif measurment_chosen == 'Indoor Water Use (All Water Sources) (kgal)':
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[2000, 8000],
                                    labels={'Indoor Water Use (All Water Sources) (kgal)': 'Indoor Water Use'}, map_style=map_style, colorscale=colorscale)
    elif measurment_chosen == 'Year Built':
        df_filtered['Year Built'] = df_filtered['Year Built'].astype(int)
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[1950, 2000], labels=None, map_style=map_style, colorscale=colorscale)

    return fig

@callback(
    Output('filler', 'children'),
    Input('zip-map', 'clickData'),
    Input('measurments', 'value')
)
def display_details(clicked_data, measurment_chosen):
    if clicked_data:
        zipcode = clicked_data['points'][0]['location']
        df_filtered = df[df["Postal Code"] == zipcode]

        if not df_filtered.empty:
            bar_fig = px.bar(
                df_filtered,
                x="Property Name",
                y=measurment_chosen,
                color=measurment_chosen,
                labels={measurment_chosen: "Value"},
                height=400
            )

            table = dt.DataTable(
                id='details-table',
                columns=[{"name": col, "id": col} for col in df_filtered.columns],
                data=df_filtered.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(209, 79, 79)',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'textAlign': 'left'
                },
                page_size=10
            )

            return html.Div([
                html.H4(f"Details for Postal Code: {zipcode}", style={"textAlign": "center"}),
                dcc.Graph(figure=bar_fig),
                html.Hr(),
                html.H4("Detailed Data Table", style={"textAlign": "center"}),
                table
            ])
        else:
            return html.Div(f"No data available for ZIP Code: {zipcode}")
    else:
        return no_update
