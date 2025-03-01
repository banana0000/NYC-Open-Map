from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import register_page

# Load and clean data
data = pd.read_csv('data/data_reduced.csv')

# Convert all relevant columns to numeric, handling errors
data['ENERGY STAR Score'] = pd.to_numeric(data['ENERGY STAR Score'], errors='coerce')
data['Site Energy Use (kBtu)'] = pd.to_numeric(data['Site Energy Use (kBtu)'], errors='coerce')

# Remove rows with NaN in 'ENERGY STAR Score' and 'Site Energy Use (kBtu)'
data = data.dropna(subset=['ENERGY STAR Score', 'Site Energy Use (kBtu)'])

# Filter data for Calendar Year >= 1985
data = data[data['Year Built'] >= 1985]

load_figure_template("darkly")

# Default map style
default_map_style = 'carto-darkmatter'

# Create map visualization with gradient color scale
def create_map(style, df=None, highlight_id=None, measure_col='ENERGY STAR Score'):
    if df is None:
        df = data

    # Handle color scale dynamically based on the selected column
    fig = px.scatter_mapbox(
        df, lat='Latitude', lon='Longitude',
        hover_data=['Address 1', 'ENERGY STAR Score'],
        custom_data=['Property ID', 'Postal Code'],
        mapbox_style=style,
        animation_frame = "Year Built",
        zoom=12,
        color=measure_col,
        color_continuous_scale=px.colors.sequential.Viridis,
        range_color=[df[measure_col].min(), df[measure_col].max()]  # Dynamic range based on selected measurement
    )

    if highlight_id:
        fig.update_traces(marker=dict(size=10))
    else:
        fig.update_traces(marker=dict(size=10))

    return fig

data_scatter_map = create_map(default_map_style)

register_page(
    __name__,
    path="/scatter",
    title="Scatter Map",
    name="Scatter"
)

# Prepare a list of years for the dropdown
year_options = [{'label': str(year), 'value': year} for year in range(1985, data['Year Built'].max() + 1)]

layout = dbc.Container([
    dbc.Row([
        dbc.Col([  # AgGrid Table
            dag.AgGrid(
                id='my-grid',
                rowData=data.to_dict("records"),
                columnDefs=[{"field": i, "filter":True} for i in data.columns],
                dashGridOptions={"pagination": True, "paginationPageSize": 100},
                className="ag-theme-alpine-dark"
            ),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([  # Map Style Dropdown
            html.H5("Select Map Style", style={"color": "white", "textAlign": "center", "marginBottom": "5px"}),
            dbc.Select(
                id='map-style',
                options=[
                    {'label': 'Light Mode', 'value': 'open-street-map'},
                    {'label': 'Dark Mode', 'value': 'carto-darkmatter'},
                ],
                value=default_map_style,
                style={
                    'backgroundColor': '#121212',
                    'color': 'white',
                    'border': '1px solid #28a745',
                    'borderRadius': '5px',
                    'padding': '10px',
                    'fontSize': '16px',
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.2)',
                    'cursor': 'pointer'
                }
            )
        ], width=4, className='mb-4'),
        dbc.Col([  # Measurement Dropdown
            html.H5("Select Measurement", style={"color": "white", "textAlign": "center", "marginBottom": "5px"}),
            dbc.Select(
                id='my-dropdown',
                options=[
                    {'label': 'Year Built', 'value': 'Year Built'},
                    {'label': 'ENERGY STAR Score', 'value': 'ENERGY STAR Score'},
                    {'label': 'Site Energy Use (kBtu)', 'value': 'Site Energy Use (kBtu)'}
                ],
                value='ENERGY STAR Score',
                style={
                    'backgroundColor': '#121212',
                    'color': 'white',
                    'border': '1px solid #28a745',
                    'borderRadius': '5px',
                    'padding': '10px',
                    'fontSize': '16px',
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.2)',
                    'cursor': 'pointer'
                }
            )
        ], width=4, className='mb-4'),
    ]),
    html.Br(),
    dbc.Row([  # Placeholder for Graph and Map
        dbc.Col([  # Graph placeholder
            dcc.Graph(id='my-graph', figure=data_scatter_map, config={'scrollZoom': True})
        ], width=12),
    ]),
    html.Br(),
    dbc.Row([  # Detail Figure Placeholder
        dbc.Col([  # Figure Placeholder
            html.Div(id='figure-space'),
        ], width=12),
    ]),
], fluid=True)


@callback(
    Output('figure-space', 'children'),
    Output('my-graph', 'figure'),
    Input('my-graph', 'clickData'),
    Input('my-dropdown', 'value'),
    Input('map-style', 'value'),
    prevent_initial_call=True
)
def more_info(clicked_data, col_selected, map_style):
    # Update the map and scatter plot based on dropdown changes and map interactions
    if clicked_data is None:
        return no_update, create_map(map_style, measure_col=col_selected)

    try:
        clicked_property_id = clicked_data['points'][0]['customdata'][0]
        clicked_zip_code = clicked_data['points'][0]['customdata'][1]
    except (KeyError, IndexError) as e:
        return html.Div("Error: Could not retrieve data for the clicked point."), create_map(map_style, measure_col=col_selected)

    df_limited = data[data['Postal Code'] == clicked_zip_code].copy()
    df_limited[col_selected] = pd.to_numeric(df_limited[col_selected], errors='coerce')

    if clicked_property_id not in df_limited['Property ID'].values:
        return no_update, create_map(map_style, df_limited, clicked_property_id, measure_col=col_selected)

    x_axis_annotation = df_limited[df_limited['Property ID'] == clicked_property_id][col_selected].iloc[0]

    fig = px.scatter(
        df_limited, x=col_selected, y='ENERGY STAR Score',
        title=f'Visualization for buildings in zip code: {clicked_zip_code}',
        color=df_limited['Property ID'].apply(lambda x: 'Clicked' if x == clicked_property_id else 'Other'),
        color_discrete_map={'Clicked': 'blue', 'Other': 'red'},
    )

    fig.update_traces(marker=dict(size=10))

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='gray'
        ),
        yaxis=dict(
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='gray'
        ),
        legend=dict(
            font=dict(color='white')
        )
    )

    fig.add_annotation(
        x=x_axis_annotation,
        y=df_limited[df_limited['Property ID'] == clicked_property_id]['ENERGY STAR Score'].iloc[0],
        text="Your clicked building",
        showarrow=True,
        arrowhead=2,
        font=dict(size=19),
        yshift=10
    )

    updated_map = create_map(map_style, df_limited, clicked_property_id, measure_col=col_selected)

    return html.Div([dcc.Graph(figure=fig)]), updated_map
