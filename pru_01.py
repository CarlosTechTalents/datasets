import datetime
import dash_daq as daq

from dash_iconify import DashIconify
from dash import Dash, html, Input, Output, State, callback, dcc, set_props

app = Dash()
app.layout = html.Div([

    html.Div([
        dcc.Slider(
            id='interval-slider-1',
            min=0.5,
            max=5,
            step=0.5,
            value=1,
            ),
    ], style={'width': '20%', 'padding':'20px'}),

    html.Div(id='latest-timestamp-1', style={"padding": "20px"}),

    html.Div([
        dcc.Slider(
            id='interval-slider-2',
            min=0.5,
            max=5,
            step=0.5,
            value=1,
            ),
    ], style={'width': '20%', 'padding':'20px'}),

    html.Div(id='latest-timestamp-2', style={"padding": "20px"}),

    html.Div([
        daq.ToggleSwitch(
            id = 'switch-gps',
            label={'label':'GPS','style':{'margin-bottom':'10px', 'margin-left': '10px','font-size':'1.5rem', }},
            labelPosition='Left',
            color='darkcyan',
            value=True)],
        style= {'display':'flex','align-content':'center','width':'20%', 'padding':'20px'}
    ),

    dcc.Interval(
            id='interval-1',
            interval=1 * 1000,
            n_intervals=0
    ),

    dcc.Interval(
            id='interval-2',
            interval=1 * 1000,
            n_intervals=0
    ),
])

@callback(
    Output(component_id='interval-1',component_property='interval'),
    Input('interval-slider-1', 'value')
    )
def update_refresh_rate_1(value):
    return value * 1000

@callback(
    Output('latest-timestamp-1', 'children'),
    Input('interval-1', 'n_intervals')
    )
def update_timestamp_1(interval):
    return [html.Span(f"Last updated: {datetime.datetime.now()}")] 

@callback(
    Output('interval-2','interval'),
    Input('interval-slider-2', 'value')
    )
def update_refresh_rate_1(value):
    return value * 1000

@callback(
    Output('latest-timestamp-2', 'children'),
    Input('interval-2', 'n_intervals')
    )
def update_timestamp_1(interval):
    return [html.Span(f"Last updated: {datetime.datetime.now()}")] 

@callback(
    Output('interval-1', 'disabled'),
    Input('switch-gps','value'),
    prevent_initial_call=True,
    )
def stop_interval(value):
    set_props("interval-2", {"disabled": value})
    return value

if __name__ == '__main__':
    app.run_server(debug=True)