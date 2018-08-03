#!/usr/bin/python
# -*- coding: utf-8

import os
def create_topics_list(journals, topics, output_folder, details=False):
    for topic in topics:
        if not 'journals' in topic:
            topic['journals'] = []
        for journal in journals:
            if topic['id'] in range(0, len(journal['topics'])) and journal['topics'][topic['id']] > 0:
                topic['journals'].append(journal)
            #else: print topic['id'], journal['name']
        topic['journals'] = sorted(topic['journals'], key=lambda journal: journal['topics'][topic['id']], reverse=True)

    filename = "topics_journals"
    if details:
        rowspan = 10
        filename = filename + "_details"
    else:
        rowspan = 5
    filename = filename + ".html"

    with open(os.path.join(output_folder, filename), "w") as file:
        file.write(u"<head><meta charset=\"utf-8\"><link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\"><link rel=\"stylesheet\" href=\"https://code.getmdl.io/1.3.0/material.indigo-pink.min.css\"><script defer src=\"https://code.getmdl.io/1.3.0/material.min.js\"></script></head><body>")
        file.write(u"<table class=\"mdl-data-table mdl-js-data-table mdl-shadow--2dp\"><thead><tr><th class=\"mdl-data-table__cell--non-numeric\">ID</th><th class=\"mdl-data-table__cell--non-numeric\">Name</th><th cellspan='5' class=\"mdl-data-table__cell--non-numeric\">Journals</th></tr></thead><tbody>")

        for topic in topics:
            file.write(u"<tr>")
            file.write(u"<td rowspan='" + str(rowspan) + "' class=\"mdl-data-table__cell--non-numeric\">" + str(topic['id']) + u"</td>")
            if 'name' in topic:
                file.write(u"<td rowspan='" + str(rowspan) + "' class=\"mdl-data-table__cell--non-numeric\">" + topic['name'].encode('utf8') + u"</td>")
            else:
                file.write(u"<td rowspan='" + str(rowspan) + "' class=\"mdl-data-table__cell--non-numeric\"></td>")
            for row in range(0, 5):
                if row == 2: file.write(u"<tr>")
                for cell in range(0, 5):
                    if len(topic['journals']) <= (row * 5) + cell:
                        file.write(u"<td style='text-align:right;'></td>")
                    else:
                        journal = topic['journals'][(row * 5) + cell]
                        file.write(u"<td class=\"mdl-data-table__cell--non-numeric\"><em>")
                        file.write(str((row * 5) + cell + 1) + ") " + journal['name'])
                        file.write(u"</em></td>")
                if details:
                    file.write(u"</tr><tr>")
                    for cell in range(0, 5):
                        if len(topic['journals']) <= (row * 5) + cell:
                            file.write(u"<td style='text-align:right;'></td>")
                        else:
                            journal = topic['journals'][(row * 5) + cell]
                            file.write(u"<td style='text-align:right;'>")
                            file.write(u"{:10.10f}".format(journal['topics'][topic['id']]))
                            file.write(u"</td>")
                file.write(u"</tr>")
            file.write(u"</tr></tbody>")
        file.write(u"</table></body>")
