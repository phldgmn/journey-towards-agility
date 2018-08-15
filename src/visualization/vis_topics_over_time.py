#!/usr/bin/python
# -*- coding: utf-8

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Dark2_8 as palette
from bokeh.models import Legend
import itertools
import os
import graph_line_styles
from tqdm import tqdm

def create_topics_over_time(documents, topics, years, output_folder, normalize=False, absolute=False, num_topics=-1, topic_groups=None, skip_last_year=False, plot_width=1000, file_appendix=""):
    topic_year = {}

    if num_topics > 0:
        reduced_topics = True
        num_topics = min(num_topics,len(topics))
    else:
        reduced_topics = False
        num_topics = len(topics)

    topics = topics[:num_topics]

    if skip_last_year:
        last_year = years[-1]
        years = years[:-1]
    else:
        last_year = years[-1] + 1

    for document in tqdm(documents):
        if document['year'] <= years[0] or document['year'] >= last_year:
            continue

        for topic in topics:
            target_id = topic['id']
            if topic_groups is not None:
                if str(target_id) not in topic_groups:
                    continue
                target_id = topic_groups[str(target_id)]['id']

            if target_id not in topic_year:
                topic_year[target_id] = [[] for i in range(len(years))]
            topic_year[target_id][years.index(document['year'])].append(document['topics'][topic['id']])

    if topic_groups is not None:
        _topics = []
        for topic in topics:
            if str(topic['id']) not in topic_groups:
                continue
            if topic_groups[str(topic['id'])] in _topics:
                continue
            _topics.append(topic_groups[str(topic['id'])])
        topics = _topics

    for topic in topics:
        for year in years:
            tmp = topic_year[topic['id']][years.index(year)]
            if len(tmp) <= 0:
                topic_year[topic['id']][years.index(year)] = 0
                continue
            if absolute:
                topic_year[topic['id']][years.index(year)] = reduce(lambda x, y: x + y, tmp)
            else:
                topic_year[topic['id']][years.index(year)] = reduce(lambda x, y: x + y, tmp) / len(tmp)

    min_value = 999999999
    max_value = 0
    for topic in topics:
        for year in years:
            value = topic_year[topic['id']][years.index(year)]
            if value > max_value: max_value = value
            if value < min_value: min_value = value

    if normalize:
        for topic in topics:
            for year in years:
                topic_year[topic['id']][years.index(year)] = (topic_year[topic['id']][years.index(year)] - min_value)/(max_value - min_value)
        min_value = 0
        max_value = 1

    filename = 'topics_over_time'
    if reduced_topics and (topic_groups is None or len(topic_groups) <= 0):
        filename = filename + '_' + str(num_topics)
    elif topic_groups is not None and len(topic_groups) > 0:
        filename = 'topic_groups_over_time'
    if not absolute:
        filename = filename + '_relative'
    filename = filename + file_appendix + '.html'

    output_file(os.path.join(output_folder, filename))
    p = figure(
       tools="pan,box_zoom,reset,save",
       y_range=[min_value, max_value * 1.05], x_range=[(years[0] - 1), (years[-1] + 1)], title="Toggle topics by clicking on them in the legend.",
       x_axis_label='year', y_axis_label='probability',
       plot_width=1024, toolbar_location='above',
       plot_height=1500
    )
    p.legend.visible = False

    legend_it = []

    colors = itertools.cycle(palette)
    styles = itertools.cycle(graph_line_styles.STYLES)

    count_colors = len(palette)
    counter = 0
    for topic, color in itertools.izip(topics, colors):
        if counter % count_colors == 0:
            style = next(styles)
        counter = counter + 1

        line = p.line(years, topic_year[topic['id']], line_width=2, line_alpha=0.9, color=color, line_dash=style['line-dash'], muted_color=color, muted_alpha=0.0)
        plot_parts = [line]
        if style['add-dots']:
            circle = p.circle(years, topic_year[topic['id']], size=5, alpha=0.5, color=color, muted_color=color, muted_alpha=0.0)
            plot_parts.append(circle)
        legend_it.append((topic['name'], plot_parts))

    legend = Legend(items=legend_it, location=(0, 0), margin=15, spacing=1)
    legend.click_policy="hide" #mute

    p.add_layout(legend, 'below')

    p.plot_height = 750 + 25 + (len(legend_it) * 21)
    p.plot_width = plot_width

    return p
