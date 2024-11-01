import dash
from dash import html, Input, Output
import dash_ag_grid as dag

app = dash.Dash(__name__)

rowData = [
    {"make": "Toyota", "model": "Celica", "price": 35000},
    {"make": "Ford", "model": "Mondeo", "price": 32000},
    {"make": "Porsche", "model": "Boxster", "price": 72000},
]

columnDefs = [
    {"headerName": "Make", "field": "make", "sortable": True},
    {"headerName": "Model", "field": "model"},
    {"headerName": "Price", "field": "price"},
]

app.layout = html.Div(
    [
        dag.AgGrid(
            id="virtual-row-data-example",
            rowData=rowData,
            columnDefs=columnDefs,
            defaultColDef={"sortable": True, "filter": True},
            columnSize="sizeToFit",
        ),
        html.Div(id="div-virtual-row-data-example"),
    ]
)


@app.callback(
    Output("div-virtual-row-data-example", "children"),
    Input("virtual-row-data-example", "virtualRowData"),
)
def get_virtual_data(virtual):
    return str(virtual)


if __name__ == "__main__":
    app.run(debug=True)
