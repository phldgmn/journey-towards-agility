#!/usr/bin/python
# -*- coding: utf-8

import sys
import os
import jsonlines
import shutil

from bokeh.plotting import save

import support_functions
import vis_topics_over_time
import vis_journals_over_time
import vis_keywordlist
import vis_topics_papers
import vis_topics_journals
import vis_outlet_types_over_time
import vis_outlet_details
import vis_count_topics
import vis_count_paper
import vis_selected_outlets_over_time
import vis_aggregated_conferences_over_time

def main(input_output_sub_folder='', enable_logging=True):
    dirname = os.path.abspath('.')
    input_folder = os.path.join(dirname, 'output', input_output_sub_folder)
    output_folder = os.path.join(dirname, 'visualization', input_output_sub_folder)
    archive_folder = os.path.join(dirname, 'archive')

    support_functions.prepare_folders(input_folder, output_folder, archive_folder)

    if os.path.exists(os.path.join(input_folder, 'ldavis.html')) and not os.path.exists(os.path.join(input_folder, 'lda_model.html')):
        shutil.copy(os.path.join(input_folder, 'ldavis.html'), os.path.join(output_folder, 'lda_model.html'))

    topics, papers, journals = support_functions.read_text_mining_result(os.path.join(input_folder, 'topics.jsonl'), os.path.join(input_folder, 'papers.jsonl'), os.path.join(input_folder, 'journals.jsonl'))

    years = initialize_years(papers, enable_logging)
    groups = []
    if os.path.exists(os.path.join(input_folder, 'topic_groups.jsonl')):
        with jsonlines.open(os.path.join(input_folder, 'topic_groups.jsonl')) as reader:
            for obj in reader:
                groups.append(obj)

    selected_topics = [topics[0], topics[1], topics[16], topics[18], topics[25]]
    years_subset = []
    for year in years:
        if year >= 2000:
            years_subset.append(year)
    save(vis_topics_over_time.create_topics_over_time(papers, selected_topics, years_subset, output_folder, normalize=True, absolute=True, file_appendix="selected"))

    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True))
    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, num_topics=25))
    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, num_topics=10))
    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, absolute=True))
    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, absolute=True, num_topics=25))
    save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, absolute=True, num_topics=10))
    if groups is not None and len(groups) > 0:
        topic_groups = {}
        for group in groups:
            for topic in group['topics']:
                topic_groups[str(topic)] = {
                    'id': group['id'],
                    'name': group['name']
                }
        save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, topic_groups=topic_groups))
        save(vis_topics_over_time.create_topics_over_time(papers, topics, years, output_folder, normalize=True, absolute=True, topic_groups=topic_groups))

    save(vis_journals_over_time.create_journals_over_time(journals, papers, years, output_folder, False))

    selected_journals = []
    selected_journal_names = ['Americas Conference on Information Systems (AMCIS)', 'Information and Software Technology', 'Hawaii International Conference on System Sciences (HICSS)', 'Pacific Asia Conference on Information Systems (PACIS)', 'European Conference on Information Systems (ECIS)', 'International Conference on Information Systems (ICIS)', 'Journal of Systems and Software', 'IEEE Software', 'IEEE Transactions on Software Engineering', 'Computer', 'European Journal of Information Systems (EJIS)']
    for journal in journals:
        if journal['name'] in selected_journal_names:
            selected_journals.append(journal)

    save(vis_selected_outlets_over_time.create_selected_outlets_over_time(selected_journals, papers, years, output_folder, False))

    outlet_aggregation = []
    if os.path.exists(os.path.join(input_folder, 'outlet_groups.jsonl')):
        with jsonlines.open(os.path.join(input_folder, 'outlet_groups.jsonl')) as reader:
            for obj in reader:
                outlet_aggregation.append(obj)

    if outlet_aggregation is not None and len(outlet_aggregation) > 0:
        years_subset = []
        for year in years:
            if year >= 2000:
                years_subset.append(year)
        save(vis_aggregated_conferences_over_time.vis_aggregated_conferences_over_time(journals, outlet_aggregation, papers, years_subset, output_folder, normalize=True, skip_last_year=True))
        save(vis_aggregated_conferences_over_time.vis_aggregated_conferences_over_time(journals, outlet_aggregation, papers, years_subset, output_folder, normalize=False, skip_last_year=True))

    save(vis_count_topics.create_count_topics_over_time(papers, topics, years, output_folder))
    save(vis_count_paper.create_count_paper_over_time(papers, years, output_folder))
    save(vis_count_paper.create_count_paper_over_time(papers, years, output_folder, journals, include_basket=True, aggregate_basket=False))
    save(vis_count_paper.create_count_paper_over_time(papers, years, output_folder, journals, include_basket=True, aggregate_basket=True))
    save(vis_outlet_types_over_time.create_outlet_types_over_time(journals, papers, years, output_folder, False))
    vis_keywordlist.create_topics_list(topics, output_folder)
    vis_keywordlist.create_topics_list(topics, output_folder, details=True)
    vis_topics_papers.create_topics_list(papers, topics, output_folder)
    vis_topics_papers.create_topics_list(papers, topics, output_folder, details=True)
    vis_topics_journals.create_topics_list(journals, topics, output_folder)
    vis_topics_journals.create_topics_list(journals, topics, output_folder, details=True)
    vis_outlet_details.create_outlet_details(journals, papers, output_folder)

def initialize_years(papers, enable_logging):
    years = []
    min_year = 9999
    max_year = 0
    for document in papers:
        if document['year'] > max_year: max_year = document['year']
        if document['year'] > 0 and document['year'] < min_year: min_year = document['year']
        if enable_logging and document['year'] <= 0: print document['file_name']

    for year in range(min_year, max_year):
        years.append(year)

    return years

if __name__ == "__main__":
    # execute only if run as a script
    main()
