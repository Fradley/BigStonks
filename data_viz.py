import pandas as pd
import os
from os.path import join, isfile
from bokeh.palettes import inferno
from bokeh.plotting import figure, save
from bokeh.io import output_file, show
from bokeh.layouts import column
from datetime import datetime
from bokeh.models import HoverTool, ColumnDataSource, Legend, CustomJS

def build_dataset(fpath, ext='.csv'):
    files = [join(fpath, f) for f in os.listdir(fpath) if isfile(join(fpath, f))]
    dfs = list()
    for f in files:
        dfs.append(pd.read_csv(f))
    df = pd.concat(dfs)
    df.columns = [col[0].upper() + col[1:] for col in df.columns]
    df['Time'] = pd.to_datetime(df['Time'])
    df.sort_values('Time', ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.drop_duplicates('Time', keep='first', inplace=True)
    return df


def build_visualization(symbol, fpath='Data/', outpath='Visualizations/', bad_vars=['Time', 'Volume']):
    symbol = symbol.lower()
    datasets = dict()
    datasets['Daily'] = build_dataset(fpath + f'{symbol}/{symbol}_daily/')
    datasets['Intraday'] = build_dataset(fpath + f'{symbol}/{symbol}_intraday/')
    datasets['Sentiment'] = build_dataset(fpath + f'{symbol}/{symbol}_sentiment/')
    figs = list()
    for dataset in datasets.keys():
        s = figure(plot_width=1600, plot_height=500, x_axis_type="datetime")
        s.title.text = f'Data from {dataset}'
        columns = [c for c in list(datasets[dataset].columns) if c not in bad_vars]
        colors = inferno(len(columns))
        for col, color in zip(columns, colors):
            line = s.line(x='Time', y=col, source=datasets[dataset], line_width=2, color=color, alpha=0.8, legend_label=col)
            s.add_tools(HoverTool(renderers=[line], tooltips=[('date', '@Time{%F}'), (f'{col}',f'@{col}'), ('Volume', f'@Volume')], formatters={'Time': 'datetime', f'{col}': f'numeral', 'Volume': f'numeral'},mode='mouse'))
        s.legend.location = "top_left"
        s.legend.click_policy="hide"
        figs.append(s)
    now = datetime.now()
    output_file(outpath + f'{symbol}_viz_{now.year}_{now.month}_{now.day}.html', title=f'Plots for {symbol}')
    c = column(*figs)
    show(c)
    save(c)