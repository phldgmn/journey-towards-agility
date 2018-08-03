# -*- coding: utf-8 -*-
"""
An example for topic modeling evaluation with the [lda package](http://pythonhosted.org/lda/).
"""

import matplotlib as mpl
mpl.use('Agg')

import logging
import sys
import lda  # for the Reuters dataset

import sys
sys.path.insert(0, "..")
sys.path.insert(0, "../tmtoolkit")

from tmtoolkit.utils import pickle_data
from tmtoolkit.topicmod import tm_lda
from tmtoolkit.topicmod.evaluate import results_by_parameter
from tmtoolkit.topicmod.model_io import print_ldamodel_topic_words, print_ldamodel_doc_topics, \
    save_ldamodel_summary_to_excel, save_ldamodel_to_pickle
from tmtoolkit.topicmod.visualize import plot_eval_results
from tmtoolkit.dtm import save_dtm_to_pickle, load_dtm_from_pickle

import matplotlib.pyplot as plt
plt.style.use('ggplot')


logging.basicConfig(level=logging.INFO)
tmtoolkit_log = logging.getLogger('tmtoolkit')
tmtoolkit_log.setLevel(logging.INFO)
tmtoolkit_log.propagate = True

logger = logging.getLogger('lda')
logger.setLevel(logging.WARNING)

import sys
import inspect

def get_size(obj, seen=None):
    """Recursively finds size of objects in bytes"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if hasattr(obj, '__dict__'):
        for cls in obj.__class__.__mro__:
            if '__dict__' in cls.__dict__:
                d = cls.__dict__['__dict__']
                if inspect.isgetsetdescriptor(d) or inspect.ismemberdescriptor(d):
                    size += get_size(obj.__dict__, seen)
                break
    if isinstance(obj, dict):
        size += sum((get_size(v, seen) for v in obj.values()))
        size += sum((get_size(k, seen) for k in obj.keys()))
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum((get_size(i, seen) for i in obj))
    return size


## OPTIONS
initialize_data = False
save_models = False

if __name__ == '__main__':   # this is necessary for multiprocessing on Windows!
    # load the Reuters News dataset provided by lda
    print('loading data')

    if initialize_data:
        from jsonlines import jsonlines
        from tmtoolkit.preprocess import TMPreproc
        corpus = {}
        with jsonlines.open('../../input/papers.jsonl') as reader:
            for paper_container in reader:
                if isinstance(paper_container, list):
                    paper = paper_container[1]
                else:
                    paper = paper_container
                if paper['text'] is None or len(paper['text']) <= 0:
                    continue
                corpus[paper['file_name'].encode("utf-8").decode("utf-8") ] = paper['text']

        preproc = TMPreproc(corpus, language='english')
        print(len(corpus.keys()), " keys", get_size(corpus), ' bytes')
        preproc.tokenize().tokens_to_lowercase().clean_tokens(remove_longer_than=500)
        doc_labels, vocab, dtm = preproc.get_dtm()
        save_dtm_to_pickle(dtm, vocab, doc_labels, './data.pickle')
    else:
        dtm, vocab, doc_labels = load_dtm_from_pickle('./data.pickle')

    print('%d documents with vocab size %d' % (len(doc_labels), len(vocab)))
    assert dtm.shape[0] == len(doc_labels)
    assert dtm.shape[1] == len(vocab)

    # evaluate topic models with different parameters
    const_params = dict(n_iter=150, random_state=1, refresh=10, eta=0.1)    # beta is called eta in the 'lda' package
    ks = list(range(10, 70, 2)) + list(range(73, 100, 3))
    varying_params = [dict(n_topics=k, alpha=1.0/k) for k in ks]

    # this will evaluate all models in parallel using the metrics in tm_lda.DEFAULT_METRICS
    # still, this will take some time
    print('evaluating %d topic models' % len(varying_params))
    models = tm_lda.evaluate_topic_models(dtm, varying_params, const_params,
                                          return_models=save_models)  # retain the calculated models

    if save_models:
        # save the results as pickle
        print('saving results')
        pickle_data(models, 'results/lda_evaluation_results.pickle')

    # plot the results
    print('plotting evaluation results')
    results_by_n_topics = results_by_parameter(models, 'n_topics')
    plot_eval_results(results_by_n_topics, xaxislabel='num. topics k',
                      title='Evaluation results for alpha=1/k, beta=0.1', figsize=(8, 6))
    plt.savefig('results/lda_evaluation_plot.png')
    plt.show()

    # print the distributions of this model
    n_topics_best_model = 0

    if n_topics_best_model > 0 and models is not None:
        best_model = dict(results_by_n_topics)[n_topics_best_model]['model']

        print('saving final model with n_topics=%d' % n_topics_best_model)
        save_ldamodel_to_pickle('data/lda_evaluation_finalmodel.pickle', best_model, vocab, doc_labels, dtm)

        #print('printing final model')
        #print_ldamodel_topic_words(best_model.topic_word_, vocab)
        #print_ldamodel_doc_topics(best_model.doc_topic_, doc_labels)

        # export it as Excel file
        excel_file = 'data/lda_evaluation_summary.xlsx'
        print('saving model summary as Excel file to `%s`' % excel_file)
        save_ldamodel_summary_to_excel(excel_file,
                                       best_model.topic_word_, best_model.doc_topic_,
                                       doc_labels, vocab, dtm=dtm)
