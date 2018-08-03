#!/usr/bin/python
# -*- coding: utf-8

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Dark2_8 as palette
from bokeh.models import Legend
import itertools
import os
import graph_line_styles
from tqdm import tqdm

def create_outlet_types_over_time(outlets, documents, years, output_folder, normalize=False, skip_last_year=False):
    outlet_type_year = {}
    outlet_types = []

    if skip_last_year:
        last_year = years[-1]
        years = years[:-1]
    else:
        last_year = years[-1] + 1

    for outlet in tqdm(outlets):
        for document in documents:
            if document['year'] >= last_year:
                continue

            if outlet['type'] not in outlet_type_year:
                outlet_types.append(outlet['type'])
                outlet_type_year[outlet['type']] = [0 for i in range(0, len(years))]
            if document['journal'] == outlet['name']:
                outlet_type_year[outlet['type']][years.index(document['year'])] = outlet_type_year[outlet['type']][years.index(document['year'])] + 1

    min_value = 999999999
    max_value = 0
    for outlet in outlets:
        for year in years:
            value = outlet_type_year[outlet['type']][years.index(year)]
            if value > max_value: max_value = value
            if value < min_value: min_value = value

    if normalize:
        for outlet in outlets:
            for year in years:
                outlet_type_year[outlet['type']][years.index(year)] = (outlet_type_year[outlet['type']][years.index(year)] - min_value)/(max_value - min_value)
        min_value = 0
        max_value = 1

    output_file(os.path.join(output_folder, 'outlet_types_over_time.html'))
    p = figure(
       tools="pan,box_zoom,reset,save",
       y_range=[min_value, max_value * 1.05], x_range=[(years[0] - 1), (years[-1] + 1)], title="Toggle journals by clicking on them in the legend.",
       x_axis_label='year', y_axis_label='count articles',
       plot_width=1024, toolbar_location='above',
       plot_height=1500
    )
    p.legend.visible = False

    legend_it = []

    colors = itertools.cycle(palette)
    styles = itertools.cycle(graph_line_styles.STYLES)

    count_colors = len(palette)
    counter = 0
    for outlet_type, color in itertools.izip(outlet_types, colors):
        if counter % count_colors == 0:
            style = next(styles)
        counter = counter + 1

        line = p.line(years, outlet_type_year[outlet_type], line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
        plot_parts = [line]
        if style['add-dots']:
            circle = p.circle(years, outlet_type_year[outlet_type], size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
            plot_parts.append(circle)
        legend_it.append((outlet_type, plot_parts))

    legend = Legend(items=legend_it, location=(0, 0), margin=15, spacing=1)
    legend.click_policy="hide" #mute

    p.add_layout(legend, 'below')

    p.plot_height = 750 + 25 + (len(legend_it) * 21)

    return p
