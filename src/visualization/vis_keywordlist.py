#!/usr/bin/python
# -*- coding: utf-8

import os
def create_topics_list(topics, output_folder, num_display=25, details=False):
    filename = "keywords"
    max_count_keywords = 0
    for topic in topics:
        if len(topic['keywords']) > max_count_keywords:
            max_count_keywords = len(topic['keywords'])
    if num_display > 0:
        max_count_keywords = min(max_count_keywords, num_display)
    rowspan = int(max_count_keywords / 5)
    if max_count_keywords % 5 != 0:
        rowspan = rowspan + 1
    if details:
        rowspan = 2 * rowspan
        filename = filename + "_details"
    filename = filename + ".html"

    with open(os.path.join(output_folder, filename), "w") as file:
        file.write(u"<head><meta charset=\"utf-8\"><link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\"><link rel=\"stylesheet\" href=\"https://code.getmdl.io/1.3.0/material.indigo-pink.min.css\"><script defer src=\"https://code.getmdl.io/1.3.0/material.min.js\"></script></head><body>")
        file.write(u"<table class=\"mdl-data-table mdl-js-data-table mdl-shadow--2dp\"><thead><tr><th class=\"mdl-data-table__cell--non-numeric\">ID</th><th class=\"mdl-data-table__cell--non-numeric\">Name</th><th cellspan='5' class=\"mdl-data-table__cell--non-numeric\">Keywords</th></tr></thead><tbody>")

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
            file.write(u"</td>")
            for row in range(rowspan):
                if row == 2: file.write(u"<tr>")
                for cell in range(5):
                    if len(topic['keywords']) <= ((row * 5) + cell):
                         file.write(u"<td class=\"mdl-data-table__cell--non-numeric\"></td>")
                    else:
                        keyword = topic['keywords'][(row * 5) + cell]
                        file.write(u"<td class=\"mdl-data-table__cell--non-numeric\"><em>")
                        file.write(str((row * 5) + cell + 1) + ") " + keyword['name'].encode('utf8'))
                        file.write(u"</em></td>")
                if details:
                    file.write(u"</tr><tr>")
                    for cell in range(5):
                        if len(topic['keywords']) <= ((row * 5) + cell):
                             file.write(u"<td class=\"mdl-data-table__cell--non-numeric\"></td>")
                        else:
                            keyword = topic['keywords'][(row * 5) + cell]
                            file.write(u"<td style='text-align:right;'>")
                            file.write(u"{:10.4f}".format(keyword['probability']))
                            file.write(u"</td>")
                file.write(u"</tr>")
            file.write(u"</tr></tbody>")
        file.write(u"</table></body>")
