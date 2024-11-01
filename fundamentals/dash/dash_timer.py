
from time import time, perf_counter
from dash import Dash, dcc, html, Input, Output, State, callback, no_update


app = Dash()
activo = True
n_keys = 0

app.layout = html.Div(
    [
        dcc.Interval(id="interval", interval=100, disabled=True),
        html.P(id="output"),
        html.Button("Start/Stop", id="button"),
    ]
)

# Callback del botón que modifica el estado del interval
@app.callback(
    Output("interval", "disabled"),
    [Input("button", "n_clicks")],
    [State("interval", "disabled")],
)
def toggle_interval(n, disabled):
    global n_keys
    n_keys += 1
    if n:
        return not disabled
    return disabled

# Callback del interval que actualiza el elemento output de HTML
@app.callback(
    Output("output", "children"),
    [Input("interval", "n_intervals"),
     Input("interval", "disabled")]
)
def display_count(n, estado):
    global n_keys, activo
    if activo:
        return f"Interval has fired {n} times and pushed {n_keys} keys. Disabled status is {estado}. Activo es: '{activo}'. Time stamp {round (perf_counter(),1)}"
    else:
        return no_update


if __name__ == "__main__":
    app.run(port=8050, debug=True)

