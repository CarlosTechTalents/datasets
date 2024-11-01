from dash import Dash, html, Input, Output, State, callback
import dash_daq as daq

app = Dash(__name__)

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

rootLayout = html.Div([
    daq.BooleanSwitch(
        on=True,
        className='dark-theme-control'
    ), html.Br(),
    daq.ToggleSwitch(
        className='dark-theme-control'
    ), html.Br(),
    daq.ColorPicker(
        value=dict(hex='#171717'),
        className='dark-theme-control'
    ), html.Br(),
    daq.Gauge(
        min=0,
        max=10,
        value=6,
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.GraduatedBar(
        value=4,
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.Indicator(
        value=True,
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.Knob(
        min=0,
        max=10,
        value=6,
        className='dark-theme-control'
    ), html.Br(),
    daq.LEDDisplay(
        value="3.14159",
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.NumericInput(
        min=0,
        max=10,
        value=4,
        className='dark-theme-control'
    ), html.Br(),
    daq.PowerButton(
        on=True,
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.PrecisionInput(
        precision=4,
        value=299792458,
        className='dark-theme-control'
    ), html.Br(),
    daq.StopButton(
        className='dark-theme-control'
    ), html.Br(),
    daq.Slider(
        min=0,
        max=100,
        value=30,
        targets={"25": {"label": "TARGET"}},
        color=theme['primary'],
        className='dark-theme-control'
    ), html.Br(),
    daq.Tank(
        min=0,
        max=10,
        value=5,
        className='dark-theme-control'
    ), html.Br(),
    daq.Thermometer(
        min=95,
        max=105,
        value=98.6,
        className='dark-theme-control'
    ), html.Br()

])


app.layout = html.Div([
    daq.ToggleSwitch(
        id='toggle-dark',
        label=['Light', 'Dark'],
        value=True
    ),
    html.Br(),
    html.Div([
        daq.ColorPicker(
            id='color-primary',
            label='Primary color',
            value=dict(hex='#00EA64')
        ),
        daq.ColorPicker(
            id='color-secondary',
            label='Accent color',
            value=dict(hex='#6E6E6E')
        ),
        daq.ColorPicker(
            id='color-detail',
            label='Detail color',
            value=dict(hex='#007439')
        )
    ]),
    html.Div(id='dark-theme-components', children=[
        daq.DarkThemeProvider(theme=theme, children=rootLayout)
    ], style={
        'border': 'solid 1px #A2B1C6',
        'border-radius': '5px',
        'padding': '50px',
        'marginTop': '20px'
    })
], style={'padding': '50px'})


@callback(
    Output('dark-theme-components', 'children'),
    Input('toggle-dark', 'value'),
    Input('color-primary', 'value'),
    Input('color-secondary', 'value'),
    Input('color-detail', 'value')
)
def edit_theme(dark, p, s, d):

    if(dark):
        theme.update(dark=True)
    else:
        theme.update(dark=False)

    if p is not None:
        theme.update(primary=p['hex'])
        for child in getattr(rootLayout, 'children'):
            if hasattr(child, 'color'):
                setattr(child, 'color', p['hex'])

    if s is not None:
        theme.update(secondary=s['hex'])
    if d is not None:
        theme.update(detail=d['hex'])
    return daq.DarkThemeProvider(theme=theme, children=rootLayout)


@callback(
    Output('dark-theme-components', 'style'),
    Input('toggle-dark', 'value'),
    State('dark-theme-components', 'style')
)
def switch_bg(dark, currentStyle):
    if(dark):
        currentStyle.update(backgroundColor='#303030')
    else:
        currentStyle.update(backgroundColor='white')
    return currentStyle


if __name__ == '__main__':
    app.run(debug=True)
