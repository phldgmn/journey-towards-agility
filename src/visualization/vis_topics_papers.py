#!/usr/bin/python
# -*- coding: utf-8

import os
from tqdm import tqdm

def create_topics_list(documents, topics, output_folder, details=False):
    for topic in tqdm(topics):
        if not 'documents' in topic:
            topic['documents'] = []
        if not 'sig_documents' in topic:
            topic['sig_documents'] = 0
        for document in documents:
            if topic['id'] in range(0, len(document['topics'])) and document['topics'][topic['id']] > 0:
                topic['documents'].append(document)
                if document['topics'][topic['id']] > 0.01:
                    topic['sig_documents'] = topic['sig_documents'] + 1
            #else: print topic['id'], document['file_name']
        topic['documents'] = sorted(topic['documents'], key=lambda document: document['topics'][topic['id']], reverse=True)

    filename = "topics_papers"
    if details:
        rowspan = 10
        filename = filename + "_details"
    else:
        rowspan = 5
    filename = filename + ".html"

    with open(os.path.join(output_folder, filename), "w") as file:
        file.write(u"<head><meta charset=\"utf-8\"><link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\"><link rel=\"stylesheet\" href=\"https://code.getmdl.io/1.3.0/material.indigo-pink.min.css\"><script defer src=\"https://code.getmdl.io/1.3.0/material.min.js\"></script></head><body>")
        file.write(u"<table class=\"mdl-data-table mdl-js-data-table mdl-shadow--2dp\"><thead><tr><th class=\"mdl-data-table__cell--non-numeric\">ID</th><th class=\"mdl-data-table__cell--non-numeric\">Name</th><th cellspan='5' class=\"mdl-data-table__cell--non-numeric\">Papers</th></tr></thead><tbody>")

        for topic in topics:
            file.write(u"<tr>")
            file.write(u"<td rowspan='" + str(rowspan) + "' class=\"mdl-data-table__cell--non-numeric\">" + str(topic['id']) + u"</td>")
            file.write(u"<td rowspan='" + str(rowspan) + "' class=\"mdl-data-table__cell--non-numeric\">")
            if 'name' in topic:
                file.write(topic['name'].encode('utf8'))
            if 'proportion' in topic:
                if 'name' in topic:
                    file.write(u"<br/>")
                file.write(u"{:10.3f}%".format(topic['proportion']*100))
            file.write(u"<br/>")
            file.write(str(topic['sig_documents']) + u" papers > 0.01")
            file.write(u"</td>")
            for row in range(0, 5):
                if row == 2: file.write(u"<tr>")
                for cell in range(0, 5):
                    if len(topic['documents']) <= (row * 5) + cell:
                        file.write(u"<td style='text-align:right;'></td>")
                    else:
                        document = topic['documents'][(row * 5) + cell]
                        file.write(u"<td class=\"mdl-data-table__cell--non-numeric\"><em>")
                        file.write(str((row * 5) + cell + 1) + ") " + get_document_display_name(document))
                        file.write(u"</em></td>")
                if details:
                    file.write(u"</tr><tr>")
                    for cell in range(0, 5):
                        if len(topic['documents']) <= (row * 5) + cell:
                            file.write(u"<td style='text-align:right;'></td>")
                        else:
                            document = topic['documents'][(row * 5) + cell]
                            file.write(u"<td style='text-align:right;'>")
                            file.write(u"{:10.10f}".format(document['topics'][topic['id']]))
                            file.write(u"</td>")
                file.write(u"</tr>")
            file.write(u"</tr></tbody>")
        file.write(u"</table></body>")

def get_document_display_name(document):
    authors = ''
    for author_key, author_obj in document['authors'].iteritems():
        author_key = author_key.strip()
        if len(authors) > 0 and (len(authors) < 2 or authors[-2:] != ', '): authors = authors + ', '
        if len(author_key) <= 1:
            continue
        else:
            authors = authors + author_key
    if len(authors) <= 1:
        return document['file_name'].replace('.txt', '')
    else:
        return authors + ' (' + str(document['year']) + '): ' + document['title']
