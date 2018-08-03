#!/usr/bin/python
# -*- coding: utf-8

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Dark2_8 as palette
from bokeh.models import Legend
import itertools
import os
import graph_line_styles

def create_count_topics_over_time(documents, topics, years, output_folder, max_topics=25):
    years_topics = []

    for year in years:
        years_topics.append([0 for topic in topics])

    for year_index, year in enumerate(years):
        for document in documents:
            if document['year'] != year:
                continue
            for topic, value in enumerate(document['topics']):
                if max_topics > 0 and topic >= max_topics:
                    continue
                if value >= 0.01 and value != 0.02:
                    years_topics[year_index][topic] = 1
        years_topics[year_index] = reduce(lambda x, y: x + y, years_topics[year_index])


    min_value = 999999999
    max_value = 0
    for topic in topics:
        for year in years:
            value = years_topics[years.index(year)]
            if value > max_value: max_value = value
            if value < min_value: min_value = value

    output_file(os.path.join(output_folder, 'count_topics_over_time.html'))
    title = "Number of "
    if max_topics > 0:
        title = title + "top " + str(max_topics) + " "
    title = title + "topics per year with at least 0.01."

    p = figure(
       tools="pan,box_zoom,reset,save",
       y_range=[min_value, max_value * 1.05], x_range=[(years[0] - 1), (years[-1] + 1)], title=title,
       x_axis_label='year', y_axis_label='number of topics',
       plot_width=1024, toolbar_location='above',
       plot_height=1500
    )
    p.legend.visible = False

    legend_it = []

    colors = itertools.cycle(palette)
    styles = itertools.cycle(graph_line_styles.STYLES)
    style = next(styles)
    color = next(colors)


    line = p.line(years, years_topics, line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
    plot_parts = [line]
    if style['add-dots']:
        circle = p.circle(years, years_topics, size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
        plot_parts.append(circle)
    legend_it.append(('Number of Topics', plot_parts))

    legend = Legend(items=legend_it, location=(0, 0), margin=15, spacing=1)
    legend.click_policy="hide" #mute

    p.add_layout(legend, 'below')

    p.plot_height = 750 + 25 + (len(legend_it) * 21)

    return p
