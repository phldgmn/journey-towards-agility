#!/usr/bin/python
# -*- coding: utf-8

import os
from tqdm import tqdm

def create_outlet_details(outlets, documents, output_folder):
    outlets = sorted(outlets, key=lambda outlet: outlet['name'])

    for outlet in tqdm(outlets):
        for document in documents:
            if 'documents' not in outlet:
                outlet['documents'] = []
            if document['journal'] == outlet['name']:
                outlet['documents'].append(document)

    for outlet in tqdm(outlets):
        min_year = 9999
        max_year = 0000
        for document in outlet['documents']:
            if min_year > document['year']:
                min_year = document['year']
            if max_year < document['year']:
                max_year = document['year']

        outlet['min-year'] = min_year
        outlet['max-year'] = max_year

    filename = "outlet_details.html"

    with open(os.path.join(output_folder, filename), "w") as file:
        file.write(u"<head><meta charset=\"utf-8\"><link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\"><link rel=\"stylesheet\" href=\"https://code.getmdl.io/1.3.0/material.indigo-pink.min.css\"><script defer src=\"https://code.getmdl.io/1.3.0/material.min.js\"></script></head><body>")
        file.write(u"<table class=\"mdl-data-table mdl-js-data-table mdl-shadow--2dp\"><thead><tr>")
        file.write(u"<th class=\"mdl-data-table__cell--non-numeric\">Name</th>")
        file.write(u"<th class=\"mdl-data-table__cell--non-numeric\">Type</th>")
        file.write(u"<th class=\"mdl-data-table__cell--numeric\"># Papers</th>")
        file.write(u"<th class=\"mdl-data-table__cell--numeric\">First Year</th>")
        file.write(u"<th class=\"mdl-data-table__cell--numeric\">Last Year</th>")
        file.write(u"</tr></thead><tbody>")

        for outlet in outlets:
            file.write(u"<tr>")
            file.write(u"<td class=\"mdl-data-table__cell--non-numeric\">" + str(outlet['name']) + u"</td>")
            file.write(u"<td class=\"mdl-data-table__cell--non-numeric\">" + str(outlet['type']) + u"</td>")
            file.write(u"<td class=\"mdl-data-table__cell--numeric\">" + str(len(outlet['documents'])) + u"</td>")
            if outlet['min-year'] == 9999:
                file.write(u"<td class=\"mdl-data-table__cell--numeric\">--</td>")
            else:
                file.write(u"<td class=\"mdl-data-table__cell--numeric\">" + str(outlet['min-year']) + u"</td>")
            if outlet['max-year'] == 0:
                file.write(u"<td class=\"mdl-data-table__cell--numeric\">--</td>")
            else:
                file.write(u"<td class=\"mdl-data-table__cell--numeric\">" + str(outlet['max-year']) + u"</td>")
            file.write(u"</tr>")
        file.write(u"</tbody></table></body>")
