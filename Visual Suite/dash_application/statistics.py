import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def create_stats_dash(flask_app):
    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/statistics/",
        external_stylesheets=[dbc.themes.DARKLY]
    )

    @dash_app.callback(
        Output('column-dropdown', 'options'),
        Input('column-dropdown', 'value'),
        State('stored-data', 'data')
    )
    def update_dropdown_options(selected_column, data):
        if data is None:
            return []
        df = pd.read_json(data, orient='split')
        numeric_columns = df.select_dtypes(include=['number'])
        column_names = numeric_columns.columns.tolist()
        dropdown_options = [{'label': col, 'value': col} for col in column_names]
        return dropdown_options

    @dash_app.callback(
        [Output('column-stats', 'children'),
         Output('column-plot', 'children')],
        Input('column-dropdown', 'value'),
        State('stored-data', 'data')
    )
    def update_content(selected_column, data):
        if data is None:
            return dcc.Markdown("No data available."), ""
        
        df = pd.read_json(data, orient='split')
        stats_content = dcc.Markdown("No column selected.")
        plot_content = ""

        if selected_column:
            # Compute main statistics
            stats = df[selected_column].describe()

            # Format each statistic into a string with a newline between them
            stats_str = "\n".join([f"{stat_name}: {stat_value}\n" for stat_name, stat_value in stats.items()])

            # Remove the trailing newline character
            stats_str = stats_str.rstrip("\n")

            # Compute outliers
            Q1 = df[selected_column].quantile(0.25)
            Q3 = df[selected_column].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[selected_column] < (Q1 - 1.5 * IQR)) | (df[selected_column] > (Q3 + 1.5 * IQR))][selected_column]
            unique_outliers = outliers.unique()

            # Unique values
            unique_values = df[selected_column].nunique()

            # Create a plot for the selected column
            fig = px.histogram(df, x=selected_column)
            fig.update_layout(
                plot_bgcolor='#333333',
                paper_bgcolor='#333333',
                font=dict(color='white')
            )

            # Format the outliers and unique values
            outliers_str = "\n".join([f"{outlier}" for outlier in unique_outliers])
            unique_values_str = f"Unique Values: {unique_values}"

            # Concatenate all strings
            stats_content = dcc.Markdown(f"\n{stats_str}\n\n**Outliers:**\n{outliers_str}\n\n{unique_values_str}")
            plot_content = dcc.Graph(figure=fig, style={'width': '100%', 'height': '100%'})  # Adjusted graph size

        return stats_content, plot_content

    navbar = dbc.Navbar(
        [
            dbc.NavbarBrand(
                html.Img(src="/static/images/heading.png", height="70px"),
                className="me-auto",
                style={'margin-right': '20px'}
            )
        ],
        color="dark",
        dark=True,
        className='bg-dark'
    )

    navbar_container = html.Div(navbar)

    dash_app.layout = html.Div(
        children=[
            navbar_container,
            html.Div(
                className="container",
                children=[
                    html.Div(
                        className="left-section",
                        children=[
                            html.Div(
                                className="data-preview",
                                children=[
                                    html.Div(
                                        className="data-preview-container",
                                        children=[
                                            html.H3("Column Statistics", style={'font-size': '30px'}),
                                            dcc.Dropdown(
                                                id='column-dropdown',
                                                options=[],
                                                value=None,
                                                placeholder="Select a column",
                                                style={'backgroundColor': '#888888', 'color': '#000000', 'font-size': '22px'}
                                            ),
                                            html.Div(id="column-stats", style={'font-size': '22px'})
                                        ]
                                    )
                                ]
                            )
                        ],
                        style={'width': '35%', 'padding-right': '10px', 'height': 'calc(100vh - 70px)', 'overflowY': 'auto'}  # Adjusted width and height
                    ),
                    html.Div(
                        className="right-section",
                        children=[
                            html.Div(
                                className="data-visualization",
                                children=[
                                    html.Div(
                                        className="data-visualization-container",
                                        children=[
                                            html.Div(id="column-plot", style={'width': '100%', 'height': '100%'})  # Adjusted graph size
                                        ]
                                    )
                                ]
                            )
                        ],
                        style={'width': '65%', 'padding-left': '10px', 'height': 'calc(100vh - 70px)', 'overflowY': 'auto'}  # Adjusted width and height
                    )
                ],
                style={'display': 'flex', 'flexDirection': 'row'}
            ),
            dcc.Store(id='stored-data')
        ],
        style={'width': '100%', 'backgroundColor': '#333333'}
    )

    return dash_app

def update_stats_dash(dash_app, df):
    if df is not None and not df.empty:
        numeric_columns = df.select_dtypes(include=['number'])
        column_names = numeric_columns.columns.tolist()

        dropdown_options = [{'label': col, 'value': col} for col in column_names]

        left_section = html.Div(
            className="left-section",
            children=[
                html.Div(
                    className="data-preview",
                    children=[
                        html.Div(
                            className="data-preview-container",
                            children=[
                                html.H3("Column Statistics", style={'font-size': '30px'}),
                                dcc.Dropdown(
                                    id='column-dropdown',
                                    options=dropdown_options,
                                    value=None,
                                    placeholder="Select a column",
                                    style={'backgroundColor': '#888888', 'color': '#000000', 'font-size': '22px'}
                                ),
                                html.Div(id="column-stats", style={'font-size': '22px'})
                            ]
                        )
                    ]
                )
            ],
            style={'width': '35%', 'padding-right': '10px', 'height': 'calc(100vh - 70px)', 'overflowY': 'auto'}  # Adjusted width and height
        )

        right_section = html.Div(
    className="right-section",
    children=[
        html.Div(
            className="data-visualization",
            children=[
                html.Div(
                    className="data-visualization-container",
                    children=[
                        html.Div(id="column-plot", style={'width': '100%', 'height': '100%'})  # Adjusted width and height
                    ]
                )
            ]
        )
    ],
    style={'width': '85%', 'padding-left': '10px', 'height': '100vh', 'overflowY': 'auto'}  # Adjusted width and height
)




        navbar = dbc.Navbar(
            [
                dbc.NavbarBrand(
                    html.Img(src="/static/images/heading.png", height="70px"),
                    className="me-auto",
                    style={'margin-right': '20px'}
                )
            ],
            color="dark",
            dark=True,
            className='bg-dark'
        )

        navbar_container = html.Div(navbar)

        dash_app.layout = html.Div(
            children=[
                navbar_container,
                html.Div(
                    className="container",
                    children=[
                        html.Div(
                            children=[left_section, right_section],
                            style={'display': 'flex', 'flexDirection': 'row', 'height': 'calc(100vh - 70px)'}
                        ),
                        dcc.Store(id='stored-data', data=df.to_json(orient='split'))
                    ],
                    style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'backgroundColor': '#333333'}
                )
            ],
            style={'width': '100%', 'backgroundColor': '#333333'}
        )
    else:
        dash_app.layout = html.Div([
            html.H1("No Data Available", style={'color': '#FFFFFF'})
        ], style={'backgroundColor': '#333333'})

    return dash_app



