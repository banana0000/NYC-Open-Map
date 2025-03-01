import dash
import dash_bootstrap_components as dbc
from dash import html

# Oldal regisztrálása
dash.register_page(__name__, path="/", name="Summary")

# Stílus beállítása
CARD_STYLE = {
    "backgroundColor": "#1e1e1e",
    "color": "white",
    "padding": "20px",
    "borderRadius": "10px",
    "boxShadow": "2px 2px 10px rgba(255, 255, 255, 0.1)",
}

# Layout
layout = dbc.Container([ 
    html.H1("Application Summary", className="text-center text-white mt-4 display-4"),  # Növelt betűméret
    html.Br(),
    html.H2("This dashboard provides insights into NYC postal codes and buildings.", 
           className="text-center text-light"),
    html.Br(),
    dbc.Row([  # Kártyák középre igazítása
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Postal Codes", className="text-white"),
            dbc.CardBody(html.H3("2143", className="text-white display-4")),  # Növelt betűméret
        ], style=CARD_STYLE), width=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Buildings", className="text-white"),
            dbc.CardBody(html.H3("982,345", className="text-white display-4")),  # Növelt betűméret
        ], style=CARD_STYLE), width=4),
    ], justify="center", className="mt-4"),

    html.Br(),

    dbc.Row([  # Kártyák középre igazítása
        dbc.Col(dbc.Card([
            dbc.CardHeader("Postal Code Analysis", className="text-white"),
            dbc.CardBody(html.H3("Choropleth map: analyze postal codes across NYC.")),
        ], style=CARD_STYLE), width=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Building Density", className="text-white"),
            dbc.CardBody(html.H3("Scatter plot: analyze  building density across NYC.")),
        ], style=CARD_STYLE), width=4),
    ], justify="center", className="sm-6"),

    html.Br()
], fluid=True)
