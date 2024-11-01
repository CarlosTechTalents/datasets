from dash import Dash, html, dcc, dash_table, Input, Output, callback, no_update
import plotly.express as px
import pandas as pd

app = Dash()

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app.layout = html.Div([
    dcc.Store(id='memory-output'),
    dcc.Dropdown(
        df.country.unique(),
        ['Canada', 'United States'],
        multi=True,
        id='memory-countries',
    ),
    dcc.Dropdown(
        {'lifeExp': 'Life expectancy', 'gdpPercap': 'GDP per capita'},
        'lifeExp',
        id='memory-field'
    ),
    dcc.Graph(id='memory-graph'),
    dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in df.columns],
        id='memory-table',
    )
])


@callback(Output('memory-output', 'data'), Input('memory-countries', 'value'))
def filter_countries(countries_selected):
    if not countries_selected:
        return df.to_dict('records')
    dff = df[df['country'].isin(countries_selected)]
    return dff.to_dict('records')


@callback(Output('memory-table', 'data'), Input('memory-output', 'data'))
def update_table(data):
    if data is None:
        return no_update
    return data


@callback(Output('memory-graph', 'figure'), Input('memory-output', 'data'), Input('memory-field', 'value'))
def update_graph(data, field):
    if data is None:
        return no_update
    dff = pd.DataFrame(data)
    fig = px.line(
        dff,
        x='year',
        y=field,
        color='country',
        markers=True,
        title=f'{field} over time'
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)
