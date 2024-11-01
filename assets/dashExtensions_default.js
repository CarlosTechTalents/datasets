window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {
            layer.bindTooltip(`${feature.properties.name} (${feature.properties.rssi})`)
        },
        function1: function(feature, latlng, context) {
            const {
                min,
                max,
                colorscale,
                circleOptions,
                colorProp
            } = context.hideout;
            const csc = chroma.scale(colorscale).domain([min, max]); // chroma lib to construct colorscale
            circleOptions.fillColor = csc(feature.properties[colorProp]); // set color based on color prop
            return L.circleMarker(latlng, circleOptions); // render a simple circle marker
        },
        function2: function(feature, context) {
            const {
                selected
            } = context.hideout;
            if (selected.includes(feature.properties.name)) {
                return {
                    fillColor: 'red',
                    color: 'grey'
                }
            }
            return {
                fillColor: 'grey',
                color: 'grey'
            }
        }
    }
});