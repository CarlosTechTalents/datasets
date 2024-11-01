from dash import Dash, html, Input, Output

app = Dash(prevent_initial_callbacks=True)

app.layout = html.Div(
    [
        html.Button("Button 1", id="btn1"),
        html.Button("Button 2", id="btn2"),
        html.Button("Button 3", id="btn3"),
        html.Div(id="log"),
    ]
)

app.clientside_callback(
    """
    function(){
        console.log(dash_clientside.callback_context);
        const triggered_id = dash_clientside.callback_context.triggered_id;
        return "triggered id: " + triggered_id
    }
    """,
    Output("log", "children"),
    Input("btn1", "n_clicks"),
    Input("btn2", "n_clicks"),
    Input("btn3", "n_clicks"),
)

if __name__ == "__main__":
    app.run_server()

