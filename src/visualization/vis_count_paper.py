#!/usr/bin/python
# -*- coding: utf-8

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Dark2_8 as palette
from bokeh.models import Legend
import itertools
import os
import graph_line_styles

def create_count_paper_over_time(documents, years, output_folder, outlets=None, include_basket=False, aggregate_basket=False, skip_last_year=False):
    basket = [
        'European Journal of Information Systems (EJIS)',
        'Information Systems Journal (ISJ)',
        'Information Systems Research (ISR)',
        'Journal of the Association for Information Systems (JAIS)',
        'Journal of Information Technology (JIT)',
        'Journal of Management Information Systems (JMIS)',
        'Journal of Strategic Information Systems (JSIS)',
        'Management Information Systems Quarterly (MISQ)']

    years_paper = []

    if skip_last_year:
        last_year = years[-1]
        years = years[:-1]
    else:
        last_year = years[-1] + 1

    for year in years:
        years_paper.append(0)

    for document in documents:
        if document['year'] >= last_year:
            continue
        years_paper[years.index(document['year'])] = years_paper[years.index(document['year'])] + 1

    min_value = 999999999
    max_value = 0
    for year in years:
        value = years_paper[years.index(year)]
        if value > max_value: max_value = value
        if value < min_value: min_value = value

    filename = 'count_papers_over_time'
    if include_basket:
        filename = filename + '_basket'
        if aggregate_basket:
            filename = filename + '_aggregated'
    filename = filename + '.html'
    output_file(os.path.join(output_folder, filename))
    title = "Number of papers per year."

    p = figure(
       tools="pan,box_zoom,reset,save",
       y_range=[min_value, max_value * 1.05], x_range=[(years[0] - 1), (years[-1] + 1)], title=title,
       x_axis_label='year', y_axis_label='number of papers',
       plot_width=1024, toolbar_location='above',
       plot_height=1500
    )
    p.legend.visible = False

    legend_it = []

    colors = itertools.cycle(palette)
    styles = itertools.cycle(graph_line_styles.STYLES)
    style = next(styles)
    color = next(colors)

    line = p.line(years, years_paper, line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
    plot_parts = [line]
    if style['add-dots']:
        circle = p.circle(years, years_paper, size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
        plot_parts.append(circle)
    legend_it.append(('Number of Papers', plot_parts))

    if outlets is not None:
        if include_basket:
            if aggregate_basket:
                years_basket = []

                for year in years:
                    years_basket.append(0)

                for document in documents:
                    if document['year'] >= last_year:
                        continue
                    if document['journal'] in basket:
                        years_basket[years.index(document['year'])] = years_basket[years.index(document['year'])] + 1

                color = next(colors)

                line = p.line(years, years_basket, line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
                plot_parts = [line]
                if style['add-dots']:
                    circle = p.circle(years, years_basket, size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
                    plot_parts.append(circle)
                legend_it.append(('Senior Scholars\' Basket', plot_parts))
            else:
                count_colors = len(palette)
                counter = 1
                for journal, color in itertools.izip(basket, colors):
                    if counter % count_colors == 0:
                        style = next(styles)
                    counter = counter + 1
                    years_basket = []

                    for year in years:
                        years_basket.append(0)

                    for document in documents:
                        if document['year'] >= last_year:
                            continue
                        if document['journal'] == journal:
                            years_basket[years.index(document['year'])] = years_basket[years.index(document['year'])] + 1

                    color = next(colors)

                    line = p.line(years, years_basket, line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
                    plot_parts = [line]
                    if style['add-dots']:
                        circle = p.circle(years, years_basket, size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
                        plot_parts.append(circle)
                    legend_it.append((journal, plot_parts))


    legend = Legend(items=legend_it, location=(0, 0), margin=15, spacing=1)
    legend.click_policy="hide" #mute

    p.add_layout(legend, 'below')

    p.plot_height = 750 + 25 + (len(legend_it) * 21)

    return p
