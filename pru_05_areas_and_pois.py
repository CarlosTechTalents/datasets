import dash_leaflet as dl
from dash import Dash, Output, Input, State
from dash_extensions.javascript import assign

# Color selected state(s) red.
style_handle = assign("""function(feature, context){
    const {selected} = context.hideout;
    if(selected.includes(feature.properties.name)){
        return {fillColor: 'red', color: 'grey'}
    }
    return {fillColor: 'grey', color: 'grey'}
}""")
# Create small example app.
app = Dash()
app.layout = dl.Map([
    dl.TileLayer(),
    dl.GeoJSON(url="/assets/fox_lane_areas_and_pois.json", zoomToBounds=True, id="geojson",
               hideout=dict(selected=[]), style=style_handle)
], style={'height': '50vh'}, center=[56, 10], zoom=6)

@app.callback(
    Output("geojson", "hideout"),
    Input("geojson", "n_clicks"),
    State("geojson", "clickData"),
    State("geojson", "hideout"),
    prevent_initial_call=True)
def toggle_select(_, feature, hideout):
    selected = hideout["selected"]
    name = feature["properties"]["name"]
    if name in selected:
        selected.remove(name)
    else:
        selected.append(name)
    return hideout

if __name__ == '__main__':
    app.run_server()