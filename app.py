import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import plotly.graph_objects as go
import urllib.request
from dash.dependencies import Input, Output

external_stylesheets = [{
    'href': 'https://fonts.googleapis.com/css?family=Raleway:400,700,800&display=swap',
    'rel': 'stylesheet',
}]

req = urllib.request.Request('https://raw.githubusercontent.com/empet/Datasets/master/car.obj')

response = urllib.request.urlopen(req)
obj_data = response.read().decode('utf-8')

def obj_data_to_mesh3d(odata):
    # odata is the string read from an obj file
    vertices = []
    faces = []
    lines = odata.splitlines()

    for line in lines:
        slist = line.split()
        if slist:
            if slist[0] == 'v':
                vertex = np.array(slist[1:], dtype=float)
                vertices.append(vertex)
            elif slist[0] == 'f':
                face = []
                for k in range(1, len(slist)):
                    face.append([int(s) for s in slist[k].replace('//', '/').split('/')])
                if len(face) > 3:  # triangulate the n-polyonal face, n>3
                    faces.extend(
                        [[face[0][0] - 1, face[k][0] - 1, face[k + 1][0] - 1] for k in range(1, len(face) - 1)])
                else:
                    faces.append([face[j][0] - 1 for j in range(len(face))])
            else:
                pass

    return np.array(vertices), np.array(faces)


vertices, faces = obj_data_to_mesh3d(obj_data)

x, y, z = vertices[:, :3].T
I, J, K = faces.T

app = dash.Dash()
app.title = 'Car Colour Selector'
app.layout = html.Div([
    html.Div(
        className = 'header',
        children=[
            html.H1(
                'CADA Car Colour Selector'
            )
        ]
    ),

    
    dcc.Graph(
        id='mygraph'
    ),

    html.Div(
        title='select style for molecule representation',
        className="app-controls-block",
        id='car-colour',
        children=[
            html.P(
                'Colour Palette',
                style={
                    'font-weight': 'bold',
                    'margin-bottom': '10px',
                }
            ),
            dcc.Dropdown(
                id='dropdown-colours',
                options=[
                    {'label': 'Red', 'value': 'red'},
                    {'label': 'Green', 'value': 'green'},
                    {'label': 'Blue', 'value': 'blue'},
                ],
                value='red',
            )
        ],
    )
])


@app.callback(
    Output('mygraph', 'figure'),
    [Input('dropdown-colours', 'value')])
def update_graph(dropdown_val):
    mesh = go.Mesh3d(
        x=-x,
        y=-y,
        z=z,
        vertexcolor=vertices[:, 3:],  # the color codes must be triplets of floats  in [0,1]!!
        i=I,
        j=J,
        k=K,
        name='',
        showscale=False)

    mesh.update(lighting=dict(ambient=0.18,
                              diffuse=1,
                              fresnel=.1,
                              specular=1,
                              roughness=.1),

                lightposition=dict(x=100,
                                   y=200,
                                   z=150))

    pl_mygray = [[0.0, 'rgb(255, 0, 0)'],
                 [0.25, 'rgb(255, 0, 0)'],
                 [0.5, 'rgb(255, 0, 0)'],
                 [0.75, 'rgb(255, 0, 0)'],
                 [1.0, 'rgb(255, 0, 0)'],
                 ]

    if dropdown_val == 'red':
        pl_mygray = [[0.0, 'rgb(255, 0, 0)'],
                     [0.25, 'rgb(255, 0, 0)'],
                     [0.5, 'rgb(255, 0, 0)'],
                     [0.75, 'rgb(255, 0, 0)'],
                     [1.0, 'rgb(255, 0, 0)'],
                     ]
    if dropdown_val == 'green':
        pl_mygray = [[0.0, 'rgb(0, 255, 0)'],
                     [0.25, 'rgb(0, 255, 0)'],
                     [0.5, 'rgb(0, 255, 0)'],
                     [0.75, 'rgb(0, 255, 0)'],
                     [1.0, 'rgb(0, 255, 0)'],
                     ]

    if dropdown_val == 'blue':
        pl_mygray = [[0.0, 'rgb(0, 0, 255)'],
                     [0.25, 'rgb(0, 0, 255)'],
                     [0.5, 'rgb(0, 0, 255)'],
                     [0.75, 'rgb(0, 0, 255)'],
                     [1.0, 'rgb(0, 0, 255)'],
                     ]

    mesh.update(intensity=z, colorscale=pl_mygray)
    mesh.pop('vertexcolor')

    layout = go.Layout(title='',
                       font=dict(size=14, color='black'),
                       width=800,
                       height=600,
                       scene=dict(xaxis=dict(visible=False),
                                  yaxis=dict(visible=False),
                                  zaxis=dict(visible=False),
                                  aspectratio=dict(x=1.5,
                                                   y=0.9,
                                                   z=0.5
                                                   ),
                                  camera=dict(eye=dict(x=1, y=1., z=0.5)),
                                  ),
                       margin=dict(t=175))

    return {'data': [mesh], 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
