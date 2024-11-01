from dash import Dash, html, Input, Output, callback

app = Dash()
app.layout = html.Div(
    [
        html.Button("execute callback", id="button_1"),
        html.Div(children="callback not executed", id="first_output_1"),
        html.Div(children="callback not executed", id="second_output_1"),
    ]
)


@callback(
    Output("first_output_1", "children"),
    Output("second_output_1", "children"),
    Input("button_1", "n_clicks")
)
def change_text(n_clicks):
    return ["n_clicks is " + str(n_clicks), "n_clicks is " + str(n_clicks)]

if __name__ == '__main__':
    app.run(debug=True)
