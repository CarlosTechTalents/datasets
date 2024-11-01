import subprocess
import re
import os
import json

from dash import Dash, html, dcc, callback, Output, Input, State, set_props, ctx, callback_context, DiskcacheManager, no_update
from dash.exceptions import PreventUpdate
import dash_daq as daq
import diskcache
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc

import plotly.express as px
from pynput.keyboard import Key, Listener, KeyCode, Controller

import pandas as pd

from time import sleep
from time import time
import datetime
from datetime import datetime as dt
from threading import Thread, Event
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
frecuencia_muestreo = 2
df = pd.DataFrame()
gps = Gps ()
wifi = Wifi()
df_pru = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')


# **************************************************************************************
# *** Preguntar por el puerto al que está conectado el GPS y el interface de la wifi ***
# **************************************************************************************

gps.get_serial_port()
wifi.get_interfaces()
wifi.print_interfaces_list()


# ******************************
# *** Inicialización de Dash ***
# ******************************

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)
app = Dash(__name__, background_callback_manager=background_callback_manager)
#app = Dash(__name__, background_callback_manager=background_callback_manager, external_stylesheets=[dbc.themes.COSMO])
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=external_stylesheets, background_callback_manager=background_callback_manager)

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
        
        titulo_pagina('Wifi scanner'),

        html.Div(
            [
                boton_play_stop('GPS','gps'),
                boton_play_stop('Wifi', 'wifi'),
                html.Div([
                    daq.ToggleSwitch(
                        id = 'switch-wifi-scan',
                        label={'label':'Wifi Scan','style':{'margin-bottom':'10px', 'margin-left': '10px','font-size':'1.5rem', }},
                        labelPosition='Left',
                        color='darkcyan',
                        value=False,
                        style={'margin-left':'10px', 'margin-top':'2px'}
                        )],
                    # style= {'display':'flex','align-content':'center','width':'20%', 'padding':'20px'},
                    className='two-button-container'
                ),
                ],
            className='two-x-two-button-container'
            ),
        
        dcc.Dropdown(['Off', 'On', 'Pause', 'Resume'], 'Off', id='dropdown-gps', style={'width':'120px'}),

        html.Div(
            [
            html.Span('Estado GPS: '),
            html.Span ('Off', id='estado-gps'),
            ],
            style={'margin': '10px 0'}
            ),
        
        dcc.Textarea(
        id='textarea-gps',
        value='No GPS data, yet!',
        style={'width': '80%', 'height': '4rem'},
        ),

        dcc.Dropdown(['Off', 'On', 'Pause', 'Resume'], 'Off', id='dropdown-wifi_scan', style={'width':'120px'}),

        html.Div(
            [
            html.Span('Estado Wifi: '),
            html.Span ('Off', id='estado-wifi'),
            ],
            style={'margin': '10px 0'}
            ),

        dcc.Textarea(
        id='textarea-wifi',
        value='No Wifi data, yet!',
        style={'width': '80%', 'height': '12rem'},
        ),

        dcc.Dropdown(df_pru.country.unique(), 'Canada', id='dropdown-selection', style={'width':'360px'}),
        dcc.Graph(id='graph-content'),

        dcc.Interval(
                id='interval-wifi',
                interval=2000,
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
    ])

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
        return True, False 
    else:
        set_props('gps-start-button', {'style':{'color':'green', 'cursor':'pointer'}})
        set_props('gps-stop-button', {'style':{'color':'lightGrey', 'cursor':'not-allowed'}})
        return False, True

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
    Output('estado-gps', 'children'),
    Input('store-gps', 'data'),
    prevent_initial_call = True,
)
def data_gps(data):
    ahora = dt.now()
    estado_gps = f'Running. Última lectura: {ahora.strftime("%H:%M:%S")}'
    return json.dumps(data), estado_gps

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


# Callback para iniciar o parar la lectura del escaneo Wifi
"""
@callback(
    Input('wifi-start-button','n_clicks'),
    State('store-gps', 'data'),
    background=True,
    cancel=[Input("wifi-stop-button", "n_clicks")],
    prevent_initial_call = True,
    )
def run_wifi(n_clicks, gps_data):

    global frecuencia_muestreo
    
    wifi.get_interfaces()
    wifi.print_interfaces_list()
    
    while not gps_data:
        ahora = dt.now()
        set_props('textarea-wifi',{'value':ahora.strftime("%m/%d/%Y, %H:%M:%S")+'\n'+'Esperando a que el GPS se posicione'})
        print ('Esperando a que el GPS se posicione')
        sleep(1)
    
    position=gps_data

    while True:
        ahora = dt.now()
        #start = time()
        wifi_scan=wifi.scan_wifi(position)
        #print(f'LECTURAS DEL GPS: {gps.counter}')
        gps.print_position()

        # wifi.print_full_wifi_networks()
        wifi.print_wifi_networks()
        # print(wifi.wifi_networks_pd)
        #tiempo_escaneo = time()- start
        #print (f'Duración del escaneo de wifis: {time()- start}sg.')
        #if tiempo_escaneo < frecuencia_muestreo:
        #    sleep(frecuencia_muestreo-tiempo_escaneo)
        set_props('textarea-wifi',{'value':ahora.strftime("%m/%d/%Y, %H:%M:%S")+'\n'+json.dumps(wifi_scan)})
    return
"""

# ***********************************
# *** Callback Wifi Scan Interval ***
# ***********************************

# Wifi Interval Start/Stop
@callback(
    Output('interval-wifi', 'disabled'),
    Input('switch-wifi-scan','value'),
    prevent_initial_call = True,
    )
def start_stop_interval(value):
    print (value)
    return not value

# Wifi Interval Execution
@callback(
    Output('store-wifi', 'data'),
    Output('estado-wifi', 'children'),
    Input('interval-wifi', 'n_intervals'),
    State('store-gps', 'data'),
    prevent_initial_call = True,
    running=[(Output("interval-wifi", "disabled"), True, False)]
    )
def update_interval_1(interval, gps_data):

    global frecuencia_muestreo
    global wifi

    ahora = dt.now()
    print(interval)

    if gps_data:

        ahora = dt.now()
        #start = time()
        wifi_scan=wifi.scan_wifi(gps_data)

        # wifi.print_full_wifi_networks()
        wifi.print_wifi_networks()
        # print(wifi.wifi_networks_pd)
        #tiempo_escaneo = time()- start
        #print (f'Duración del escaneo de wifis: {time()- start}sg.')
        #if tiempo_escaneo < frecuencia_muestreo:
        #    sleep(frecuencia_muestreo-tiempo_escaneo)

        estado_wifi = f'Escaneando redes. Último escaneo: {ahora.strftime("%H:%M:%S")}'
        return wifi_scan, estado_wifi

    else:
        estado_wifi = f'Esperando a que el GPS se posicione! {ahora.strftime("%H:%M:%S")}'
        return no_update, estado_wifi

# Mostrar la lectura de las wifis en un text area de la página
@callback(
    Output('textarea-wifi', 'value'),
    Input('store-wifi', 'data'),
    prevent_initial_call = True,
)
def data_wifi(data):
    return json.dumps(data)

# ************************
# *** Callback gráfica ***
# ************************

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df_pru[df_pru.country==value]    
    return px.line(dff, x='year', y='pop')

# ********************************
# *** Callbacks GPS por Thread *** OLD
# ********************************

@callback(
    Input('dropdown-gps', 'value'),
    prevent_initial_call=True,
)
def dropdown_gps(value):
    global gps
    global stop_gps
    global thread_gps
    global event_gps

    if value == 'On':
        print (f'{value}: Thread is alive {thread_gps.is_alive()}')
        event_gps.set()
        if thread_gps.is_alive():
            print ('El thread ya esta inicializado')
        else:
            print (f'{value}: Inizializando el thread')
            thread_gps.start()

    elif value == 'Pause':
        print (f'{value}: Thread is alive {thread_gps.is_alive()}')
        event_gps.clear()

    elif value == 'Resume':
        print (f'{value}: Thread is alive {thread_gps.is_alive()}')
        event_gps.set()

    else:
        print (f'{value}: Thread is alive {thread_gps.is_alive()}')
        if thread_gps.is_alive():
            event_gps.set()
            stop_gps = True
            print('\nWaiting for the thread...')
            thread_gps.join()
            print (gps.position)
        print ('Bye Bye')
    
    return None

# *********************************
# *** Callbacks Wifi por Thread *** OLD
# *********************************

@callback(
    Input('dropdown-wifi_scan', 'value'),
    prevent_initial_call=True,
)
def dropdown_wifi_scan(value):
    global gps
    global stop_wifi_scan
    global thread_wifi_scan
    global event_wifi_scan

    if value == 'On':
        print (f'{value}: Thread is alive {thread_wifi_scan.is_alive()}')
        event_wifi_scan.set()
        if thread_wifi_scan.is_alive():
            print ('El thread ya esta inicializado')
        else:
            print (f'{value}: Inizializando el thread')
            thread_wifi_scan.start()

    elif value == 'Pause':
        print (f'{value}: Thread is alive {thread_wifi_scan.is_alive()}')
        event_wifi_scan.clear()

    elif value == 'Resume':
        print (f'{value}: Thread is alive {thread_wifi_scan.is_alive()}')
        event_wifi_scan.set()

    else:
        print (f'{value}: Thread is alive {thread_wifi_scan.is_alive()}')
        if thread_wifi_scan.is_alive():
            event_wifi_scan.set()
            stop_wifi_scan = True
            print('\nWaiting for the thread...')
            thread_wifi_scan.join()
            wifi.print_wifi_networks
        print ('Bye Bye')
    
    return None

# ***************
# *** Threads *** OLD
# ***************

# Lectura del GPS en otro hilo
def task_gps_read(event_gps):
    global stop_gps
    global gps

    while not stop_gps:
        event_gps.wait()
        gps.get_position()

# Escaneo de redes wifi disponibles en otro hilo
def task_wifi_scan(event_wifi_scan):
    global stop_gps
    global frecuencia_muestreo
    global gps
    global stop_gps
    global stop_wifi_scan
    
    wifi.get_interfaces()
    wifi.print_interfaces_list()

    while not gps.position:
        print ('Esperando a que el GPS se posicione')
        sleep(1)

    while not stop_wifi_scan:
        event_wifi_scan.wait()
        start = time()
        wifi.scan_wifi(gps.position)
        print(f'LECTURAS DEL GPS: {gps.counter}')
        gps.print_position()

        # wifi.print_full_wifi_networks()
        wifi.print_wifi_networks()
        # print(wifi.wifi_networks_pd)
        tiempo_escaneo = time()- start
        print (f'Duración del escaneo de wifis: {time()- start}sg.')
        if tiempo_escaneo < frecuencia_muestreo:
            sleep(frecuencia_muestreo-tiempo_escaneo)

# *******************************
# *** Interrupción de teclado *** OLD
# *******************************
"""
def on_press(key):
    global n_keys, activo
    n_keys += 1
    if key == Key.up:
        activo = True
        print(f'Activo = {activo}')

    if key == Key.down:
        activo = False
        print(f'Activo = {activo}')

    if key == Key.space:
        # Clear Screen
        os.system('cls' if os.name == 'nt' else 'clear')
"""     

# ************
# *** Main ***
# ************

if __name__ == "__main__":
    
    # os.system('cls' if os.name == 'nt' else 'clear')

    # *** Thread y evento del GPS *** OLD
    #event_gps = Event()
    #thread_gps = Thread(target=task_gps_read, args=(event_gps, ))
    
    # *** Thread y evento del escaneo Wifi *** OLD
    event_wifi_scan = Event()
    thread_wifi_scan = Thread(target=task_wifi_scan, args=(event_wifi_scan, ))
    
    # *** Iniciar el servidor de Dash ***
    app.run(port= 8050, debug=True)
    exit()

    # *** Interrupción de teclado *** OLD
    # n_keys = 0
    # activo = False

    #keyboard_listener = Listener(on_press=on_press)
    #keyboard_listener.start()
    
    # *** Preguntar por el puerto al que está conectado el GPS ***
    #gps.get_serial_port()


    # *** Obtener el/los interfaces de red wifi ***
    wifi.get_interfaces()
    wifi.print_interfaces_list()

    # *** Obtener los datos de la wifi a la que esta conectado este ordenador ***
    wifi.get_current_wifi_info()
    wifi.print_current_wifi_info()
    
    # *** Excepción de interrupción de teclado *** PRU
    """
    except KeyboardInterrupt:

        # Finalizar el hilo de lectura del GPS
        stop_gps = True
        print('Waiting for the thread...')
        #thread_gps.join()
        #thread_wifi_scan.join()
        #print (gps.position)
        print ('Bye Bye')
        exit()
        
    except:
        print('Saliendo')
        exit()
    """
    
    exit()
