#!/usr/bin/python
# -*- coding: utf-8

import sys
import os

import support_functions
import tm_functions

def main(output_sub_folder='', enable_logging=True, interactive=True, no_features=1000, no_topics=25, no_top_words=100):
    dirname = os.path.abspath('.')
    input_folder = os.path.join(dirname, 'input')
    output_folder = os.path.join(dirname, 'output', output_sub_folder)
    archive_folder = os.path.join(dirname, 'archive')

    support_functions.prepare_folders(input_folder, output_folder, archive_folder)

    if interactive:
        no_topics = support_functions.ask_for_int("Number of Topics", 0, 1000, no_topics)
        #no_features = support_functions.ask_for_int("Number of Features", 0, 100000, no_features)

    papers, journals, texts = support_functions.read_dataset(input_folder)
    if enable_logging:
        print len(papers), " papers ", len(journals), " journals ", len(texts), " texts "
    vectorizer, fitted, feature_names, model = tm_functions.run_lda(texts, no_topics, no_features)
    doc_topic = model.transform(fitted)

    # sorts by topic distribution, just as ldaVIS normally would
    ordering, topic_proportion = support_functions.sort_topics(model, fitted, vectorizer)

    topics = []
    #for topic_idx, topic in enumerate(model.components_):
    for new_index, old_index in enumerate(ordering):
        keywords = []
        topic = model.components_[old_index]
        for i in topic.argsort()[:-no_top_words - 1:-1]:
            keywords.append({
                'name': feature_names[i],
                'probability': topic[i]
            })

        topics.append({
            'id': new_index,
            'name': 'Topic ' + str(new_index + 1),
            'keywords': keywords,
            'proportion': topic_proportion[old_index]
        })

    for i in range(doc_topic.shape[0]):
        papers[i]['topics'] = []
        #for j in range(0, len(doc_topic[i])):
        for new_index, old_index in enumerate(ordering):
            papers[i]['topics'].append(doc_topic[i][old_index])

    for paper in papers:
        if len(journals[paper['journal']]['topics']) <= 0:
            journals[paper['journal']]['topics'] = [[0 for topic in range(len(topics))] for topic in range(len(topics))]
        for topic in range(len(topics)):
            journals[paper['journal']]['topics'][topic].append(paper['topics'][topic])

    for journal_key, journal in journals.iteritems():
        for topic in range(len(journal['topics'])):
            journal['topics'][topic] = reduce(lambda x, y: x + y, journal['topics'][topic]) / len(journal['topics'][topic])

    support_functions.export_lda_visualization(output_folder, model, fitted, vectorizer)

    support_functions.write_dataset(output_folder, 'topics', topics)
    support_functions.write_dataset(output_folder, 'papers', papers)
    _journals = []
    for journal_key, journal in journals.iteritems():
        _journals.append(journal)

    support_functions.write_dataset(output_folder, 'journals', _journals)

if __name__ == "__main__":
    # execute only if run as a script
    main()
