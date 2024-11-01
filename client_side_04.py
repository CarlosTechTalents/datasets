from dash import Dash, html, dcc, Input, Output

app = Dash()

app.layout = html.Div(
    [
        html.Span(
            [
                "Press ",
                html.Kbd("Ctrl"),
                " + ",
                html.Kbd("R"),
                " to refresh the app's data",
            ]
        ),
        dcc.Store(id="store-events", data={}),
        html.Div(id="container-events"),
    ],
    id="document",
)


app.clientside_callback(
    """
    function () {
        document.addEventListener('keydown', function(e) {

            if (e.ctrlKey && e.keyCode == 82) {
                // Simulate getting new data
                newData = JSON.stringify(new Date())

                // Update dcc.Store with ID store-events
                dash_clientside.set_props("store-events", {data: newData})

                event.preventDefault()
                event.stopPropagation()
                return dash_clientside.no_update;
            }
        });
        return dash_clientside.no_update;
    }
    """,
    Output('document', 'id'),
    Input('document', 'id'),
)


@app.callback(
    Output('container-events', 'children'),
    Input('store-events', 'data'),
    prevent_initial_call=True
)
def handle_key_press(data):
    return f"Current data value: {data}"


if __name__ == '__main__':
    app.run(debug=True)
