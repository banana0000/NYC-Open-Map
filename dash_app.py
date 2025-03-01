import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], use_pages=True)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # URL monitor

    # Navigation Bar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand('NYC Energy', className='ms-2', style={"color": "white", "font-size": "24px"}),

            dbc.Nav([
                dbc.NavItem(dbc.NavLink('Home', href="/", id="link-home", 
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Postal Codes", href="/choropleth", id="link-postal", 
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Buildings", href="/scatter", id="link-buildings", 
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Weather", href="/weather", id="link-weather", 
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),

            ], className="ms-auto", navbar=True, style={"margin-left": "auto", "padding-right": "50px"})
        ], fluid=True),
        className="navbar-custom mb-4",
        style={"background": "linear-gradient(90deg, red, blue)"}
    ),

    dash.page_container,  # This loads content for each page
])

# Callback to update link styles based on the active page
@app.callback(
    [
        Output("link-home", "style"),
        Output("link-postal", "style"),
        Output("link-buildings", "style"),
        Output("link-weather", "style"),  # Added weather link
    ],
    Input("url", "pathname")
)
def update_link_style(pathname):
    default_style = {"color": "white", "font-size": "25px", "textDecoration": "none"}
    selected_style = {"color": "white", "textDecoration": "underline", "font-size": "25px"}

    if pathname == "/":
        return selected_style, default_style, default_style, default_style
    elif pathname == "/choropleth":
        return default_style, selected_style, default_style, default_style
    elif pathname == "/scatter":
        return default_style, default_style, selected_style, default_style
    elif pathname == "/weather":
        return default_style, default_style, default_style, selected_style
    return default_style, default_style, default_style, default_style

# Running the server
if __name__ == "__main__":
    app.run(debug=True)
