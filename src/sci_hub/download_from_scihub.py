#!/usr/bin/python
# -*- coding: utf-8

import os
import csv
from scihub import SciHub
import sys
import urllib3
import logging
import warnings

dirname = os.path.abspath('..')
output_folder = os.path.join(dirname, 'input_pdf')

def main():
    sh = SciHub()
    print "expecting csv-file (tab-separated) with columns (case sensitive!): "
    columns = ["Author", "Year", "Title", "Secondary Title", "ISBN/ISSN", "URL", "DOI"]
    print columns
    input_path = raw_input("read papers from file: ").strip()
    google_abuse = raw_input("get google abuse by openening " + "https://scholar.google.com/scholar?q=abc&start=0" + " and paste the value of the google_abuse key: ").strip()

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    failed = []

    #startProgress('downloading paper from sci hub...')
    counter = 0.0
    row_count = 1.0

    with open(input_path, 'rb') as csvfile:
        row_count = sum(1 for row in csvfile)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger = logging.getLogger()
    logger.disabled = True
    warnings.filterwarnings("ignore", module='bs4')

    with open(input_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        for row in reader:
            author = row[columns.index("Author")]
            year = row[columns.index("Year")]
            title = row[columns.index("Title")]
            url = row[columns.index("URL")]
            doi = row[columns.index("DOI")]
            if author == "Author" or year == "Year" or title == "Title" or url == "URL" or doi == "DOI":
                continue

            identifier = None
            if url is not None and len(url) > 0:
                identifier = url
            elif doi is not None and len(doi) > 0:
                identifier = doi
                continue
            else:
                identifier = title

            filename = str(author) + "-" + str(year) + "-" + str(title[:min(20, len(title) - 1)]) + ".pdf"
            filename = filename.replace(" ", "_")

            try:
                if not download_and_save(sh, identifier, output_folder, filename):
                    identifier = search_paper(sh, author, year, title, google_abuse)
                    if not download_and_save(sh, identifier, output_folder, filename):
                        raise Exception("could not fetch article: " + str(author) + " | " + str(year) + " | " + str(url) + " | " + str(doi) + ": " + identifier)
            except Exception as e:
                print e
                failed.append(str(author) + ' (' + str(year) + ')')

            counter = counter + 1.0
            #progress(counter / row_count)

    #endProgress()
    logger.disabled = False
    print len(failed), ' failed: ', failed

def search_paper(sh, author, year, title, google_abuse):
    results = sh.search(author + ' ' + year + ' ' + ' ' + title, 1, google_abuse=google_abuse)

    if 'papers' in results and len(results) > 0: return results['papers'][0]['url']
    else: return None

def download_and_save(sh, identifier, output_folder, filename):
    print "trying to download: ", identifier
    result = sh.fetch(identifier=identifier)

    if result is None or 'pdf' not in result or result['pdf'] is None:
        print 'invalid result: ', result
        return False

    if 'err' in result:
        print pdf['err']

    with open(os.path.join(output_folder, filename), 'wb') as f:
        f.write(result['pdf'])

    return True

def startProgress(title):
    global progress_x
    sys.stdout = open(os.devnull, "w")
    sys.__stdout__.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
    sys.__stdout__.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    if x != progress_x:
        sys.__stdout__.write("#" * (x - progress_x))
        sys.__stdout__.flush()
        progress_x = x

def endProgress():
    sys.__stdout__.write("#" * (40 - progress_x) + "]\n")
    sys.__stdout__.flush()
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
