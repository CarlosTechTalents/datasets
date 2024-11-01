import dash_leaflet as dl
from dash_extensions.javascript import assign
from dash import Dash

colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # rainbow
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # js lib used for colors
# Create a colorbar.
vmin = 0
vmax = 10000000
colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=vmin, max=vmax, unit='population')
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
on_each_feature = assign("""function(feature, layer, context){
    layer.bindTooltip(`${feature.properties.name} (${feature.properties.pop_max})`)
}""")
point_to_layer = assign("""function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop
    return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
}""")
# Create geojson.
geojson = dl.GeoJSON(url="/assets/fox_lane_pois.json",
                     zoomToBounds=True,  # when true, zooms to bounds when data changes
                     pointToLayer=point_to_layer,  # how to draw points
                     onEachFeature=on_each_feature,  # add (custom) tooltip
                     hideout=dict(colorProp='pop_max', circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                                  min=vmin, max=vmax, colorscale=colorscale))
# Create the app.
app = Dash(external_scripts=[chroma], prevent_initial_callbacks=True)
app.layout = dl.Map([
    dl.TileLayer(), geojson, colorbar
], style={'height': '50vh'}, center=[56, 10], zoom=6)

if __name__ == '__main__':
    app.run_server()