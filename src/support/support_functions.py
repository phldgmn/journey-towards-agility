#!/usr/bin/python
# -*- coding: utf-8

import pyLDAvis.sklearn
import jsonlines
import os
import sys
import shutil
import datetime
import funcy as fp

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print "Topic %d:" % (topic_idx)
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]])

def read_dataset(folder):
    papers = []
    journals = {}
    texts = []
    with jsonlines.open(os.path.join(folder, 'papers.jsonl')) as reader:
        for obj in reader:
            paper = obj[-1]
            papers.append(paper)
            text = paper['text']
            text = prepare_text(text)
            texts.append(text)

    with jsonlines.open(os.path.join(folder, 'journals.jsonl')) as reader:
        for obj in reader:
            journal = obj[-1]
            journals[journal['name']] = journal

    return papers, journals, texts

def prepare_text(text):
    text = text.replace('^', '').replace('ˆ', '').replace('ˇ', '').replace('~', '')
    text = text.replace(u'\u0302', '').replace(u'\u02C7', '')

    return text

def read_text_mining_result(topic_file, papers_file, journals_file):
    papers = []
    topics = []
    journals = []
    with jsonlines.open(topic_file) as reader:
        for obj in reader:
            topics.append(obj)
    with jsonlines.open(papers_file) as reader:
        for obj in reader:
            papers.append(obj)
    with jsonlines.open(journals_file) as reader:
        for obj in reader:
            journals.append(obj)

    return topics, papers, journals

def export_lda_visualization(output_folder, model, fitted, vectorizer):
    panel = pyLDAvis.sklearn.prepare(model, fitted, vectorizer, mds='tsne', sort_topics=True)
    pyLDAvis.save_html(panel, os.path.join(output_folder, 'ldavis.html'))

def write_dataset(output_folder, type, documents):
    with jsonlines.open(os.path.join(output_folder, type + '.jsonl'), mode='w') as writer:
        for paper in documents:
            writer.write(paper)

def prepare_folders(input_folder, output_folder, archive_folder):
    if not os.path.exists(input_folder):
        os.mkdir(input_folder)
    if os.path.exists(output_folder) and os.listdir(output_folder) != []:
        shutil.move(output_folder, os.path.join(archive_folder, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

def ask_for_int(text, min, max, default):
    input = None
    while input is None or (isinstance(input, int) and (input < min and input > max)):
        try:
            input_raw = raw_input(text + " (" + str(min) + ".." + str(max) + ", default " + str(default) + "): ")
            if input_raw is None or len(input_raw) <= 0:
                input = default
            else:
                input = int(input_raw)
        except Exception as e:
            print e
            input = default
            pass
    return input

def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    if x != progress_x:
        sys.stdout.write("#" * (x - progress_x))
        sys.stdout.flush()
        progress_x = x

def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()

def sort_topics(lda_model, dtm, vectorizer, **kwargs):
    vocab = pyLDAvis.sklearn._get_vocab(vectorizer)
    doc_lengths = pyLDAvis.sklearn._get_doc_lengths(dtm)
    term_frequency = pyLDAvis.sklearn._get_term_freqs(dtm)
    topic_term_dists = pyLDAvis.sklearn._get_topic_term_dists(lda_model)
    doc_topic_dists = pyLDAvis.sklearn._get_doc_topic_dists(lda_model, dtm)

    topic_term_dists = pyLDAvis._prepare._df_with_names(topic_term_dists, 'topic', 'term')
    doc_topic_dists  = pyLDAvis._prepare._df_with_names(doc_topic_dists, 'doc', 'topic')
    term_frequency   = pyLDAvis._prepare._series_with_name(term_frequency, 'term_frequency')
    doc_lengths      = pyLDAvis._prepare._series_with_name(doc_lengths, 'doc_length')
    vocab            = pyLDAvis._prepare._series_with_name(vocab, 'vocab')
    pyLDAvis._prepare._input_validate(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency)
    R = min(30, len(vocab))

    topic_freq       = (doc_topic_dists.T * doc_lengths).T.sum()
    # topic_freq       = np.dot(doc_topic_dists.T, doc_lengths)
    topic_proportion = (topic_freq / topic_freq.sum()).sort_values(ascending=False)
    topic_order      = topic_proportion.index.tolist()
    return topic_order, topic_proportion

    # reorder all data based on new ordering of topics
    #topic_freq       = topic_freq[topic_order]
    #topic_term_dists = topic_term_dists.iloc[topic_order]
    #doc_topic_dists  = doc_topic_dists[topic_order]
