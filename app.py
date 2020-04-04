import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import plotly.graph_objects as go
import urllib.request
from dash.dependencies import Input, Output, State

external_stylesheets = [{
    'href': 'https://fonts.googleapis.com/css?family=Montserrat:400,500,700,800,900&display=swap',
    'rel': 'stylesheet',
}]

req = urllib.request.Request('https://raw.githubusercontent.com/empet/Datasets/master/car.obj')
response = urllib.request.urlopen(req)
vantage = response.read().decode('utf-8')

with open('lambo.obj', 'r') as obj:
    lambo = obj.read()
with open('audi.obj', 'r') as obj:
    audi = obj.read()


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


vantage_vertices, vantage_faces = obj_data_to_mesh3d(vantage)
lambo_vertices, lambo_faces = obj_data_to_mesh3d(lambo)
audi_vertices, audi_faces = obj_data_to_mesh3d(audi)

app = dash.Dash()
app.title = 'Car Colour Selector'
app.layout = html.Div([
    html.Header(
        className='header',
        children=[
            html.H1(
                className='header-h1',
                children='CADA Car Colour Selector'
            ),

            html.H2(
                className='header-h2',
                children='Designed by: Harsohail, Ryan, Gary, Sean'
            )
        ]
    ),

    html.Div(
        className='customize-car-title',
        children=[
            html.P(
                'Customize Your Car'
            )
        ]
    ),

    html.Nav(
        className='camera-nav',
        children=[
            html.P(
                'Camera View:'
            ),

            dcc.Dropdown(
                id='dropdown-view',
                options=[
                    {'label': 'Exterior', 'value': 'exterior'},
                    {'label': 'Interior', 'value': 'interior'},
                ],
                value='exterior',
            )
        ]
    ),

    html.Nav(
        className='customization-nav',
        children=[

            html.P(
                'Model:'
            ),

            dcc.Dropdown(
                id='dropdown-model',
                options=[
                    {'label': 'Lambo', 'value': 'lambo'},
                    {'label': 'Audi', 'value': 'audi'},
                    {'label': 'Vantage', 'value': 'vantage'}
                ],
                value='lambo',
            ),

            html.P(
                'Exterior Colour:'
            ),

            dcc.Dropdown(
                id='dropdown-colours',
                options=[
                    {'label': 'Red', 'value': 'red'},
                    {'label': 'Green', 'value': 'green'},
                    {'label': 'Blue', 'value': 'blue'},
                ],
                value='red',
            ),

            html.P(
                'Interior Colour'
            ),

            dcc.Dropdown(
                id='dropdown-colours-interior',
                options=[
                    {'label': 'Red', 'value': 'red'},
                    {'label': 'Green', 'value': 'green'},
                    {'label': 'Blue', 'value': 'blue'},
                ],
                value='red',
            ),
            # #debug code
            #     dcc.Dropdown(
            #         id='lol',
            #         options=[
            #             {'label': 'Red', 'value': 'red'},
            #             {'label': 'Green', 'value': 'green'},
            #             {'label': 'Blue', 'value': 'blue'},
            #         ],
            #         value='red',
            #     )
        ]
    ),

    dcc.Loading(dcc.Graph(
        id='mygraph'
    ))
])


# # debug code to get camera position
# @app.callback(
#     Output('lol', 'value'),
#     [Input('dropdown-colours-interior', 'value'),
#      Input('mygraph', 'figure')])
# def asdf(button_val, graph):
#     # if graph:
#     print(graph['layout']['scene'])
#     return 'red'


@app.callback(
    Output('mygraph', 'figure'),
    [Input('dropdown-colours', 'value'),
     Input('dropdown-view', 'value'),
     Input('dropdown-model', 'value'),
     Input('dropdown-colours-interior', 'value')])
def update_graph(dropdown_exterior_colour, camera_val, model_val, dropdown_interior_colour):
    if model_val == 'lambo':
        vertices = lambo_vertices
        faces = lambo_faces
    elif model_val == 'vantage':
        vertices = vantage_vertices
        faces = vantage_faces
    else:
        vertices = audi_vertices
        faces = audi_faces

    x, y, z = vertices[:, :3].T
    I, J, K = faces.T

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

    pl_mygray = [[0.0, 'rgb(255, 255, 255)'],
                 [0.25, 'rgb(255, 0, 0)'],
                 [0.5, 'rgb(255, 255, 255)'],
                 [0.75, 'rgb(255, 0, 0)'],
                 [1.0, 'rgb(255, 255, 255)'],
                 ]
    if camera_val == 'exterior':
        colour = dropdown_exterior_colour
    else:
        colour = dropdown_interior_colour

    if colour == 'red':
        pl_mygray = [[0.0, 'rgb(255, 0, 0)'],
                     [0.25, 'rgb(255, 0, 0)'],
                     [0.5, 'rgb(255, 0, 0)'],
                     [0.75, 'rgb(255, 0, 0)'],
                     [1.0, 'rgb(255, 0, 0)'],
                     ]
    if colour == 'green':
        pl_mygray = [[0.0, 'rgb(0, 255, 0)'],
                     [0.25, 'rgb(0, 255, 0)'],
                     [0.5, 'rgb(0, 255, 0)'],
                     [0.75, 'rgb(0, 255, 0)'],
                     [1.0, 'rgb(0, 255, 0)'],
                     ]

    if colour == 'blue':
        pl_mygray = [[0.0, 'rgb(0, 0, 255)'],
                     [0.25, 'rgb(0, 0, 255)'],
                     [0.5, 'rgb(0, 0, 255)'],
                     [0.75, 'rgb(0, 0, 255)'],
                     [1.0, 'rgb(0, 0, 255)'],
                     ]

    mesh.update(intensity=z, colorscale=pl_mygray)
    mesh.pop('vertexcolor')

    if model_val == 'vantage':
        if camera_val == 'exterior':
            scene = dict(xaxis=dict(visible=False),
                         yaxis=dict(visible=False),
                         zaxis=dict(visible=False),
                         aspectratio=dict(x=1.5,
                                          y=0.9,
                                          z=0.5
                                          ),
                         camera=dict(eye=dict(x=1, y=1, z=0.5)),
                         )
        else:
            scene = {'aspectratio': {'x': 1.5, 'y': 0.9, 'z': 0.5},
                     'camera': {'up': {'x': 0, 'y': 0, 'z': 1}, 'center': {'x': 0, 'y': 0, 'z': 0},
                                'eye': {'x': 0.03665043677438262, 'y': -0.2970576578847514, 'z': 0.040847084541866675},
                                'projection': {'type': 'perspective'}}, 'xaxis': {'visible': False, 'type': 'linear'},
                     'yaxis': {'visible': False, 'type': 'linear'}, 'zaxis': {'visible': False, 'type': 'linear'}}

    elif model_val == 'lambo':
        if camera_val == 'exterior':
            scene = {'aspectratio': {'x': 0.9, 'y': 0.5, 'z': 2},
                     'camera': {'up': {'x': 0.14442241321160956, 'y': -0.989509736925293, 'z': -0.0035562750418050987},
                                'center': {'x': -7.703719777548943e-34, 'y': 2.465190328815662e-32, 'z': 0},
                                'eye': {'x': -1.564680987397105, 'y': -0.23286301255893346, 'z': 1.2499635540987735},
                                'projection': {'type': 'perspective'}}, 'xaxis': {'type': 'linear', 'visible': False},
                     'yaxis': {'type': 'linear', 'visible': False}, 'zaxis': {'type': 'linear', 'visible': False},
                     'dragmode': 'orbit'}
        else:
            scene = {'aspectratio': {'x': 0.9, 'y': 0.5, 'z': 2},
                     'camera': {'up': {'x': -0.014483746767562214, 'y': -0.9956270315878076, 'z': 0.09228778386777226},
                                'center': {'x': 4.440892098500626e-16, 'y': 3.3306690738754696e-16,
                                           'z': 2.220446049250313e-16},
                                'eye': {'x': 0.2536461540801174, 'y': 0.005561370600775682, 'z': 0.09980516576570062},
                                'projection': {'type': 'perspective'}}, 'dragmode': 'orbit',
                     'xaxis': {'type': 'linear', 'visible': False}, 'yaxis': {'type': 'linear', 'visible': False},
                     'zaxis': {'type': 'linear', 'visible': False}}
    else:
        if camera_val == 'exterior':
            scene = {'aspectratio': {'x': 0.9, 'y': 0.5, 'z': 1.75},
                     'camera': {'up': {'x': 0.09007644334960926, 'y': -0.9846864125430299, 'z': -0.1492611915623835},
                                'center': {'x': -5.421010862427522e-20, 'y': 2.7755575615628914e-17,
                                           'z': -4.440892098500626e-16},
                                'eye': {'x': -1.3340932844006177, 'y': -0.3311417986381644, 'z': 1.3794640752455618},
                                'projection': {'type': 'perspective'}}, 'dragmode': 'orbit',
                     'xaxis': {'type': 'linear', 'visible': False}, 'yaxis': {'type': 'linear', 'visible': False},
                     'zaxis': {'type': 'linear', 'visible': False}}
        else:
            scene = {'aspectratio': {'x': 0.9, 'y': 0.5, 'z': 1.75},
                     'camera': {'up': {'x': -0.09831774394368466, 'y': -0.9864960043387793, 'z': -0.13099333818728312},
                                'center': {'x': -5.421010862427522e-20, 'y': 2.7755575615628914e-17,
                                           'z': -4.440892098500626e-16},
                                'eye': {'x': 0.26492391480148875, 'y': -0.04032404615404929, 'z': 0.10483578004628624},
                                'projection': {'type': 'perspective'}}, 'dragmode': 'orbit',
                     'xaxis': {'type': 'linear', 'visible': False}, 'yaxis': {'type': 'linear', 'visible': False},
                     'zaxis': {'type': 'linear', 'visible': False}}

    layout = go.Layout(title='',
                       font=dict(size=14, color='black'),
                       width=800,
                       height=600,
                       scene=scene,
                       margin=dict(t=175))

    return {'data': [mesh], 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
