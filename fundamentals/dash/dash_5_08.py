import base64

from dash import Dash, html, Input, Output, dcc, callback, State


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("No Output Example"),
        dcc.Upload(
            id='upload-data-to-server',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        ),
    ]
)


@callback(
    Input("upload-data-to-server", "contents"),
    State('upload-data-to-server', 'filename'),
    # We could also use `running` on the callback to disable the button
    # while the callback is running:
    # running=[(Output("upload-data-to-server", "disabled"), True, False)]
)
def update_output_div(contents, filename):
    if contents is not None:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        directory = './uploaded_files'
        with open(f'{directory}/{filename}', 'wb') as f:
            f.write(decoded)


if __name__ == "__main__":
    app.run(debug=True)
