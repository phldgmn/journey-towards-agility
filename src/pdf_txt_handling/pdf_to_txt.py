#!/usr/bin/python
# -*- coding: utf-8

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import support_functions
from cStringIO import StringIO
import os
import sys
import pdfminer
import codecs
from datetime import datetime
import unicodedata
from openpyxl import Workbook
from joblib import Parallel, delayed
from tqdm import tqdm

import PyPDF2
import textract

import warnings
warnings.filterwarnings("ignore")

def remove_control_characters(s):
    return u"".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def convert_pdf_to_txt_old(path):
    print path,
    sys.stdout.flush()
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        print ".",
        sys.stdout.flush()
    fp.close()
    print ""
    sys.stdout.flush()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

def convert_pdf_to_txt(path):
    pdf_file = open(path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    num_pages = pdf_reader.numPages
    count = 0
    text = ""

    while count < num_pages:
        page = pdf_reader.getPage(count)
        count = count + 1
        text = text + " " + page.extractText()

    if len(text) <= 1:
       text = textract.process(path, method='tesseract', language='eng')

    return text

def import_pdfs(input_folder, output_folder, counter=0.0, total_count=1.0, is_child_call=False, parallel=None):
    if not is_child_call:
        startTime = datetime.now()

    additional_subfolder = ""
    folder = os.listdir(input_folder)
    pdf_list = []

    counter = float(counter)
    total_count = float(total_count)

    if not is_child_call:
        support_functions.startProgress("parsing PDFs...")

    for obj in tqdm(folder):
        if os.path.isdir(os.path.join(input_folder, obj)):
            os.mkdir(os.path.join(output_folder, obj))
            counter = import_pdfs(os.path.join(input_folder, obj), os.path.join(output_folder, obj), counter=counter, total_count=total_count, is_child_call=True, parallel=parallel)
        elif ".pdf" in obj and not os.path.isfile(os.path.join(output_folder, obj.replace(".pdf", ".txt"))):
            if parallel is None:
                process_pdf_file(obj, input_folder, output_folder)
                counter = counter + 1
                support_functions.progress(counter / total_count * 100.0)
            else:
                pdf_list.append(os.path.join(input_folder, obj))

    if parallel is not None:
        parallel(delayed(process_pdf_file)(pdf_list[i], input_folder) for i in range(len(pdf_list)))
        counter = counter + len(pdf_list)
        support_functions.progress(counter / total_count * 100.0)

    if not is_child_call:
        support_functions.endProgress()
        print "duration: ", datetime.now() - startTime

    return counter

def process_pdf_file(obj, input_folder, output_folder):
    try:
        content = convert_pdf_to_txt(os.path.join(input_folder, obj))
        additional_subfolder = ""
    except Exception as e:
        #print e
        content = ""
        additional_subfolder = "encrypted"
        if not os.path.exists(os.path.join(output_folder, additional_subfolder)):
            os.mkdir(os.path.join(output_folder, additional_subfolder))

    content = content.decode('utf-8')

    with codecs.open(os.path.join(output_folder, additional_subfolder, obj.replace(".pdf", ".txt")), "w", encoding="utf8") as file:
        file.write(content)

def createJSON(input_folder, output_folder):
    files_in_dir = os.listdir(input_folder)
    combinedJSON = "["
    i=0
    for file_in_dir in files_in_dir:
        if ".txt" in file_in_dir:
            content = unicode("")

            with codecs.open(os.path.join(input_folder, file_in_dir), 'r', encoding="utf8") as content_file:
                content = unicode(content_file.read())
            content = remove_control_characters(content).encode('utf-8')
            content = content.replace("\"", "'").replace("\n", " ").replace("\r", "").replace("\\", "")

            if content and len(content) > 0:
                if len(combinedJSON) > 2: combinedJSON += ","
                json = "{ \"text\": \"" + content + "\", \"filename\": \"" + file_in_dir + "\", \"date\": \"2016-11-25\" }"
                combinedJSON += json
    combinedJSON += "]"

    with codecs.open(os.path.join(output_folder, "output.json"), 'w', encoding="utf8") as file:
        file.write(combinedJSON.decode('utf-8'))

def createCSV(input_folder, output_folder):
    files_in_dir = os.listdir(input_folder)
    combinedCSV = "text;filename;date\n"
    i=0
    for file_in_dir in files_in_dir:
        if ".txt" in file_in_dir:
            content = unicode("")

            with codecs.open(os.path.join(input_folder, file_in_dir), 'r', encoding="utf8") as content_file:
                content = unicode(content_file.read())
            content = remove_control_characters(content).encode('utf-8')
            content = content.replace(";", ",").replace("\n", " ").replace("\r", "").replace("\\", "")

            if content and len(content) > 0:
                if len(combinedCSV) > 2: combinedCSV += ","
                csv = content + ";" + file_in_dir + ";2016-11-25\n"
                combinedCSV += csv
    combinedCSV += ""

    with codecs.open(os.path.join(output_folder, "output.csv"), 'w', encoding="utf8") as file:
        file.write(combinedCSV.decode('utf-8'))

def createXLSX(input_folder, output_folder):
    files_in_dir = os.listdir(input_folder)
    wb = Workbook()
    ws = wb.active
    ws.append(["text", "filename", "date"])

    i=0
    for file_in_dir in files_in_dir:
        if ".txt" in file_in_dir:
            content = unicode("")

            with codecs.open(os.path.join(input_folder, file_in_dir), 'r', encoding="utf8") as content_file:
                content = unicode(content_file.read())
            content = remove_control_characters(content).encode('utf-8')

            if content and len(content) > 0:
                ws.append([content, file_in_dir, "2016-11-25"])

    wb.save(os.path.join(output_folder, "output.xlsx"))

def createMineMyTextFiles(input_folder, output_folder):
    files_in_dir = os.listdir(input_folder)
    wb = Workbook()
    ws = wb.active
    ws.append(["text", "date", "author", "year", "title", "filename"])

    combinedCSV = "text;date;author;year;title;filename\n"
    combinedJSON = "["

    i=0
    for file_in_dir in files_in_dir:
        if ".txt" in file_in_dir:
            fileNameParts = filter(None, file_in_dir.split(' - '))

            author = ""
            title = ""
            year = ""

            if len(fileNameParts) > 0:
                authorYear = fileNameParts[0];
                authorYearParts = filter(None, authorYear.split(' '))
                year = authorYearParts[-1]
                date = year + "-01-01"
                author = " ".join(authorYearParts[0:len(authorYearParts) - 1])
                title = " - ".join(fileNameParts[1:len(authorYearParts)])
                title = title.replace(".txt", "").strip()

            if len(author) <= 0 or len(title) <= 0 or len(year) <= 0 or not year.isdigit():
                author = ""
                title = ""
                date = ""
                year = ""
                parts = filter(None, file_in_dir.split('-'))

                if len(parts) > 0:
                    if len(year) <= 0:
                        year = parts[1]
                    if len(date) <= 0:
                        date = year + "-01-01"
                    if len(author) <= 0:
                        author = parts[0]
                    if len(title) <= 0:
                        title = "-".join(parts[2:len(parts)])
                        title = title.replace(".txt", "").strip()
                if not year.isdigit() and len(year) > 0 and len(filter(str.isdigit, year)) > 0:
                    year = int(filter(str.isdigit, year))
                    date = str(year) + "-01-01"
                if not year.isdigit() and len(author) > 0 and len(filter(str.isdigit, author)) > 0:
                    year = int(filter(str.isdigit, author))
                    date = str(year) + "-01-01"

            content = unicode("")

            with codecs.open(os.path.join(input_folder, file_in_dir), 'r', encoding="utf8") as content_file:
                content = unicode(content_file.read())
            content = remove_control_characters(content).encode('utf-8').strip()

            if content and len(content) > 0:
                ws.append([content, date, author, year, title, file_in_dir])

                contentCSV = content
                contentCSV = contentCSV.replace(";", ",").replace("\n", " ").replace("\r", "").replace("\\", "")

                if len(combinedCSV) > 2: combinedCSV += ","
                csv = contentCSV + ";" + file_in_dir + ";" + date + "\n"
                combinedCSV += csv

                contentJSON = content
                contentJSON = contentJSON.replace("\"", "'").replace("\n", " ").replace("\r", "").replace("\\", "")

                if len(combinedJSON) > 2: combinedJSON += ","
                json = "{ \"text\": \"" + contentJSON + "\", \"date\": \"" + date + "\", \"author\": \"" + author + "\", \"year\": " + str(year) + ", \"title\": \"" + title + "\", \"filename\": \"" + file_in_dir + "\" }"
                combinedJSON += json

    wb.save(os.path.join(output_folder, "output.xlsx"))

    with codecs.open(os.path.join(output_folder, "output.csv"), 'w', encoding="utf8") as file:
        file.write(combinedCSV.decode('utf-8'))

    combinedJSON += "]"

    with codecs.open(os.path.join(output_folder, "output.json"), 'w', encoding="utf8") as file:
        file.write(combinedJSON.decode('utf-8'))

def count_pdfs_recursively(folder):
    counter = 0
    for obj in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, obj)):
            counter = counter + count_pdfs_recursively(os.path.join(folder, obj))
        elif ".pdf" in obj:
            counter = counter + 1
    return counter

def main(_input_folder=None, _createMineMyTextFiles=False):
    dirname = os.path.abspath('.')
    if _input_folder is None:
        input_folder = os.path.join(dirname, 'input_pdf')
    else:
        input_folder = _input_folder
    output_folder = os.path.join(dirname, 'input_raw')
    archive_folder = os.path.join(dirname, 'archive')

    support_functions.prepare_folders(input_folder, output_folder, archive_folder)

    parallel = None #Parallel(n_jobs=2)
    import_pdfs(input_folder, output_folder, total_count=count_pdfs_recursively(input_folder), parallel=parallel)

    if _createMineMyTextFiles:
        createMineMyTextFiles(input_folder, output_folder)

if __name__ == "__main__":
    main(_createMineMyTextFiles=True)
