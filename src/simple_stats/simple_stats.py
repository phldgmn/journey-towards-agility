#!/usr/bin/python
# -*- coding: utf-8

import sys
import os
import jsonlines
import shutil
import support_functions
from tqdm import tqdm

def main(input_output_sub_folder='', enable_logging=True):
    dirname = os.path.abspath('.')
    input_folder = os.path.join(dirname, 'output', input_output_sub_folder)

    topics, papers, journals = support_functions.read_text_mining_result(os.path.join(input_folder, 'topics.jsonl'), os.path.join(input_folder, 'papers.jsonl'), os.path.join(input_folder, 'journals.jsonl'))

    count_journal_types = {}
    for paper in tqdm(papers):
        journal = find_journal(journals, paper['journal'])

        if journal['type'] not in count_journal_types:
            count_journal_types[journal['type']] = 1
        else:
            count_journal_types[journal['type']] = count_journal_types[journal['type']] + 1

    print "total count paper:", len(papers)
    print "count paper per outlet type:"
    for type, count in count_journal_types.items():
        print type, count

def find_journal(journals, name):
    for journal in journals:
        if journal['name'] == name:
            return journal
