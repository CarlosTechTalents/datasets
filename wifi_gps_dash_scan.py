import os
import json
from io import StringIO
from pathlib import Path
import random

from dash import Dash, html, dcc, Output, Input, State, DiskcacheManager, dash_table, callback, set_props, callback_context, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_daq as daq
import diskcache
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign

import plotly.express as px
import plotly.graph_objects as go

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import numpy as np


from time import sleep
from time import time
import datetime
from datetime import datetime as dt

import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports

from gps import Gps
from wifi import Wifi
import wifi

# **************************
# *** Variables globales ***
# **************************

stop_gps = False
stop_wifi_scan = False
df = pd.DataFrame()
gps = Gps ()
wifi = Wifi()

gps_latitudes = [40.6043, 40.6043, 40.6042, 40.6041]
gps_longitudes = [-4.0648, -4.0647, -4.0647, -4.0648]

# **************************************************************************************
# *** Preguntar por el puerto al que está conectado el GPS y el interface de la wifi ***
# **************************************************************************************

gps.get_serial_port()
wifi.get_interfaces()
wifi.print_interfaces_list()


# ******************************
# *** Inicialización de Dash ***
# ******************************
chroma = "/assets/chroma.min.js"  # js lib used for colors
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)
app = Dash(__name__, background_callback_manager=background_callback_manager, external_scripts=[chroma])
#app = Dash(__name__, background_callback_manager=background_callback_manager, external_stylesheets=[dbc.themes.COSMO])
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=external_stylesheets, background_callback_manager=background_callback_manager)

#
# *** MAPAS ***
#

CP94 = dlx.dicts_to_geojson([dict(lat=40.605837666666666, lon=-4.063023, popup="Access Point CP94")])
colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # rainbow
vmin = 0
vmax = 100

# Client side callbacks

# *** POIS ***
# Geojson rendering logic, must be JavaScript as it is executed in clientside.

on_each_feature = assign("""function(feature, layer, context){
    layer.bindTooltip(`${feature.properties.name} (${feature.properties.rssi})`)
}""")

point_to_layer = assign("""function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop
    return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
}""")

# Polygons ***
# Color selected polygons in red.
style_handle = assign("""function(feature, context){
    const {selected} = context.hideout;
    if(selected.includes(feature.properties.name)){
        return {fillColor: 'red', color: 'grey'}
    }
    return {fillColor: 'grey', color: 'grey'}
}""")

# *************************
# *** Layout Components ***
# *************************

# Título página
def titulo_pagina(texto):
    return html.H1(
        children=texto,
        style={'textAlign':'center'}
        )

# Botón Start/Stop
def boton_play_stop(texto, id):
    return html.Div(
        [
        html.Button(
            DashIconify(
                id='icon-'+id+'-start',
                icon="ph:play-fill",
                width=30,
                ),
            id=id+'-start-button',
            style={'color':'green', 'cursor':'pointer'},
            disabled=False),
        
        html.Div(texto, style={'font-size':'1.5rem', 'margin-top': '10px'}),
        
        html.Button(
            DashIconify(
                id='icon-'+id+'-stop',
                icon="f7:playpause-fill",
                width=30,
                ),
            id=id+'-stop-button',
            style={'color':'lightGrey', 'cursor':'not-allowed'},
            disabled=True),
        ],
        className='two-button-container'
        )

# *************************
# *** Layout aplicación ***
# *************************

app.layout = html.Div(
    id='page_container',
    children=[
        
        # *** Inicio Título Página
        # titulo_pagina('Wifi scanner'),
        # *** Fin Título Página


        dcc.Tabs(
            parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[
                dcc.Tab(
                    label='Wifi Scanner',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    children=[

                        # *** Inicio Sección Cabecera
                        html.Div([
                            # *** Inicio Sección Cabecera Izquierda
                            html.Div(
                                className='flex-column',
                                style={'flex':'30%'},
                                children=[
                                    
                                    boton_play_stop('GPS','gps'),
                                    
                                    html.Div(
                                        children=[
                                            html.Span('Estado GPS: '),
                                            html.Span ('Off', id='estado-gps'),
                                            html.Hr(style = {'size' : '50', 'borderColor':'darkcyan','borderHeight': "2vh", "width": "95%",}),
                                        ],
                                        style={'margin-left':'10px'}
                                    ),
                                    
                                    boton_play_stop('Wifi', 'wifi'),
                                    
                                    html.Hr(style = {'size' : '50', 'borderColor':'darkcyan','borderHeight': "2vh", "width": "95%",}),

                                    html.Div(
                                        className='two-button-container',
                                        children=[
                                            daq.ToggleSwitch(
                                                id = 'switch-wifi-scan',
                                                label={'label':'Wifi Scan','style':{'margin-left': '10px','font-size':'1.5rem', }},
                                                labelPosition='Left',
                                                color='darkcyan',
                                                value=False,
                                                style={'margin-left':'10px', 'margin-top':'2px'}
                                                )
                                            ],
                                    ),

                                    html.Div(
                                        children=[
                                        html.Span('Estado Wifi: '),
                                        html.Span ('Off', id='estado-wifi'),
                                        ],
                                        style={'margin-bottom':'10px', 'margin-left':'10px'}
                                    ),

                                    html.Div(
                                        children=[
                                            html.Div('Filtrar SSIDs que contienen:'),
                                            dcc.Input(id="input-filtro-wifis", type="text", placeholder="Filtro SSIDs", style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),
                                        ],
                                        style={'margin-left':'10px'}
                                    ),

                                    html.Hr(style = {'size' : '50', 'borderColor':'darkcyan','borderHeight': "2vh", "width": "95%",}),

                                    html.Div(
                                        children=[
                                            html.Button("Save CSV", id="btn-save-csv"),
                                            dcc.Download(id="download-dataframe-csv"),
                                            html.Button('Load CSV', id='load-csv-button', n_clicks=0, style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),
                                            dcc.Input(id="input-nombre-csv-load", type="text", placeholder="Nombre archivo csv", style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),
                                            html.Button('Borrar datos', id='btn-borrar-datos', n_clicks=0, style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),                                            
                                        ],
                                        style={'margin-left':'10px'}
                                    ),
                                ],
                            ),
                                # *** Fin Sección Cabecera Izquierda***
                                
                            # *** Inicio Sección Cabecera Derecha
                            html.Div([
                                dcc.Graph(id='wifis-graph-1', style={'height':'100%'}),
                                ],className='flex-column', style={'flex':'70%'}),
                            ],className='flex-row'),
                            # *** Fin Sección Cabecera Derecha
                        # ***Fin Sección Cabecera

                        dcc.Tabs(
                            parent_className='custom-tabs',
                            className='custom-tabs-container',
                            children=[
                                dcc.Tab(
                                    label='Current readings',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected',
                                    children=[
                                        html.Div('Lecturas del GPS', style={'margin-left':'10px', 'margin-top':'10px', 'margin-bottom':'5px'}),
                                        dcc.Textarea(
                                            id='textarea-gps',
                                            value='No GPS data, yet!',
                                            style={'width': '80%', 'height': '4rem'},
                                            ),
                                        html.Div('Lecturas del escaneo Wifi', style={'margin-left':'10px', 'margin-top':'10px', 'margin-bottom':'5px'}),
                                        dcc.Textarea(
                                        id='textarea-wifi',
                                        value='No Wifi data, yet!',
                                        style={'width': '80%', 'height': '3rem'},
                                        ),
                                        ]
                                    ),

                                dcc.Tab(
                                    label='RSSIs Graph',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected',
                                    children=[
                                        dcc.Graph(id='wifis-graph-2'),
                                        ]
                                    ),

                                dcc.Tab(
                                    label='Geolocation Graph',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected',
                                    children=[
                                        dcc.Graph(id='wifis-graph-3'),
                                        ]
                                    ),

                                dcc.Tab(
                                    label='Aggregate Datatable',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected',
                                    children=[
                                        dash_table.DataTable(
                                            id = 'wifis-datatable',
                                            style_table={'width': '80%'}),
                                        ]
                                    ),
                                ]
                            ),

                        html.Div(id='tabs-content-classes'),
                    ],
                ),
                dcc.Tab(
                    label='Devices',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    children=[
                        html.Button(
                            'Zoom +',
                            id='btn-graph-4',
                        ),
                        html.Div(id='graph-4-info'),
                        dcc.Graph(id='graph-4'),
                    ],
                ),

                dcc.Tab(
                    label='Navigation',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    children=[
                        html.Div(
                            children=[
                                dcc.Input(id="input-ref-poi", type="text", placeholder="Referencia punto/polígono GPS", style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px', 'width':'12%'}),
                                html.Button('Save GPS Point', id='btn-save-gps-point', n_clicks=0, style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),
                                html.Button('Save GPS Polygon', id='btn-save-gps-poly', n_clicks=0, style={'marginRight':'10px', 'fontsize':'1.5rem', 'padding':'10px'}),                                            
                                html.Button("Save GeoJson", id="btn-save-gps-json"),
                                html.Button("Mark Current Position", id="btn-current-position"),
                                dcc.Download(id="download-gps-json"),
                                html.Button("Load GeoJson", id="btn-load-geojson"),
                                dcc.ConfirmDialog(
                                    id='confirm-popup',
                                    message='Se ha grabado la posición del GPS',
                                ),
                            ],
                            style={'margin-left':'10px', 'margin-top':'10px'}
                        ),
                        html.Div(
                            style={'margin-top':'20px', 'width':'90%'},
                            children=[

                                # *** MAP 1 ***
                                dl.Map(
                                    style={'height': '80vh', 'margin': '10px'},
                                    center=[40.6058, -4.0630],
                                    zoom=16,
                                    children=[
                                        dl.LayersControl(
                                            id= 'lc',
                                            children= [
                                                dl.TileLayer(
                                                    maxZoom=19,
                                                    updateWhenZooming=True
                                                    ),
                                                dl.Overlay(
                                                    name='polygon',
                                                    checked=True,
                                                    children=[
                                                        dl.LayerGroup([
                                                                                                                        
                                                            dl.GeoJSON(
                                                                id="geojson_polygons",
                                                                url="/assets/fox_polygons.geojson",
                                                                zoomToBounds=True,
                                                                zoomToBoundsOnClick=True,
                                                                superClusterOptions={"radius": 100},
                                                                hideout=dict(selected=[]),
                                                                style=style_handle,
                                                                hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))                                            
                                                                ),
                                                        ])
                                                    ]
                                                ),

                                                dl.Overlay(
                                                    name='wifi scans',
                                                    checked=True,
                                                    children=[
                                                        dl.LayerGroup([

                                                            # Create geojson.
                                                            dl.GeoJSON(
                                                                id="geojson_points",
                                                                url="/assets/fox_points.geojson",
                                                                zoomToBounds=True,  # when true, zooms to bounds when data changes
                                                                pointToLayer=point_to_layer,  # how to draw points
                                                                onEachFeature=on_each_feature,  # add (custom) tooltip
                                                                hideout=dict(colorProp='rssi',
                                                                            circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                                                                            min=vmin,
                                                                            max=vmax,
                                                                            colorscale=colorscale)
                                                                ),

                                                            # Create a colorbar.
                                                            dl.Colorbar(colorscale=colorscale, width=20, height=150, min=vmin, max=vmax, unit='dB'),
                                                        ])
                                                    ]
                                                ),

                                                dl.Overlay(
                                                    name='markers',
                                                    checked=True,
                                                    children=[
                                                        dl.LayerGroup([

                                                            dl.GeoJSON(
                                                                data=dlx.dicts_to_geojson([dict(lat=40.6065, lon=-4.0635)] * 50),
                                                                cluster=True
                                                                ),

                                                            dl.GeoJSON(id='current-position-marker', data=CP94),  # in-memory geojson (slowest option)

                                                        ])
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),

        dcc.Interval(
                id='interval-current-wifi',
                interval=1000,
                n_intervals=0,
                disabled=True
        ),

        dcc.Interval(
                id='interval-scan-wifis',
                interval=1000,
                n_intervals=0,
                disabled=True
        ),

        # Store para almacenar los datos de lectura del GPS
        dcc.Store(
            id='store-gps',
            data=[],
            storage_type='memory' # 'local' or 'session'
        ),
        
        # Store para almacenar los datos de lectura de las redes Wifi
        dcc.Store(
            id='store-wifi',
            data=[],
            storage_type='memory' # 'local' or 'session'
        ),
        
        # Store para almacenar los datos de lectura de las redes Wifi
        dcc.Store(
            id='store-wifi-historic',
            data=[],
            storage_type='memory' # 'local' or 'session'
        ),
        
        # Store para almacenar puntos de interés del GPS
        dcc.Store(
            id='store-gps-poi',
            data=[],
            storage_type='memory' # 'local' or 'session'
        ),
    ],
)

#
# *** MAP ***
#

@app.callback(
    Output("geojson_polygons", "hideout"),
    Input("geojson_polygons", "n_clicks"),
    State("geojson_polygons", "clickData"),
    State("geojson_polygons", "hideout"),
    prevent_initial_call=True)
def toggle_select(_, feature, hideout):
    selected = hideout["selected"]
    name = feature["properties"]["name"]
    if name in selected:
        selected.remove(name)
    else:
        selected.append(name)
    return hideout

@app.callback(
    Output('current-position-marker', 'data'),
    Input('btn-current-position', 'n_clicks'),
    State('store-gps', 'data'),
    prevent_initial_call=True)
def update_current_position(n_clicks, gps_data):
    print (gps_data)
    positions = [
        dlx.dicts_to_geojson([dict(lat=gps_data['Latitude'], lon=gps_data['Longitude'], popup="Home")]),
        dlx.dicts_to_geojson([dict(lat=40.605837666666666, lon=-4.063023, popup="Access Point CP94")])
        ]
    return random.choice(positions)
    
    
# *****************************
# *** Callback on page load ***
# *****************************

@callback(
    Input('page_container', 'loading_state')
)
def on_page_load(value):
    # print (f'Valor de pagina principal')
    return
    

# *************************
# *** Callbacks del GPS ***
# *************************

# Callback para cambiar el estado de los botones de Start/Stop del GPS
@callback(
    Output('gps-start-button', 'disabled'),
    Output('gps-stop-button', 'disabled'),
    Output('estado-gps', 'children'),
    Input('gps-start-button', 'n_clicks'),
    Input('gps-stop-button', 'n_clicks'),
    prevent_initial_call = True
)
def gps_start_stop_button(n_clicks_start, n_clicks_stop):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'gps-start-button':
        set_props('gps-start-button', {'style':{'color':'lightGrey', 'cursor':'wait'}})
        set_props('gps-stop-button', {'style':{'color':'red', 'cursor':'pointer'}})
        return True, False, no_update
    else:
        set_props('gps-start-button', {'style':{'color':'green', 'cursor':'pointer'}})
        set_props('gps-stop-button', {'style':{'color':'lightGrey', 'cursor':'not-allowed'}})
        return False, True, f'En Pausa desde: {dt.now().strftime("%H:%M:%S")}'

# Callback para iniciar o parar la lectura del GPS
@callback(
    Input('gps-start-button','n_clicks'),
    background=True,
    cancel=[Input("gps-stop-button", "n_clicks")],
    prevent_initial_call = True,
    )
def run_gps(n_clicks):
    global gps

    while True:
        gps.gps_reset_input_buffer()
        ahora = dt.now()
        position=gps.get_position()
        set_props('store-gps', {'data':position})
        # set_props('estado-gps', {'children': f'Última lectura: {ahora.strftime("%H:%M:%S")}'})
    return

# Mostrar la lectura del GPS en un text area de la página
@callback(
    Output('textarea-gps', 'value'),
    Input('store-gps', 'data'),
    prevent_initial_call = True,
)
def data_gps(data):
    ahora = dt.now()
    estado_gps = f'Running. Última lectura: {ahora.strftime("%H:%M:%S")}'
    set_props('estado-gps', {'children': estado_gps})

    return json.dumps(data)

# **********************************
# *** Callbacks del escaneo Wifi ***
# **********************************

# Callback para cambiar el estado de los botones de Start/Stop del escaneo Wifi
@callback(
    Output('wifi-start-button', 'disabled'),
    Output('wifi-stop-button', 'disabled'),
    Input('wifi-start-button', 'n_clicks'),
    Input('wifi-stop-button', 'n_clicks'),
    prevent_initial_call = True
)
def gps_start_stop_button(n_clicks_start, n_clicks_stop):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'wifi-start-button':
        set_props('wifi-start-button', {'style':{'color':'lightGrey', 'cursor':'wait'}})
        set_props('wifi-stop-button', {'style':{'color':'red', 'cursor':'pointer'}})
        return True, False 
    else:
        set_props('wifi-start-button', {'style':{'color':'green', 'cursor':'pointer'}})
        set_props('wifi-stop-button', {'style':{'color':'lightGrey', 'cursor':'not-allowed'}})
        return False, True

# ***********************************
# *** Callback Wifi Scan Interval ***
# ***********************************

# Wifi Interval Start/Stop
@callback(
    Output('interval-scan-wifis', 'disabled'),
    Output('interval-scan-wifis', 'max_intervals'),
    Input('switch-wifi-scan','value'),
    prevent_initial_call = True,
    )
def start_stop_interval(value):
    max_intervals = -1 if value else 0
    if not value:
        set_props('estado-wifi', {'children':f'Escaneado de redes en pause. Último escaneo: {dt.now().strftime("%H:%M:%S")}'})
    print (value)
    return not value, max_intervals

# Wifi Interval Execution
@callback(
    Output('store-wifi', 'data'),
    Output('estado-wifi', 'children'),
    Input('interval-scan-wifis', 'n_intervals'),
    State('store-gps', 'data'),
    prevent_initial_call = True,
    # background=True,
    running=[(Output("interval-scan-wifis", "disabled"), True, False)]
    )
def update_interval_1(interval, gps_data):

    global wifi

    ahora = dt.now()
    print(interval)

    if gps_data:

        ahora = dt.now()
        wifi_scan=wifi.scan_wifi(gps_data)
        wifi.print_wifi_networks()

        estado_wifi = f'Escaneando redes. Último escaneo: {ahora.strftime("%H:%M:%S")}'
        return wifi_scan, estado_wifi

    else:
        estado_wifi = f'Esperando a que el GPS se posicione! {ahora.strftime("%H:%M:%S")}'
        return no_update, estado_wifi

# Mostrar la lectura de las wifis en un text area de la página
@callback(
    Output('textarea-wifi', 'value'),
    Output('textarea-wifi', 'style'),
    Output('wifis-datatable', 'data'),
    Output('store-wifi-historic', 'data'),
    Output('wifis-graph-1', 'figure'),
    Input('store-wifi', 'data'),
    State('store-wifi-historic', 'data'),
    prevent_initial_call = True,
)
def data_wifi(data, data_historic):
    if data:
        wifis_df = pd.DataFrame(data)[
            ['ssid',
             'rssi',
             'gps_latitude',
             'gps_longitude',
             'gps_orthometric_heigth',
             'gps_utc',
             'computer_timestamp',
             'computer_time_local']
            ].sort_values(by=['rssi','ssid'], ascending=[True, True])
        
        wifis_df['rssi_abs'] = wifis_df['rssi'] + 100
        wifis_df.round({'gps_latitude':6, 'gps_longitude':6, 'computer_timestamp':12})
        
        wifis_string = wifis_df.to_string(index=False, justify='center', show_dimensions=True,float_format='{:.6f}'.format)
        
        wifis_datatable = wifis_df.to_dict('records')
        
        style = {'width': '80%', 'height': f'{len(wifis_df)+3}rem'}
        
        # Crea un bar chart de las wifis encontradas

        fig_1 = px.bar(
            wifis_df,
            x='rssi_abs',
            y='ssid',
            color='rssi_abs',
            barmode='overlay',
            orientation='h',
            color_continuous_scale=[
                (0.00, 'red'),
                (0.20, 'orange'),
                (0.40, 'yellow'),
                (0.60, 'green'),
                (0.80, 'cyan'),
                (1.00,'blue')],
            color_continuous_midpoint=50,
            range_color=[0,100],
            hover_name='ssid',
            hover_data=['rssi', 'gps_latitude', 'gps_longitude']
            )
        fig_1.update_traces(
            width=0.5,
            marker_line_width=1.5
            )
        #fig_1.update_xaxes(range=[0, 100])
#        fig_1.update_layout(bargap=0.1)
        fig_1.update_layout(
            xaxis = dict(
                range=[0,100],
                tickmode = 'linear',
                tick0 = 0,
                dtick = 10
            )
        )

        # Adding the new records to the historic data
        if data_historic:
            data_historic_df = pd.DataFrame(data_historic)
            data_historic_df = pd.concat([data_historic_df, wifis_df])
            data_historic_new = data_historic_df.to_dict('records')
        else:
            data_historic_new = wifis_datatable

        """
        for i, network in enumerate(data, start=1):
            wifis_string += f"Red {i}: SSID: {network['ssid']}, BSSID: {network['bssid']}, RSSI: {network['rssi']} dBm, Lat.: {network['gps_latitude']}, Long.: {network['gps_longitude']}\n"
        """

        return wifis_string, style, wifis_datatable, data_historic_new, fig_1

    else:
        wifis_string = "No se encontraron redes WiFi."
        style = {'width': '80%', 'height': '4rem'}
        return wifis_string, style, no_update, no_update, no_update

@callback(
    Output('input-filtro-wifis', 'value'),
    Input('wifis-graph-1', 'clickData'),
    prevent_initial_call = True
)
def graph_1_click (click_data):
    return click_data['points'][0]['label']
    

# *******************************
# *** Callback gráficas wifis ***
# *******************************
@callback(
    Output('graph-4-info', 'children'),
    Input("graph-4", "relayoutData"),
    State('graph-4', 'figure'),
    prevent_initial_call = True
)
def max_zoom(relay, fig_4_state):
    print(relay)
    if fig_4_state and (type(relay)==dict and 'map.zoom' in relay.keys()):
    #print (json.dumps(fig_4_state['layout']['map'], indent=2))
        if relay['map.zoom']>22:
            fig_4 = fig_4_state
            fig_4['layout']['map']['zoom'] = 22
            set_props('graph-4', {'figure':fig_4})
        return f'Relay: {relay}{"\n"}fig-4_state zoom:{fig_4_state['layout']['map']['zoom']}'

    return f'Relay: {relay}'


@callback(
    Output('graph-4', 'figure', allow_duplicate=True),
    Input("btn-graph-4", "n_clicks"),
    State('graph-4', 'figure'),
    prevent_initial_call = True
)
def update_graph_4(n_clicks, fig_4_state):

    if fig_4_state:
        fig_4 = fig_4_state
        fig_4['layout']['map']['zoom'] = fig_4['layout']['map']['zoom'] + 1
        # set_props('graph-4', {'figure':fig_4_state})
        return fig_4
    
    return no_update

# *** Actualizar gráficos al cambiar el store de las wifis escaneadas ***
@callback(
    Output('wifis-graph-2', 'figure'),
    Output('wifis-graph-3', 'figure'),
    Output('graph-4', 'figure'),
    Input('store-wifi-historic', 'data'),
    Input('input-filtro-wifis', 'value'),
    State('wifis-graph-3', 'figure'),
    State('graph-4', 'figure'),
    prevent_initial_call = True,
)
def update_wifis_graph(data, filtro_wifis,fig_3_state, fig_4_state):
    # *** Preparar el dataframe ***
    wifis_df = pd.DataFrame(data)
    wifis_df.dropna(subset=['ssid', 'rssi', 'rssi_abs', 'gps_latitude', 'gps_longitude'])
    wifis_df = wifis_df[wifis_df.ssid != '']
    #wifis_df = wifis_df[wifis_df.rssi > -80]
    min_timestamp = wifis_df['computer_timestamp'].min()
    wifis_df['timestamp_from_start'] = (wifis_df['computer_timestamp'] - min_timestamp).round(1)
    #wifis_df['color'] = 0.5

    if filtro_wifis:
        #wifis_df = wifis_df[wifis_df['ssid'].str.contains(filtro_wifis)]
        wifis_df = wifis_df[wifis_df['ssid'].str.fullmatch(filtro_wifis, case=False, )]
        
    # *** GRAPH 2 ***
    fig_2 = px.line(
        wifis_df,
        x="timestamp_from_start",
        y="rssi_abs",
        color='ssid',
        #line_shape='hv'
        )
    fig_2.update_layout(
        uirevision='hello',
        hovermode="x unified",
        autosize=True,
        margin={"r":0,"t":0,"l":0,"b":0},
        height=700,
        )
    fig_2.update_yaxes(range=[0, 100])
    
    # *** GRAPH 3 ***
    fig_3 = px.scatter_map(
        data_frame=wifis_df,
        lat="gps_latitude",
        lon="gps_longitude",
        size="rssi_abs",
        #size_max=20,
        #text="ssid",
        #color="ssid",
        color="rssi_abs",
        color_continuous_scale=[
            (0.00, 'red'),
            (0.20, 'orange'),
            (0.40, 'yellow'),
            (0.60, 'green'),
            (0.80, 'cyan'),
            (1.00,'blue')],
        color_continuous_midpoint=50,
        range_color=[0,100],
        hover_name='ssid',
        hover_data=['rssi', 'gps_latitude', 'gps_longitude'],
        zoom=19,
        height = 900,
        center={
            "lat":wifis_df.iloc[-1]['gps_latitude'],
            "lon":wifis_df.iloc[-1]['gps_longitude']
            },
        #map_style="carto-voyager",
        )
    
    fig_3.update_layout(
        uirevision='no-update-3',
        autosize=True,
        margin={"r":0,"t":0,"l":0,"b":0},
        hovermode='closest',
        map=dict(
            bearing = 0,
            #bearing = int(dt.now().strftime("%S")),
            pitch = 0,
            #style="carto-voyager",
            #style="open-street-map"
        ),
    )

    # *** GRAPH 4 zoom ***
    if fig_4_state:
        #print (fig_4_state)
        #print (fig_4_state['layout']['map'])
        #print (fig_4_state['layout']['map']['zoom'])
        zoom = fig_4_state['layout']['map']['zoom']
    
    # *** GRAPH 4 ***
    fig_4 = go.Figure()
    fig_4.add_trace(
        go.Scattermap(
            lat = wifis_df.gps_latitude,
            lon = wifis_df.gps_longitude,
            mode='markers',
            marker=go.scattermap.Marker(
                color=wifis_df.rssi_abs,
                size=14
            ),
            text=['Wifi scan'],
            cluster={'maxzoom': 16}
            )
        )

    fig_4.update_layout(
        uirevision='no-update-4',
        hovermode='closest',
        map=dict(
            bearing = 0,
            #bearing = int(dt.now().strftime("%S")),
            center=go.layout.map.Center(
                lat = wifis_df.iloc[-1]['gps_latitude'],
                lon = wifis_df.iloc[-1]['gps_longitude'],
            ),
            pitch = 0,
            zoom = 18,
            style="carto-voyager",
        ),
        height = 900
    )
    
    """
    *** Mapas posibles ***
    "basic"
    "carto-darkmatter"
    "carto-darkmatter-nolabels"
    "carto-positron"
    "carto-positron-nolabels"
    "carto-voyager"
    "carto-voyager-nolabels"
    "dark"
    "light"
    "open-street-map" # Este mapa da problemas con zoom superior a 18
    "outdoors"
    "satellite"
    "satellite-streets"
    "streets"
    "white-bg"
    """
    
    return fig_2, fig_3, fig_4

# **************************************************
# *** Guardar en fichero CSV el escaneo de Wifis ***
# **************************************************
@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-save-csv", "n_clicks"),
    State('store-wifi-historic', 'data'),
    prevent_initial_call=True,
)
def save_wifis_csv(n_clicks, data):
    if data:
        wifis_df = pd.DataFrame(data)
        wifis_df = wifis_df[wifis_df.ssid != '']
        min_timestamp = wifis_df['computer_timestamp'].min()
        wifis_df['timestamp_from_start'] = (wifis_df['computer_timestamp'] - min_timestamp).round(1)
        nombre_fichero = f'wifi_scanner_{dt.now().strftime("%Y_%m_%d_%H_%M_%S")}.csv'
        path_fichero = Path.cwd()/'data'/nombre_fichero
        print(path_fichero)
        return dcc.send_data_frame(wifis_df.to_csv, nombre_fichero)
    else:
        no_update



# **************************************************
# *** Guardar en fichero CSV el escaneo de Wifis ***
# **************************************************
@callback(
    Input("btn-borrar-datos", "n_clicks"),
    prevent_initial_call=True,
)
def delete_wifi_historic(n_clicks):
    set_props('store-wifi-historic', {'data':{}})
    return

# ***********************************************
# *** Guardar POI (Point Of Interest) del GPS ***
# ***********************************************
@callback(
    Output('store-gps-poi', 'data'),
    Output('confirm-popup', 'displayed'),
    Input('btn-save-gps-point', 'n_clicks'),
    State('store-gps', 'data'),
    State('store-gps-poi', 'data'),
    State('input-ref-poi', 'value'),
    prevent_initial_call=True,
)
def save_gps_poi(n_clicks, gps_data, poi_data, poi_ref):
    if gps_data:
        gps_data.pop('line')
        gps_data['ref']=poi_ref

        if not poi_data:
            poi_data = []

        poi_data.append(gps_data)

        print (poi_data)
        return poi_data, True
    else:
        return no_update, False


# ***********************************************
# *** Guardar en fichero Json los POI del GPS ***
# ***********************************************
@callback(
    Output("download-gps-json", "data"),
    Input("btn-save-gps-json", "n_clicks"),
    State('store-gps-poi', 'data'),
    prevent_initial_call=True,
)
def save_pois_geojson(n_clicks, poi_data):
    if poi_data:
        #poi_df = pd.DataFrame(list(poi_data))
        nombre_fichero = f'gps_poi_{dt.now().strftime("%Y_%m_%d_%H_%M_%S")}.json'
        path_fichero = Path.cwd()/'data'/nombre_fichero
        #print(path_fichero)        
        return dict(content=json.dumps(poi_data), filename=nombre_fichero)
    else:
        return no_update

# ************************************************************************
# *** Cargar los datos del fichero json a los geojson correspondientes ***
# ************************************************************************
@callback(
#    Output('confirm-popup', 'displayed'),
    Input("btn-load-geojson", "n_clicks"),
    prevent_initial_call=True,
)
def load_pois_geogson(n_clicks):
    df = pd.read_json('cp94_poi.json', orient='records')
    df['rssi'] = np.random.randint(10,100, size=len(df))

    # *** Primero los puntos    
    df_points = df[df['type']=='Point']
    
    """
    # Crear una geometría a partir de la latitud y longitud    
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)

    # Convertir el DataFrame de pandas en un GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    """

    gdf_points = gpd.GeoDataFrame(df_points, geometry=gpd.points_from_xy(df_points.Longitude, df_points.Latitude), crs="EPSG:4326")
    gdf_points.to_file('./assets/fox_points.geojson', driver="GeoJSON")

    
    # *** Y después los poligonos ***
    
    df_polygons_list = df[df['type']=='Polygon'].groupby('ref').agg(list).reset_index(drop=False)
    df_polygons = df[df['type']=='Polygon'].groupby('ref').first().reset_index(drop=False)
    df_polygons['Latitude'] = df_polygons_list['Latitude']
    df_polygons['Longitude'] = df_polygons_list['Longitude']
    df_polygons['Orthometric Heigth'] = df_polygons_list['Orthometric Heigth']
    
    df_polygons['geometry'] = df_polygons.apply(lambda x: Polygon(np.column_stack((x['Longitude'], x['Latitude']))), axis=1)
    gpf_polygons = gpd.GeoDataFrame(df_polygons, geometry=df_polygons['geometry'], crs='EPSG:4326')
    gpf_polygons.to_file('./assets/fox_polygons.geojson', driver="GeoJSON")
        
    return

# ************
# *** Main ***
# ************

if __name__ == "__main__":
    
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    # *** Iniciar el servidor de Dash ***
    app.run(port= 8050, debug=True)
    exit()

    # *** Obtener los datos de la wifi a la que esta conectado este ordenador ***
    wifi.get_current_wifi_info()
    wifi.print_current_wifi_info()
    
    exit()
