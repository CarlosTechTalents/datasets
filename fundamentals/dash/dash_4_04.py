
from dash import Dash, html, dcc, Output, Input, State, callback, MATCH, no_update

# This example uses pattern matching callbacks since it needs 2 callbacks for each button.
# For more info see https://dash.plotly.com/pattern-matching-callbacks

app = Dash(__name__)

app.layout = html.Div([
    html.Div("Click to store in:"),

    # The memory store reverts to the default on every page refresh
    dcc.Store(id={'type': 'storage', 'index': 'memory'}),

    # The local store will take the initial data
    # only the first time the page is loaded
    # and keep it until it is cleared.
    dcc.Store(id={'type': 'storage', 'index': 'local'}, storage_type='local'),

    # Same as the local store but will lose the data
    # when the browser/tab closes.
    dcc.Store(id={'type': 'storage', 'index': 'session'}, storage_type='session'),

    html.Button('Memory Storage', id={'type': 'button-storage', 'index': 'memory'}),
    html.Button('Local Storage', id={'type': 'button-storage', 'index': 'local'}),
    html.Button('Session Storage', id={'type': 'button-storage', 'index': 'session'}),
    html.Hr(),

    html.Div([html.Span(0, id={'type': 'output-storage', 'index': 'memory'}), " Memory Clicks"]),
    html.Div([html.Span(0, id={'type': 'output-storage', 'index': 'local'}), " Local Clicks"]),
    html.Div([html.Span(0, id={'type': 'output-storage', 'index': 'session'}), " Session Clicks"]),
])


@callback(
    Output({'type': 'storage', 'index': MATCH}, 'data'), 
    Input({'type': 'button-storage', 'index': MATCH}, 'n_clicks'),
    State({'type': 'storage', 'index': MATCH}, 'data'))
def on_click(n_clicks, data):
    if n_clicks is None:
        return no_update

    # Give a default data dict with 0 clicks if there's no data.
    data = data or {'clicks': 0}

    data['clicks'] = data['clicks'] + 1
    return data

# Since we use the data prop in an output, we cannot get the initial data on load with the data prop.
# Instead, we use the modified_timestamp as Input and the data as State.
@callback(
    Output({'type': 'output-storage', 'index': MATCH}, 'children'),
    Input({'type': 'storage', 'index': MATCH}, 'modified_timestamp'),
    State({'type': 'storage', 'index': MATCH}, 'data'))
def on_data(ts, data):
    if ts is None:
        return no_update
    data = data or {}
    return data.get('clicks', 0)


if __name__ == '__main__':
    app.run(debug=True)
