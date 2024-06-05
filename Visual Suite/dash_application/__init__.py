import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.figure_factory as ff

def create_missing_dash_application(flask_app):
    dash_app = dash.Dash(
        server=flask_app, 
        name="Dashboard", 
        url_base_pathname="/dash/", 
        external_stylesheets=[dbc.themes.DARKLY]
    )

    navbar = dbc.Navbar(
        [
            dbc.NavbarBrand(
                html.Img(src="/static/images/heading.png", height="70px"),
                className="me-auto",
                style={'margin-right': '20px'}  # Add margin-right here
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Missing Analysis", href="/dash/", style={'color': 'white'})),
                    dbc.NavItem(dbc.NavLink("Correlation Matrix", href="/dash1/", style={'color': 'white'})),
                ],
                className="ml-auto",
            ),
        ],
        color="dark",  # Use the 'dark' color theme
        dark=True,
        className='bg-dark'
    )

    colors = {
        'background': '#333333',
        'text': 'white'
    }

    layout = html.Div([
        navbar,
        html.H1("Non-Missing Values Analysis", style={'color': colors['text']}),
        dcc.Graph(
            id='non-missing-values-bar',
            figure={
                'layout': {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }
        )
    ], style={'backgroundColor': colors['background']})

    dash_app.layout = layout
    return dash_app

def update_dash_app(dash_app, df):  
    if df is not None and not df.empty:
        non_missing_values = df.notnull().sum()
        non_missing_df = pd.DataFrame({'Column': non_missing_values.index, 'Non-Missing Values': non_missing_values.values})

        fig = px.bar(non_missing_df, x='Column', y='Non-Missing Values',
                     labels={'Column': 'Columns', 'Non-Missing Values': 'Number of Non-Missing Values'})
        fig.update_traces(marker_color='#FEE600')
        fig.update_layout(
            plot_bgcolor='#333333',
            paper_bgcolor='#333333',
            font=dict(color='white')
        )

        navbar = dbc.Navbar(
            [
                dbc.NavbarBrand(
                    html.Img(src="/static/images/heading.png", height="70px"),
                    className="me-auto",
                    style={'margin-right': '20px'}  # Add margin-right here
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Missing Analysis", href="/dash/", style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("Correlation Matrix", href="/dash1/", style={'color': 'white'})),
                    ],
                    className="ml-auto",
                ),
            ],
            color="dark",  # Use the 'dark' color theme
            dark=True,
            className='bg-dark'
        )

        colors = {
            'background': '#333333',
            'text': 'white'
        }

        layout = html.Div([
            navbar,
            html.H1("Non-Missing Values Analysis", style={'color': colors['text']}),
            dcc.Graph(
                id='non-missing-values-bar',
                figure=fig  # Use the updated figure here
            )
        ], style={'backgroundColor': colors['background']})

        dash_app.layout = layout

def create_cm_dash(flask_app):
    dash_app = dash.Dash(
        server=flask_app, 
        name="Dashboard", 
        url_base_pathname="/dash1/", 
        external_stylesheets=[dbc.themes.DARKLY]
    )

    navbar = dbc.Navbar(
        [
            dbc.NavbarBrand(
                html.Img(src="/static/images/heading.png", height="70px"),
                className="me-auto",
                style={'margin-right': '20px'}  # Add margin-right here
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Missing Analysis", href="/dash/", style={'color': 'white'})),
                    dbc.NavItem(dbc.NavLink("Correlation Matrix", href="/dash1/", style={'color': 'white'})),
                ],
                className="ml-auto",
            ),
        ],
        color="dark",  # Use the 'dark' color theme
        dark=True,
        className='bg-dark'
    )

    colors = {
        'background': '#333333',
        'text': 'white'
    }

    layout = html.Div([
        navbar,
        html.H1("Correlation Matrix", style={'color': colors['text']}),
        html.Div([
            dcc.Dropdown(
                id='dropdown1',
                value=None,
                placeholder="Select column"
            ),
            dcc.Dropdown(
                id='dropdown2',
                value=None,
                placeholder="Select column"
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='heatmap', 
                  figure={'layout': {'plot_bgcolor': colors['background'], 'paper_bgcolor': colors['background'], 'font': {'color': colors['text']}}}
        )
    ], style={'backgroundColor': colors['background']})

    dash_app.layout = layout
    return dash_app

def update_cm_dash(dash_app, df):
    if df is not None and not df.empty:
        numeric_columns = df.select_dtypes(include=['number'])
        correlation_matrix = numeric_columns.corr()
        column_names = correlation_matrix.columns.tolist()

        dropdown1 = dcc.Dropdown(
            id='dropdown1',
            value=None,
            options=[{'label': col, 'value': col} for col in column_names],
            placeholder="Select column",
            style={'color': 'black'}
        )

        dropdown2 = dcc.Dropdown(
            id='dropdown2',
            value=None,
            options=[{'label': col, 'value': col} for col in column_names],
            placeholder="Select column",
            style={'color': 'black'}
        )

        heatmap = dcc.Graph(id='heatmap')

        @dash_app.callback(
            [Output('dropdown1', 'options'),
             Output('dropdown2', 'options')],
            [Input('dropdown1', 'value'),
             Input('dropdown2', 'value')]
        )
        def update_dropdowns(selected_column1, selected_column2):
            options = [{'label': col, 'value': col} for col in column_names]
            return options, options

        @dash_app.callback(
            Output('heatmap', 'figure'),
            [Input('dropdown1', 'value'),
             Input('dropdown2', 'value')]
        )
        def update_heatmap(column1, column2):
            if column1 is None or column2 is None:
                selected_correlation_matrix = correlation_matrix
                x = column_names
                y = column_names
            else:
                selected_correlation_matrix = df[[column1, column2]].corr()
                x = [column1, column2]
                y = [column1, column2]

            fig = ff.create_annotated_heatmap(
                z=selected_correlation_matrix.values,
                x=x,
                y=y,
                colorscale=[[0, 'grey'], [0.5, '#FFE600'], [1, 'grey']],  # Yellow-Orange-Red palette
                showscale=True,
                annotation_text=selected_correlation_matrix.values.round(2),
                hoverinfo='z',
                xgap=1, ygap=1,
                font_colors=['white']  # Set text color to white
            )
            fig.update_layout(
                plot_bgcolor='#333333',
                paper_bgcolor='#333333',
                xaxis=dict(tickfont=dict(color='white')),  # Set x-axis text color to white
                yaxis=dict(tickfont=dict(color='white'))   # Set y-axis text color to white
            )
            return fig

        navbar = dbc.Navbar(
            [
                dbc.NavbarBrand(
                    html.Img(src="/static/images/heading.png", height="70px"),
                    className="me-auto",
                    style={'margin-right': '20px'}  # Add margin-right here
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Missing Analysis", href="/dash/", style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("Correlation Matrix", href="/dash1/", style={'color': 'white'})),
                    ],
                    className="ml-auto",
                ),
            ],
            color="dark",  # Use the 'dark' color theme
            dark=True,
            className='bg-dark'
        )

        # Update the layout with the new structure
        dash_app.layout = html.Div([
            navbar,
            html.H1("Correlation Matrix", style={'color': '#FFFFFF'}),
            html.Div([dropdown1, dropdown2], style={'width': '50%', 'display': 'inline-block'}),
            heatmap
        ], style={'backgroundColor': '#333333'})
