#!/usr/bin/python
# -*- coding: utf-8

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import re
import stop_words

def run_model(_vectorizer, texts, no_features):
    vectorizer = _vectorizer(max_df=0.95, min_df=2, ngram_range=(0,3), max_features=no_features, preprocessor=no_number_preprocessor, stop_words=stop_words.STOP_WORDS)
    fitted = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names()

    return vectorizer, fitted, feature_names

def run_nmf(texts, no_topics, no_features):
    # NMF is able to use tf-idf
    vectorizer, fitted, feature_names = run_model(TfidfVectorizer, texts, no_features)
    # Run NMF
    model = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd', n_jobs=-1).fit(fitted)

    return vectorizer, fitted, feature_names, model

def run_lda(texts, no_topics, no_features):
    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    vectorizer, fitted, feature_names = run_model(_vectorizer=CountVectorizer, texts=texts, no_features=no_features)
    # Run LDA
    model = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0, n_jobs=-1).fit(fitted)

    return vectorizer, fitted, feature_names, model

def no_number_preprocessor(tokens):
    r = re.sub('(\d)+', '', tokens.lower())
    #r = re.sub('[!@#$%^ˆˇ&*~]', '', r)
    return r
