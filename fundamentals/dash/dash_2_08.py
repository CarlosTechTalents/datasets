from dash import Dash, dcc, html, Input, Output, callback

app = Dash(__name__)

my_input = dcc.Input(value='initial value', type='text')
my_output = html.Div()

app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        my_input
    ]),
    html.Br(),
    my_output
])


@callback(
    Output(my_output, 'children'),
    Input(my_input, 'value')
)
def update_output_div(input_value):
    return f'Output: {input_value}'


if __name__ == '__main__':
    app.run(debug=True)
