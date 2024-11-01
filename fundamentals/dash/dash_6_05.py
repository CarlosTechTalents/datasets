import threading
import time
import uuid

import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__)

@app.server.errorhandler(dash.exceptions.PreventUpdate)
def _handle_error(error):
    """Replace the default handler with one that does not print anything"""
    return '', 204

def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div([
    dcc.Interval(
        id='interval',
        interval=1*1000,
        n_intervals=0
    ),
    html.P(
        id='text',
        children='Loading...'
    ),
    html.Div(children=session_id, id='session-id', style={'display': 'none'})
])

app.layout = serve_layout

lock = threading.Lock()
d = set()
def acquire(id):
    with lock:
        if id in d:
            return False
        else:
            d.add(id)
            return True

def release(id):
    with lock:
        d.remove(id)

@app.callback(
    Output('text', 'children'),
    [Input('interval', 'n_intervals'), Input('session-id', 'children')]
)
def update(n, session_id):
    if acquire(session_id):
        try:
            print(f'{threading.current_thread()} {n} Not re-entrant! {session_id}')
            time.sleep(10.)
            print(f'---------------------- returning {n}')
            return n
        finally:
            release(session_id)
    else:
        print(f'{threading.current_thread()} {n} Re-entrant! {session_id}')
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=False)