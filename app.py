import os
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.figure_factory as ff

from Data import *

app = dash.Dash(__name__)
# server = app.server
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

df = pd.read_csv("data/spc_data.csv")
params = list(df)


def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {
            'height': '100px',
            'width': '100%',
        }
    return html.Div(
        id=id,
        className='row metric-row',
        style=style,
        children=[
            html.Div(
                id=col1['id'],
                style={},
                className='one column',
                children=col1['children']
            ),
            html.Div(
                id=col2['id'],
                style={},
                className='one column',
                children=col2['children']
            ),
            html.Div(
                id=col3['id'],
                style={
                    'height': '100%',
                },
                className='five columns',
                children=col3['children']
            ),
            html.Div(
                id=col4['id'],
                style={},
                className='one column',
                children=col4['children']
            ),
            html.Div(
                id=col5['id'],
                style={},
                className='three columns',
                children=col5['children']
            ),
            html.Div(
                id=col6['id'],
                style={},
                className='one column',
                children=col6['children']
            )
        ]
    )


def create_callback(retfunc):
    """
    pass *input_value to retfunc

    creates a callback function
    """

    def callback(*input_values):
        if input_values is not None and input_values != 'None':
            try:
                retval = retfunc(*input_values)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('Callback Exception:', e, exc_type, fname, exc_tb.tb_lineno)
                print('parameters:', *input_values)
            return retval
        else:
            return []

    return callback


def generate_graph(interval, value, curr_fig):
    dff, count, mean, ucl, lcl, min, max = get_graph_stats(df, value)

    if curr_fig['data'][0]['name'] != value:
        curr_fig['data'][0]['y'] = []
        curr_fig['data'][0]['x'] = []

    len_figure=len(curr_fig['data'][0]['x'])
    # print('length of figure: ', len_figure)

    layout = dict(title='Individual measurements', showlegend=True, xaxis={
        'zeroline': False,
        'title': 'Batch_Num',
        'showline': False
    }, yaxis={
        'title': value,
        'autorange': True
    }, annotations=[
        {'x': len_figure+2, 'y': lcl, 'xref': 'x', 'yref': 'y', 'text': 'LCL:'+str(round(lcl, 2)), 'showarrow': True},
        {'x': len_figure+2, 'y': ucl, 'xref': 'x', 'yref': 'y', 'text': 'UCL: '+str(round(ucl,2)), 'showarrow': True},
    ], shapes=[
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': ucl,
            'x1': len_figure + 2,
            'y1': ucl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': mean,
            'x1': len_figure + 2,
            'y1': mean,
            'line': {
                'color': 'rgb(255,127,80)',
                'width': 2
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': lcl,
            'x1': len_figure + 2,
            'y1': lcl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        }
    ])

    x_array = dff['Batch'].tolist()
    y_array = dff[value].tolist()

    curr_fig['data'][0]['name'] = value

    if len(curr_fig['data'][0]['x']) < count:
        curr_fig['data'][0]['x'].append(x_array[len(curr_fig['data'][0]['x'])])
        curr_fig['data'][0]['y'].append(y_array[len(curr_fig['data'][0]['y'])])
        curr_fig['layout'] = layout

    return curr_fig


def generate_metric_list():
    # 1 build header
    metric_header_div = [
        generate_metric_row(
            'metric_header',
            {
                'height': '50px'
            },
            {
                'id': "m_header_1",
                'children': html.Div("Parameter")
            },
            {
                'id': "m_header_2",
                'children': html.Div("Count")
            },
            {
                'id': "m_header_3",
                'children': html.Div("Sparkline")
            },
            {
                'id': "m_header_4",
                'children': html.Div("%OOC")
            },
            {
                'id': "m_header_5",
                'children': html.Div("%OOC")
            },
            {
                'id': "m_header_6",
                'children': html.Div("Pass / Fail")
            }),
    ]

    input_list = []
    children = []
    for index in range(1, len(params)):
        item = params[index]
        input_list.append(Input(item, 'n_clicks'))

        sparkline_graph_id = item + '_sparkline_graph_' + str(index)

        children.append(
            generate_metric_row(
                item, None,
                {
                    'id': item + "_" + str(index),
                    'children': item
                },
                {
                    'id': item + '_count_' + str(index),
                    'children': 0
                },
                {
                    'id': item + '_sparkline_' + str(index),
                    'children': dcc.Graph(
                        id=sparkline_graph_id,
                        style={
                            'width': '100%',
                            'height': '95%',
                            'border': '1px solid red'  # todo delete this
                        },
                        config={
                            'staticPlot': False,
                            'editable': False,
                            'displayModeBar': False
                        },
                        figure=go.Figure({
                            'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': item, }],
                            'layout': {
                                'margin': dict(
                                    l=0, r=0, t=4, b=4, pad=0
                                )
                            }
                        }))
                },
                {
                    'id': item + '_OCCnumber_' + str(index),
                    'children': 0
                },
                {
                    'id': item + '_OCCgraph_' + str(index),
                    'children': html.Div('aaa')
                },
                {
                    'id': item + '_pf_' + str(index),
                    'children': html.Div('aaa')
                }
            )
        )

        @app.callback(
            output=Output(sparkline_graph_id, 'figure'),
            inputs=[
                Input('interval-component', 'n_intervals')
            ],
            state=[
                State(sparkline_graph_id, 'figure')
            ])
        def generate_sparkline_graph(interval, curr_graph):
            param = curr_graph['data'][0]['name']
            dff = df[['Batch', param]][:]
            x_array = dff['Batch'].tolist()
            y_array = dff[param].tolist()
            count = len(x_array)

            if len(curr_graph['data'][0]['x']) < count:
                curr_graph['data'][0]['x'].append(x_array[len(curr_graph['data'][0]['x'])])
                curr_graph['data'][0]['y'].append(y_array[len(curr_graph['data'][0]['y'])])

            return curr_graph

    metric_header_div.append(
        html.Div(
            style={
                'height': '100%',
                'overflow': 'scroll'
            },
            children=children
        )
    )

    def update_graph(*inputs):
        click_state = inputs[-1]
        interval = inputs[-3]
        figure = inputs[-2]

        if len(click_state) == 0:
            return generate_graph(interval, params[8], figure), inputs[:-3]
        for j in range(len(inputs) - 3):
            if click_state[j] != inputs[j]:
                return generate_graph(interval, params[j + 1], figure), inputs[:-3]

        curr_fig = figure['data'][0]['name']
        return generate_graph(interval, curr_fig, figure), inputs[:-3]

    input_list.append(Input('interval-component', 'n_intervals'))
    # app referencing the dash app object
    app.callback(output=[Output('control-chart-live', 'figure'), Output('click_state', 'data')],
                 inputs=input_list,
                 state=[State('control-chart-live', 'figure'), State('click_state', 'data')]
                 )(create_callback(update_graph))

    return html.Div(
        id='metric_list',
        className='row',
        style={
            'height': '100%'
        },
        children=metric_header_div
    )


def generate_tree_map():
    return html.Div(
        children=[
            html.Label(
                id='test_label',
                children="0"
            ),
            dcc.Store(
                id='click_state',
                data=[]
            ),
        ])


def build_top_panel():
    return html.Div(
        id='top-section-container',
        className='row',
        style={
            'height': '45vh'
        },
        children=[
            # Metrics summary
            html.Div(
                id='metric-summary-session',
                className='six columns',
                style={'height': '100%'},
                children=[
                    generate_section_banner('Process Control Metrics Summary'),
                    html.Div(
                        id='metric_div',
                        style={
                            'height': '100%',
                            'width': '100%',
                        },
                        children=generate_metric_list()
                    )
                ]
            ),
            # Tree Map
            html.Div(
                id='treemap-session',
                className='six columns',
                children=[
                    generate_section_banner('% OOC per Parameter'),
                    generate_tree_map()
                ]
            )
        ]
    )


def build_chart_panel():
    return html.Div(
        id='control-chart-container',
        className='twelve columns',
        children=[
            generate_section_banner('Live SPC Chart'),

            dcc.Dropdown(
                # Select for live-stream figure display
                id='dropdown-select',
                options=list({'label': i, 'value': i} for i in params),
                value="Para4"
            ),

            dcc.Interval(
                id='interval-component',
                interval=2 * 1000,  # in milliseconds
                n_intervals=0
            ),

            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': 'Para4'}]
                }
                )
            ),

            dcc.Graph(
                id="moving-range",
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers'}]
                }
                )
            )
        ])


def generate_section_banner(title):
    return html.Div(
        className="section-banner",
        children=title
    )


app.layout = html.Div(
    children=[
        # Banner
        html.Div(
            id='banner',
            className="banner", children=[
                html.H5('Manufacturing SPC Dashboard - Process Control and Exception Reporting'),
                html.Img(
                    src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
                )
            ]
        ),

        # Tabs
        html.Div(
            id='tab-bar',
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="tab-2",
                    children=[
                        dcc.Tab(label='What is SPC?', value='tab-1'),
                        dcc.Tab(label='Control Chart Dashboard 1', value='tab-2'),
                        dcc.Tab(label='Control Chart Dashboard 2', value='tab-3'),
                    ]
                )
            ]
        ),
        # Main app
        html.Div(
            id='tabs-content',
            className='container scalable',
            children=[
                build_top_panel(),
                build_chart_panel(),
                # Control chart
            ]
        )
    ]
)


# Live SPC updates by Batch_Num
# @app.callback(
#     Output('control-chart-live', 'figure'),
#     [Input('interval-component', 'n_intervals'),
#      Input('dropdown-select', 'value')],
#     state=[State('control-chart-live', 'figure')]
# )
def update_chart(interval, value, curr_fig):
    dff, count, mean, ucl, lcl, min, max = get_graph_stats(df, value)

    if curr_fig['data'][0]['name'] != value:
        curr_fig['data'][0]['y'] = []
        curr_fig['data'][0]['x'] = []

    layout = dict(title='Individual measurements', showlegend=True, xaxis={
        'zeroline': False,
        'title': 'Batch_Num',
        'showline': False
    }, yaxis={
        'title': value,
        'autorange': True
    }, annotations=[
        {'x': 2, 'y': lcl, 'xref': 'x', 'yref': 'y', 'text': 'LCL', 'showarrow': True},
    ], shapes=[
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': ucl,
            'x1': interval + 2,
            'y1': ucl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': mean,
            'x1': interval + 2,
            'y1': mean,
            'line': {
                'color': 'rgb(255,127,80)',
                'width': 2
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': lcl,
            'x1': interval + 2,
            'y1': lcl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        }
    ])

    x_array = dff['Batch'].tolist()
    y_array = dff[value].tolist()

    curr_fig['data'][0]['name'] = value

    if len(curr_fig['data'][0]['x']) < count:
        curr_fig['data'][0]['x'].append(x_array[len(curr_fig['data'][0]['x'])])
        curr_fig['data'][0]['y'].append(y_array[len(curr_fig['data'][0]['y'])])
        curr_fig['layout'] = layout

    return curr_fig


# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)
