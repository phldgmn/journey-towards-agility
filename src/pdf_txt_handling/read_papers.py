#!/usr/bin/python
# -*- coding: utf-8

import os
import shutil
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
from os.path import splitext
import json
import jsonlines
import unicodedata
import codecs
from tqdm import tqdm

dirname = os.path.abspath('.')
input_folder = os.path.join(dirname, 'input_raw')
output_folder = os.path.join(dirname, 'input')
archive_folder = os.path.join(dirname, 'archive')

def main():
    prepare_folders()

    journals = {}
    papers = {}
    subfolders_to_check = ['conferences', 'journals', 'top_journals']
    for subfolder in subfolders_to_check:
        journals_, papers_ = read_journals(os.path.join(input_folder, subfolder))
        journals.update(journals_)
        papers.update(papers_)

    write_papers(output_folder, papers)
    write_journals(output_folder, journals)

def prepare_folders():
    if not os.path.exists(input_folder):
        os.mkdir(input_folder)
    if os.path.exists(output_folder) and os.listdir(output_folder) != []:
        shutil.move(output_folder, os.path.join(archive_folder, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

def read_journals(folder):
    journals = {}
    papers = {}
    type = ''
    if 'journal' in folder:
        type = 'journal'
    elif 'conference' in folder:
        type = 'conference'

    if not os.path.isdir(folder):
        return journals, papers

    for journal_folder in tqdm(os.listdir(folder)):
        if not os.path.isdir(os.path.join(folder, journal_folder)):
            continue
        journals[journal_folder] = {
            'name': journal_folder,
            'type': type,
            'topics': []
        }
        papers.update(read_papers(os.path.join(folder, journal_folder), journal_folder))

    return journals, papers

def read_papers(folder, journal_name):
    papers = {}

    for paper_file in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, paper_file)) or paper_file.startswith('.'):
            continue

        paper_file_name = '.'.join(splitext(paper_file)[0:-1])

        year = parse_year(paper_file_name)
        authors_short = paper_file.split(' - ')[0].strip()
        title = ' - '.join(paper_file.split(' - ')[2:]).strip()

        single_authors = clean_authors(authors_short).split(',')

        try:
            with codecs.open(os.path.join(folder, paper_file), 'r', 'utf-8') as file:
                lines = file.readlines()
        except:
            with codecs.open(os.path.join(folder, paper_file), 'r', 'latin-1') as file:
                lines = file.readlines()

        authors = {}
        for author in single_authors:
            author = unicode(author.strip(), 'utf-8')
            for i in range(0, min(50, len(lines))):
                if author in lines[i]:
                    authors[author] = { 'main': lines[i].replace('\n', '').strip() }
                elif i > 0 and author in lines[i - 1]:
                    authors[author]['sub1'] = lines[i].replace('\n', '').strip()
                elif i > 1 and author in lines[i - 2]:
                    authors[author]['sub2'] = lines[i].replace('\n', '').strip()

        text = '\n'.join(lines)

        paper = {
            'file_name': paper_file,
            'year': year,
            'title': title,
            'authors_short': authors_short,
            'authors': authors,
            'journal': journal_name,
            'text': text
        }
        papers[paper['file_name']] = paper

    return papers


def clean_authors(authors):
    stopwords = ['et al.', 'et. al.', 'et. al', 'et al']
    authors_tmp = authors
    for stopword in stopwords:
        authors_tmp = authors_tmp.replace(stopword, '')
    authors_tmp = authors_tmp.replace('and', ',')
    authors_tmp = authors_tmp.replace('&', ',')
    authors_tmp = authors_tmp.replace(', ', ',')
    return authors_tmp.strip()

def parse_year(paper_file_name):
    year = 0
    for upper_part in paper_file_name.split(' - '):
        upper_part = upper_part.strip()
        for lower_part in upper_part.split(' '):
            lower_part = lower_part.strip()
            if len(lower_part) == 4 and lower_part.isdigit() and (lower_part.startswith('19') or lower_part.startswith('20')):
                year = int(lower_part)
                break
        if year > 0:
            break
    if year <= 0:
        raise Exception(paper_file_name)
    return year

def write_papers(output_folder, papers):
    with jsonlines.open(os.path.join(output_folder, 'papers.jsonl'), mode='w') as writer:
        for paper in tqdm(papers.iteritems()):
            writer.write(paper)

def write_journals(output_folder, journals):
    with jsonlines.open(os.path.join(output_folder, 'journals.jsonl'), mode='w') as writer:
        for journal in tqdm(journals.iteritems()):
            try:
                writer.write(journal)
            except Exception as e:
                print(journal)
                print(e)

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
