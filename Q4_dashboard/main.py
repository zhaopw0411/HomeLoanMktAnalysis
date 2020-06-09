from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import sqlite3 as sql
import pandas as pd
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.sampledata.movies_data import movie_path

loan = pd.read_csv('bokeh_year.csv')
loan.fillna(0, inplace=True)


axis_map = {
    "Total Loan Value": "Sum",
    "Median Loan": "Median",
    "Loan Volume": "Count",
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=1600)

# Create Input controls
min_market_share = Slider(title="Choose Market Share Range:", value=0, start=0.01, end=0.5, step=0.01)

min_count = Slider(title="Choose Loan Volume Range", start=0, end=20000, value=0, step=100)

state = Select(title="Select State", value="VA",options=loan['State'].unique().tolist())

company_name = TextInput(title="Search for Company Name")

y_axis = Select(title="Choose Y Axis", options=sorted(axis_map.keys()), value="Median Loan")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict( x=[], y=[],Percentage=[],Respondent_Name_CR=[], Sum=[], Median=[],Count=[]))

hover = HoverTool(tooltips=[
    ("Respondent Name", "@Respondent_Name_CR"),
    ("Market Share", "@Percentage"),
    ("Total Loan Value", "@Sum"),
    ("Loan Volume", "@Count"),
    ("Median Loan", "@Median")
])

p = figure(plot_height=600, plot_width=700, title="Circle Size Represents market share", x_range = (2011,2015),toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source, size='Percentage',fill_color="grey", hover_fill_color="firebrick",
                fill_alpha=0.3, hover_alpha=0.5,line_color=None,hover_line_color='white')
p.xaxis.ticker = [2012,2013,2014]


def select_movies():
    genre_val = state.value
    director_val = company_name.value.strip()
    selected = loan[
        (loan.Percentage >= min_market_share.value) &
        (loan.Count >= min_count.value)
    ]
    if (genre_val != ""):
        selected = selected[selected.State.str.contains(genre_val)==True]
    if (director_val != ""):
        selected = selected[selected.Respondent_Name_CR.str.contains(director_val)==True]
    return selected


def update():
    df = select_movies()
    y_name = axis_map[y_axis.value]

    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d point selected" % len(df)
    source.data = dict(
        x=df['As_of_Year'],#df[x_name],
        y=df[y_name],#
        Percentage=(df['Percentage']*400),
        Respondent_Name_CR=df['Respondent_Name_CR'], Sum=df['Sum'], Median=df['Median'],Count = df['Count']

    )

controls = [min_market_share,min_count,state,company_name,y_axis] #[reviews, boxoffice, genre, min_year, max_year, oscars, director, cast, x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)


update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Movies"