#!/usr/bin/python
# -*- coding: utf-8

import sys
import os
import jsonlines
from shutil import copyfile
from tqdm import tqdm

import support_functions

def main(input_output_sub_folder='', enable_logging=True):
    dirname = os.path.abspath('.')
    input_folder = os.path.join(dirname, 'output', input_output_sub_folder)
    file_input_folder = os.path.join(dirname, 'input_pdf', input_output_sub_folder)
    output_folder = os.path.join(dirname, 'extraction', input_output_sub_folder)
    archive_folder = os.path.join(dirname, 'archive')

    support_functions.prepare_folders(input_folder, output_folder, archive_folder)

    topics, papers, journals = support_functions.read_text_mining_result(os.path.join(input_folder, 'topics.jsonl'), os.path.join(input_folder, 'papers.jsonl'), os.path.join(input_folder, 'journals.jsonl'))

    topic_ids = input_int_array('Enter Topic ID(s) separated by \',\': ')
    cutoff = input_float('Enter cutoff value for topics (0.01): ', 0.01)

    topics = [topic for topic in topics if topic['id'] in topic_ids]

    unique_results = []
    total_counter = 0

    for paper in tqdm(papers):
        for topic_id in topic_ids:
            if paper['topics'][topic_id] > cutoff:
                if os.path.exists(os.path.join(file_input_folder, 'journals', paper['journal'])):
                    origin_path = os.path.join(file_input_folder, 'journals', paper['journal'], paper['file_name'].replace('.txt', '.pdf'))
                else:
                    origin_path = os.path.join(file_input_folder, 'conferences', paper['journal'], paper['file_name'].replace('.txt', '.pdf'))

                if not os.path.exists(os.path.join(output_folder, 'Topic_' + str(topic_id))):
                    os.makedirs(os.path.join(output_folder, 'Topic_' + str(topic_id)))

                copyfile(origin_path, os.path.join(output_folder, 'Topic_' + str(topic_id), paper['file_name'].replace('.txt', '.pdf')))

                if paper['file_name'] not in unique_results:
                    unique_results.append(paper['file_name'])
                total_counter = total_counter + 1

    print('found a total of ' + str(total_counter) + ' results, ' + str(len(unique_results)) + ' of which are unique.')

def initialize_years(papers, enable_logging):
    years = []
    min_year = 9999
    max_year = 0
    for document in papers:
        if document['year'] > max_year: max_year = document['year']
        if document['year'] > 0 and document['year'] < min_year: min_year = document['year']
        if enable_logging and document['year'] <= 0: print(document['file_name'])

    for year in range(min_year, max_year):
        years.append(year)

    return years

def input_float(text = '', default = None):
    while True:
        try:
            input_candidate = raw_input(text)
            if default is not None and (input_candidate == None or len(str(input_candidate)) <= 0):
                return default
            else:
                return float(input_candidate)
        except Exception:
            pass

def input_int_array(text = '', default = None):
    while True:
        try:
            input_candidate = raw_input(text)
            if default is not None and (input_candidate == None or len(str(input_candidate)) <= 0):
                return default
            else:
                return map(int, map(str.strip, input_candidate.split(',')))
        except Exception as e:
            print(e)
            pass

if __name__ == "__main__":
    # execute only if run as a script
    main()
