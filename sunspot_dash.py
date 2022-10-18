import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


def read_csv(file_name):
    """
    Read in sunspot csv

    Parameters:
        file_name : name of csv file to read in

    Returns:
        df : data frame containing the sunspot data from the file
    """
    # read in csv
    df = pd.read_csv(file_name, sep=';', header=None)

    # create column titles and drop unnecessary columns
    df.columns = ['year', 'month', 'decimal year', 'SNvalue', 'SNerror', 'Nb observation1', 'Nb observation2']
    df = df.drop(['Nb observation1', 'Nb observation2'], axis=1)

    return df


def plot_line_chart(df, years, smoothing_val):
    """
    Plots a line chart of data given

    Parameters:
        df : data frame containing the sunspot data from the file
        years : list with the min year range at [0] and the max year range aat [1]
        smoothing_val : int of number of months to use to smooth the data

    Returns:
        fig : figure object containing the graph to display
    """
    # narrow the df down to the year range selected
    df = df[df['year'] >= years[0]]
    df = df[df['year'] <= years[1]]

    # create the figure
    fig = go.Figure()

    # plot the line graph
    fig.add_trace(go.Scatter(x=df['year'], y=df['SNvalue'], mode='lines', name='Monthly'))
    fig.update_layout(xaxis_title="Time (years)", yaxis_title="Number of Sunspots")

    # create the smoothed column in the df
    df['smoothed_data'] = df.SNvalue.rolling(window=smoothing_val, center=True).mean()

    # plot the smoothing over the line graph
    fig.add_trace(go.Scatter(x=df['decimal year'], y=df['smoothed_data'], mode='lines', name='Smoothed'))

    return fig


# read in the sunspot data
df = read_csv('Sunspot_data.csv')

# creates a dictionary for the marks on the range slider
marks_dict = {1749: '1749', 1760: '1760', 1780: '1780',
              1800: '1800', 1820: '1820', 1840: '1840', 1860: '1860', 1880: '1880',
              1900: '1900', 1920: '1920', 1940: '1940', 1960: '1960', 1980: '1980',
              2000: '2000', 2022: '2022'}

# build an app
app = Dash(__name__)

# set up app layout
app.layout = html.Div([

    # Div for sunspots over time plot
    html.Div([

        # set title to the graph and make plot
        html.H1('International Sunspot Frequency Trends by Year'),
        dcc.Graph(id='graph'),

        # set a minimum and maximum year slider to adjust the range
        html.P('Select start year'),
        dcc.RangeSlider(id='years', min=df['year'].min(), max=df['year'].max(), marks=marks_dict,
                        value=[df['year'].min(), df['year'].max()]),

        # set slider for data smoothing
        html.P('Select the month value to smooth by'),
        dcc.Slider(id='smoothing_val', min=1, max=40, step=4, value=25)
    ]),

    # Div for cycle scatterplot
    html.Div([

        # set title to the graph and make plot
        html.H1('Sunspot Cycles Scatterplot'),
        dcc.Graph(id='graph2', style={'height': '40%', 'weight': '40%'}),

        # set cycle length
        html.P('Select the year value to cycle at'),
        dcc.Slider(id='cycle_len', min=1, max=12, step=1, value=10)

    ]),

    # Div for live sun image
    html.Div([

        # set title to the graph and make plot
        html.H1('Sunspot View - Real Time Image'),

        # import image of the sun (could replace with image, but preferred the up-to-date three-month view)
        html.Img(
            src='https://soho.nascom.nasa.gov/data/LATEST/current_eit_304.gif'
        )

    ])

])


# create a callback with the outputs and inputs
@app.callback(
    Output("graph", "figure"),
    Input("years", "value"),
    Input("smoothing_val", "value")
)
def display_line_plot(years, smoothing_val):
    """
    Displays the line plot with the capability to make adjustments using the callback

    Parameters:
        years : list with the min year range at [0] and the max year range aat [1]
        smoothing_val : int of number of months to use to smooth the data

    Returns:
        fig : figure object containing the graph to display
    """
    # create the figure using the line_chart function
    fig = plot_line_chart(df, years, smoothing_val)

    return fig


@app.callback(
    Output("graph2", "figure"),
    Input("cycle_len", "value")
)
def display_scatter_plot(cycle_len):
    """
    Displays the scatter plot with the capability to make adjustments using the callback

    Parameters:
        cycle_len : int with length of cycle to calculate by for scatterplot

    Returns:
        fig : figure object containing the graph to display
    """
    # create column
    temp_df = df
    temp_df['cycle'] = temp_df['decimal year'] % cycle_len

    # create the figure
    fig = go.Figure()

    # plot the scatter plot
    fig.add_trace(go.Scatter(x=temp_df['cycle'], y=temp_df['SNvalue'], mode='markers'))
    fig.update_layout(xaxis_title="Year of Cycle", yaxis_title="Number of Sunspots", width=650, height=550)

    return fig


# run the dashboard with a debugger
app.run_server(debug=True)
