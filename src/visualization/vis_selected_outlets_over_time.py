#!/usr/bin/python
# -*- coding: utf-8

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Dark2_8 as palette
from bokeh.models import Legend
import itertools
import os
import graph_line_styles

def create_selected_outlets_over_time(journals, documents, years, output_folder, normalize=False, skip_last_year=False):
    journal_year = {}

    if skip_last_year:
        last_year = years[-1]
        years = years[:-1]
    else:
        last_year = years[-1] + 1
        
    first_year = years[10]
    years = years[10:]

    for journal in journals:
        for document in documents:
            if document['year'] >= last_year or document['year'] <= first_year:
                continue

            if journal['name'] not in journal_year:
                journal_year[journal['name']] = [0 for i in range(0, len(years))]
            if document['journal'] == journal['name']:
                journal_year[journal['name']][years.index(document['year'])] = journal_year[journal['name']][years.index(document['year'])] + 1

    min_value = 999999999
    max_value = 0
    for journal in journals:
        for year in years:
            value = journal_year[journal['name']][years.index(year)]
            if value > max_value: max_value = value
            if value < min_value: min_value = value

    if normalize:
        for journal in journals:
            for year in years:
                journal_year[journal['name']][years.index(year)] = (journal_year[journal['name']][years.index(year)] - min_value)/(max_value - min_value)
        min_value = 0
        max_value = 1

    output_file(os.path.join(output_folder, 'selected_journals_over_time.html'))
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
    for journal, color in itertools.izip(journals, colors):
        if counter % count_colors == 0:
            style = next(styles)
        counter = counter + 1

        line = p.line(years, journal_year[journal['name']], line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
        plot_parts = [line]
        if style['add-dots']:
            circle = p.circle(years, journal_year[journal['name']], size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
            plot_parts.append(circle)
        legend_it.append((journal['name'], plot_parts))

    legend = Legend(items=legend_it, location=(0, 0), margin=15, spacing=1)
    legend.click_policy="hide" #mute

    p.add_layout(legend, 'below')

    p.plot_height = 750 + 25 + (len(legend_it) * 21)

    return p
