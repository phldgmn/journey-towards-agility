#!/usr/bin/python
# -*- coding: utf-8

import support_functions
from ..topic_modeling import topic_modeling
from ..visualization import create_visualizations

def main():
    min_topics = 5
    max_topics = 75
    step = 5
    no_features = 1000
    no_top_words = 25

    min_topics = support_functions.ask_for_int("Minimum number of topics: ", 1, 10000, min_topics)
    max_topics = support_functions.ask_for_int("Maximum number of topics: ", 1, 10000, max_topics)
    step = support_functions.ask_for_int("Step size: ", 1, 1000, step)
    no_features = support_functions.ask_for_int("Number of Features", 1, 100000, no_features)
    no_top_words = support_functions.ask_for_int("Number of Top Words", 1, 10000, no_top_words)

    support_functions.startProgress("Running topics...")

    counter = 0.0
    total = float(max_topics + step - 1 - min_topics)
    for num_topics in xrange(min_topics, max_topics + step - 1, step):
        sub_folder = str(num_topics) + '_Topics'
        topic_modeling.main(output_sub_folder=sub_folder, enable_logging=False, interactive=False, no_topics=num_topics, no_top_words=no_top_words, no_features=no_features)
        create_visualizations.main(input_output_sub_folder=sub_folder, enable_logging=False)
        counter = counter + 1.0
        support_functions.progress(counter / total * 100.0)

    support_functions.endProgress()

if __name__ == "__main__":
    # execute only if run as a script
    main()
