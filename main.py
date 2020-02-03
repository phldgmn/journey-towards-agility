#!/usr/bin/python
# -*- coding: utf-8

import sys
import os
sys.path.append(os.path.join(os.path.abspath('.'), 'src', 'support'))

from src.pdf_txt_handling import pdf_to_txt
from src.pdf_txt_handling import read_papers
from src.topic_modeling import topic_modeling
from src.visualization import create_visualizations
from src.sci_hub import download_from_scihub
from src.batch import batch_processing
from src.simple_stats import simple_stats
from src.extraction import topic_extraction
from src.extraction import topic_extraction_by_cutoff

ACTIONS = {
    '1': { 'desc': 'download from sci hub', 'method': download_from_scihub.main},
    '2': { 'desc': 'parse PDFs', 'method': pdf_to_txt.main},
    '3': { 'desc': 'read Texts', 'method': read_papers.main},
    '4': { 'desc': 'topic modeling', 'method': topic_modeling.main},
    '5': { 'desc': 'visualize results', 'method': create_visualizations.main},
    '6': { 'desc': 'display simple stats', 'method': simple_stats.main},
    '7': { 'desc': 'batch create topic models and visualize', 'method': batch_processing.main},
    '8': { 'desc': 'extract papers from topics (by top X%)', 'method': topic_extraction.main},
    '9': { 'desc': 'extract papers from topics (by cutoff)', 'method': topic_extraction_by_cutoff.main},
    'e': { 'desc': 'exit', 'method': None},
}

def main():
    continue_command = 'y'
    while continue_command == 'y' or continue_command == 'Y':
        print "Available actions:"
        for action_key in sorted(ACTIONS.iterkeys()):
            print action_key, ": ", ACTIONS[action_key]['desc']

        command = raw_input("Select action: ")

        if command not in ACTIONS:
            print 'unknown command'
        else:
            action = ACTIONS[command]
            if action['method'] is None:
                break
            else:
                print 'running command', command, ': ', action['desc']
                action['method']()
                print 'done.'

        print "====\n\n"

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    try:
        main()
    except KeyboardInterrupt:
        print ''
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
