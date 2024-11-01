import datetime
import dash_daq as daq

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, html, Input, Output, State, callback, dcc, _dash_renderer
_dash_renderer._set_react_version("18.2.0")

theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=25), darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
    ],
    variant="transparent",
    color="yellow",
    id="color-scheme-toggle",
    size="lg",
    ms="auto",
)

app = Dash(external_stylesheets=dmc.styles.ALL)
app.layout = dmc.MantineProvider(
    [theme_toggle,
    html.Div(children=[
        dcc.Slider(min=0.5, max=5, step=0.5, value=1, id='interval-refresh'),
    ], style={'width': '20%'}),
    html.Div(id='latest-timestamp', style={"padding": "20px"}),
    html.Div([
        daq.ToggleSwitch(
            id = 'toggle_gps',
            label={'label':'GPS','style':{'margin-bottom':'10px', 'margin-left': '10px','font-size':'1.5rem', }},
            labelPosition='Left',
            color='darkcyan')],
        style= {'display':'flex','align-content':'center','width':'20%', 'margin':'10px'}
    ),
    dmc.Switch(id="switch-gps", label="GPS", checked=False, onLabel="ON", offLabel="OFF", size="xl", radius="xl"),
    dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
    ),
    ],
    id="mantine-provider",
    forceColorScheme="light",
)

@callback(
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-toggle", "n_clicks"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def switch_theme(_, theme):
    return "dark" if theme == "light" else "light"


@callback(
    Output(component_id='interval-component',component_property='interval'),
    Input('interval-refresh', 'value')
    )
def update_refresh_rate(value):
    return value * 1000

@callback(
    Output(component_id='latest-timestamp', component_property='children'),
    Input('interval-component', 'n_intervals')
    )
def update_timestamp(interval):
    return [html.Span(f"Last updated: {datetime.datetime.now()}")] 

if __name__ == '__main__':
    app.run_server(debug=True)