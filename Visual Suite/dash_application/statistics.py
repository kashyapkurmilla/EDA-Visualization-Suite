import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

def create_stats_dash(flask_app):
    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/statistics/",
        external_stylesheets=[dbc.themes.DARKLY]
    )

    navbar = dbc.Navbar(
        [
            dbc.NavbarBrand(
                html.Img(src="/static/images/heading.png", height="70px"),
                className="me-auto",
                style={'margin-right': '20px'}  # Add margin-right here
            )
        ],
        color="dark",  # Use the 'dark' color theme
        dark=True,
        className='bg-dark'
    )

    # Define left and right sections
    left_section = html.Div(
        className="left-section",
        children=[
            html.Div(
                className="data-preview",
                children=[
                    html.Div(
                        className="data-preview-container",
                        children=[
                            html.H3("Column Statistics"),
                            dcc.Dropdown(
                                id='column-dropdown',
                                options=[],
                                value=None,
                                placeholder="Select a column",
                                style={'backgroundColor': '#888888', 'color': '#000000'}
                            ),
                            html.Div(id="column-stats")  # Placeholder for stats
                        ]
                    )
                ]
            )
        ],
        style={'width': '30%'}  # Reduced width to 30%
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
                            html.Div(id="column-plot")  # Placeholder for plot
                        ]
                    )
                ]
            )
        ],
        style={'width': '70%'}  # Increased width to 70%
    )

    navbar_container = html.Div(navbar)  # Wrap navbar in its own container

    dash_app.layout = html.Div(
        className="container",
        children=[
            navbar_container,  # Add the navbar container here
            html.Div([left_section, right_section], style={'display': 'flex', 'flexDirection': 'row'}),  # Wrap left and right sections in a container
        ],
        style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'backgroundColor': '#333333'}
    )

    return dash_app

def update_stats_dash(dash_app, df):
    if df is not None and not df.empty:
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        @dash_app.callback(
            Output('column-dropdown', 'options'),
            Input('column-dropdown', 'value')
        )
        def update_dropdown_options(selected_column):
            options = [{'label': col, 'value': col} for col in numeric_columns]
            return options
    
        @dash_app.callback(
        [Output('column-stats', 'children'),
        Output('column-plot', 'children')],
        Input('column-dropdown', 'value')
            )
        def update_content(selected_column):
            print("Selected Column:", selected_column)  # Debugging line

            # Initialize stats and plot content
            stats_content = dcc.Markdown("No column selected.")
            plot_content = ""

            if selected_column:
                print("Inside selected_column condition")  # Debugging line
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
                print("Q1:", Q1)
                print("Q3:", Q3)
                print("IQR:", IQR)
                outliers = df[(df[selected_column] < (Q1 - 1.5 * IQR)) | (df[selected_column] > (Q3 + 1.5 * IQR))][selected_column]
                print("Outliers:", outliers)  # Debugging line
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
                stats_content = dcc.Markdown(f"\n\n{stats_str}\n\n**Outliers:**\n\n{outliers_str}\n\n{unique_values_str}")
                plot_content = dcc.Graph(figure=fig)

            return stats_content, plot_content

    else:
        dash_app.layout = html.Div([
            html.H1("No Data Available", style={'color': '#FFFFFF'})
        ], style={'backgroundColor': '#333333'})

