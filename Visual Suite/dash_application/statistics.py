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
        url_base_pathname="/stats/",
        external_stylesheets=[dbc.themes.DARKLY]
    )

    dash_app.layout = html.Div(
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
                                    html.H2("Select Column"),
                                    dcc.Dropdown(
                                        id='column-dropdown',
                                        options=[],
                                        value=None,
                                        placeholder="Select a column"
                                    ),
                                    html.Div(id="column-stats")  # Placeholder for stats
                                ]
                            )
                        ]
                    )
                ],
                style={'position': 'absolute', 'left': '0', 'top': '0', 'width': '50%', 'height': '100vh', 'overflowY': 'auto'}
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
                                    html.H2("Plots and Stats"),
                                    html.Div(id="column-plot")  # Placeholder for plot
                                ]
                            )
                        ]
                    )
                ],
                style={'position': 'absolute', 'right': '0', 'top': '0', 'width': '50%', 'height': '100vh', 'overflowY': 'auto'}
            )
        ],
        style={"position": "relative"}
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
                stats_content = dcc.Markdown(f"**Main Statistics:**\n{stats_str}\n\n**Outliers:**\n{outliers_str}\n\n{unique_values_str}")
                plot_content = dcc.Graph(figure=fig)

            return stats_content, plot_content

    else:
        dash_app.layout = html.Div([
            html.H1("No Data Available", style={'color': '#FFFFFF'})
        ], style={'backgroundColor': '#333333'})